from django.views import generic
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from . import models
from .svc import Services
from .svc.impl.base import RegionService, ZoneService


class FilteringListView(generic.ListView):
    filter_fields = ['name']
    extra_context = {}

    class Filter:
        def __init__(self, view):
            self.providers = models.Provider.objects.all()
            self._provider = None
            self.regions = []
            self._region = None
            self.kw = ''
            self.view = view

        @property
        def provider(self):
            return self._provider

        @provider.setter
        def provider(self, pk):
            if not pk:
                return
            try:
                self._provider = models.Provider.objects.get(pk=pk)
                self.regions = models.Region.objects.filter(provider=self.provider)
            except models.Provider.DoesNotExist:
                pass

        @property
        def region(self):
            return self._region

        @region.setter
        def region(self, pk):
            if not pk:
                return
            try:
                self._region = models.Region.objects.get(pk=pk)
            except models.Region.DoesNotExist:
                pass

        def make_queryset(self, request, queryset):
            qs = queryset
            self.provider = request.GET.get('provider')
            self.region = request.GET.get('region')
            self.kw = request.GET.get('kw')
            if self.provider:
                if hasattr(self.view.model, 'provider'):
                    qs = qs.filter(provider__id=self.provider.id)
                if hasattr(self.view.model, 'region'):
                    qs = qs.filter(region__provider__id=self.provider.id)
            if self.region:
                qs = qs.filter(region__id=self.region.id)
            if self.kw:
                q = Q()
                for field in self.view.get_filter_fields():
                    kwargs = {f'{field}__icontains': self.kw}
                    q = q | Q(**kwargs)
                qs = qs.filter(q)
            return qs

    def get_filter_fields(self):
        if isinstance(self.filter_fields, str):
            return [self.filter_fields]
        return self.filter_fields

    def get_queryset(self):
        fl = FilteringListView.Filter(self)
        queryset = super(FilteringListView, self).get_queryset()
        queryset = fl.make_queryset(self.request, queryset)
        self.extra_context['filter'] = fl
        return queryset


# Create your views here.
class CreateProviderView(PermissionRequiredMixin, generic.CreateView):
    model = models.Provider
    fields = '__all__'
    permission_required = 'common.add_provider'
    success_url = reverse_lazy('common:provider-list')


class UpdateProviderView(PermissionRequiredMixin, generic.UpdateView):
    model = models.Provider
    fields = '__all__'
    permission_required = 'common.change_provider'
    success_url = reverse_lazy('common:provider-list')


class DeleteProviderView(PermissionRequiredMixin, generic.DeleteView):
    model = models.Provider
    permission_required = 'common.delete_provider'
    success_url = reverse_lazy('common:provider-list')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class ListProviderView(PermissionRequiredMixin, generic.ListView):
    model = models.Provider
    permission_required = 'common.view_provider'
    paginate_by = 20
    extra_context = {}

    def get_queryset(self):
        queryset = self.model.objects.all()
        kw = self.request.GET.get('fl')
        if kw:
            self.extra_context['fl'] = kw
            queryset = queryset.filter(name__icontains=kw)
        return queryset


class SyncRegionView(PermissionRequiredMixin, generic.RedirectView):
    permission_required = ['common.add_region', 'common.change_region']
    url = reverse_lazy('common:region-list')

    def get(self, request, *args, **kwargs):
        try:
            provider = models.Provider.objects.get(pk=kwargs.get('provider'))
            service = Services.get(RegionService, provider)
            service.sync_to_model()
        except models.Provider.DoesNotExist:
            pass

        return super().get(request, *args, **kwargs)


class ListRegionView(PermissionRequiredMixin, generic.ListView):
    model = models.Region
    permission_required = 'common.view_region'
    paginate_by = 10
    extra_context = {'providers': models.Provider.objects.all()}

    def get_queryset(self):
        queryset = self.model.objects.all()
        provider = self.request.GET.get('provider', 0)
        if provider:
            self.extra_context['provider_filter_id'] = int(provider)
            queryset = queryset.filter(provider__id=int(provider))
        kw = self.request.GET.get('fl')
        if kw:
            self.extra_context['fl'] = kw
            queryset = queryset.filter(Q(name__icontains=kw) | Q(display__icontains=kw))
        return queryset


class ListZoneView(PermissionRequiredMixin, FilteringListView):
    model = models.Zone
    permission_required = 'common.view_zone'
    paginate_by = 10
    filter_fields = ['name', 'display']


class SyncZoneView(PermissionRequiredMixin, generic.RedirectView):
    permission_required = ['common.add_zone', 'common.change_zone']
    url = reverse_lazy('common:zone-list')

    def get(self, request, *args, **kwargs):
        try:
            region = models.Region.objects.get(pk=kwargs.get('region'))
            service = Services.get(ZoneService, provider=region.provider, region=region.name)
            service.sync_to_model()
        except models.Provider.DoesNotExist:
            pass

        return super().get(request, *args, **kwargs)
