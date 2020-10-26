import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mcm.settings')
django.setup()

import grpc
from helloworld.helloworld_pb2 import HelloRequest
from helloworld.helloworld_pb2_grpc import GreeterStub


def call():
    channel = grpc.insecure_channel('127.0.0.1:5051')  # 表示如何找到服务端
    stub = GreeterStub(channel)  # 其实是一个发起RPC请求的代理
    resp = stub.SayHello(HelloRequest(name='magedu'))  # 像本地调用一样， 调用远程服务
    print(resp.message)


if __name__ == '__main__':
    call()
