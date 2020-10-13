import json
from django.db.models import Model


def get(model, default=None, *args, **kwargs):
    if issubclass(model, Model):
        try:
            return model.objects.get(*args, **kwargs)
        except model.DoesNotExist:
            pass
    return default


def remove_suffix(s: str, suffix: str):
    idx = s.rfind(suffix)
    if idx > 0:
        return s[:idx]
    return s


def remove_prefix(s: str, prefix: str):
    return s.replace(prefix, '', 1)


def boolean(s, default: bool):
    if s:
        return json.loads(s)
    return default
