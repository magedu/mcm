from django.shortcuts import render
from django.views import generic
from django.urls import reverse_lazy
from .models import VPC
from common.models import Task


# Create your views here.
class CreateVPCView(generic.CreateView):
    model = VPC
    fields = '__all__'
    success_url = reverse_lazy('network:vpc-list')

    def form_valid(self, form):
        ret = super().form_valid(form)
        task = Task()
        task.service = ''
        task.model = VPC.__name__
        task.identity = ret.id
        task.save()
        return ret


class UpdateVPCView(generic.UpdateView):
    model = VPC
    exclude = ['identity']
    success_url = reverse_lazy('network:vpc-list')


class DeleteVPCView(generic.DeleteView):
    pass


class ListVPCView(generic.ListView):
    pass
