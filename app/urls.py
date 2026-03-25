from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_order, name='create_order'),
    path('accept/<int:order_id>/', views.accept_order, name='accept_order'),
    path('profile/', views.profile_view, name='profile'),
    path('wallet/', views.wallet_view, name='wallet'),
    path('mentors/', views.mentors_list, name='mentors_list'),

    # НОВОЕ: Просмотр чужого профиля (ментора)
    path('user/<str:username>/', views.user_detail, name='user_detail'),

    # Логика работы с заказом
    path('submit/<int:order_id>/', views.submit_order, name='submit_order'),
    path('confirm/<int:order_id>/', views.confirm_order, name='confirm_order'),

    # Универсальный путь для P2P рейтинга
    path('leave_review/<int:order_id>/', views.leave_review, name='leave_review'),

    # Авторизация
    path('login/', auth_views.LoginView.as_view(template_name='app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
]