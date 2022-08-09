from oauth2_provider.decorators import protected_resource
from hackman_payments import api as payment_api
from oauth2_provider.models import AccessToken
from django.http.response import HttpResponse
import json


@protected_resource()
def profile(request):
    user = AccessToken.objects.get(token=request.GET.get("access_token")).user
    return HttpResponse(
        json.dumps(
            {
                # Lets pretend like we are the email provider, dont want to leak info
                "email": "@".join((user.username.split("@")[0], "dimsumlabs.com"))
            }
        ),
        content_type="application/json",
    )


def tags_not_matching(request):
    return HttpResponse(
        json.dumps(payment_api.tags_not_matching()), content_type="application/json"
    )
