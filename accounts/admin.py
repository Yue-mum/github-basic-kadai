from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, EmailVerificationToken, PasswordResetToken

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    #一覧表示
    list_display = ('email', 'name', 'member_type', 'status', 'is_email_verified','date_joined')
    list_filter = ('member_type', 'status', 'is_staff')
    search_fields = ('email', 'name')
    ordering = ('-date_joined',)
    #詳細画面のレイアウト。models.py振り返ってね～
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('個人情報', {'fields': ('name', 'phone')}),
        ('会員情報', {'fields': ('member_type', 'status', 'is_email_verified')}),
        ('権限', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('日時', {'fields': ('date_joined', 'last_login')}),
    )
    #新規作成画面のレイアウト
    add_fieldsets = (
        #第一引数をNoneに変換して
        ('新規作成', {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2')
        })
    )
@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at')
@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'is_used', 'created_at')

