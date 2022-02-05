from ctrlf_auth.serializers import LoginSerializer


def _login(user_data):
    return LoginSerializer().validate(user_data)["token"]


def _get_header(token):
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"} if token else {}
