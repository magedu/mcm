from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth import logout


# Create your views here.
def signout(request):
    logout(request)
    return redirect(reverse_lazy('account:signin'))
