import uuid
import jwt
from datetime import timedelta
from django.shortcuts import redirect
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth import logout, authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from .models import Token


# Create your views here.
def signout(request):
    logout(request)
    return redirect(reverse_lazy('account:signin'))


@csrf_exempt
def signin(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        user = authenticate(request, username=data.get('username'), password=data.get('password'))
        if user:
            # token = Token()
            # token.user = user
            # token.key = str(uuid.uuid4()).replace('-', '')
            # token.save()
            # return JsonResponse({'token': token.key, 'ex': token.created + timedelta(hours=8)})
            ex = (timezone.now() + timedelta(hours=8)).timestamp()
            token = jwt.encode(payload={'uid': user.id, 'exp': ex}, key=settings.SECRET_KEY, algorithm='HS256')
            return JsonResponse({'token': token.decode(), 'ex': ex})
