import os
import shutil
import pkg_resources
from pathlib import Path
from django.core.management.base import BaseCommand
from grpc_tools.protoc import main
from ._config import GrpcFrameworkSettings
from ._utils import LoggingMixIn


class Command(LoggingMixIn, BaseCommand):
    help = 'Compile protobuf files'
    proto_include = pkg_resources.resource_filename('grpc_tools', '_proto')
    settings = GrpcFrameworkSettings()
    verbosity = 1

    def make_arguments(self):
        proto_path = Path(self.settings.protobuf_dir)
        if proto_path.exists() and proto_path.is_dir():
            proto_files = [str(f) for f in proto_path.glob("**/*.proto")]
            arguments = [f'-I{self.proto_include}',
                         f'-I{proto_path}',
                         f'--python_out={self.settings.temporary_dir}',
                         f'--grpc_python_out={self.settings.temporary_dir}']
            arguments.extend(proto_files)
            return arguments

    def compile(self):
        arguments = self.make_arguments()
        if arguments:
            self.info(f'protoc {" ".join(arguments)}')
            if main(arguments) != 0:
                self.error('compile protobuf file FAILED')
                return False
            self.success('compile protobuf file DONE')
            return True

    def copy(self):
        prefix = self.settings.temporary_dir
        for root, dirs, files in os.walk(prefix):
            for file in files:
                source = Path(root).joinpath(file).absolute()
                target = self.settings.base_dir.joinpath(source.relative_to(prefix))
                self.info(f"cp {source} {target}")
                if not target.parent.exists():
                    target.parent.mkdir(parents=True)
                shutil.copyfile(source, target)
                init_file = target.parent.joinpath('__init__.py')
                if not init_file.exists():
                    self.info(f'create {init_file}')
                    init_file.touch(exist_ok=True)

    def handle(self, *args, **options):
        self.verbosity = options.get('verbosity')
        path = Path(self.settings.temporary_dir)
        if not path.exists():
            path.mkdir()
        self.compile()
        self.copy()
