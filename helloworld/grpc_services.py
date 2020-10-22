from grpc_framework import get_server
from helloworld.helloworld_pb2_grpc import add_GreeterServicer_to_server, GreeterServicer
from helloworld.helloworld_pb2 import HelloReply
from common.models import Provider


class Greeter(GreeterServicer):
    def SayHello(self, request, context):
        provider = Provider.objects.first()
        return HelloReply(message=f'Hello {request.name} {provider.name}')


add_GreeterServicer_to_server(Greeter(), get_server())
