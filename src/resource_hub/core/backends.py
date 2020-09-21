from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class CustomAuthBackend(ModelBackend):
    '''
    customize https://github.com/django/django/blob/master/django/contrib/auth/backends.py to allow for registering with email or username
    '''

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return
        try:
            # validation has to ensure this query doesn't return two results
            query = Q(username=username)
            query.add(Q(email=username), Q.OR)

            user = UserModel.objects.get(query)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
