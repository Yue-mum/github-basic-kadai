from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('signup/done/', views.SignupDoneView.as_view(), name='signup_done'),#サインアップ完了URLパターン。
    path('verify/<str:token>/', views.VerifyEmailView.as_view(), name='verify_email'),#メール認証URLパターン。
    path('login/', views.LoginView.as_view(), name='login'),#ログインURLパターン。
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('password_change/', views.PasswordChangeRequestView.as_view(), name='password_change_request'),
    path('password_change/sent/', views.PasswordChangeSentView.as_view(), name='password_change_sent'),#パスワード変更メール送信完了URLパターン。
    path('password_change/<str:token>/', views.PasswordChangeView.as_view(), name='password_change'),#パスワード変更URLパターン。
    path('withdraw/', views.WithdrawView.as_view(), name='withdraw'),#退会URLパターン。

]
