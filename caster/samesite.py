from django.utils.deprecation import MiddlewareMixin


class SameSiteMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        origin = request.headers.get('Origin', 'localhost')
        if 'localhost' not in origin:
            if "sessionid" in response.cookies:
                response.cookies["sessionid"]["samesite"] = "None"
                response.cookies["sessionid"]["secure"] = True
            if "csrftoken" in response.cookies:
                response.cookies["csrftoken"]["samesite"] = "None"
                response.cookies["csrftoken"]["secure"] = True

        return response
