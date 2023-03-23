
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.shortcuts import redirect

from pst.models import SpendingFile



class SpendingFileMixin:
    def handle_files(self,spending,form, request):
        file_list = request.FILES.getlist('file')
        if file_list:
            SpendingFile.objects.filter(spending=spending[0]).delete()
            for file in file_list:
                SpendingFile.objects.create(
                    spending=spending[0],
                    file=file
                )
        if form.cleaned_data['delete_file']:
          
            SpendingFile.objects.filter(spending=spending[0]).delete()
        



class LoginProhibitedMixin:
    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        """Returns the url to redirect to when not logged in."""
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        else:
            return self.redirect_when_logged_in_url
        


