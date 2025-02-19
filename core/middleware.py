from django.utils.deprecation import MiddlewareMixin
from user_agents import parse

class BaseTemplateMiddleware(MiddlewareMixin):
    def process_template_response(self, request, response):
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        user_agent_parsed = parse(user_agent)
        is_mobile = user_agent_parsed.is_mobile
        base_template = 'base_mobile.html' if is_mobile else 'base.html'
        if response.context_data is None:
            response.context_data = {}
        response.context_data['base_template'] = base_template
        return response