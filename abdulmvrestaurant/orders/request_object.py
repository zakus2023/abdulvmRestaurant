# the whole of this was done during v dashboard

from . import models

def RequestObjectMiddleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        # write custom code here

        # the request object is coming from the models.py of this folder
        models.request_object = request

        # then go to settings.py and add this RequestObjectMiddleware to the middleware section


        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware