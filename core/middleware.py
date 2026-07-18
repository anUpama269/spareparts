from contextvars import ContextVar


_current_user = ContextVar('audit_current_user', default=None)
_request_context = ContextVar('audit_request_context', default={})


def get_current_user():
    return _current_user.get()


def get_request_context():
    return _request_context.get()


class AuditUserMiddleware:
    """Expose the authenticated request user to model audit signals."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else None
        user_token = _current_user.set(user)
        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
        ip_address = forwarded_for.split(',')[0].strip() if forwarded_for else request.META.get('REMOTE_ADDR')
        context_token = _request_context.set({
            'method': request.method,
            'path': request.path,
            'ip_address': ip_address,
        })
        try:
            return self.get_response(request)
        finally:
            _request_context.reset(context_token)
            _current_user.reset(user_token)
