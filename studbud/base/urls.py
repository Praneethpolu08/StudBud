from django.urls import path
from . import views
from .views import home

urlpatterns = [
    path('login/',views.loginPage,name='login'),
    path('logout/',views.logoutUser,name='logout'),
    path('register/',views.registerPage,name='register'),
    path('', home, name='home'),
    path('room/<str:pk>',views.room,name='room'),
    path('profile/<str:pk>',views.userProfile,name='user_profile'),
    path('create-room/',views.create_Room,name='create_room'),

    path('delete-room/<str:pk>',views.delete_Room,name='delete_room'),

    path('delete-message/<str:pk>',views.deletemessage,name='deletemessage'),


    path('update-room/<str:pk>',views.update_Room,name='update-room'),
]