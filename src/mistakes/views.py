from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Max
from django.utils import timezone
from datetime import timedelta
from .models import Subject, Group, KnowledgePoint, Mistake, MistakeImage, ReviewRecord


@login_required
def mistake_list_view(request):
    mistakes = Mistake.objects.filter(user=request.user)
    
    subject_id = request.GET.get('subject')
    group_id = request.GET.get('group')
    error_cause = request.GET.get('error_cause')
    mastery_level = request.GET.get('mastery_level')
    search = request.GET.get('search')
    sort_by = request.GET.get('sort_by', '-created_at')
    
    if subject_id:
        mistakes = mistakes.filter(subject_id=subject_id)
    if group_id:
        mistakes = mistakes.filter(group_id=group_id)
    if error_cause:
        mistakes = mistakes.filter(error_cause=error_cause)
    if mastery_level:
        mistakes = mistakes.filter(mastery_level=mastery_level)
    if search:
        mistakes = mistakes.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search) |
            Q(knowledge_points__name__icontains=search)
        ).distinct()
    
    if sort_by in ['created_at', '-created_at', 'review_count', '-review_count', 'difficulty', '-difficulty']:
        mistakes = mistakes.order_by(sort_by)
    
    subjects = Subject.objects.filter(user=request.user)
    groups = Group.objects.filter(user=request.user)
    
    context = {
        'mistakes': mistakes,
        'subjects': subjects,
        'groups': groups,
    }
    return render(request, 'mistakes/list.html', context)


@login_required
def mistake_detail_view(request, pk):
    mistake = get_object_or_404(Mistake, pk=pk, user=request.user)
    review_records = mistake.review_records.all()
    
    context = {
        'mistake': mistake,
        'review_records': review_records,
    }
    return render(request, 'mistakes/detail.html', context)


