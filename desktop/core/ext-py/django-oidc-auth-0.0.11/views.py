from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    user = request.user
    oidc_account = user.oidc_account
    message = 'Succesfully logged! Email: %s; sub: %s' % (user, oidc_account.sub)

    return HttpResponse(message)
