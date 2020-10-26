from django.urls import path
from django.contrib.auth.views import LoginView
from .views import signout, signin

app_name = 'account'

urlpatterns = [
    path('signin', LoginView.as_view(template_name='account/signin.html'), name='signin'),
    path('signout', signout, name='signout'),
    path('api/signin/', signin, name='api=signin')
]