@login_required
def mistake_create_view(request):
    subjects = Subject.objects.filter(user=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        solution = request.POST.get('solution')
        correct_answer = request.POST.get('correct_answer')
        user_answer = request.POST.get('user_answer')
        analysis = request.POST.get('analysis')
        error_cause = request.POST.get('error_cause')
        custom_error_cause = request.POST.get('custom_error_cause')
        difficulty = request.POST.get('difficulty')
        subject_id = request.POST.get('subject')
        group_id = request.POST.get('group')
        knowledge_point_ids = request.POST.getlist('knowledge_points')
        
        subject = get_object_or_404(Subject, pk=subject_id, user=request.user)
        group = None
        if group_id:
            group = get_object_or_404(Group, pk=group_id, user=request.user)
        
        # 确保content字段不为空
        if not content and 'image' in request.FILES:
            content = '图片题目'
        
        mistake = Mistake.objects.create(
            title=title,
            content=content,
            solution=solution,
            correct_answer=correct_answer,
            user_answer=user_answer,
            analysis=analysis,
            error_cause=error_cause,
            custom_error_cause=custom_error_cause,
            difficulty=int(difficulty),
            subject=subject,
            group=group,
            user=request.user,
            next_review_at=timezone.now() + timedelta(days=1)
        )
        
        # 处理图片上传
        if 'image' in request.FILES:
            image_file = request.FILES['image']
            MistakeImage.objects.create(
                mistake=mistake,
                image=image_file
            )
        
        # 处理解题过程图片上传
        if 'solution_image' in request.FILES:
            solution_image_file = request.FILES['solution_image']
            MistakeImage.objects.create(
                mistake=mistake,
                image=solution_image_file
            )
        
        # 处理正确答案图片上传
        if 'correct_answer_image' in request.FILES:
            correct_answer_image_file = request.FILES['correct_answer_image']
            MistakeImage.objects.create(
                mistake=mistake,
                image=correct_answer_image_file
            )
        
        # 处理我的答案图片上传
        if 'user_answer_image' in request.FILES:
            user_answer_image_file = request.FILES['user_answer_image']
            MistakeImage.objects.create(
                mistake=mistake,
                image=user_answer_image_file
            )
        
        if knowledge_point_ids:
            mistake.knowledge_points.add(*knowledge_point_ids)
        
        messages.success(request, '错题添加成功')
        return redirect('mistake_detail', pk=mistake.pk)
    
    context = {
        'subjects': subjects,
    }
    return render(request, 'mistakes/create.html', context)


@login_required
def mistake_edit_view(request, pk):
    mistake = get_object_or_404(Mistake, pk=pk, user=request.user)
    subjects = Subject.objects.filter(user=request.user)
    knowledge_points = KnowledgePoint.objects.filter(subject=mistake.subject, user=request.user)
    
    if request.method == 'POST':
        mistake.title = request.POST.get('title')
        mistake.content = request.POST.get('content')
        mistake.solution = request.POST.get('solution')
        mistake.correct_answer = request.POST.get('correct_answer')
        mistake.user_answer = request.POST.get('user_answer')
        mistake.analysis = request.POST.get('analysis')
        mistake.error_cause = request.POST.get('error_cause')
        mistake.custom_error_cause = request.POST.get('custom_error_cause')
        mistake.difficulty = int(request.POST.get('difficulty'))
        
        subject_id = request.POST.get('subject')
        group_id = request.POST.get('group')
        knowledge_point_ids = request.POST.getlist('knowledge_points')
        
        mistake.subject = get_object_or_404(Subject, pk=subject_id, user=request.user)
        if group_id:
            mistake.group = get_object_or_404(Group, pk=group_id, user=request.user)
        else:
            mistake.group = None
        
        # 处理图片上传
        if 'image' in request.FILES:
            # 删除旧图片
            mistake.images.all().delete()
            # 添加新图片
            image_file = request.FILES['image']
            MistakeImage.objects.create(
                mistake=mistake,
                image=image_file
            )
        
        # 处理解题过程图片上传
        if 'solution_image' in request.FILES:
            # 添加新图片
            solution_image_file = request.FILES['solution_image']
            MistakeImage.objects.create(
                mistake=mistake,
                image=solution_image_file
            )
        
        # 处理正确答案图片上传
        if 'correct_answer_image' in request.FILES:
            # 添加新图片
            correct_answer_image_file = request.FILES['correct_answer_image']
            MistakeImage.objects.create(
                mistake=mistake,
                image=correct_answer_image_file
            )
        
        # 处理我的答案图片上传
        if 'user_answer_image' in request.FILES:
            # 添加新图片
            user_answer_image_file = request.FILES['user_answer_image']
            MistakeImage.objects.create(
                mistake=mistake,
                image=user_answer_image_file
            )
            # 确保content字段不为空
            if not mistake.content:
                mistake.content = '图片题目'
        
        mistake.knowledge_points.set(knowledge_point_ids)
        mistake.save()
        
        messages.success(request, '错题更新成功')
        return redirect('mistake_detail', pk=mistake.pk)
    
    context = {
        'mistake': mistake,
        'subjects': subjects,
        'knowledge_points': knowledge_points,
    }
    return render(request, 'mistakes/edit.html', context)


@login_required
def mistake_delete_view(request, pk):
    mistake = get_object_or_404(Mistake, pk=pk, user=request.user)
    if request.method == 'POST':
        mistake.delete()
        messages.success(request, '错题删除成功')
        return redirect('mistake_list')
    return render(request, 'mistakes/delete.html', {'mistake': mistake})


@login_required
def subject_list_view(request):
    subjects = Subject.objects.filter(user=request.user)
    
    # 定义默认排序顺序
    default_order = ['语文', '数学', '英语', '物理', '化学', '生物', '政治', '历史', '地理', '技术', '信息', '通用']
    
    # 按规则排序学科
    def get_subject_order(subject):
        if subject.name in default_order:
            return default_order.index(subject.name)
        else:
            # 其他学科按首字母排序，放在默认学科后面
            return len(default_order) + ord(subject.name[0])
    
    # 排序学科列表
    sorted_subjects = sorted(subjects, key=get_subject_order)
    
    # 更新数据库中的order字段
    for index, subject in enumerate(sorted_subjects):
        if subject.order != index:
            subject.order = index
            subject.save()
    
    return render(request, 'mistakes/subjects.html', {'subjects': sorted_subjects})


@login_required
def subject_create_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        color = request.POST.get('color', '#007bff')
        
        if Subject.objects.filter(name=name, user=request.user).exists():
            messages.error(request, '该学科已存在')
        else:
            # 定义默认排序顺序
            default_order = ['语文', '数学', '英语', '物理', '化学', '生物', '政治', '历史', '地理', '技术', '信息', '通用']
            
            # 计算新学科的排序值
            if name in default_order:
                order = default_order.index(name)
            else:
                # 其他学科按首字母排序，放在默认学科后面
                order = len(default_order) + ord(name[0])
            
            Subject.objects.create(name=name, color=color, user=request.user, order=order)
            messages.success(request, '学科添加成功')
            return redirect('subject_list')
    
    return render(request, 'mistakes/subject_create.html')


@login_required
def subject_delete_view(request, pk):
    subject = get_object_or_404(Subject, pk=pk, user=request.user)
    
    # 检查是否有错题关联
    if subject.mistakes.exists():
        messages.error(request, '该学科下还有错题，无法删除')
        return redirect('subject_list')
    
    subject.delete()
    messages.success(request, '学科删除成功')
    return redirect('subject_list')





@login_required
def review_mistake_view(request, pk):
    mistake = get_object_or_404(Mistake, pk=pk, user=request.user)
    
    if request.method == 'POST':
        result = request.POST.get('result')
        notes = request.POST.get('notes')
        
        ReviewRecord.objects.create(
            mistake=mistake,
            result=result,
            notes=notes
        )
        
        mistake.review_count += 1
        mistake.last_reviewed_at = timezone.now()
        
        if result == 'mastered':
            mistake.mastery_level = 'mastered'
            mistake.next_review_at = timezone.now() + timedelta(days=7)
        else:
            mistake.mastery_level = 'to_review'
            mistake.next_review_at = timezone.now() + timedelta(days=1)
        
        mistake.save()
        
        messages.success(request, '复习记录已保存')
        return redirect('mistake_detail', pk=mistake.pk)
    
    return render(request, 'mistakes/review.html', {'mistake': mistake})
