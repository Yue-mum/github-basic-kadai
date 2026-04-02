import secrets
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User

#会員登録フォーム
class SignupForm(forms.ModelForm):
    password = forms.CharField(label='パスワード',widget=forms.PasswordInput,)
    password_confirm = forms.CharField(label='パスワード（確認）',widget=forms.PasswordInput,)

    class Meta:
        model = User
        fields = ['name', 'email', 'phone', 'password']
    #フォーム全体のバリデーション
    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get('password')
        pw2 = cleaned.get('password_confirm')

        if pw and pw2 and pw != pw2:
            raise forms.ValidationError('パスワードが一致しません。')
        return cleaned
    #saveメソッドのオーバーライド
    def save(self, commit=True):
        #DBに保存しない状態のオブジェクトの取得
        user = super().save(commit=False)
        #パスワードのハッシュ化
        user.set_password(self.cleaned_data['password'])
        user.is_active = False
        user.is_email_verified = False#メール認証前だから
        if commit:
            user.save()
        return user

#ログインフォーム
#AuthenticationFormを継承して、usernameをemailに変更
class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='メールアドレス')
#会員情報編集
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'email', 'phone']
#再設定メール
class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label='メールアドレス')
#パスワード再設定フォーム
class PasswordResetForm(forms.Form):
    password = forms.CharField(label='新しいパスワード', widget=forms.PasswordInput,)
    password_confirm = forms.CharField(label='パスワード（確認）', widget=forms.PasswordInput,)
    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get('password')
        pw2 = cleaned.get('password_confirm')
        if pw and pw2 and pw != pw2:
            raise forms.ValidationError('パスワードが一致しません。')
        return cleaned