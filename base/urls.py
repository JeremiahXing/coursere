from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('login/', views.logInPage, name='log-in'),
    path('logout/', views.logOutUser, name='log-out'),
    path('', views.home, name='home'),
    path('course/', views.course, name='course'),
    path('signup/', views.signUp, name='sign-up'),
    path('user/<int:userid>/', views.user, name='user'),
    path('room/<int:roomid>/', views.room, name='room'),
    path('user/<int:userid>/create-room', views.createRoom, name='create-room'),
    path('user/<int:userid>/update-room/<int:roomid>', views.updateRoom, name='update-room'),
    path('room/<int:roomid>/delete', views.deleteRoom, name='delete-room'),
    path('message/<int:messageid>/delete', views.deleteMessage, name='delete-message'),
    path('profile/<int:userid>/', views.userProfile, name='user-profile'),
    path('profile-edit/<int:userid>/', views.editUser, name='profile-edit'),
    path('leave/<int:userid>/<int:roomid>/', views.leaveRoom, name='leave-room'),
    path('activate-user/<uidb64>/<token>', views.activate_user, name='activate'),
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='authentication/resetpassword.html'),name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)