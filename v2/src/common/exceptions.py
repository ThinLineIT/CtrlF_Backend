from ctrlfbe.constants import ERR_NOT_FOUND_MSG_MAP, ERR_PAGE_NOT_FOUND
from rest_framework import status
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response.status_code == status.HTTP_403_FORBIDDEN or response.status_code == status.HTTP_401_UNAUTHORIZED:
        response.data = {"message": "인증이 유효하지 않습니다."}
    elif response.status_code == status.HTTP_404_NOT_FOUND or "Invalid pk" in str(exc.args):
        model = get_not_found_model(exc, response.status_code)
        response.status_code = status.HTTP_404_NOT_FOUND
        response.data = {
            "message": ERR_NOT_FOUND_MSG_MAP.get(model, ERR_PAGE_NOT_FOUND),
        }
    elif response.status_code == status.HTTP_400_BAD_REQUEST:
        response.data = {"message": "요청이 올바르지 않습니다."}
    return response


def get_not_found_model(exc, status_code):
    if status_code == status.HTTP_404_NOT_FOUND:
        model = str(exc.args).split()[1].lower()
    else:
        model = list(exc.args[0].keys())[0]
    return model
