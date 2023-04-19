from utils.enums import CustomEnum


class EndPoint(CustomEnum):
    """
    Enum class to hold all the endpoints available on the system
    """
    USER_ENDPOINT = '/api/user'
    MEMBERSHIP_ENDPOINT = '/api/membership'
    FITNESS_CLUB_ENDPOINT = '/api/fitnessclub'
    CHECKIN_ENDPOINT = '/api/checkin'
    INVOICE_ENDPOINT = '/api/invoice'
