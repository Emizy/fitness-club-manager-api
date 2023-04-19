class CustomEnum(object):
    """
    Base Enum class in which all the enums configuration could inherit from.
    """

    class Enum(object):
        name = None
        value = None
        type = None

        def __init__(self, name, value, type):
            self.key = name
            self.name = name
            self.value = value
            self.type = type

        def __str__(self):
            return self.name

        def __repr__(self):
            return self.name

        def __eq__(self, other):
            if other is None:
                return False
            if isinstance(other, CustomEnum.Enum):
                return self.value == other.value
            raise TypeError

    @classmethod
    def choices(c):
        """
        Methods return a tuple / list representation of the class attribute
        """
        attrs = [a for a in c.__dict__.keys() if a.isupper()]
        values = [
            (c.__dict__[v], CustomEnum.Enum(v, c.__dict__[v], c).__str__())
            for v in attrs
        ]
        return sorted(values, key=lambda x: x[0])


class MembershipEnum(CustomEnum):
    """
    This handle demonstrate the various state in which a user membership could be
    """
    ACTIVE = 'active'
    CANCELLED = 'cancelled'

    @classmethod
    def choices(c):
        return (
            (c.ACTIVE, 'Active'),
            (c.CANCELLED, 'Cancelled'),
        )


class InvoiceStateEnum(CustomEnum):
    """
    This handle demonstrate the various state in which a user invoice object could be
    """
    OUTSTANDING = 'outstanding'
    PAID = 'paid'
    VOID = 'void'

    @classmethod
    def choices(c):
        return (
            (c.OUTSTANDING, "Outstanding"),
            (c.PAID, "Paid"),
            (c.VOID, "Void"),
        )


class GlobalVariablEnum(CustomEnum):
    FIXED_AMOUNT_CHARGE = 1000  # default amount charge per month
