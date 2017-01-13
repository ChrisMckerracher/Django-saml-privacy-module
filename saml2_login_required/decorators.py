

def saml2_login_required(cls):
    """
    Functions similarly to django's login required.
    Works specifically for django rest framework apps
    Decorator to require okta sso login for specific views
    """
    from .django_saml2_auth_lite import signin
    from django.http import HttpRequest
    import types
    def wrapper(*args, **kwargs):
        for i in args:
            if isinstance(i, HttpRequest):
                if not(i.user.is_authenticated):
                    return signin(i)
        return cls(*args, **kwargs)

    if isinstance(cls, types.FunctionType) or isinstance(cls, types.MethodType):
        return wrapper

    class Wrapped(cls):
        def __getattribute__(self,attribute, **kwargs):
            actual_attribute = super().__getattribute__(attribute, **kwargs)
            
            if isinstance(actual_attribute, types.FunctionType) or isinstance(actual_attribute, types.MethodType):
                return okta_login_required(actual_attribute)
            return actual_attribute
    return Wrapped