from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, GroupViewSet

router = DefaultRouter()
router.register('user', UserViewSet)
router.register('group', GroupViewSet)

urlpatterns = [
    path('api/', include(router.urls))
]
