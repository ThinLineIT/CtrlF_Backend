from ctrlf_auth.authentication import CtrlfAuthentication


class CtrlfAuthenticationMixin:
    def __init__(self):
        self.auth = CtrlfAuthentication()

    def _ctrlf_authentication(self, request):
        self.authentication_classes = [CtrlfAuthentication]
        user, _ = self.auth.authenticate(request)
        return user
