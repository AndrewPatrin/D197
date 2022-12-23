from django.shortcuts import redirect
from .models import Post


def user_permission_to_edit(function=None, redirect_url='/posts/'):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            path = request.path.strip().split('/')[-2]
            post = Post.objects.get(slug=path)
            if request.user != post.user or request.user.is_superuser:
                return redirect(redirect_url)
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    if function:
        return decorator(function)

    return


def user_not_authenticated(function=None, redirect_url='/posts/'):

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                return redirect(redirect_url)

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    if function:
        return decorator(function)

    return



