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


@login_required
def announcement_detail_view(request, announcement_id):
    # 直接返回固定的markdown内容，避免文件读取问题
    if announcement_id == 1:
        markdown_content = '''# 系统更新公告

## 错题猎手系统已完成更新

### 新增功能

- **AI辅导功能**：智能分析错题，提供个性化学习建议
- **知识点关联分析**：自动识别相关知识点，帮助构建知识体系
- **学习进度可视化**：通过图表直观展示学习情况

### 优化内容

- 界面响应速度提升
- 错题录入流程简化
- 复习计划算法优化

### 技术支持

如有任何问题，请联系我们的技术支持团队。

---

**发布日期**：2026-02-15
**版本号**：v2.0.0'''
    elif announcement_id == 2:
        markdown_content = '''# 使用指南

## 如何高效使用错题猎手进行备考复习

### 1. 错题录入

- **手动录入**：点击"添加错题"按钮，填写题目信息、答案和解析
- **批量导入**：支持从Excel文件批量导入错题
- **拍照上传**：通过手机拍照，自动识别题目内容

### 2. 错题分类

- **按学科分类**：将错题归类到不同学科
- **按知识点分类**：添加知识点标签，便于查找
- **按难度分类**：标记题目难度，有针对性地复习

### 3. 复习计划

- **智能复习**：系统根据艾宾浩斯遗忘曲线自动生成复习计划
- **自定义复习**：手动设置复习时间和频率
- **复习提醒**：通过邮件或短信提醒复习

### 4. 统计分析

- **学习数据**：查看错题总数、已掌握和待复习的数量
- **薄弱环节**：分析易错知识点，针对性加强
- **学习趋势**：追踪学习进度，调整学习策略

### 5. 实用技巧

- 定期回顾错题，加深记忆
- 结合AI助手解答疑惑
- 利用"举一反三"功能巩固知识点

---

**发布日期**：2026-02-10'''
    elif announcement_id == 3:
        markdown_content = '''# 功能预告

## 即将上线的新功能：知识点关联分析

### 功能介绍

**知识点关联分析**是错题猎手即将推出的核心功能，旨在帮助用户构建完整的知识体系，提高学习效率。

### 主要特点

- **智能关联**：自动识别题目之间的知识点关联
- **知识图谱**：生成可视化的知识图谱，直观展示知识点之间的联系
- **弱点分析**：通过知识图谱分析学习薄弱环节
- **推荐学习路径**：基于知识关联，推荐最优学习顺序

### 技术原理

- 采用自然语言处理技术识别知识点
- 使用图数据库存储知识点关联
- 应用机器学习算法优化关联分析

### 上线时间

预计将于2026年3月正式上线，敬请期待！

---

**发布日期**：2026-02-05'''
    else:
        markdown_content = '# 公告不存在'
    
    context = {
        'announcement_id': announcement_id,
        'markdown_content': markdown_content,
    }
    return render(request, 'announcement_detail.html', context)
