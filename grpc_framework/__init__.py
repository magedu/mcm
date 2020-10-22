default_app_config = 'grpc_framework.apps.GrpcFrameworkConfig'

from .management.commands._utils import get_server

__all__ = ['get_server']
