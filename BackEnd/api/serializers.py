from rest_framework import serializers
from .models import Account, Category, Transaction
from drf_spectacular.utils import OpenApiExample


# this file serves to convert model instances to JSON and vice versa

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']
        examples = [
            OpenApiExample(
                name="Expense transaction",
                value={
                    "type": "expense",
                    "account": 1,
                    "category": 2,
                    "amount": "45.50",
                    "date": "2025-01-10",
                    "note": "Groceries",
                    "description": "Weekly grocery shopping"
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Transaction response",
                value={
                    "id": 10,
                    "type": "expense",
                    "account": 1,
                    "category": 2,
                    "amount": "45.50",
                    "date": "2025-01-10",
                    "note": "Groceries",
                    "description": "Weekly grocery shopping",
                    "created_at": "2025-01-10T12:00:00Z"
                },
                response_only=True,
            ),
        ]
