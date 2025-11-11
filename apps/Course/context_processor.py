# from .utility import get_all_streams, get_all_users,  get_all_live_classes,get_all_videos

from .utility import get_all_academic_levels

def current_path(request):
    print(f"---------------------Request Path:: {request.path}---------------------")
    return {'current_path': request.path}

def get_all_classes_processor(request):
    return get_all_academic_levels()


def messages_processor(request):
    try:
        messages = [m for m in request._messages]  
    except Exception:
        messages = []
    return {'messages': messages or None}


def current_user_details(request):
    user = getattr(request, 'user', None)
    message = user.username if user and user.is_authenticated else 'Guest'
    profile_image_url = None
    try:
        if user and getattr(user, 'profile_picture', None):
            profile_image_url = user.profile_picture.url
    except Exception:
        profile_image_url = None
    return {
        'current_user': user,
        'profile_image_url': profile_image_url,
        'message': message
    }
