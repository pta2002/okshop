from django.shortcuts import redirect
from django.urls import reverse
from django.http import JsonResponse
from functools import wraps
from django.conf import settings


def auth_required(forid):
    def realone(func):
        @wraps(func)
        def _wrapped_view(request, *args, **kw):
            if request.user.userextra.has_authorization(request, forid) or \
             getattr(settings, 'TESTING', False):
                return func(request, *args, **kw)
            else:
                return redirect(reverse('shop:authorize',
                                        kwargs={'forid': forid})
                                + '?next=' + request.path)
        return _wrapped_view
    return realone


def auth_required_api(forid, goto=None):
    def realone(func):
        @wraps(func)
        def _wrapped_view(request, *args, **kw):
            if request.user.userextra.has_authorization(request, forid) or \
             getattr(settings, 'TESTING', False):
                return func(request, *args, **kw)
            else:
                return JsonResponse({
                    'redirect': reverse('shop:authorize',
                                        kwargs={'forid': forid})
                                    + '?next=' + goto or request.path})
        return _wrapped_view
    return realone
