from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, PositionViewSet

router = DefaultRouter()
router.register(r'', DepartmentViewSet, basename='department')
router.register(r'positions', PositionViewSet, basename='position')

urlpatterns = router.urls
