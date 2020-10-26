from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('snippets', views.SnippetViewSet)
router.register('users', views.UserViewSet)

app_name = 'snippets'
urlpatterns = [
    # path('snippets/', views.SnippetList2.as_view(), name='snippet-list'),
    # path('snippets/<int:pk>/', views.SnippetDetail2.as_view(), name='snippet-detail'),
    # path('users/', views.UserList.as_view(), name='user-list'),
    # path('users/<int:pk>/', views.UserDetail.as_view(), name='user-detail')
    path('', include(router.urls))
]
