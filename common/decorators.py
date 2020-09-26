import logging
from functools import wraps
from test.tc import TencentCloudSDKException
from .svc import Services

tencent_sdk_logger = logging.getLogger('tencent.cloud.request')


def suppress_tencent_cloud_exception(logger=None):
    if logger is None:
        logger = tencent_sdk_logger

    def decorator(fn):
        @wraps(fn)
        def wrap(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except TencentCloudSDKException as e:
                logger.exception('request error', e)

        return wrap

    return decorator


def service_register(cls):
    Services.add(cls)
    return cls
