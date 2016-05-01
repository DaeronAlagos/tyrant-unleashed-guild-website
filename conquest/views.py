from django.shortcuts import render
from jedisite.views import is_officer
from jedisite.models import GameAccount
from django.contrib.auth.decorators import login_required, user_passes_test
from utils.tyrant_utils import ConquestUpdate
import random


@login_required
@user_passes_test(is_officer)
def conquest_overview(request):

    from collections import OrderedDict

    random_index = random.randint(0, GameAccount.objects.filter(guild='MasterJedis').count() - 1)
    account = GameAccount.objects.filter(guild='MasterJedis').exclude(postdata=None)[random_index]

    zone_tiers = ["Asphodel Nexus", "Phobos Station",
                      "The Spire", "Magma Foundry", "Baron's Claw Labs", "Andar Quarantine", "Red Maw Base",
                      "Norhaven", "Infested Depot", "Cleave Rock", "Enclave Landing", "Elder Port"]

    zone_data = {}

    conquest_update = ConquestUpdate()
    conquest_data = conquest_update.getConquestUpdate_data(account.postdata)

    try:
        for zone in conquest_data['conquest_data']['zone_data']:
            zone_data.update({conquest_data['conquest_data']['zone_data'][zone]['name']: []})

            for rank in conquest_data['conquest_data']['zone_data'][zone]['rankings']['rankings']['data']:
                try:
                    zone_data.setdefault(conquest_data['conquest_data']['zone_data'][zone]['name']).append(
                        {'rank': rank['rank'], 'name': rank['name'], 'influence': int(rank['influence'])}
                    )
                except KeyError, e:
                    try:
                        zone_data.setdefault(conquest_data['conquest_data']['zone_data'][zone]['name']).append(
                            {'rank': rank['rank'], 'name': rank['name'], 'influence': int(rank['last_influence'])}
                        )
                    except KeyError:
                        pass

        ordered_zone_data = OrderedDict((key, zone_data.get(key)) for key in zone_tiers)

        enemy_guilds = ['Bairzerkers', 'SlowlyDownward']

        return render(request, "conquest_overview.html", {'zone_data': ordered_zone_data,
                                                          'enemy_guilds': enemy_guilds})

    except TypeError:
        return render(request, "conquest_overview.html")


@login_required
@user_passes_test(is_officer)
def command(request):

    conquest_update = ConquestUpdate()
    accounts = GameAccount.objects.filter(guild='MasterJedis').exclude(postdata=None)
    print "Accounts:", accounts

    account_data = []

    for account in accounts:
        stamina = conquest_update.getConquestUpdate_data(
            account.postdata)['conquest_data']['user_conquest_data']['energy']['battle_energy']
        account_data.append({'name': account.name, 'stamina': stamina})

    return render(request, "command.html", {'account_data': account_data})
