import json
import requests
from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Conversation, Message
from mistakes.models import Mistake, MistakeImage
from config import API_KEY


def index(request):
    return render(request, 'chat/index.html')


@csrf_exempt
@require_http_methods(["GET"])
def get_conversations(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': '用户未登录'}, status=401)
    conversations = Conversation.objects.filter(user=request.user)
    data = [
        {
            'id': conv.id,
            'title': conv.title,
            'created_at': conv.created_at.isoformat(),
            'updated_at': conv.updated_at.isoformat()
        }
        for conv in conversations
    ]
    return JsonResponse({'conversations': data})


@csrf_exempt
@require_http_methods(["POST"])
def create_conversation(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': '用户未登录'}, status=401)
    conversation = Conversation.objects.create(title='新对话', user=request.user)
    return JsonResponse({
        'id': conversation.id,
        'title': conversation.title,
        'created_at': conversation.created_at.isoformat(),
        'updated_at': conversation.updated_at.isoformat()
    })


@csrf_exempt
@require_http_methods(["GET"])
def get_conversation_messages(request, conversation_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': '用户未登录'}, status=401)
    try:
        conversation = Conversation.objects.get(id=conversation_id, user=request.user)
        messages = conversation.messages.all()
        data = [
            {
                'role': msg.role,
                'content': msg.content
            }
            for msg in messages
        ]
        return JsonResponse({'messages': data})
    except Conversation.DoesNotExist:
        return JsonResponse({'error': '对话不存在'}, status=404)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_conversation(request, conversation_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': '用户未登录'}, status=401)
    try:
        conversation = Conversation.objects.get(id=conversation_id, user=request.user)
        conversation.delete()
        return JsonResponse({'success': True})
    except Conversation.DoesNotExist:
        return JsonResponse({'error': '对话不存在'}, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def chat_stream(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': '用户未登录'}, status=401)
    try:
        data = json.loads(request.body.decode('utf-8'))
        user_message = data.get('message', '')
        conversation_id = data.get('conversation_id')

        if not conversation_id:
            return JsonResponse({'error': '请选择或创建对话'}, status=400)

        try:
            conversation = Conversation.objects.get(id=conversation_id, user=request.user)
        except Conversation.DoesNotExist:
            return JsonResponse({'error': '对话不存在'}, status=404)

        message_history = list(conversation.messages.values('role', 'content'))

        url = "https://spark-api-open.xf-yun.com/v1/chat/completions"
        payload = {
            "max_tokens": 4096,
            "top_k": 4,
            "temperature": 0.5,
            "messages": message_history + [
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "model": "lite",
            "stream": True
        }
        headers = {
            "Authorization": f"Bearer {API_KEY}"
        }

        user_msg = Message.objects.create(
            conversation=conversation,
            role='user',
            content=user_message
        )

        if conversation.title == '新对话' and len(user_message) > 0:
            conversation.title = user_message[:30] if len(user_message) > 30 else user_message
            conversation.save()

        assistant_content = ''

        def generate():
            nonlocal assistant_content
            response = requests.post(url, headers=headers, json=payload, stream=True)
            response.encoding = "utf-8"
            
            for line in response.iter_lines(decode_unicode="utf-8"):
                if line:
                    if line.startswith('data: '):
                        data_line = line[6:]
                        if data_line != '[DONE]':
                            try:
                                json_data = json.loads(data_line)
                                if json_data.get('choices'):
                                    delta = json_data['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        assistant_content += delta['content']
                            except:
                                pass
                        yield line + '\n'
                    else:
                        yield f'data: {line}\n'
            
            if assistant_content:
                Message.objects.create(
                    conversation=conversation,
                    role='assistant',
                    content=assistant_content
                )

        return StreamingHttpResponse(generate(), content_type='text/event-stream')

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_recent_mistakes(request):
    try:
        mistakes = Mistake.objects.select_related('subject').prefetch_related('images').order_by('-created_at')[:20]
        data = []
        for mistake in mistakes:
            image_url = None
            ocr_content = ''
            if mistake.images.exists():
                first_image = mistake.images.first()
                if first_image:
                    image_url = first_image.image.url
                    ocr_content = first_image.ocr_text
            data.append({
                'id': mistake.id,
                'title': mistake.title,
                'content': ocr_content,
                'subject_name': mistake.subject.name,
                'created_at': mistake.created_at.isoformat(),
                'image_url': image_url
            })
        return JsonResponse({'mistakes': data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def analyze_stream(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        analysis_message = data.get('message', '')

        if not analysis_message:
            return JsonResponse({'error': '消息不能为空'}, status=400)

        url = "https://spark-api-open.xf-yun.com/v1/chat/completions"
        payload = {
            "max_tokens": 4096,
            "top_k": 4,
            "temperature": 0.5,
            "messages": [
                {
                    "role": "user",
                    "content": analysis_message
                }
            ],
            "model": "lite",
            "stream": True
        }
        headers = {
            "Authorization": f"Bearer {API_KEY}"
        }

        def generate():
            response = requests.post(url, headers=headers, json=payload, stream=True)
            response.encoding = "utf-8"
            
            for line in response.iter_lines(decode_unicode="utf-8"):
                if line:
                    if line.startswith('data: '):
                        yield line + '\n'
                    else:
                        yield f'data: {line}\n'

        return StreamingHttpResponse(generate(), content_type='text/event-stream')

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
