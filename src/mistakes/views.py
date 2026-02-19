from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from .models import Mistake, Subject, Group, KnowledgePoint, MistakeImage, ReviewRecord, ReviewImage, PointsRecord
from django.db.models import Q
from WebITRTeach import FormulaRecognizer
import os
import threading


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


# 初始化FormulaRecognizer
APPID = "bd6d7a3c"
APIKey = "ca854ccd4fa3c72a8ea1b0fbf3afac1c"
Secret = "MTEzNjZlZDZhMTVjYTRiM2NiMmU3YzQz"
recognizer = FormulaRecognizer(APPID, APIKey, Secret)

# 后台线程处理OCR识别
def process_ocr_in_background(mistake_image_id):
    try:
        mistake_image = MistakeImage.objects.get(pk=mistake_image_id)
        # 使用 Django 的 settings.MEDIA_ROOT 来构建正确的路径
        image_path = os.path.join(settings.MEDIA_ROOT, str(mistake_image.image))
        
        print(f"开始处理OCR识别，图片路径: {image_path}")
        
        if os.path.exists(image_path):
            APPID = "bd6d7a3c"
            APIKey = "ca854ccd4fa3c72a8ea1b0fbf3afac1c"
            Secret = "MTEzNjZlZDZhMTVjYTRiM2NiMmU3YzQz"
            
            recognizer = FormulaRecognizer(APPID, APIKey, Secret)
            
            image_path = "D:/ocr_test.jpg"
            
            try:
                ocr_result = recognizer.recognize(image_path)
                print("识别结果：")
                print(ocr_result)
            except Exception as e:
                print(f"识别失败：{e}")
            
            # 更新数据库
            mistake_image.ocr_text = ocr_result
            mistake_image.save()
            
            # 同时更新 Mistake 的 content 字段
            mistake = mistake_image.mistake
            # 只有当 content 为空或者是默认值时才更新
            if not mistake.content or mistake.content == '图片题目':
                mistake.content = ocr_result
                mistake.save()
                print(f"已更新题目content: {ocr_result}")
        else:
            print(f"图片文件不存在: {image_path}")
    except Exception as e:
        import traceback
        print(f"后台OCR识别失败: {e}")
        print(traceback.format_exc())


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
            mistake_image = MistakeImage.objects.create(
                mistake=mistake,
                image=image_file
            )
            # 创建后台线程处理OCR识别
            thread = threading.Thread(
                target=process_ocr_in_background,
                args=(mistake_image.pk,)
            )
            thread.daemon = True
            thread.start()
        
        # 处理解题过程图片上传
        if 'solution_image' in request.FILES:
            solution_image_file = request.FILES['solution_image']
            mistake_image = MistakeImage.objects.create(
                mistake=mistake,
                image=solution_image_file
            )
            # 创建后台线程处理OCR识别
            thread = threading.Thread(
                target=process_ocr_in_background,
                args=(mistake_image.pk,)
            )
            thread.daemon = True
            thread.start()
        
        # 处理正确答案图片上传
        if 'correct_answer_image' in request.FILES:
            correct_answer_image_file = request.FILES['correct_answer_image']
            mistake_image = MistakeImage.objects.create(
                mistake=mistake,
                image=correct_answer_image_file
            )
            # 创建后台线程处理OCR识别
            thread = threading.Thread(
                target=process_ocr_in_background,
                args=(mistake_image.pk,)
            )
            thread.daemon = True
            thread.start()
        
        # 处理我的答案图片上传
        if 'user_answer_image' in request.FILES:
            user_answer_image_file = request.FILES['user_answer_image']
            mistake_image = MistakeImage.objects.create(
                mistake=mistake,
                image=user_answer_image_file
            )
            # 创建后台线程处理OCR识别
            thread = threading.Thread(
                target=process_ocr_in_background,
                args=(mistake_image.pk,)
            )
            thread.daemon = True
            thread.start()
        
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
            mistake_image = MistakeImage.objects.create(
                mistake=mistake,
                image=image_file
            )
            # 创建后台线程处理OCR识别
            thread = threading.Thread(
                target=process_ocr_in_background,
                args=(mistake_image.pk,)
            )
            thread.daemon = True
            thread.start()
        
        # 处理解题过程图片上传
        if 'solution_image' in request.FILES:
            # 添加新图片
            solution_image_file = request.FILES['solution_image']
            mistake_image = MistakeImage.objects.create(
                mistake=mistake,
                image=solution_image_file
            )
            # 创建后台线程处理OCR识别
            thread = threading.Thread(
                target=process_ocr_in_background,
                args=(mistake_image.pk,)
            )
            thread.daemon = True
            thread.start()
        
        # 处理正确答案图片上传
        if 'correct_answer_image' in request.FILES:
            # 添加新图片
            correct_answer_image_file = request.FILES['correct_answer_image']
            mistake_image = MistakeImage.objects.create(
                mistake=mistake,
                image=correct_answer_image_file
            )
            # 创建后台线程处理OCR识别
            thread = threading.Thread(
                target=process_ocr_in_background,
                args=(mistake_image.pk,)
            )
            thread.daemon = True
            thread.start()
        
        # 处理我的答案图片上传
        if 'user_answer_image' in request.FILES:
            # 添加新图片
            user_answer_image_file = request.FILES['user_answer_image']
            mistake_image = MistakeImage.objects.create(
                mistake=mistake,
                image=user_answer_image_file
            )
            # 创建后台线程处理OCR识别
            thread = threading.Thread(
                target=process_ocr_in_background,
                args=(mistake_image.pk,)
            )
            thread.daemon = True
            thread.start()
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
        
        # 创建复习记录
        review_record = ReviewRecord.objects.create(
            mistake=mistake,
            result=result,
            notes=notes
        )
        
        # 处理复习笔记图片上传
        if 'notes_image' in request.FILES:
            notes_image_file = request.FILES['notes_image']
            ReviewImage.objects.create(
                review_record=review_record,
                image=notes_image_file
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
        
        # 计算积分奖励
        total_points = 0
        now = timezone.now()
        
        # 基础复习积分
        base_points = 5
        total_points += base_points
        PointsRecord.objects.create(
            user=request.user,
            points=base_points,
            reason='review',
            mistake=mistake
        )
        
        # 时间奖励
        time_diff = now - mistake.next_review_at
        if time_diff.days <= 0:
            # 提前或按时复习
            if time_diff.days == 0:
                # 按时复习奖励
                on_time_points = 3
                total_points += on_time_points
                PointsRecord.objects.create(
                    user=request.user,
                    points=on_time_points,
                    reason='on_time_review',
                    mistake=mistake
                )
            else:
                # 提前复习奖励（提前越多奖励越少）
                early_days = abs(time_diff.days)
                early_points = max(1, 3 - early_days)
                total_points += early_points
                PointsRecord.objects.create(
                    user=request.user,
                    points=early_points,
                    reason='early_review',
                    mistake=mistake
                )
        
        # 难度奖励
        difficulty_bonus = mistake.difficulty
        total_points += difficulty_bonus
        PointsRecord.objects.create(
            user=request.user,
            points=difficulty_bonus,
            reason='difficulty_bonus',
            mistake=mistake
        )
        
        # 更新用户积分
        request.user.points += total_points
        request.user.save()
        
        messages.success(request, f'复习记录已保存，获得 {total_points} 积分！')
        return redirect('mistake_detail', pk=mistake.pk)
    
    return render(request, 'mistakes/review.html', {'mistake': mistake})


@login_required
def generate_review_plan_view(request):
    try:
        if request.method == 'POST':
            # 获取每日复习数量，设置默认值为10
            daily_limit = int(request.POST.get('daily_limit', 10))
            
            # 保存设置到用户模型
            try:
                request.user.daily_review_limit = daily_limit
                request.user.save()
            except Exception as e:
                print(f"保存用户设置时出错: {e}")
            
            # 收集所有待复习的题目（包括所有题目，无论复习时间）
            now = timezone.now()
            # 获取所有题目，按复习时间排序，并预加载图片
            all_mistakes = Mistake.objects.filter(
                user=request.user
            ).prefetch_related('images').order_by('next_review_at')  # 优先选择即将到期的
            
            # 最多获取每日限制的2倍，确保有足够的题目
            reviewable_mistakes = list(all_mistakes[:daily_limit * 2])
            
            # 计算每道题的优先级分数
            prioritized_mistakes = []
            for mistake in reviewable_mistakes:
                # 基础分数计算
                priority_score = 0
                
                # 1. 基于复习时间的优先级
                days_overdue = (now - mistake.next_review_at).days
                if days_overdue > 0:
                    priority_score += days_overdue * 10
                else:
                    # 对于未到复习时间的题目，根据距离复习时间的远近计算分数
                    days_until_review = (mistake.next_review_at - now).days
                    priority_score += max(0, 20 - days_until_review * 2)  # 距离越近分数越高
                
                # 2. 基于掌握程度的优先级
                if mistake.mastery_level == 'to_review':
                    priority_score += 50
                
                # 3. 基于难度的优先级
                priority_score += mistake.difficulty * 10
                
                # 4. 基于复习次数的优先级（复习次数少的优先级高）
                priority_score += (10 - min(mistake.review_count, 10)) * 5
                
                prioritized_mistakes.append((priority_score, mistake))
            
            # 按优先级分数排序
            prioritized_mistakes.sort(reverse=True, key=lambda x: x[0])
            
            # 生成每日复习计划
            daily_plan = []
            subject_count = {}
            knowledge_point_count = {}
            
            for score, mistake in prioritized_mistakes:
                # 检查是否达到每日上限
                if len(daily_plan) >= daily_limit:
                    break
                
                # 检查学科均衡性
                subject_name = mistake.subject.name
                if subject_count.get(subject_name, 0) >= daily_limit // 3:
                    continue
                
                # 检查知识点均衡性
                knowledge_points = mistake.knowledge_points.all()
                kp_skip = False
                for kp in knowledge_points:
                    if knowledge_point_count.get(kp.name, 0) >= 3:
                        kp_skip = True
                        break
                if kp_skip:
                    continue
                
                # 添加到复习计划
                daily_plan.append(mistake)
                
                # 更新计数
                subject_count[subject_name] = subject_count.get(subject_name, 0) + 1
                for kp in knowledge_points:
                    knowledge_point_count[kp.name] = knowledge_point_count.get(kp.name, 0) + 1
            
            # 如果计划不足，补充一些题目
            if len(daily_plan) < daily_limit:
                for score, mistake in prioritized_mistakes:
                    if len(daily_plan) >= daily_limit:
                        break
                    if mistake not in daily_plan:
                        daily_plan.append(mistake)
            
            context = {
                'daily_plan': daily_plan,
                'daily_limit': daily_limit,
                'total_available': len(reviewable_mistakes),
                'default_daily_limit': daily_limit
            }
            return render(request, 'mistakes/review_plan.html', context)
        
        # GET请求时，也生成复习计划
        try:
            daily_limit = request.user.daily_review_limit
        except Exception as e:
            print(f"获取用户设置时出错: {e}")
            daily_limit = 10
        
        # 收集所有待复习的题目（包括所有题目，无论复习时间）
        now = timezone.now()
        # 获取所有题目，按复习时间排序，并预加载图片
        all_mistakes = Mistake.objects.filter(
            user=request.user
        ).prefetch_related('images').order_by('next_review_at')  # 优先选择即将到期的
        
        # 最多获取每日限制的2倍，确保有足够的题目
        reviewable_mistakes = list(all_mistakes[:daily_limit * 2])
        
        # 计算每道题的优先级分数
        prioritized_mistakes = []
        for mistake in reviewable_mistakes:
            # 基础分数计算
            priority_score = 0
            
            # 1. 基于复习时间的优先级
            days_overdue = (now - mistake.next_review_at).days
            if days_overdue > 0:
                priority_score += days_overdue * 10
            else:
                # 对于未到复习时间的题目，根据距离复习时间的远近计算分数
                days_until_review = (mistake.next_review_at - now).days
                priority_score += max(0, 20 - days_until_review * 2)  # 距离越近分数越高
            
            # 2. 基于掌握程度的优先级
            if mistake.mastery_level == 'to_review':
                priority_score += 50
            
            # 3. 基于难度的优先级
            priority_score += mistake.difficulty * 10
            
            # 4. 基于复习次数的优先级（复习次数少的优先级高）
            priority_score += (10 - min(mistake.review_count, 10)) * 5
            
            prioritized_mistakes.append((priority_score, mistake))
        
        # 按优先级分数排序
        prioritized_mistakes.sort(reverse=True, key=lambda x: x[0])
        
        # 生成每日复习计划
        daily_plan = []
        subject_count = {}
        knowledge_point_count = {}
        
        for score, mistake in prioritized_mistakes:
            # 检查是否达到每日上限
            if len(daily_plan) >= daily_limit:
                break
            
            # 检查学科均衡性
            subject_name = mistake.subject.name
            if subject_count.get(subject_name, 0) >= daily_limit // 3:
                continue
            
            # 检查知识点均衡性
            knowledge_points = mistake.knowledge_points.all()
            kp_skip = False
            for kp in knowledge_points:
                if knowledge_point_count.get(kp.name, 0) >= 3:
                    kp_skip = True
                    break
            if kp_skip:
                continue
            
            # 添加到复习计划
            daily_plan.append(mistake)
            
            # 更新计数
            subject_count[subject_name] = subject_count.get(subject_name, 0) + 1
            for kp in knowledge_points:
                knowledge_point_count[kp.name] = knowledge_point_count.get(kp.name, 0) + 1
        
        # 如果计划不足，补充一些题目
        if len(daily_plan) < daily_limit:
            for score, mistake in prioritized_mistakes:
                if len(daily_plan) >= daily_limit:
                    break
                if mistake not in daily_plan:
                    daily_plan.append(mistake)
        
        context = {
            'daily_plan': daily_plan,
            'daily_limit': daily_limit,
            'total_available': len(reviewable_mistakes),
            'default_daily_limit': daily_limit
        }
        return render(request, 'mistakes/review_plan.html', context)
    except Exception as e:
        print(f"处理复习计划请求时出错: {e}")
        # 出错时返回默认值
        context = {
            'default_daily_limit': 10
        }
        return render(request, 'mistakes/review_plan.html', context)


@login_required
def review_records_view(request):
    # 获取当前用户的所有复习记录，按复习时间倒序排列
    review_records = ReviewRecord.objects.filter(
        mistake__user=request.user
    ).prefetch_related('mistake', 'images').order_by('-reviewed_at')
    
    context = {
        'review_records': review_records
    }
    return render(request, 'mistakes/review_records.html', context)


@login_required
def points_center_view(request):
    # 获取用户的积分记录，按创建时间倒序排列
    points_records = PointsRecord.objects.filter(
        user=request.user
    ).prefetch_related('mistake').order_by('-created_at')
    
    # 计算积分统计
    total_points = request.user.points
    
    # 按原因统计积分
    points_by_reason = {}
    for record in points_records:
        reason = record.get_reason_display()
        if reason not in points_by_reason:
            points_by_reason[reason] = 0
        points_by_reason[reason] += record.points
    
    context = {
        'total_points': total_points,
        'points_records': points_records,
        'points_by_reason': points_by_reason
    }
    return render(request, 'mistakes/points_center.html', context)
