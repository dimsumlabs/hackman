from django.http import HttpRequest


def get_remote_ip(request: HttpRequest) -> str:
    remote_ip = request.META.get(
        "HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR")
    )
    if not remote_ip:
        raise ValueError("Missing remote IP")

    return remote_ip.split(",")[0]  # type: ignore
