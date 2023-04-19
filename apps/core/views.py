import logging
from django.core.exceptions import ValidationError
from datetime import datetime
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.core.models import User, MemberShip, FitnessClub, CheckIn
from apps.core.serializer import UserSerializer, UserFormSerializer, MemberShipSerializer, FitnessClubSerializer, \
    FitnessClubFormSerializer, CheckInSerializer, CheckInFormSerializer
from traceback_with_variables import format_exc
from utils.base import BaseViewSet, InvoiceManager
from utils.enums import MembershipEnum, GlobalVariablEnum

logger = logging.getLogger('core')


class UserViewSet(BaseViewSet):
    queryset = User.objects.select_related('membership').all()
    serializer_class = UserSerializer
    serializer_form_class = UserFormSerializer

    def get_queryset(self):
        return self.queryset.order_by('-pk')

    def get_object(self):
        return get_object_or_404(User, id=self.kwargs.get('pk'))

    @swagger_auto_schema(request_body=UserFormSerializer,
                         operation_description="The endpoint handle on-boarding of "
                                               "new customer / user on the system",
                         responses={},
                         operation_summary="User account create"
                         )
    def create(self, request, *args, **kwargs):
        """
        This endpoint handles user creating account request
        Method: POST
        """
        context = {'status': status.HTTP_201_CREATED}
        logger.info('New account creation request')
        try:
            data = self.get_data(request)
            serializer = self.serializer_form_class(data=data)
            if serializer.is_valid():
                if self.get_queryset().filter(email=serializer.validated_data.get('email')).exists():
                    raise ValidationError('Email already exist')
                instance = serializer.create(serializer.validated_data)
                context.update({'data': self.serializer_class(instance).data})
            else:
                context.update({"status": status.HTTP_400_BAD_REQUEST,
                                'errors': self.error_message_formatter(serializer_errors=serializer.errors)})
        except ValidationError as ex:
            context.update({'message': ex.messages[0], 'status': status.HTTP_400_BAD_REQUEST})
        except Exception as ex:
            logger.error(f'Error occurred while creating a new user account due to {str(ex)}')
            logger.error(format_exc(ex))
            context.update({'status': status.HTTP_400_BAD_REQUEST, 'message': str(ex)})
        return Response(context, status=context['status'])


class MemberShipViewSet(BaseViewSet):
    """
    This class contains methods related to a user membership account.
    Its inherit from the baseviewset class

    Methods:
        list: List all membership account already created on the list
        cancel: This handle terminating of user membership on the system
    """
    queryset = MemberShip.objects.all()
    serializer_class = MemberShipSerializer

    def get_object(self):
        return get_object_or_404(MemberShip, id=self.kwargs.get('pk'))

    def get_queryset(self):
        return self.queryset

    @swagger_auto_schema(
        operation_description="The endpoint handle cancel user membership account.",
        responses={},
        operation_summary="Cancel user membership"
    )
    @action(detail=True, methods=['put'], description='Cancel user membership')
    def cancel(self, request, *args, **kwargs):
        """
        This endpoint handle user membership cancellation request
        """
        context = {'status': status.HTTP_204_NO_CONTENT}
        try:
            instance = self.get_object()
            if instance.state == MembershipEnum.CANCELLED:
                raise ValidationError('Membership has been cancelled')
            instance.state = MembershipEnum.CANCELLED
            instance.save(update_fields=['state'])
        except ValidationError as ex:
            context.update({'status': status.HTTP_400_BAD_REQUEST, 'message': ex.messages[0]})
        except Exception as ex:
            logger.error(
                f'Error cancelling a user membership account due to {str(ex)} : Membership ID {self.kwargs.get("id")}')
            logger.error(format_exc(ex))
            context.update({'status': status.HTTP_400_BAD_REQUEST, 'message': str(ex)})
        return Response(context, status=context['status'])


class FitnessClubViewSet(BaseViewSet):
    """
    This class handle managing of all the fitness club on the system
    methods:
        list: list all fitness club on the system
        create: Create a new fitness club on the system
    """
    queryset = FitnessClub.objects.all()
    serializer_class = FitnessClubSerializer
    serializer_form_class = FitnessClubFormSerializer

    def get_object(self):
        return get_object_or_404(FitnessClub, id=self.kwargs.get('pk'))

    def get_queryset(self):
        return self.queryset

    @swagger_auto_schema(request_body=FitnessClubFormSerializer,
                         operation_description="The endpoint handle creating of new fitness club on the system",
                         responses={},
                         operation_summary="Create a new fitness club"
                         )
    def create(self, request, *args, **kwargs):
        context = {'status': status.HTTP_201_CREATED}
        try:
            data = self.get_data(request)
            serializer = self.serializer_form_class(data=data)
            if serializer.is_valid():
                instance = serializer.create(serializer.validated_data)
                context.update({'data': self.serializer_class(instance).data})
            else:
                context.update(
                    {'status': status.HTTP_400_BAD_REQUEST,
                     'errors': self.error_message_formatter(serializer.errors)})
        except Exception as ex:
            logger.error(f'Error occurred while creating a fitness club due to {str(ex)}')
            logger.error(format_exc(ex))
            context.update({'status': status.HTTP_400_BAD_REQUEST, 'message': str(ex)})
        return Response(context, status=context['status'])


