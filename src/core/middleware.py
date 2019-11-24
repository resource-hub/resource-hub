from django.utils.functional import SimpleLazyObject
from django.contrib.auth import user_logged_in
from django.dispatch import receiver

from core.models import Actor


class ActorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # lazy load actor object
        request.actor = SimpleLazyObject(
            lambda: ActorMiddleware.get_actor(request))
        response = self.get_response(request)
        return response

    @receiver(user_logged_in)
    def set_initial_actor(sender, request, user, **kwargs):
        actor_id = actor = Actor.objects.get(
            user=user, organization__isnull=True).id
        request.session['actor_id'] = actor_id

    def get_actor(request):
        if 'actor_id' in request.session:
            actor_id = request.session['actor_id']
            actor = Actor.objects.get(id=actor_id)
        else:
            actor = None
        return actor
