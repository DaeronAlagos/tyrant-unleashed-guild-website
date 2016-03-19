from django.shortcuts import render
from jedisite.views import is_officer
from conquest.models import ConquestZones
from django.contrib.auth.decorators import login_required, user_passes_test


@login_required
@user_passes_test(is_officer)
def conquest_overview(request):

    zones = ConquestZones.objects.order_by('-tier', 'name').values()

    return render(request, "conquest_overview.html", {'zones': zones})

