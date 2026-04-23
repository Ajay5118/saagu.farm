from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/',           views.login_view,          name='login'),
    path('firebase-verify/', views.firebase_verify_view, name='firebase_verify'),
    path('logout/',          views.logout_view,          name='logout'),
    path('profile/',         views.profile_view,         name='profile'),
    path('address/add/',     views.add_address_view,     name='add_address'),
    path('address/<int:pk>/delete/', views.delete_address_view, name='delete_address'),
]
