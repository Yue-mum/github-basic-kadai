from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from .forms import UserEditForm

#マイページのトップ
class MyPageView(View):
    @method_decorator(login_required)
    def get(self, request):
        return render(request, 'accounts/mypage.html')
    
#会員情報詳細
class UserDetailView(View):
    @method_decorator(login_required)
    def get(self, request):
        return render(request, 'accounts/user_detail.html')
    
#会員情報編集
class UserEditView(View):
    @method_decorator(login_required)
    def get(self, request):
        form = UserEditForm(instance=request.user)
        return render(request, 'accounts/user_edit.html', {'form': form})

    @method_decorator(login_required)
    def post(self, request):
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('mypage:user_detail')
        return render(request, 'accounts/user_edit.html', {'form': form})