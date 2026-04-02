from django.urls import path
from .views import (
    AdminTopView,
    #店舗・レビュー管理
    AdminShopListView,
    AdminShopCreateView,
    AdminShopDetailView,
    AdminShopEditView,
    AdminReviewListView,
    AdminReviewDetailView,
    AdminReviewDeleteView,
    #会員管理
    AdminMemberListView,
    AdminMemberDetailView,
    #カテゴリー管理
    AdminCategoryListView,
    AdminCategoryCreateView,
    AdminCategoryEditView,
    AdminCategoryDeleteView,
    #売上管理
    AdminSalesView,
    #サービス管理
    AdminServiceView,
    AdminServiceEditView,
    AdminTermsEditView,

)

app_name = 'admin_panel'

urlpatterns = [
    path('', AdminTopView.as_view(), name='admin_top'),#管理トップURLパターン。
    #店舗管理
    path('shops/', AdminShopListView.as_view(), name='shop_list'),
    path('shops/create/', AdminShopCreateView.as_view(), name='shop_create'),
    path('shops/<int:pk>/', AdminShopDetailView.as_view(), name='shop_detail'),
    path('shops/<int:pk>/edit/', AdminShopEditView.as_view(), name='shop_edit'),
    path('shops/<int:shop_pk>/reviews/', AdminReviewListView.as_view(), name='review_list'),
    path('reviews/<int:pk>/', AdminReviewDetailView.as_view(), name='review_detail'),
    path('reviews/<int:pk>/delete/', AdminReviewDeleteView.as_view(), name='review_delete'),
    #会員管理
    path('members/', AdminMemberListView.as_view(), name='member_list'),
    path('members/<int:pk>/', AdminMemberDetailView.as_view(), name='member_detail'),
    #カテゴリー管理
    path('categories/', AdminCategoryListView.as_view(), name='category_list'),
    path('categories/create/', AdminCategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', AdminCategoryEditView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', AdminCategoryDeleteView.as_view(), name='category_delete'),
    #売上管理
    path('sales/', AdminSalesView.as_view(), name='sales'),
    #サービス管理
    path('service/', AdminServiceView.as_view(), name='service'),
    path('service/edit/', AdminServiceEditView.as_view(), name='service_edit'),
    path('service/terms/', AdminTermsEditView.as_view(), name='terms_edit'),
]