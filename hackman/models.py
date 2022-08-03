# Set unique emails for users, a bit hacky but works well enough
from django.contrib.auth.models import User


User._meta.get_field("email")._unique = True
