import logging
from django.core.management.base import BaseCommand
from django.utils.autoreload import run_with_reloader
from ._utils import get_server, autodiscover_services
from ._config import GrpcFrameworkSettings


class Command(BaseCommand):
    help = 'Run gRPC server'
    settings = GrpcFrameworkSettings()
    verbosity = 1
    bind = None

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('bind', type=str, nargs='?')

    def run(self):
        server = get_server()
        server.stop(grace=True)
        autodiscover_services()
        server.add_insecure_port(self.bind)
        try:
            logging.info(f'Starting grpc server at {self.bind}')
            server.start()
            server.wait_for_termination()
        except KeyboardInterrupt:
            server.stop(grace=True)

    def handle(self, *args, **options):
        self.bind = options.get('bind')
        if not self.bind:
            self.bind = self.settings.bind
        run_with_reloader(self.run)
