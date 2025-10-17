from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # 🏠 Home & Core Features
    path('', views.home, name='home'),
    path('book/<int:sport_id>/', views.book_sport, name='book_sport'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('add-players/<int:booking_id>/', views.add_players, name='add_players'),
    path('player/<int:player_id>/', views.player_detail, name='player_detail'),

    # 👤 Authentication
    path('signup/', views.signup_view, name='signup'),

    # 🧑‍💻 Login Page (Django built-in)
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html',
        redirect_authenticated_user=True
    ), name='login'),

    # 🚪 Logout Page (Django built-in)
    path('logout/', auth_views.LogoutView.as_view(
        next_page='home'
    ), name='logout'),
    path('player/<int:player_id>/', views.player_detail, name='player_detail'),
    # path('player/<int:player_id>/qr/', views.player_qr_toggle, name='toggle_player_status')
    # path('player/<int:player_id>/toggle/', views.player_qr_toggle, name='toggle_player_status'),



]
