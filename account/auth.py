import logging
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User, Group
from ldap3 import Server, Connection, ALL_ATTRIBUTES
from django.conf import settings
from django.utils import timezone

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
