# 测试个人API有哪些模型可用
from core.kimi_api import KimiAPI

api_key = "XXXXXXXXXXX"
kimi = KimiAPI(api_key=api_key)
try:
    models = kimi.get_models()
    print(models)
except Exception as e:
    print(e)