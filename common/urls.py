from django.urls import path, reverse_lazy
from django.views.generic import RedirectView
from . import views
from .svc.impl import tencentcloud

app_name = 'common'

urlpatterns = [
    path('', RedirectView.as_view(url=reverse_lazy('common:provider-account-list')), name='index'),
    path('account', views.ListProviderAccountView.as_view(), name='provider-account-list'),
    path('account/add/', views.CreateProviderAccountView.as_view(), name='provider-account-create'),
    path('account/<int:pk>', views.UpdateProviderAccountView.as_view(), name='provider-account-update'),
    path('region', views.ListRegionView.as_view(), name='region-list'),
    path('region/<int:pk>/toggle', views.ToggleRegionAvailableView.as_view(), name='region-toggle'),
    path('zone', views.ListZoneView.as_view(), name='zone-list'),
    path('zone/<int:pk>/toggle', views.ToggleZoneAvailableView.as_view(), name='zone-toggle'),
]
