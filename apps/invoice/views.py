import logging
from rest_framework import status

from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from django.core.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from traceback_with_variables import format_exc
from utils.base import InvoiceManager
from apps.core.models import MemberShip
from apps.invoice.serializer import InvoiceSerializer, InvoiceFormSerializer, InvoiceRowFormSerializer, \
    InvoiceRowSerializer
from utils.base import BaseViewSet
from apps.invoice.models import Invoice
from utils.enums import InvoiceStateEnum, MembershipEnum

logger = logging.getLogger('invoice')


class InvoiceViewSet(BaseViewSet):
    """
    This class handle performing crud operation on an invoice
    methods:
        list: list all invoice available on the system
        create: Generate a new invoice for a particular membership account
    """
    queryset = Invoice.objects.select_related('membership').prefetch_related('rows').all()
    serializer_class = InvoiceSerializer
    serializer_form_class = InvoiceFormSerializer

    def get_object(self):
        return get_object_or_404(Invoice, id=self.kwargs.get('pk'))

    def get_queryset(self):
        return self.queryset

    @swagger_auto_schema(request_body=InvoiceFormSerializer,
                         responses={},
                         operation_summary="Create this endpoint create a new invoice"
                         )
    def create(self, request, *args, **kwargs):
        context = {'status': status.HTTP_201_CREATED}
        try:
            data = self.get_data(request)
            serializer = self.serializer_form_class(data=data)
            if serializer.is_valid():
                membership = get_object_or_404(MemberShip, id=serializer.validated_data.get('membership'))
                if membership.state == MembershipEnum.CANCELLED:
                    raise ValidationError('Invoice could not be created since membership has already been cancelled')
                invoice_manager = InvoiceManager(membership, **{'amount': serializer.validated_data.get('amount')})
                invoice = invoice_manager.create_invoice()
                context.update({'data': self.serializer_class(invoice).data})
            else:
                context.update(
                    {'status': status.HTTP_400_BAD_REQUEST,
                     'errors': self.error_message_formatter(serializer.errors)})
        except ValidationError as ex:
            context.update({'status': status.HTTP_400_BAD_REQUEST, 'message': ex.messages[0]})
        except Exception as ex:
            logger.error(f'Error occurred while creating an invoice  due to {str(ex)}')
            logger.error(format_exc(ex))
            context.update({'status': status.HTTP_400_BAD_REQUEST, 'message': str(ex)})
        return Response(context, status=context['status'])

    @swagger_auto_schema(request_body=InvoiceRowFormSerializer,
                         responses={},
                         operation_summary="This endpoint handle add of new invoice row to an already existing invoice"
                         )
    @action(detail=True, methods=['put'], description='Add new row to invoice', url_path='add_row')
    def add_new_row(self, request, *args, **kwargs):
        context = {'status': status.HTTP_200_OK}
        try:
            invoice = self.get_object()
            if invoice.status == InvoiceStateEnum.VOID:
                raise ValidationError('Invoice already void')
            data = self.get_data(request)
            serializer = InvoiceRowFormSerializer(data=data)
            if serializer.is_valid():
                if invoice.membership.state == MembershipEnum.CANCELLED:
                    raise ValidationError('Invoice could not be created since membership has already been cancelled')
                invoice_manager = InvoiceManager(invoice.membership)
                row = invoice_manager.add_invoice_row(invoice, serializer.validated_data.get('amount'),
                                                      serializer.validated_data.get('description'))
                invoice.amount += row.amount
                invoice.save(update_fields=['amount'])
                context.update({'data': InvoiceRowSerializer(row).data})
            else:
                context.update({'status': status.HTTP_400_BAD_REQUEST,
                                'errors': self.error_message_formatter(serializer_errors=serializer.errors)})
        except ValidationError as ex:
            context.update({'status': status.HTTP_400_BAD_REQUEST, 'message': ex.messages[0]})
        except Exception as ex:
            context.update({'status': status.HTTP_400_BAD_REQUEST, 'message': str(ex)})
        return Response(context, status=context['status'])

    @swagger_auto_schema(request_body=InvoiceFormSerializer,
                         responses={},
                         operation_summary="This method handles deleting of an invoice from the system"
                         )
    def destroy(self, request, *args, **kwargs):
        context = {'status': status.HTTP_204_NO_CONTENT}
        try:
            instance = self.get_object()
            instance.delete()
        except Exception as ex:
            context.update({'status': status.HTTP_400_BAD_REQUEST, 'message': str(ex)})
        return Response(context, status=context['status'])

    @swagger_auto_schema(
        responses={},
        operation_summary="Render an invoice void"
    )
    @action(detail=True, methods=['put'], description='Render an invoice void', url_name='void')
    def void(self, request, *args, **kwargs):
        context = {'status': status.HTTP_204_NO_CONTENT}
        try:
            invoice = self.get_object()
            if invoice.status == InvoiceStateEnum.VOID:
                raise ValidationError('Invoice already void')
            invoice.status = InvoiceStateEnum.VOID
            invoice.save(update_fields=['status'])
        except ValidationError as ex:
            context.update({'status': status.HTTP_400_BAD_REQUEST, 'message': ex.messages[0]})
        except Exception as ex:
            context.update({'status': status.HTTP_400_BAD_REQUEST, 'message': str(ex)})
        return Response(context, status=context['status'])
