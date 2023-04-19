import logging
from abc import abstractmethod
from datetime import datetime, timedelta
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.core.models import MemberShip
from apps.invoice.models import Invoice, InvoiceRow
from utils.enums import InvoiceStateEnum, MembershipEnum
from utils.pagination import CustomPaginator

logger = logging.getLogger('invoice')


class CustomFilter(DjangoFilterBackend):
    """
    Custom filter that inherit from django filter backend
    """

    def filter_queryset(self, request, queryset, view):
        filter_class = self.get_filterset_class(view, queryset)

        if filter_class:
            return filter_class(request.query_params, queryset=queryset, request=request).qs
        return queryset


class BaseViewSet(ViewSet):
    """
    This class serve as a base class which inherit rest framework viewset , however this class is will serve
    as a BASE CLASS in which all the endpoint needed to inherit from, in other to have interface consistency and also make
    the project to follow DRY principle

    # The choice of usage is to make the API swagger documentation to be more precise and eliminate unnecessary / unused
    endpoint.
    """
    custom_filter_class = CustomFilter()
    search_backends = SearchFilter()
    order_backend = OrderingFilter()
    paginator_class = CustomPaginator()
    serializer_class = None

    @abstractmethod
    def get_queryset(self):
        return

    @abstractmethod
    def get_object(self):
        return

    @staticmethod
    def get_data(request) -> dict:
        return request.data if isinstance(request.data, dict) else request.data.dict()

    def get_list(self, queryset):
        if 'search' in self.request.query_params:
            query_set = self.search_backends.filter_queryset(request=self.request,
                                                             queryset=queryset,
                                                             view=self)
        elif self.request.query_params:
            query_set = self.custom_filter_class.filter_queryset(request=self.request,
                                                                 queryset=queryset,
                                                                 view=self)
        else:
            query_set = queryset
        if 'ordering' in self.request.query_params:
            query_set = self.order_backend.filter_queryset(query_set, self.request, self)
        else:
            query_set = query_set.order_by('-pk')
        return query_set

    def paginator(self, queryset, serializer_class):
        paginated_data = self.paginator_class.generate_response(queryset, serializer_class, self.request)
        return paginated_data

    @swagger_auto_schema(
        operation_description="List all entries available",
        operation_summary="List all entries available ",
    )
    def list(self, request, *args, **kwargs):
        """
        This method
        """
        context = {"status": status.HTTP_200_OK}
        try:
            paginate = self.paginator(
                queryset=self.get_list(self.get_queryset()), serializer_class=self.serializer_class
            )
            context.update({"status": status.HTTP_200_OK, "message": "OK", "data": paginate})
        except Exception as ex:
            context.update({"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)})
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        operation_description="Retrieve a single entry",
        operation_summary="Retrieve a single entry",
    )
    def retrieve(self, request, *args, **kwargs):
        """
        This method serve as an endpoint for retrieving detailed information about an entry based on supplied pk or id
        """
        context = {'status': status.HTTP_200_OK}
        try:
            context.update({'data': self.serializer_class(self.get_object()).data})
        except Exception as ex:
            context.update({'status': status.HTTP_400_BAD_REQUEST, 'message': str(ex)})
        return Response(context, status=context['status'])

    @staticmethod
    def error_message_formatter(serializer_errors):
        """
        This method help format serializer errors messages to a dictionary in order to maintain consistency in error display
        """
        return {name: message[0] for name, message in serializer_errors.items()}


class InvoiceManager:
    """
    This class serve has invoice manager which handles the following:
    1. Create an invoice for the user membership by calling the create_invoice invoice method
    2. Add new invoice line to the invoice by calling the add_invoice_row method
    3. Compute equivalent credit for the invoice amount created for the month by calling compute_credit
    4. Update merchant account with the equivalent credit and set new start_date and end_date for the
        membership account by calling the  update_merchant_account method


    Args:
        membership: an instance of user membership
        kwargs: This contain other necessary information that will be used e.g amount to be added
    """

    def __init__(self, membership: MemberShip, **kwargs):
        logger.info('=== Initialization Invoice Manager ====')
        self.membership = membership
        self.kwargs = kwargs
        logger.info(f'=== Done initializing Invoice Manager for membership account {self.membership}')

    def create_invoice(self):
        """
        This method handles creating a new invoice for a user membership account
         - If the method is being called, its will create an invoice for the membership account supplier via the
            class constructor and also generate an invoice line for the user account
        """
        logger.info(f'Generating new invoice for membership {self.membership}')
        invoice = Invoice.objects.create(**{
            'membership': self.membership,
            'status': InvoiceStateEnum.OUTSTANDING,
            'description': f'{self.membership.user.name} membership invoice',
            'date': datetime.today().date()
        })
        # create an invoice row
        _ = self.add_invoice_row(invoice, float(self.kwargs.get('amount')),
                                 f'Invoice line for month of {invoice.date.strftime("%Y-%m")}')
        # since the only one invoice line is added update the invoice total amount
        invoice.amount = float(self.kwargs.get('amount'))
        invoice.save(update_fields=['amount'])
        # update the merchant account credit
        self.update_merchant_account(float(self.kwargs.get('amount')))
        logger.info(f'Done generating new invoice for membership {self.membership}')
        return invoice

    @staticmethod
    def compute_credit(amount: float):
        """
        this method handle computing the equivalent credit of the amount supplied
        Args:
            amount: float

        1 credit = 2 euro
        x credit = amount
        """
        credit = amount / 2
        return int(credit)

    @staticmethod
    def add_invoice_row(invoice: Invoice, amount: float, description: str):
        """
        This method handles adding of new invoice line to an invoice
        Args:
            invoice:
            amount
            description
        """
        row = InvoiceRow.objects.create(**{
            'amount': amount,
            'invoice': invoice,
            'description': description
        })
        logger.info(f'Created new invoice line for {invoice.membership} month of : {invoice.date.strftime("%Y-%m")}')
        return row

    def update_merchant_account(self, amount):
        """
        This method handles updating of merchant account with membership renewal information
        Args:
            amount: Amount of fee charged for the monthly subscription
        """
        credit = self.compute_credit(amount)
        logger.info(f'Updating {self.membership} merchant account with total amount of credit {credit}')
        start_date = datetime.today().date()
        end_date = start_date + timedelta(days=30)
        payload = {
            'amount_of_credit': credit,
            'start_date': start_date,
            'end_date': end_date,
            'state': MembershipEnum.ACTIVE  # just to ascertain the membership profile is active
        }
        _ = MemberShip.objects.filter(id=self.membership.id).update(**payload)

        logger.info(f'Done updating {self.membership} merchant account with total amount of credit {credit}')
