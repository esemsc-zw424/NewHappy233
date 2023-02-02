

from django.conf import settings
from django.shortcuts import redirect


def login_prohibited(view_function):
    def modified_view_function(request):
        user = request.user
        if user.is_authenticated:
            groups = [group.name for group in user.groups.all()]
            if 'director' in groups or 'admin' in groups:
                return redirect(settings.ADMIN_DIRECTOR_REDIRECT_URL_WHEN_LOGGED_IN)
            else:
                return redirect(settings.STUDENT_REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)

    return modified_view_function


