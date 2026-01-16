from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('app/', views.dashboard, name='dashboard'),
    path('play/<int:realm_id>/', views.play, name='play'),
    path('api/realms/create/', views.create_realm, name='create_realm'),
    path('api/realms/<int:realm_id>/', views.get_realm, name='get_realm'),
    path('api/profile/update/', views.update_profile, name='update_profile'),
]
