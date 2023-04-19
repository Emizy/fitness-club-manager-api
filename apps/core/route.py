from rest_framework.routers import DefaultRouter
from .views import UserViewSet, MemberShipViewSet, CheckInViewSet, FitnessClubViewSet

router = DefaultRouter()
router.register(r'user', UserViewSet, basename='api-user')
router.register(r'membership', MemberShipViewSet, basename='api-membership')
router.register(r'fitnessclub', FitnessClubViewSet, basename='api-fitnessclub')
router.register(r'checkin', CheckInViewSet, basename='api-checkin')
