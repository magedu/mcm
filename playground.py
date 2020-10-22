import os
import grpc
import django
from concurrent import futures

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mcm.settings')
django.setup()

from helloworld.helloworld_pb2_grpc import GreeterStub
from helloworld.helloworld_pb2 import HelloRequest


def call():
    with grpc.insecure_channel(target="127.0.0.1:5051") as channel:
        stub = GreeterStub(channel)
        resp = stub.SayHello(HelloRequest(name='comyn'))
        return resp.message


if __name__ == '__main__':
    print(call())
