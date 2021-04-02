from django.shortcuts import redirect
from django.http import HttpResponseForbidden


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('store')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func


def staff_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("!!!Access Denied, You are not authorize to view this resource!!!")
    return wrapper_func
