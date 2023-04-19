from django.db import models


class MembershipAbstract(models.Model):
    """
    an abstract class for membership to be inherited by all class attached to a membership
    """
    membership = models.ForeignKey(
        "core.MemberShip", related_name="%(class)s", on_delete=models.CASCADE, null=True, blank=True
    )

    class Meta:
        abstract = True
