from django.utils.deprecation import MiddlewareMixin
# from django.conf import settings


class SameSiteMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # origin = request.headers.get('Origin')
        # if origin in settings.CORS_ORIGIN_WHITELIST:
        if "sessionid" in response.cookies:
            response.cookies["sessionid"]["samesite"] = "None"
        if "csrftoken" in response.cookies:
            response.cookies["csrftoken"]["samesite"] = "None"
        return response
