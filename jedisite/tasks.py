from __future__ import absolute_import

from jediguild.celery import app
from django.conf import settings
from jedisite.models import Benchmarks, GameAccount, WarStats
from utils.tyrant_utils import CardReader

# @perodic_task(run_every=(crontab(minute='*/15')), name="task_update_card_xmls", ignore_result=True)
# def get_card_xmls:
#
#     import urllib2
#
#     for i in range(1, 10 + 1):
#         card_xml_file = urllib2.urlopen(
#             "http://mobile-dev.tyrantonline.com/assets/cards_section_{card_id}.xml".format(
#                 card_id=i))
#         with open("cards_section_{card_id}.xml".format(card_id=i), "wb") as file_name:
#             file_name.write(card_xml_file.read())


@app.task
def benchmark_offense_sim(deck, deck_id):

    import os
    import subprocess

    tuo_path = os.path.join(settings.BASE_DIR, "utils", "tuo")
    tuo_command = os.path.join(tuo_path, "tuo.exe")
    friendly_offense_structures = "Sky Fortress, Sky Fortress"
    enemy_defense_structures = "Foreboding Archway, Foreboding Archway"
    gauntlet = "Benchmark"
    gbge = "Counterflux"

    try:
        result = subprocess.check_output(
            [
                "{tuo_command}".format(tuo_command=tuo_command),
                "{seed}".format(seed=deck),
                "{GauntletOffense}".format(GauntletOffense=gauntlet),
                "gw",
                "ordered",
                "yf",
                "{friendly_offense_structures}".format(friendly_offense_structures=friendly_offense_structures),
                "ef",
                "{enemy_defense_structures}".format(enemy_defense_structures=enemy_defense_structures),
                "_benchmark",
                "-e",
                "{gbge}".format(gbge=gbge),
                "-t",
                "{Threads}".format(Threads=1),
                "sim",
                "{Iteration}".format(Iteration=1000),
            ],
            cwd=tuo_path
        ).splitlines()
        score = result[-3].split(': ')[1].split('(')[0]
        # print score
        Benchmarks.objects.update_or_create(deck_id=deck_id, defaults={'deck_id': deck_id, 'score': score})

    except subprocess.CalledProcessError as err:
        print err


@app.task
def benchmark_defense_sim(deck, deck_id):

    import os
    import subprocess

    tuo_path = os.path.join(settings.BASE_DIR, "utils", "tuo")
    tuo_command = os.path.join(tuo_path, 'tuo.exe')
    friendly_defense_structures = "Foreboding Archway, Foreboding Archway"
    enemy_offense_structures = "Sky Fortress, Sky Fortress"
    gauntlet = "Benchmark"
    gbge = "Counterflux"

    try:
        result = subprocess.check_output(
            [
                "{tuo_command}".format(tuo_command=tuo_command),
                "{seed}".format(seed=deck),
                "{gauntlet_defense}".format(gauntlet_defense=gauntlet),
                "gw-defense",
                "enemy:ordered",
                "yf",
                "{friendly_defense_structures}".format(friendly_defense_structures=friendly_defense_structures),
                "ef",
                "{enemy_offense_structures}".format(enemy_offense_structures=enemy_offense_structures),
                "-e",
                "{gbge}".format(gbge=gbge),
                "-t",
                "{threads}".format(threads=1),
                "_benchmark",
                "sim",
                "{iterations}".format(iterations=1000),
            ],
            cwd=tuo_path,
        ).splitlines()
        # print result
        score = result[-3].split(': ')[1].split(' (')[0]
        # print score
        Benchmarks.objects.update_or_create(deck_id=deck_id, defaults={'deck_id': deck_id, 'score': score})
    except subprocess.CalledProcessError as err:
        print err


@app.task
def update_xmls():

    import os
    import urllib
    xml_path = os.path.join(settings.BASE_DIR, "utils", "tuo", "data")
    xml_files = [
        "missions",
        "tutorial",
        "items",
        "fusion_recipes_cj2",
        "codex",
        "levels",
        "skills_set",
    ]

    for i in range(1, 12 + 1):
        xml_files.append(
            "cards_section_{section_id}".format(
                section_id=i
            )
        )

    for xml_file in xml_files:
        try:
            urllib.urlretrieve(
                'http://mobile.tyrantonline.com/assets/{xml_file}.xml'.format(xml_file=xml_file),
                filename=os.path.join(xml_path, '{xml_file}.xml'.format(xml_file=xml_file)))
        except IOError:
            pass

    try:
        urllib.urlretrieve(
            'https://github.com/dsuchka/tyrant_optimize/blob/merged/data/raids.xml',
            filename=os.path.join(xml_path, 'raids.xml')
        )
    except IOError:
        pass

    try:
        urllib.urlretrieve(
            'https://github.com/dsuchka/tyrant_optimize/blob/merged/data/bges.txt',
            filename=os.path.join(xml_path, 'bges.txt')
        )
    except IOError:
        pass

    card_reader = CardReader()
    card_reader.create_all_cards_file()


@app.task
def check_war_status():

    # from datetime import datetime, timedelta
    from datetime import datetime
    from utils.tyrant_utils import TyrantAPI

    account = GameAccount.objects.get(name="connor2k")

    tyrant_api = TyrantAPI()
    response_data = tyrant_api.create_request('updateFactionWar', account.postdata)

    try:
        end_time = datetime.fromtimestamp(int(response_data['faction_war']['end_time']) - 5)
        # end_time = datetime.utcnow() + timedelta(seconds=60)
        # print end_time
        import_war_data.apply_async((), eta=end_time)

    except KeyError:

        pass


@app.task
def import_war_data():

    from utils.tyrant_utils import TyrantAPI

    account = GameAccount.objects.get(name="connor2k")

    tyrant_api = TyrantAPI()
    response_data = tyrant_api.create_request('updateFactionWar', account.postdata)

    if str(response_data['faction_war']['attacker_faction_id']) == "1778002":
        friendly_guild = "attacker"
        enemy_guild = "defender"
    else:
        friendly_guild = "defender"
        enemy_guild = "attacker"

    war_data = list()

    for member in response_data['faction_war']['{status}_faction_members'.format(status=friendly_guild)]:
        war_data.append(
            {
                "member_name": member['member_name'].encode('utf-8'),
                "wins": int(member['wins']),
                "losses": int(member['losses']),
                "defend_wins": int(member['defend_wins']),
                "defend_losses": int(member['defend_losses'])
            }
        )

    WarStats.objects.create(
        name=response_data['active_war_event']['name'],
        friendly_guild=response_data['faction_war']['{status}_faction_name'.format(status=friendly_guild)],
        enemy_guild=response_data['faction_war']['{status}_faction_name'.format(status=enemy_guild)],
        data=war_data
    )
