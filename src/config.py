"""Configuration loader for the application.

所有配置从同目录下的 config.json 读取（该文件已被 .gitignore 忽略，不会提交到仓库）。
首次部署请复制 config.example.json 为 config.json 并填写真实密钥。
"""
import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent / 'config.json'


def _load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"配置文件不存在：{CONFIG_PATH}。"
            "请复制 config.example.json 为 config.json 并填写真实的密钥配置。"
        )
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("config.json 格式错误：顶层应为 JSON 对象")
    return data


_config = _load_config()
_server = _config.get('server', {})
_api = _config.get('api', {})
_ocr = _config.get('ocr', {})
_django = _config.get('django', {})

# Server settings
PORT = _server.get('port', 80)
ALLOW_OTHERS = _server.get('allow_others', True)
ALLOWED_HOSTS = _server.get('allowed_hosts', ['*'])

# API settings (讯飞 Spark LLM)
API_KEY = _api.get('spark_api_key', '')

# OCR settings (讯飞公式识别)
OCR_APP_ID = _ocr.get('app_id', '')
OCR_API_KEY = _ocr.get('api_key', '')
OCR_SECRET = _ocr.get('secret', '')

# Django settings
DJANGO_SECRET_KEY = _django.get('secret_key', '')
