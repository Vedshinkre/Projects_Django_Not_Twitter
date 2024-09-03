from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from django.shortcuts import render
from socialnetwork.api import experts as get_experts, bullshitters as get_bullshitters


from fame.serializers import FameSerializer
from socialnetwork import api
from socialnetwork.api import _get_social_network_user, experts, bullshitters
from socialnetwork.models import SocialNetworkUsers



@require_http_methods(["GET"])
@login_required
def fame_list(request):
    # try to get the user from the request parameters:
    userid = request.GET.get("userid", None)
    user = None
    if userid is None:
        user = _get_social_network_user(request.user)
    else:
        try:
            user = SocialNetworkUsers.objects.get(id=userid)
        except ValueError:
            pass

    user, fame = api.fame(user)
    context = {
        "fame": FameSerializer(fame, many=True).data,
        "user": user if user else "",
    }
    return render(request, "fame.html", context=context)

@require_http_methods(["GET"])
@login_required
def experts_view(request):
    experts_data = get_experts()
    print(type(experts_data))  # Debugging line
    return render(request, 'experts.html', { "experts_data": experts_data})

def bullshitters_view(request):
    bullshitters_data = get_bullshitters()
  #  print(bullshitters_data)
    return render(request, 'bullshitters.html', {'bullshitters': bullshitters_data})