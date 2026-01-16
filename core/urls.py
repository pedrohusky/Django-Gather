from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('app/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('play/<int:realm_id>/', views.play, name='play'),
    path('intro/<int:realm_id>/', views.intro, name='intro'),
    path('edit/<int:realm_id>/', views.edit_realm, name='edit_realm'),
    path('join/<uuid:share_id>/', views.join_by_share_id, name='join_by_share'),
    path('api/realms/create/', views.create_realm, name='create_realm'),
    path('api/realms/<int:realm_id>/', views.get_realm, name='get_realm'),
    path('api/realms/<int:realm_id>/save/', views.save_realm_map, name='save_realm_map'),
    path('api/realms/<int:realm_id>/delete/', views.delete_realm, name='delete_realm'),
    path('api/realms/<int:realm_id>/toggle-privacy/', views.toggle_realm_privacy, name='toggle_realm_privacy'),
    path('api/profile/update/', views.update_profile, name='update_profile'),
]
