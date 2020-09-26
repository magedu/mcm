import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mcm.settings')
django.setup()

from common.models import Provider
from common.svc import Services, RegionService
from common.svc import tencentcloud

if __name__ == '__main__':
    provider = Provider.objects.get(pk=1)
    service = Services.get(RegionService, provider)
    service.sync_to_model()