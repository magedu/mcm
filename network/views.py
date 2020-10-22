from django.shortcuts import render
from django.http.response import JsonResponse
from django.core import serializers
from django.views import generic
from django.urls import reverse_lazy
from .models import VPC
from common.models import Task
from rest_framework import serializers, viewsets


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


def model_to_dict(model):
    result = {}
    for field in model._meta.fields:
        if field.is_relation:
            m = field.related_model.objects.get(**{field.target_field.name: field.value_from_object(model)})
            result[field.name] = model_to_dict(m)
        else:
            result[field.name] = field.value_from_object(model)
    return result


def list_vpc(request):
    vpc_set = VPC.objects.all()
    # return JsonResponse(serializers.serialize('json', vpc_set), safe=False)
    return JsonResponse({'vpc_set': [model_to_dict(vpc) for vpc in vpc_set]})


class VPCSerializer(serializers.ModelSerializer):
    class Meta:
        model = VPC
        fields = '__all__'


class ApiVPCViewSet(viewsets.ModelViewSet):
    queryset = VPC.objects.all()
    serializer_class = VPCSerializer