from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from .models import Profile

class TokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        user_profile = Profile.objects.get(user=user)
        return (six.text_type(user.id)+six.text_type(timestamp)+six.text_type(user_profile.email_is_verified))


generate_token = TokenGenerator()
