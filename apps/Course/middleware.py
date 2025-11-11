import logging

logger = logging.getLogger(__name__)

class UserRequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Log user info after response
        if hasattr(request, 'user') and request.user.is_authenticated:
            logger.info(
                f'User: {request.user.username} | '
                f'{request.method} {request.path} | '
                f'Status: {response.status_code}'
            )
        
        return response