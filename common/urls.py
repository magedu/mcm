from django.urls import path, reverse_lazy
from django.views.generic import RedirectView
from . import views
from .svc import tencentcloud


app_name = 'common'
urlpatterns = [
    path('', RedirectView.as_view(url=reverse_lazy('common:provider-list')), name='index'),
    path('provider/', views.ListProviderView.as_view(), name='provider-list'),
    path('provider/add/', views.CreateProviderView.as_view(), name='provider-create'),
    path('provider/<int:pk>/', views.UpdateProviderView.as_view(), name='provider-update'),
    path('provider/<int:pk>/delete/', views.DeleteProviderView.as_view(), name='provider-delete'),
    path('region', views.ListRegionView.as_view(), name='region-list'),
    path('region/<int:provider>/sync', views.SyncRegionView.as_view(), name='region-sync'),
    path('zone', views.ListZoneView.as_view(), name='zone-list'),
    path('zone/<int:region>/sync', views.SyncZoneView.as_view(), name='zone-sync'),
]
