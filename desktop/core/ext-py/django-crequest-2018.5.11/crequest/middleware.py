import threading
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object


class CrequestMiddleware(MiddlewareMixin):
    """
    Provides storage for the "current" request object, so that code anywhere
    in your project can access it, without it having to be passed to that code
    from the view.
    """
    _requests = {}

    def process_request(self, request):
        """
        Store the current request.
        """
        self.__class__.set_request(request)

    def process_response(self, request, response):
        """
        Delete the current request to avoid leaking memory.
        """
        self.__class__.del_request()
        return response

    @classmethod
    def get_request(cls, default=None):
        """
        Retrieve the request object for the current thread, or the optionally
        provided default if there is no current request.
        """
        return cls._requests.get(threading.current_thread(), default)

    @classmethod
    def set_request(cls, request):
        """
        Save the given request into storage for the current thread.
        """
        cls._requests[threading.current_thread()] = request

    @classmethod
    def del_request(cls):
        """
        Delete the request that was stored for the current thread.
        """
        cls._requests.pop(threading.current_thread(), None)
