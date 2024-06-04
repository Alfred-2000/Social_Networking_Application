"""social_networking URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from accounts.views import (
    LoginView,
    CreateUser,
    ListUsers,
    RetrieveUpdateDeleteUser,
    FollowUser,
    ListMyConnections,
    ListUserConnections,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/login/', LoginView.as_view(), name='login'),  #Login 
    path('api/signup/', CreateUser.as_view(), name='signup'),  #Signup(Create account)
    path('api/user/list/', ListUsers.as_view()),  #List profiles
    path('api/user/<uuid:user_id>/', RetrieveUpdateDeleteUser.as_view()),    #Retrieve/Update/Delete User
    path('api/follow-user/', FollowUser.as_view()),    #Send/Accept/Reject follow request
    path('api/connections/', ListMyConnections.as_view()),    #List my connections
    path('api/connections/<uuid:user_id>/', ListUserConnections.as_view()),    #List users connections
]

