from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from apps.core import route as core_router
from apps.invoice import route as invoice_router

schema_view = get_schema_view(
    openapi.Info(
        title="VIRTUAGYM API",
        default_version="v1",
        description="Endpoints showing interactable part of the system",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email=""),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny, ],
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include(core_router.router.urls)),
    path("api/", include(invoice_router.router.urls)),
    path("",
         schema_view.with_ui("swagger", cache_timeout=0),
         name="schema-swagger-ui",
         ),
]
