from django.urls import path
from .mypage_views import MyPageView, UserDetailView, UserEditView

app_name = 'mypage'

urlpatterns = [
    path('', MyPageView.as_view(), name='top'),#マイページトップURLパターン。
    path('profile/', UserDetailView.as_view(), name='user_detail'),#ユーザープロフィールURLパターン。
    path('profile/edit/', UserEditView.as_view(), name='user_edit'),#ユーザープロフィール編集URLパターン。
]

