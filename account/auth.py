import logging
import jwt
from django.conf import settings
from django.http import HttpRequest
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User, Group
from ldap3 import Server, Connection, ALL_ATTRIBUTES
from django.conf import settings
from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Token

logger = logging.getLogger('account.auth')


def get_ldap_attribute_value(entry, attribute):
    if hasattr(entry, attribute):
        return getattr(entry, attribute).value


def get_ldap_attribute_values(entry, attribute):
    if hasattr(entry, attribute):
        return getattr(entry, attribute).values
    return []


class LDAPBackend(BaseBackend):
    def __init__(self):
        self.base_dn = settings.ACCOUNT_AUTH_LDAP.get('BASE_DN', '')
        self.users_ou = settings.ACCOUNT_AUTH_LDAP.get('USERS_OU', 'users')
        self.groups_ou = settings.ACCOUNT_AUTH_LDAP.get('GROUPS_OU', 'groups')
        self.user_filter = settings.ACCOUNT_AUTH_LDAP.get('USER_FILTER', '(objectclass=*)')
        self.group_filter = settings.ACCOUNT_AUTH_LDAP.get('GROUP_FILTER', '(objectclass=*)')
        self.server = Server(settings.ACCOUNT_AUTH_LDAP['URL'])

    def authenticate(self, request, username=None, password=None, **kwargs):
        dn = ','.join([f'cn={username}', f'ou={self.users_ou}', self.base_dn])
        try:
            with Connection(self.server, dn, password, auto_bind=True) as conn:
                conn.search(dn, self.user_filter, attributes=ALL_ATTRIBUTES)
                user, exist = User.objects.get_or_create(username=username)
                if not exist:
                    user.date_joined = timezone.now()
                    user.is_active = True

                entry = conn.entries[0]
                if get_ldap_attribute_value(entry, 'shadowExpire') == 0:
                    user.is_active = False
                else:
                    user.last_login = timezone.now()

                user.save()
                if user.is_active:
                    return user
        except Exception as e:
            logger.warning('ldap authenticate failed', e)

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            logger.warning(f'user {user_id} not exist')


class TokenAuthentication(BaseAuthentication):
    def authenticate(self, request: HttpRequest):
        header = request.headers.get('Authorization')
        if not header:
            raise AuthenticationFailed()
        arr = header.split()
        if arr.pop(0).lower() == 'token' and arr:
            key = arr.pop(0)
            # 后端存储
            # try:
            #     token = Token.objects.get(key=key)
            #     now = timezone.now()
            #     if (now - token.created).total_seconds() > 8 * 3600:
            #         raise AuthenticationFailed("")
            #     return token.user, token
            # except Token.DoesNotExist:
            #     raise AuthenticationFailed("")
            # 前端存储
            payload = jwt.decode(key, settings.SECRET_KEY, algorithms=['HS256'])
            uid = payload.get('uid')
            if uid:
                # TODO exp
                try:
                    user = User.objects.get(pk=uid)
                    return user, key
                except User.DoesNotExist:
                    raise AuthenticationFailed()

        raise AuthenticationFailed()
