from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views import View

from accounts.models import User
from shops.models import Shop, Category
from django.contrib.admin.views.decorators import staff_member_required
from reviews.models import Review
from reservations.models import Reservation
from payments.models import Subscription, Payment
from .models import ServiceSettings

import datetime
from django.utils import timezone
from django.db.models import Sum, Count


def admin_required(view_func):
    return staff_member_required(view_func, login_url='/accounts/login/',)

class AdminTopView(View):
    @method_decorator(admin_required)
    def get(self, request):
        return redirect('admin_panel:shop_list')

class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = [
            'name', 'category', 'image', 'address', 'area',
            'phone', 'open_time', 'close_time', 'budget',
            'description', 'status',
        ]

#店舗一覧
class AdminShopListView(View):
    #店舗の一覧を表示するビューを作成する。店舗の名前やカテゴリー、作成日時などを表示する。
    @method_decorator(admin_required)
    def get(self, request):
        #qは、店舗の名前やカテゴリーを検索するためのクエリパラメータを取得する。qが空の場合は、全ての店舗を表示する。
        q = request.GET.get('q', '')
        #shopsは、店舗の一覧を取得するためのクエリセットを作成する。qが空の場合は、全ての店舗を取得する。qが空でない場合は、店舗の名前やカテゴリーにqが含まれる店舗を取得する。
        shops = Shop.objects.all().select_related('category').order_by('-created_at')
        #qが空でない場合は、店舗の名前やカテゴリーにqが含まれる店舗を取得する。
        # name__icontainsは、店舗の名前にqが含まれる店舗を取得するためのフィルタリング条件で、category__name__icontainsは、店舗のカテゴリーの名前にqが含まれる店舗を取得するためのフィルタリング条件。
        if q:
            shops = shops.filter(name__icontains=q)
        #returnには、店舗の一覧を表示するためのテンプレートと、店舗の一覧を渡す。テンプレートには、店舗の名前やカテゴリー、作成日時などを表示する。
        return render(request, 'admin_panel/shop_list.html', {'shops': shops, 'q': q})
    

#店舗の新規登録
class AdminShopCreateView(View):
    @method_decorator(admin_required)
    def get(self, request):
        #returnには、店舗の新規登録を表示するためのテンプレートと、店舗の新規登録フォームを渡す。テンプレートには、店舗の名前やカテゴリー、住所、電話番号、営業時間などを入力するフォームを表示する。
        return render(request, 'admin_panel/shop_form.html', {'form': ShopForm(), 'title': '店舗新規登録'})
    @method_decorator(admin_required)
    def post(self, request):
        #formに店舗の新規登録フォームをインスタンス化して、POSTリクエストからデータを渡す。request.FILESに画像などのファイルをアップロードするためのデータを渡す。
        form = ShopForm(request.POST, request.FILES)
        #if文にして、formが有効な場合は、formを保存して、店舗の一覧にリダイレクトする。formが無効な場合は、店舗の新規登録を表示するためのテンプレートと、店舗の新規登録フォームを渡す。テンプレートには、店舗の名前やカテゴリー、住所、電話番号、営業時間などを入力するフォームを表示する。
        if form.is_valid():
            form.save()
            #returnにして、店舗の一覧にリダイレクトする。
            return redirect('admin_panel:shop_list')
        #returnにして、店舗の新規登録を表示するためのテンプレートと、店舗の新規登録フォームを渡す。テンプレートには、店舗の名前やカテゴリー、住所、電話番号、営業時間などを入力するフォームを表示する。
        return render(request, 'admin_panel/shop_form.html', {'form': form, 'title': '店舗新規登録'})
#店舗の詳細
class AdminShopDetailView(View):
    @method_decorator(admin_required)
    #店舗の詳細を表示するビューを作成する。店舗の名前やカテゴリー、住所、電話番号、営業時間などを表示する。
    def get(self, request, pk):
        #shopに店舗の詳細を取得するためのget_object_or_404を使って、pkに対応する店舗を取得する。
        shop = get_object_or_404(Shop, pk=pk)
        #returnに店舗の詳細を表示するためのテンプレートと、店舗の詳細を返す
        return render(request, 'admin_panel/shop_detail.html', {'shop': shop})
#店舗の編集
class AdminShopEditView(View):
    @method_decorator(admin_required)
    #店舗の編集を表示するビューを作成する。
    def get(self, request, pk):
        shop = get_object_or_404(Shop, pk=pk)
        return render(request, 'admin_panel/shop_edit.html', {'form': ShopForm(instance=shop), 'title':'店舗編集', 'shop': shop,})
    #店舗の編集を保存するビューを作成
    @method_decorator(admin_required)
    def post(self, request, pk):
        shop = get_object_or_404(Shop, pk=pk)
        form = ShopForm(request.POST, request.FILES, instance=shop)
        #if文にして、formが有効な場合は、formを保存して、店舗の詳細にリダイレクトする。formが無効な場合は、店舗の編集を表示するためのテンプレートと、店舗の編集フォームを渡す。テンプレートには、店舗の名前やカテゴリー、住所、電話番号、営業時間などを入力するフォームを表示する。
        if form.is_valid():
            form.save()
            return redirect('admin_panel:shop_detail', pk=pk)
        return render(request, 'admin_panel/shop_form.html', {'form': form, 'title': '店舗編集', 'shop': shop,})

