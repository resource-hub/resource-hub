from django.contrib.auth import user_logged_in
from django.dispatch import receiver
from django.utils import translation
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject

from resource_hub.core.models import Actor


class ActorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # lazy load actor object
        request.actor = SimpleLazyObject(
            lambda: ActorMiddleware.get_actor(request))
        response = self.get_response(request)
        return response

    @staticmethod
    @receiver(user_logged_in)
    def set_initial_actor(sender, request, user, **kwargs):
        actor_id = Actor.objects.get(
            user=user, organization__isnull=True).id
        request.session['actor_id'] = actor_id

    @staticmethod
    def get_actor(request):
        if 'actor_id' in request.session:
            actor_id = request.session['actor_id']
            actor = Actor.objects.get(id=actor_id)
        else:
            actor = None
        return actor


class LocaleMiddleware(MiddlewareMixin):
    """
    This is a very simple middleware that parses a request
    and decides what translation object to install in the current
    thread context. This allows pages to be dynamically
    translated to the language the user desires (if the language
    is available, of course).
    """

    def process_request(self, request):
        language = translation.get_language_from_request(request)
        print(language)
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        translation.deactivate()
        return response
