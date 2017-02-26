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

    tuo_path = os.path.join(settings.BASE_DIR, 'utils/tuo/')
    tuo_command = os.path.join(tuo_path, 'tuo.exe')
    friendly_offense_structures = "Sky Fortress, Sky Fortress"
    enemy_defense_structures = "Illuminary Blockade"
    gauntlet = "Benchmark"

    result = subprocess.check_output(tuo_command +
                                     ' "{Seed}" "{GauntletOffense}" gw ordered yf "{friendly_offense_strucutures}"'
                                     ' ef "{enemy_defense_structures}" _benchmark -t {Threads} sim {Iteration}'.format(
                                         Seed=deck,
                                         GauntletOffense=gauntlet,
                                         friendly_offense_strucutures=friendly_offense_structures,
                                         enemy_defense_structures=enemy_defense_structures,
                                         Threads=1,
                                         Iteration=1000),
                                     shell=True, cwd=tuo_path).splitlines()
    score = result[-3].split(': ')[1].split('(')[0]
    # print score
    Benchmarks.objects.update_or_create(deck_id=deck_id, defaults={'deck_id': deck_id, 'score': score})


@app.task
def benchmark_defense_sim(deck, deck_id):

    import os
    import subprocess

    tuo_path = os.path.join(settings.BASE_DIR, 'utils/tuo/')
    tuo_command = os.path.join(tuo_path, 'tuo.exe')
    friendly_defense_structures = "Illuminary Blockade"
    enemy_offense_structures = "Sky Fortress, Sky Fortress"
    gauntlet = "Benchmark"

    result = subprocess.check_output(tuo_command +
                                     ' "{Seed}" "{GauntletDefense}" gw-defense enemy:ordered'
                                     ' yf "{friendly_defense_structures}" ef "{enemy_offense_structures}"'
                                     ' -t {Threads} _benchmark sim {Iteration}'.format(
                                         Seed=deck,
                                         GauntletDefense=gauntlet,
                                         friendly_defense_structures=friendly_defense_structures,
                                         enemy_offense_structures=enemy_offense_structures,
                                         Threads=1,
                                         Iteration=1000),
                                     shell=True, cwd=tuo_path).splitlines()
    # print result
    score = result[-3].split(': ')[1].split(' (')[0]
    # print score
    Benchmarks.objects.update_or_create(deck_id=deck_id, defaults={'deck_id': deck_id, 'score': score})


@app.task
def update_xmls():

    import os
    import urllib
    xml_path = os.path.join(settings.BASE_DIR, 'utils/tuo/data')

    for i in range(1, 12 + 1):
        try:
            xml_source = urllib.urlopen("http://mobile-dev.tyrantonline.com/assets/cards_section_{0}.xml".format(
                i)).read()
            with open(os.path.join(xml_path, 'cards_section_{0}.xml'.format(i)), 'w') as xml_file:
                xml_file.write(xml_source)
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
