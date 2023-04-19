from rest_framework import serializers

from apps.core.serializer import UserSerializer
from apps.invoice.models import Invoice, InvoiceRow


class InvoiceRowSerializer(serializers.ModelSerializer):
    """
    Invoice row model serializer
    """

    class Meta:
        model = InvoiceRow
        fields = ["id", "amount", "description"]


class InvoiceSerializer(serializers.ModelSerializer):
    """
    Invoice model serializer
    """
    rows = InvoiceRowSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Invoice
        fields = ["id", "amount", "description", "status", "date", "rows", "user"]


class InvoiceFormSerializer(serializers.Serializer):
    """
    Invoice serializer form
    """
    membership = serializers.IntegerField(required=True)
    amount = serializers.FloatField(required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class InvoiceRowFormSerializer(serializers.Serializer):
    """
    Invoice row serializer form
    """
    amount = serializers.FloatField(required=True, min_value=1)
    description = serializers.CharField(required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
