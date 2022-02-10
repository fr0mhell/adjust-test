from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'metrics', views.MetricViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
