from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction as db_transaction  # for atomic operations
from .models import Account, Category, Transaction
from .serializers import AccountSerializer, CategorySerializer, TransactionSerializer
from .filters import TransactionFilter
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes



# region tests only remove

# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.response import Response

# @api_view(['GET'])
# @permission_classes([permissions.IsAuthenticated])
# def test_auth(request):
#     return Response({"message": f"Hello, {request.user.username}!"})


# endregion

# Atomic usage explanation:
"""
When it's all or none situation.

For example:

You have some Ecomm app and someone submits an order. You need to create an order, transaction record, remove items from werehouse etc,

but then turns out that some operation at the end failed (For example payment processing, because client doesn't have enough money in his account).

Without atomic you will already have order and transaction created in the db and items are gone. Now you need to revert the changes somehow manually.

With atomic, when exception is raised, all changes will be reverted automatically like nothing happended
"""


class BaseUserOwnedViewSet(viewsets.ModelViewSet):
    """Base viewset that automatically filters by user."""
    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        # Filter out deleted if model has 'deleted' field
        if hasattr(self.queryset.model, 'deleted'):
            queryset = queryset.filter(deleted=False)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@extend_schema(
    tags=["Accounts"],
    summary="Accounts",
    description="Manage user accounts and balances",
    parameters=[
        OpenApiParameter(
            name="page",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Page number for pagination",
        ),
        OpenApiParameter(
            name="page_size",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Number of results per page (max 100, default 10)",
        ),
    ],
)
class AccountViewSet(BaseUserOwnedViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

@extend_schema(
    tags=["Categories"],
    summary="Categories",
    description="Manage transaction categories",
    parameters=[
        OpenApiParameter(
            name="page",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Page number for pagination",
        ),
        OpenApiParameter(
            name="page_size",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Number of results per page (max 100, default 10)",
        ),
    ],
)
class CategoryViewSet(BaseUserOwnedViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema(
    tags=["Transactions"],
    summary="Transactions",
    description="""Manage financial transactions with automatic balance updates.
    
    **Important Validation Rules:**
    - Categories must be owned by the authenticated user
    - Category type MUST match transaction type:
      - Income transactions require income categories
      - Expense transactions require expense categories
    - Violating these rules will return a 400 Bad Request error
    
    **Automatic Balance Updates:**
    - Creating/updating/deleting transactions automatically updates the linked account balance
    - Income transactions increase account balance
    - Expense transactions decrease account balance
    """,
    parameters=[
        OpenApiParameter(
            name="page",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Page number for pagination",
        ),
        OpenApiParameter(
            name="page_size",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Number of results per page (max 100, default 10)",
        ),
        OpenApiParameter(
            name="type",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Transaction type (income or expense)",
        ),
        OpenApiParameter(
            name="account",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Filter by account ID",
        ),
        OpenApiParameter(
            name="category",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Filter by category ID",
        ),
        OpenApiParameter(
            name="start_date",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description="Start date (YYYY-MM-DD)",
        ),
        OpenApiParameter(
            name="end_date",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description="End date (YYYY-MM-DD)",
        ),
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Search in note and description",
        ),
        OpenApiParameter(
            name="ordering",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Order by date, amount, created_at (prefix with - for desc)",
        ),
    ],
)
class TransactionViewSet(BaseUserOwnedViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    # 🔍 add filtering, search, and ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_class = TransactionFilter # custom filter class for date range

    # exact match filters
    filterset_fields = ['type', 'account', 'category']

    # search text fields (case-insensitive)
    search_fields = ['note', 'description']

    # sorting support
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date']  # default order: newest first

    # Example usage:
    # /api/transactions/?type=expense&account=1&start_date=2023-01-01&end_date=2023-12-31&search=groceries&ordering=-amount
    # GET /api/transactions/?type=expense&account=1&start_date=2025-10-01&end_date=2025-10-20


    # --- automatic balance updates ---
    def perform_create(self, serializer):
        self.__validate_category(serializer)
        
        with db_transaction.atomic():
            trans = serializer.save(user=self.request.user)
            self._apply_balance_change(trans, add=True)

    def perform_update(self, serializer):
        self.__validate_category(serializer)
        """When updating, revert old effect and apply the new one."""
        with db_transaction.atomic():
            old_trans = Transaction.objects.get(pk=self.get_object().pk)
            # revert old transaction effect
            self._apply_balance_change(old_trans, add=False)
            # apply new transaction effect
            trans = serializer.save(user=self.request.user)
            self._apply_balance_change(trans, add=True)

    def perform_destroy(self, instance):
        """When deleting, revert the transaction effect."""
        with db_transaction.atomic():
            self._apply_balance_change(instance, add=False)
            instance.delete()

    # helper functions
    def __validate_category(self, serializer):
        """Ensure category type matches transaction type and belongs to current user."""
        from rest_framework.exceptions import ValidationError

        transaction_type = serializer.validated_data.get('type')
        category = serializer.validated_data.get('category')

        # Check if category belongs to the current user
        if category.user != self.request.user:
            raise ValidationError(
                {"category": "Category not found"}
            )

        if transaction_type == 'income' and category.type != 'income':
            raise ValidationError(
                {"category": "For income transactions, only income categories are allowed."}
            )

        if transaction_type == 'expense' and category.type != 'expense':
            raise ValidationError(
                {"category": "For expense transactions, only expense categories are allowed."}
            )

    def _apply_balance_change(self, trans, add=True):
        """
        Updates the linked account's balance based on transaction type.
        If add=False, reverses the effect (used for updates/deletes).
        """
        account = trans.account
        amount = trans.amount

        if add:
            if trans.type == 'income':
                account.balance += amount
            else:  # expense
                account.balance -= amount
        else:
            # reverse effect
            if trans.type == 'income':
                account.balance -= amount
            else:
                account.balance += amount

        account.save()
# pagination example:
# GET /api/transactions/?page=2&page_size=2
