#classe para desabilitar cache e evitar problemas com dados armazenados pelo navegador
from django.utils.deprecation import MiddlewareMixin
from user_agents import parse

class DeviceDetectionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        user_agent_parsed = parse(user_agent)
        
        # Define se é mobile ou desktop
        if user_agent_parsed.is_mobile:
            request.is_mobile = True
        else:
            request.is_mobile = False

class NoCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):
        response = self.get_response(request)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response