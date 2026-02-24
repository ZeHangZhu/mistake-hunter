from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date
from .models import SocraticSession, SocraticMessage, ReviewPlan
from mistakes.models import Mistake


@login_required
def review_plan_view(request):
    today = date.today()
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
    mistake = get_object_or_404(Mistake, pk=mistake_id, user=request.user)
    
    session, created = SocraticSession.objects.get_or_create(
        mistake=mistake,
        user=request.user,
        is_active=True,
        defaults={'started_at': timezone.now()}
    )
    
    messages = session.messages.all()
    
    if request.method == 'POST':
        content = request.POST.get('content')
        
        SocraticMessage.objects.create(
            session=session,
            role='user',
            content=content
        )
        
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
    session = get_object_or_404(SocraticSession, pk=session_id, user=request.user)
    session.is_active = False
    session.ended_at = timezone.now()
    session.save()
    messages.success(request, '对话已结束')
    return redirect('mistake_detail', pk=session.mistake.pk)



