from rest_framework.serializers import ModelSerializer
from .models import Region


class RegionSerializer(ModelSerializer):
    class Meta:
        model = Region
        fields = ['name', 'display', 'available', 'provider']
