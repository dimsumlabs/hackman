def get_remote_ip(request):
    remote_ip = request.META.get('HTTP_X_FORWARDED_FOR',
                                 request.META.get('REMOTE_ADDR'))
    return remote_ip.split(',')[0]
