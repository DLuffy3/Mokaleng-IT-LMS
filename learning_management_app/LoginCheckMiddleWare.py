from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class LoginCheckMiddleWare(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        user = request.user
        if user.is_authenticated:
            if user.user_type == "1":
                if modulename == "learning_management_app.SystemViews":
                    pass
                elif (modulename == "learning_management_app.views" or modulename == "django.views.static"
                      or modulename == "django.contrib.auth.views"):
                    pass
                else:
                    return HttpResponseRedirect(reverse("admin_home"))
            elif user.user_type == "2":
                if modulename == "learning_management_app.StaffView" or modulename == "learning_management_app.EditViewClass":
                    pass
                elif (modulename == "learning_management_app.views" or modulename == "django.views.static"
                      or modulename == "django.contrib.auth.views"):
                    pass
                else:
                    return HttpResponseRedirect(reverse("staff_home"))
            elif user.user_type == "3":
                if modulename == "learning_management_app.StudentView":
                    pass
                elif (modulename == "learning_management_app.views" or modulename == "django.views.static"
                      or modulename == "django.contrib.auth.views"):
                    pass
                else:
                    return HttpResponseRedirect(reverse("student_home"))
        else:
            if (request.path == reverse("show_login") or request.path == reverse("do_login") or request.path == reverse("show_main_page")
                    or modulename == "django.contrib.auth.views"):
                pass
            else:
                return HttpResponseRedirect(reverse("show_login"))
