from grpc_framework import get_server
from .helloworld_pb2 import HelloRequest, HelloReply
from .helloworld_pb2_grpc import add_GreeterServicer_to_server, GreeterServicer


class Greeter(GreeterServicer):
    def SayHello(self, request: HelloRequest, context):
        return HelloReply(message=f'hello {request.name}')


add_GreeterServicer_to_server(Greeter(), get_server())
