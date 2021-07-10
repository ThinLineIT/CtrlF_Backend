from ninja import NinjaAPI, Router

from config.schema import SignUpRequestIn, ErrorSingUp400Response, SignUpRequestOut

api = NinjaAPI()
api_auth = Router()
api.add_router("/auth/", api_auth)


@api_auth.post("/signup", response={200: SignUpRequestOut, 400: ErrorSingUp400Response})
def api_signup(request, request_body: SignUpRequestIn):
    return request_body
