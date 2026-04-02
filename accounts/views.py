import secrets
import datetime
from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.views import View
from .models import User, EmailVerificationToken, PasswordResetToken
from .forms import LoginForm, PasswordResetForm, PasswordResetRequestForm, SignupForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


#会員登録手続きとメール認証の処理を行うビュー
#returnはメール認証の案内ページへリダイレクトかエラー時のフォーム再表示
#認証完了後に完了ページへリダイレクトするreturn

#会員登録
class SignupView(View):
    def get(self, request):
        form = SignupForm()
        return render(request, 'accounts/signup.html', {'form': form})
    def post(self, request):
        form = SignupForm(request.POST)#入力データはrequest.POSTに入っている
        if form.is_valid():
            user = form.save()#バリデーションを通った後、saveメソッドが呼び出される
            #メール認証のトークンを生成して保存
            token_string = secrets.token_urlsafe(32)#URLに安全なランダムな文字列を生成
            #認証メールに必要な情報を保存
            EmailVerificationToken.objects.create(user=user, token=token_string)
            #認証URLの生成
            verify_url = request.build_absolute_uri(
                f'/accounts/verify/{token_string}/'
            )
            #認証メールの送信
            send_mail(
                subject='《名古屋グルメ金鯱》メール認証のご案内',
                message=(
                    f'{user.name}様\n'
                        f'会員登録ありがとうございます。\n'
                        f'下記のURLをクリックしてメール認証を完了してください。\n'
                        f'{verify_url}'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
            #認証案内のメッセージを表示
            return redirect('accounts:signup_done')
        #バリデーションエラーがある場合は、フォームを再表示
        return render(request, 'accounts/signup.html', {'form': form})
#メール認証完了後の処理を行うビュー
class SignupDoneView(View):
    def get(self, request):
        return render(request, 'accounts/signup_done.html')

class VerifyEmailView(View):
    def get(self, request, token):
        #メールURLに含まれるトークンをもとに、アクセス時にそのトークンがＤＢに存在するか確認する
        vt = get_object_or_404(EmailVerificationToken, token=token)
        
        #トークンに期限を設定する
        expiry = vt.created_at + datetime.timedelta(minutes=5)
        if timezone.now() > expiry:
            vt.delete()
            messages.error(request, '認証URLの有効期限が切れています。再度登録をしてください。')
            return redirect('accounts:signup')
        
        #トークンが存在する場合は、そのトークンに関連付けられたユーザーのメール認証ステータスを更新する
        vt.user.is_email_verified = True
        vt.user.is_active = True
        vt.user.save()
        #トークンは一度使用されたら削除する
        vt.delete()
        return render(request, 'accounts/verify_email.html')


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('shops:top')
        form = LoginForm()                          # ← 修正
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_suspended:
                messages.error(request, 'このアカウントは停止されています。')
                return render(request, 'accounts/login.html', {'form': form})
            if not user.is_email_verified:
                messages.error(request, 'メール認証が完了していません。届いたメールのリンクをクリックしてください。')
                return render(request, 'accounts/login.html', {'form': form})
            login(request, user)
            next_url = request.GET.get('next', 'shops:top')
            return redirect(next_url)
        return render(request, 'accounts/login.html', {'form': form})


class LogoutView(View):
    def post(self, request):                   
        logout(request)
        return redirect(settings.LOGOUT_REDIRECT_URL)
class PasswordChangeRequestView(View):
    def get(self, request):
        form = PasswordResetRequestForm()
        return render(request, 'accounts/password_change_request.html', {'form': form})

    def post(self, request):
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            return redirect('accounts:password_change_sent')
        return render(request, 'accounts/password_change_request.html', {'form': form})


class PasswordChangeSentView(View):
    def get(self, request):
        return render(request, 'accounts/password_change_sent.html')


class PasswordChangeView(View):
    def get(self, request, token):
        form = PasswordResetForm()
        return render(request, 'accounts/password_change.html', {'form': form, 'token': token})

    def post(self, request, token):
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            return redirect('accounts:login')
        return render(request, 'accounts/password_change.html', {'form': form, 'token': token})


class WithdrawView(View):
    def get(self, request):
        return render(request, 'accounts/withdraw.html')
    
    @method_decorator(login_required)
    def post(self, request):
        user = request.user
        logout(request)
        user.delete()
        return redirect('shops:top')
    
class PasswordResetRequestView(View):
    def get(self, request):
        form = PasswordResetRequestForm()
        return render(request, 'accounts/password_change_request.html', {'form':form})
    def post(self, request):
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user =  User.objects.get(email=email)
                token_string = secrets.token_urlsafe(32)
                PasswordResetToken.objects.create(user=user, token=token_string)
                reset_url = request.build_absolute_uri(
                    f'/accounts/password-reset/{token_string}/'
                )
                send_mail(
                    subject='《名古屋グルメ金鯱》パスワード再設定のご案内',
                    message=(
                        f'{user.name}様\n'
                        f'パスワード再設定のリクエストを受け付けました。\n'
                        f'下記のURLをクリックして新しいパスワードを設定してください。\n'
                        f'{reset_url}'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                )
            #メールアドレスがあろうがなかろうが、送信完了メッセージを表示させる
            except User.DoesNotExist:
                pass
            return redirect('accounts:password_change_sent')
        return render(request, 'accounts/password_change_request.html', {'form': form})
#送信完了の案内ページ
class PasswordChangeSentView(View):
    def get(self, request):
        return render(request, 'accounts/password_change_sent.html')
#パスワード更新・入力
class PasswordResetView(View):
    def get(self, request, token):
        rt = get_object_or_404(PasswordResetToken, token=token, is_used=False,)
        form = PasswordResetForm()
        return render(request, 'accounts/password_change_form.html', {'form': form, 'token': token},)
    
    def post(self, request, token):
        rt = get_object_or_404(PasswordResetToken, token=token, is_used=False,)
        form = PasswordResetForm(request.POST)

        if form.is_valid():
            rt.user.set_password(form.cleaned_data['password'])
            rt.user.save()

            rt.is_used = True
            rt.save()
            messages.success(request, 'パスワードが再設定されました。新しいパスワードでログインしてください。')
            return redirect('accounts:login')
        return render(request, 'accounts/password_change_form.html', {'form': form, 'token': token},)