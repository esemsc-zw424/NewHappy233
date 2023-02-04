

from django.conf import settings
from django.shortcuts import redirect


def login_prohibited(view_function):
    def modified_view_function(request):
        user = request.user
        if user.is_authenticated:
            return redirect(settings.VISITOR_REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)

    return modified_view_function
