from rest_framework.routers import DefaultRouter
from .views import AccountViewSet, CategoryViewSet, TransactionViewSet

router = DefaultRouter()
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = router.urls


# region tests only remove
# from .views import test_auth
# from django.urls import path

# urlpatterns = [
#     path('test-auth/', test_auth),
# ] + router.urls

# endregion