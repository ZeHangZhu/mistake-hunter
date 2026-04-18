from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date
from .models import SocraticSession, SocraticMessage, ReviewPlan
from mistakes.models import Mistake


@login_required
def review_plan_view(request):
    """复习计划视图
    
    显示用户今天及之前需要复习的错题计划
    """
    today = date.today()
    # 获取今天及之前需要复习的计划
    plans = ReviewPlan.objects.filter(
        user=request.user,
        scheduled_date__lte=today,
        is_completed=False
    ).select_related('mistake')
    
    context = {
        'plans': plans,
        'today': today,
    }
    return render(request, 'aihelper/review_plan.html', context)


@login_required
def socratic_session_view(request, mistake_id):
    """苏格拉底对话视图
    
    为指定错题创建或继续AI辅导对话
    """
    # 获取错题对象
    mistake = get_object_or_404(Mistake, pk=mistake_id, user=request.user)
    
    # 获取或创建对话会话
    session, created = SocraticSession.objects.get_or_create(
        mistake=mistake,
        user=request.user,
        is_active=True,
        defaults={'started_at': timezone.now()}
    )
    
    # 获取会话中的所有消息
    messages = session.messages.all()
    
    # 处理POST请求，发送新消息
    if request.method == 'POST':
        content = request.POST.get('content')
        
        # 创建用户消息
        SocraticMessage.objects.create(
            session=session,
            role='user',
            content=content
        )
        
        # AI回复（当前为占位符，后续接入真实API）
        ai_response = f'这是对您问题"{content}"的AI回复。（AI功能占位，后续接入真实API）'
        SocraticMessage.objects.create(
            session=session,
            role='ai',
            content=ai_response
        )
        
        return redirect('socratic_session', mistake_id=mistake_id)
    
    context = {
        'session': session,
        'mistake': mistake,
        'messages': messages,
    }
    return render(request, 'aihelper/socratic.html', context)


@login_required
def end_socratic_session_view(request, session_id):
    """结束苏格拉底对话视图
    
    结束指定的AI辅导对话会话
    """
    # 获取会话对象
    session = get_object_or_404(SocraticSession, pk=session_id, user=request.user)
    # 将会话标记为已结束
    session.is_active = False
    session.ended_at = timezone.now()
    session.save()
    messages.success(request, '对话已结束')
    return redirect('mistake_detail', pk=session.mistake.pk)



