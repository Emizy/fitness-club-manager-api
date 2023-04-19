from django.db import models
from utils.enums import MembershipEnum, InvoiceStateEnum
from utils.membership import MembershipAbstract


class User(models.Model):
    name = models.CharField(max_length=255, help_text='Indicate the full name of the user')
    email = models.EmailField(max_length=255, help_text='Indicate the email address of the user', unique=True)
    phone_number = models.CharField(max_length=255, help_text='Indicate the phone number of the user', null=True,
                                    blank=True)

    def __str__(self):
        return f"{self.name} | {self.email}"

    class Meta:
        db_table = 'user'
        verbose_name_plural = 'Users'


class MemberShip(models.Model):
    """
    Model holder user membership information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    state = models.CharField(max_length=20, choices=MembershipEnum.choices(), default=MembershipEnum.ACTIVE)
    amount_of_credit = models.PositiveBigIntegerField(default=0)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.name} | {self.get_state_display()}"

    class Meta:
        db_table = 'membership'
        verbose_name_plural = 'MemberShips'

    def has_invoice(self):
        """
        method return True or False if an invoice has been generated for a membership or not
        """
        if self.invoice.filter(status__in=[InvoiceStateEnum.OUTSTANDING, InvoiceStateEnum.PAID]).exists():
            return True
        else:
            return False


class FitnessClub(models.Model):
    """
    this class store all the fit club information inside the db
    """
    name = models.CharField(max_length=255)
    description = models.TextField(default='')

    def __str__(self):
        return f"{self.name}"

    class Meta:
        db_table = 'fitnessclub'
        verbose_name_plural = 'Fitness Club'


class CheckIn(MembershipAbstract):
    """
    Model keep track of membership checkin to fitness club
    """
    club = models.ForeignKey(FitnessClub, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{str(self.club)} | {str(self.membership)}"

    class Meta:
        db_table = 'checkin'
        verbose_name_plural = 'User Club CheckIns'