#レビューの一覧
class AdminReviewListView(View):
    @method_decorator(admin_required)
    def get(self, request, pk):
        shop = get_object_or_404(Shop, pk=pk)
        #reviewsにレビューの一覧を取得するためのクエリセットを作成する。shopに対応するレビューを取得する。select_related('user')を使って、レビューのユーザー情報も一緒に取得する。order_by('-created_at')を使って、レビューの作成日時の降順で並び替える。
        reviews = Review.objects.filter(shop=shop).select_related('user').order_by('-created_at')
        #returnに、レビューの一覧を表示するためのテンプレートと、レビューの一覧を渡す。テンプレートには、レビューの内容や評価、ユーザー名などを表示する。
        return render(request, 'admin_panel/review_list.html', {'shop':shop, 'reviews':reviews})

#レビューの詳細
class AdminReviewDetailView(View):
    @method_decorator(admin_required)
    def get(self, request, pk):
        #reviewにレビューの詳細を取得するためのget_object_or_404を使って、pkに対応するレビューを取得する。
        review = get_object_or_404(Review, pk=pk)
    #returnに、レビューの詳細を表示するためのテンプレートと、レビューの詳細を渡す。テンプレートには、レビューの内容や評価、ユーザー名などを表示する。
        return render(request, 'admin_panel/review_detail.html', {'review': review})

#レビューの削除
class AdminReviewDeleteView(View):
    @method_decorator(admin_required)
    def post(self, request, pk):
        review = get_object_or_404(Review, pk=pk)
        shop_pk = review.shop.pk#レビューを削除する前に、shop_pkにレビューの店舗のpkを保存する。レビューを削除した後に、店舗の詳細にリダイレクトするために必要。
        review.delete()
        return redirect('admin_panel:review_list', pk=shop_pk)

#会員一覧
class AdminMemberListView(View):
    @method_decorator(admin_required)
    def get(self, request):
        #qは、会員の名前やメールアドレスを検索するためのクエリパラメータを取得する。qが空の場合は、全ての会員を表示する。
        q = request.GET.get('q', '')
        #管理者を除く一般ユーザーの一覧を取得するめのクエリセットを作成する。
        users = User.objects.filter(is_staff=False).order_by('-date_joined')
        if q:
            #usersに会員の名前やメールアドレスにqが含まれる会員を取得するためのフィルタリング条件を追加する。
            #フィルタリング条件はname__icontains=q（会員の名前にqが含まれる会員を取得）とemail__icontains=q（会員のメールアドレスにqが含まれる）をor条件で結合する。
            users = users.filter(name__icontains=q) or users.filter(email__icontains=q)
            users = users.distinct()#重複は除外する。
        return render(request, 'admin_panel/member_list.html', {'users': users, 'q': q})
    
#会員の詳細画面・その変更
class AdminMemberDetailView(View):
    @method_decorator(admin_required)
    def get(self, request, pk):
        member = get_object_or_404(User, pk=pk)
        return render(request, 'admin_panel/member_detail.html', {'member': member})
    @method_decorator(admin_required)
    def post(self, request, pk):
        member = get_object_or_404(User, pk=pk)
        #actionは、会員の状態を変更するためのsuspend(停止)とactivate(有効化)のどちらかを取得するためのPOSTリクエストからパラメータを取得する。
        action = request.POST.get('action')
        #利用停止・解除の処理を行う。
        if action == 'suspend':
            member.status = User.STATUS_SUSPENDED
            member.save()
        elif action == 'activate':
            member.status = User.STATUS_ACTIVE
            member.save()
        return redirect('admin_panel:member_detail', pk=pk)
    

#カテゴリのフォームを作る
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name',]


#カテゴリの一覧
class AdminCategoryListView(View):
    @method_decorator(admin_required)
    def get(self, request):
        categories = Category.objects.all().order_by('name')
        return render(request, 'admin_panel/category_list.html', {'categories': categories})
    
#カテゴリの新規登録
class AdminCategoryCreateView(View):
    @method_decorator(admin_required)
    def get(self, request):
        return render(request, 'admin_panel/category_form.html', {
            'form': CategoryForm(),
            'title': 'カテゴリ新規登録',
        })
    
#カテゴリ編集
class AdminCategoryEditView(View):
    #カテゴリの編集を表示するビューを作成する。カテゴリの名前を入力するフォームを表示する。キャンセルボタンの戻り先は'obj'にして、カテゴリの詳細に戻るようにする。
    @method_decorator(admin_required)
    def get(self, request, pk):
        cat = get_object_or_404(Category, pk=pk)
        return render(request, 'admin_panel/category_form.html', {
            'form': CategoryForm(instance=cat),
            'title': 'カテゴリ編集',
            'obj': cat,#
        })

