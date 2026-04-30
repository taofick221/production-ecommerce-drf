from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from django.urls import path
from .views import RegisterView,CustomTokenView

urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),
    path('login/',CustomTokenView.as_view(),name='login'),
    path('token/refresh/',TokenRefreshView.as_view(),name='token_refresh'),
]
