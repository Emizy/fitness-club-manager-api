from django.contrib import admin
from apps.core.models import User, MemberShip, FitnessClub, CheckIn


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email"
    )


class MemberShipAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "state",
        "amount_of_credit",
        "start_date",
        "end_date",
    )


class FitnessClubAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
    )


class CheckInAdmin(admin.ModelAdmin):
    list_display = (
        "club",
        "membership",
        "created_at",
    )


admin.site.register(User, UserAdmin)
admin.site.register(MemberShip, MemberShipAdmin)
admin.site.register(FitnessClub, FitnessClubAdmin)
admin.site.register(CheckIn, CheckInAdmin)
