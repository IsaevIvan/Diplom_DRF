from rest_framework.throttling import SimpleRateThrottle


class RegisterThrottle(SimpleRateThrottle):
    """Throttle для регистрации - защита от ботов"""
    scope = 'register'

    def get_cache_key(self, request, view):
        if request.method == 'POST' and 'register' in request.path:
            ident = self.get_ident(request)
            return self.cache_format % {
                'scope': self.scope,
                'ident': ident
            }
        return None


class LoginThrottle(SimpleRateThrottle):
    """Throttle для входа - защита от брут форса"""
    scope = 'login'

    def get_cache_key(self, request, view):
        if request.method == 'POST' and 'login' in request.path:
            email = request.data.get('email', '')
            return self.cache_format % {
                'scope': self.scope,
                'ident': email
            }
        return None