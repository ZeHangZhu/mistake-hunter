from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from .models import User


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, '两次输入的密码不一致')
            return render(request, 'users/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在')
            return render(request, 'users/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, '邮箱已被注册')
            return render(request, 'users/register.html')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=True
        )

        messages.success(request, '注册成功，请登录')
        return redirect('login')

    return render(request, 'users/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        login_input = request.POST.get('login')
        password = request.POST.get('password')

        user = None
        if '@' in login_input:
            try:
                user = User.objects.get(email=login_input)
                user = authenticate(request, username=user.username, password=password)
            except User.DoesNotExist:
                pass
        else:
            user = authenticate(request, username=login_input, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, '用户名/邮箱或密码错误')

    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            reset_url = request.build_absolute_uri(f'/reset-password/{uid}/{token}/')
            
            send_mail(
                '密码重置',
                f'请点击以下链接重置密码：{reset_url}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            messages.success(request, '重置密码的邮件已发送到您的邮箱')
        except User.DoesNotExist:
            messages.error(request, '该邮箱未注册')

    return render(request, 'users/forgot_password.html')


def reset_password_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if password != confirm_password:
                messages.error(request, '两次输入的密码不一致')
                return render(request, 'users/reset_password.html')

            user.set_password(password)
            user.save()
            messages.success(request, '密码重置成功，请登录')
            return redirect('login')

        return render(request, 'users/reset_password.html')
    else:
        messages.error(request, '重置链接无效或已过期')
        return redirect('forgot_password')


@login_required
def dashboard_view(request):
    total_mistakes = request.user.mistakes.count()
    to_review = request.user.mistakes.filter(mastery_level='to_review').count()
    mastered = request.user.mistakes.filter(mastery_level='mastered').count()
    subject_count = request.user.subjects.count()
    recent_mistakes = request.user.mistakes.all()[:5]
    
    context = {
        'total_mistakes': total_mistakes,
        'to_review': to_review,
        'mastered': mastered,
        'subject_count': subject_count,
        'recent_mistakes': recent_mistakes,
    }
    return render(request, 'dashboard.html', context)