#カテゴリ削除
class AdminCategoryDeleteView(View):
    @method_decorator(admin_required)
    #カテゴリの削除を行うビューを作成する。カテゴリを削除した後は、カテゴリの一覧にリダイレクトする。
    def post(self, request, pk):
        cat = get_object_or_404(Category, pk=pk)
        cat.delete()
        return redirect('admin_panel:category_list')
    

#売上集計
class AdminSalesView(View):
    @method_decorator(admin_required)
    def get(self, request):
        now = timezone.now()
        year = int(request.GET.get('year', now.year))
        month = int(request.GET.get('month', now.month))
        #集計期間
        start = datetime.date(year, month, 1)
        if month == 12:
            end = datetime.date(year + 1, 1, 1)
        else:
            end = datetime.date(year, month + 1, 1)#12の場合は、年を繰り上げて1月にする。
        #決済データの集計
        payments = Payment.objects.filter(
            paid_at__date__gte=start,#gte(以上)
            paid_at__date__lt=end,#lt(未満)
        ).select_related('user').order_by('-paid_at')
        #月間総売上
        total_sales = payments.filter(status=Payment.STATUS_SUCCESS).aggregate(total=Sum('amount'))['total'] or 0
        
        #会員数の集計
        total_users = User.objects.filter(is_staff=False).count()#一般ユーザーのみでis_staff=False
        free_users = User.objects.filter(is_staff=False, member_type=User.MEMBER_TYPE_FREE,).count()#一般ユーザーで無料会員の数を数えるためのクエリセットを作成する。
        paid_users = User.objects.filter(is_staff=False, member_type=User.MEMBER_TYPE_PAID,).count()#一般ユーザーで有料会員の数を数えるためのクエリセットを作成する。

        #店舗数の集計
        shop_count = Shop.objects.count()

        #予約数の集計
        reservation_count = Reservation.objects.filter(
            reserved_at__date__gte=start,
            reserved_at__date__lt=end,
        ).count()

        #年月のセレクトボックスのためのデータ
        years = range(now.year - 2, now.year + 2)
        months = range(1, 13)

        context = {
            'payments': payments,
            'total_sales': total_sales,
            'total_users': total_users,
            'free_users': free_users,
            'paid_users': paid_users,
            'shop_count': shop_count,
            'reservation_count': reservation_count,
            'year': year,
            'month': month,
            'years': years,
            'months': months,
        }
        return render(request, 'admin_panel/sales.html', context)
    
#基本の情報の管理
class ServiceSettingsForm(forms.ModelForm):
    class Meta:
        model = ServiceSettings
        fields = ['service_name', 'logo', 'contact_email']

#規約編集
class TermsForm(forms.ModelForm):
    class Meta:
        model = ServiceSettings
        fields = ['terms']
        widgets = {
            'terms': forms.Textarea(attrs={'rows': 20}),
        }

#サービス基本情報管理
class AdminServiceView(View):
    @method_decorator(admin_required)
    def get(self, request):
        #今回はget_or_createを使って、ServiceSettingsのインスタンスを１つ作って、管理画面で編集できるようにする
        obj, _ = ServiceSettings.objects.get_or_create(pk=1)
        return render(request, 'admin_panel/service.html', {'obj': obj})
    
#基本情報編集
class AdminServiceEditView(View):
    @method_decorator(admin_required)
    def get(self, request):
        obj, _ = ServiceSettings.objects.get_or_create(pk=1)
        form =  ServiceSettingsForm(instance=obj)
        return render(request, 'admin_panel/service_edit.html', {'form': form})
    @method_decorator(admin_required)
    def post(self, request):
        obj, _ = ServiceSettings.objects.get_or_create(pk=1)
        form = ServiceSettingsForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('admin_panel:service')
        return render(request, 'admin_panel/service_edit.html', {'form': form})
    

#規約編集
#formにTermsFormを使って、ServiceSettingsのtermsフィールドを編集するためのフォームを作成する。
class AdminTermsEditView(View):
    @method_decorator(admin_required)
    #規約編集の表示を行うビューを作成する。規約を編集するためのフォームを表示する。
    def get(self, request):
        obj, _ = ServiceSettings.objects.get_or_create(pk=1)
        form = TermsForm(instance=obj)
        return render(request, 'admin_panel/terms_edit.html', {'form': form})
    
    @method_decorator(admin_required)
    #規約編集の保存を行うビューを作成する。規約を保存した後は、規約編集画面にリダイレクトする。
    def post(self, request):
        obj, _ = ServiceSettings.objects.get_or_create(pk=1)
        form = TermsForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('admin_panel:terms_edit')
        return render(request, 'admin_panel/terms_edit.html', {'form': form})