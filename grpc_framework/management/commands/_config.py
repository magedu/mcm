import os
from django.conf import settings


class GrpcFrameworkSettings:
    def __init__(self):
        self.settings = getattr(settings, 'GRPC_FRAMEWORK', {})
        self.base_dir = settings.BASE_DIR

    @property
    def protobuf_dir(self):
        return settings.BASE_DIR.joinpath(self.settings.get('PROTOBUF_DIR', 'proto')).absolute()

    @property
    def temporary_dir(self):
        return settings.BASE_DIR.joinpath(self.settings.get('TMP_DIR', '.generated')).absolute()

    @property
    def bind(self):
        return self.settings.get('BIND', '127.0.0.1:5051')

    @property
    def max_workers(self):
        return self.settings.get('MAX_WORKERS', os.cpu_count())
