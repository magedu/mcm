from django import template
from urllib.parse import parse_qs, urlparse, urlencode, ParseResult
from django.contrib import messages
from django.http.request import HttpRequest
from django.utils.module_loading import import_string

register = template.Library()

bootstrap_class_map = {
    messages.INFO: 'alert-info',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
    messages.SUCCESS: 'alert-success'
}


@register.filter()
def bootstrap_alert_class(value):
    level = messages.DEFAULT_LEVELS.get(value.upper())
    return bootstrap_class_map.get(level, 'alert-primary')


@register.simple_tag
def bootstrap_alert_class_tag(value):
    level = messages.DEFAULT_LEVELS.get(value.upper())
    return bootstrap_class_map.get(level, 'alert-primary')


@register.filter(name='isinstance')
def is_instance(value, classes: str):
    return isinstance(value, tuple(import_string(x) for x in classes.split(',')))


@register.simple_tag(name='hidden')
def hidden(value, length=0, replace='*'):
    if length:
        return replace * length
    return replace * len(value)


@register.simple_tag(takes_context=True)
def build_url(context, **kwargs):
    request: HttpRequest = context['request']
    parsed = urlparse(request.build_absolute_uri(), allow_fragments=True)
    qs = parse_qs(parsed.query)
    mode = context.get('build_mode', 'replace')
    for k, v in kwargs.items():
        if mode == 'replace':
            qs[k] = [v]
        if mode == 'append':
            values = qs.get(k, [])
            values.append(v)
            qs[k] = values
        if mode == 'if_not_exist':
            if not qs.get(k):
                qs[k] = [v]
    return ParseResult(scheme=parsed.scheme, netloc=parsed.netloc, path=parsed.path, params=parsed.params,
                       query=urlencode(qs, doseq=True), fragment=parsed.fragment).geturl()


@register.simple_tag(takes_context=True)
def page_url(context, page: int):
    context['build_mode'] = 'replace'
    return build_url(context, page=page)


@register.inclusion_tag(filename='components/pagination.html', takes_context=True)
def pagination(context):
    return context
