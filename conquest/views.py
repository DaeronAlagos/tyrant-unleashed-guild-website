from django.shortcuts import render
from jedisite.views import is_officer
from jedisite.models import GameAccount, Decks
from django.contrib.auth.decorators import login_required, user_passes_test
from utils.tyrant_utils import TyrantAPI
import random


@login_required
@user_passes_test(is_officer)
def conquest_overview(request):

    from collections import OrderedDict
    import threading

    # account = GameAccount.objects.get(name="pajammyjam")
    account = GameAccount.objects.get(name="ThibautW2")

    zone_tiers = [
        ("Asphodel Nexus", 12),
        ("Phobos Station", 11),
        # Tier 2
        # ("Ashrock Redoubt", 21),
        # "The Spire",
        ("SkyCom Complex", 7),
        # ("Jotun's Pantheon", 3),
        # "Magma Foundry",
        # ("Baron's Claw Labs", 20),
        ("Andar Quarantine", 18),
        ("Borean Forges", 16),
        ("Red Maw Base", 8),
        ("Brood Nest", 6),
        # Tier 1
        ("Colonial Relay", 22),
        # "Norhaven",
        ("Infested Depot", 5),
        # ("Malort's Den", 15),
        # "Cleave Rock",
        # ("Enclave Landing", 17),
        ("Mech Graveyard", 9),
        # ("Elder Port", 19),
        ("Seismic Beacon", 10),
        ("Tyrolian Outpost", 4),
    ]

    zone_data = {}

    tyrant_api = TyrantAPI()
    try:

        def zone_request(thread_zone, thread_zone_id):

            conquest_data = tyrant_api.create_conquest_zone_request(
                "getConquestZoneRankings",
                thread_zone_id,
                account.postdata
            )

            for rank in conquest_data['conquest_zone_data']['rankings']['data']:

                try:

                    try:

                        zone_data.setdefault(thread_zone, []).append(
                            {'rank': rank['rank'], 'name': rank['name'], 'influence': int(rank['influence'])}
                        )

                    except KeyError:

                        zone_data.setdefault(thread_zone, []).append(
                            {'rank': rank['rank'], 'name': rank['name'], 'influence': int(rank['last_influence'])}
                        )

                except KeyError:

                    pass

        for zone, zone_id in zone_tiers:

            zone_thread = threading.Thread(target=zone_request(zone, zone_id))
            zone_thread.start()

        ordered_zone_data = OrderedDict((key, zone_data.get(key)) for key, key_id in zone_tiers)
        enemy_guilds = ['grizzlybairs', 'SlowlyDownward']

        return render(request, "conquest_overview.html", {'zone_data': ordered_zone_data,
                                                          'enemy_guilds': enemy_guilds})

    except TypeError:
        return render(request, "conquest_overview.html")


@login_required
@user_passes_test(is_officer)
def command(request, zone):

    zones = {
        "AsphodelNexus": "",
        "PhobosStation": "Orbital Bombardment",
        # Tier 2
        "SkyComComplex": "Network Interference",
        "BaronsClawLabs": "Experimental Toxins",
        "MagmaFoundry": "Volcanic Rain",
        "AndarQuarantine": "Andar Isolation",
        "TheSpire": "Imperial Domain",
        "AshrockRedoubt": "Counterflux",
        # Tier 1
        "MalortsDen": "Lethal Spores",
        "CleaveRock": "Splinter Legacy",
        "InfestedDepot": "Infested Supplies",
        "EnclaveLanding": "Bolstered Beachfront",
        "ElderPort": "Ballistic Barrage",
        "ColonialRelay": "Planetwide Comms",
    }

    conquest_update = ConquestUpdate()
    accounts = GameAccount.objects.filter(guild='Quasar').exclude(postdata=None)
    decks = Decks.objects.filter(guild='Quasar')
    print "Accounts:", accounts
    print "Zone BGE:", zones[zone]

    account_data = []

    for account in accounts:

        try:
            stamina = conquest_update.getConquestUpdate_data(
                account.postdata)['conquest_data']['user_conquest_data']['energy']['battle_energy']
            print("Stamina:", stamina)
            print("Name:", account.name)
            for deck in decks:
                if deck.name == account.name and deck.bge['global']['name'] == zones[zone] and deck.mode == "Offense":
                    zone_deck = deck
                    account_data.append({'name': account.name, 'stamina': stamina, 'zone_deck': zone_deck})

        except KeyError, e:
            print e

    print(account_data)

    return render(request, "command.html", {'zone': zone, 'account_data': account_data})

        # return render(request, "command.html", {})
