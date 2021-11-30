from ctrlfbe.constants import ERR_NOT_FOUND_MSG_MAP, ERR_PAGE_NOT_FOUND
from rest_framework import status
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response.status_code == status.HTTP_403_FORBIDDEN or response.status_code == status.HTTP_401_UNAUTHORIZED:
        response.data = {"message": "인증이 유효하지 않습니다."}
    if response.status_code == status.HTTP_404_NOT_FOUND:
        model = str(exc.args).split()[1].lower()
        response.data = {
            "message": ERR_NOT_FOUND_MSG_MAP.get(model, ERR_PAGE_NOT_FOUND),
        }
    return response
