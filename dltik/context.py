
def current_url(request):
    return {
        'curr_url': request.build_absolute_uri()
    }
