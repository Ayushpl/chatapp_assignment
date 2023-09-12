from base.utils import is_token_valid


class UpdateOnlineStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated:
            user.is_online = True
            user.save()
        response = self.get_response(request)
        if user.is_authenticated and not is_token_valid(user):
            user.is_online = False
            user.save()

        return response