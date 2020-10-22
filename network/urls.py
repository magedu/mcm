from django.urls import path, reverse_lazy, include
from django.views.generic import RedirectView
from rest_framework import routers
from . import views
from .svc import tencentcloud

app_name = 'network'

router = routers.DefaultRouter()
router.register("vpc", views.ApiVPCViewSet)

urlpatterns = [
    path('', RedirectView.as_view(url=reverse_lazy('network:vpc-list')), name='index'),
    path('vpc', views.ListVPCView.as_view(), name='vpc-list'),
    path('vpc/add/', views.CreateVPCView.as_view(), name='vpc-create'),
    path('vpc/<int:pk>', views.UpdateVPCView.as_view(), name='vpc-update'),
    path('vpc/<int:pk>/delete', views.DeleteVPCView.as_view(), name='vpc-delete'),
    # path('api/vpc', views.list_vpc, name='api-vpc-list')
    path('api/', include(router.urls))
]
