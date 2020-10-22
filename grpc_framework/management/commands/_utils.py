import sys
import grpc
from concurrent import futures
from django.apps import apps
from django.utils.module_loading import import_module, module_has_submodule
from ._config import GrpcFrameworkSettings

settings = GrpcFrameworkSettings()
_server = grpc.server(futures.ThreadPoolExecutor(max_workers=settings.max_workers))


def get_server() -> grpc.Server:
    return _server


def autodiscover_services():
    for app in apps.get_app_configs():
        if module_has_submodule(app.module, 'grpc_services'):
            import_module(f'{app.name}.grpc_services')


class LoggingMixIn:
    def info(self, message):
        stream = getattr(self, 'stdout', sys.stdout)
        if getattr(self, 'verbosity', 1) >= 2:
            stream.write(message)

    def success(self, message):
        stream = getattr(self, 'stdout', sys.stdout)
        if getattr(self, 'verbosity', 1) >= 1:
            if hasattr(self, 'style'):
                message = self.style.SUCCESS(message)
            stream.write(message)

    def error(self, message):
        stream = getattr(self, 'stdout', sys.stdout)
        if hasattr(self, 'style'):
            message = self.style.ERROR(message)
        stream.write(message)

    def prompt(self, message, default=False):
        if getattr(self, 'force', True):
            self.info(message)
            return True

        suffix = '(y/N)'
        if default:
            suffix = '(Y/n)'
        result = input(f'{message}? {suffix} ')
        if not result:
            return default
        return result[0].lower() == 'y'