class CheckInViewSet(BaseViewSet):
    queryset = CheckIn.objects.select_related('membership', 'club').all()
    serializer_class = CheckInSerializer
    serializer_form_class = CheckInFormSerializer

    def get_object(self):
        return get_object_or_404(CheckIn, id=self.kwargs.get('id'))

    def get_queryset(self):
        if self.request.GET.get('user_id'):
            return self.queryset.filter(membership__user__id=self.request.GET.get('user_id'))
        else:
            return self.queryset

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "user_id",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                description="User id representing the user requesting for his/her checkin history",
            )
        ],
        operation_description="List all user checkin history",
        operation_summary="List all user checkin history",
    )
    def list(self, request, *args, **kwargs):
        """
        This method handle fetching of user checking history
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

    @swagger_auto_schema(request_body=CheckInFormSerializer,
                         operation_description="The endpoint handle creating of new fitness club on the system",
                         responses={},
                         operation_summary="Check user in to fitness club"
                         )
    def create(self, request, *args, **kwargs):
        """
        This endpoint handle checking user in to one or more fitness club
        For a user to be successfully checked in to an fitness club some certain criteria needs to be meant
        1. The user membership must be active
        2. A user can not check in if they have no credit inside their membership account
        3. A user can not check in if their membership end_date has elapse

        However for a member in which an invoice has not been created for, The system auto generate the invoice for the
        member and also auto create an invoice line for the monthly invoice.
        """
        context = {'status': status.HTTP_201_CREATED}
        try:
            data = self.get_data(request)
            serializer = self.serializer_form_class(data=data)
            if serializer.is_valid():
                user = get_object_or_404(User, id=serializer.validated_data.get('user'))
                club = get_object_or_404(FitnessClub, id=serializer.validated_data.get('club'))
                # check if the user member is active or cancelled
                if user.membership.state == MembershipEnum.CANCELLED:
                    raise ValidationError('Your membership is already cancelled')
                # check if an invoice has already been generated for user membership
                if user.membership.has_invoice():
                    if user.membership.amount_of_credit <= 0.0:
                        raise ValidationError('You currently do not credit in your membership wallet')
                    # check if today is greater than the membership end_date
                    if datetime.today().date() > user.membership.end_date:
                        raise ValidationError('Your membership has expired')
                else:
                    # auto generate invoice for user membership
                    invoice_manager = InvoiceManager(membership=user.membership,
                                                     **{'amount': GlobalVariablEnum.FIXED_AMOUNT_CHARGE})
                    invoice = invoice_manager.create_invoice()
                membership = self.update_membership_credit(user.membership.id)
                instance = self.create_checkin(membership, club)
                context.update({'data': self.serializer_class(get_object_or_404(CheckIn, id=instance.id)).data,
                                'message': 'Checkin successful'})
            else:
                context.update({'status': status.HTTP_400_BAD_REQUEST,
                                'errors': self.error_message_formatter(serializer_errors=serializer.errors)})
        except ValidationError as ex:
            context.update({'status': status.HTTP_400_BAD_REQUEST, 'message': ex.messages[0]})
        except Exception as ex:
            context.update({'status': status.HTTP_400_BAD_REQUEST, 'message': str(ex)})
        return Response(context, status=context['status'])

    @staticmethod
    def create_checkin(membership, club):
        """
        method handles creating a user checkin entry
        """
        instance = CheckIn.objects.create(**{'membership': membership, 'club': club, })
        return instance

    @staticmethod
    def update_membership_credit(membership_id):
        """
        Method handle substract 1 credit from the membership account if checkin was successful
        """
        logger.info(f'Deducting 1 credit from membership with ID :: {membership_id} account')
        membership = get_object_or_404(MemberShip, id=membership_id)
        membership.amount_of_credit -= 1
        membership.save(update_fields=['amount_of_credit'])
        logger.info(
            f'Done deducting 1 credit from membership with ID :: {membership_id} account , new balance {membership.amount_of_credit}')
        return membership
