from __future__ import absolute_import

from jediguild.celery import app
from django.conf import settings
from jedisite.models import Benchmarks

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

    tuo = os.path.join(settings.BASE_DIR, 'utils/tuo/tuo.exe')
    friendly_offense_structures = "Inspiring Altar, Inspiring Altar"
    enemy_defense_structures = "Minefield"

    result = subprocess.check_output(tuo +
                                     ' "{Seed}" "{GauntletOffense}" gw ordered yf "{friendly_offense_strucutures}"'
                                     ' ef "{enemy_defense_structures}" -t {Threads} sim {Iteration}'.format(
                                         Seed=deck,
                                         GauntletOffense="april_gw_metamorph",
                                         friendly_offense_strucutures=friendly_offense_structures,
                                         enemy_defense_structures=enemy_defense_structures,
                                         Threads=1,
                                         Iteration=1000),
                                     shell=False, cwd=".\\utils\\tuo").splitlines()
    score = result[-3].split(': ')[1].split('(')[0]
    # print score
    Benchmarks.objects.update_or_create(deck_id=deck_id, defaults={'deck_id': deck_id, 'score': score})


@app.task
def benchmark_defense_sim(deck, deck_id):

    import os
    import subprocess

    tuo = os.path.join(settings.BASE_DIR, 'utils/tuo/tuo.exe')
    friendly_defense_structures = "Minefield"
    enemy_offense_structures = "Inspiring Altar, Inspiring Altar"

    result = subprocess.check_output(tuo +
                                     ' "{Seed}" "{GauntletDefense}" gw-defense enemy:ordered'
                                     ' yf "{friendly_defense_structures}" ef "{enemy_offense_structures}"'
                                     ' -t {Threads} sim {Iteration}'.format(
                                         Seed=deck,
                                         GauntletDefense="april_gw_metamorph",
                                         friendly_defense_structures=friendly_defense_structures,
                                         enemy_offense_structures=enemy_offense_structures,
                                         Threads=1,
                                         Iteration=1000),
                                     shell=False, cwd=".\\utils\\tuo").splitlines()
    print result
    score = result[-3].split(': ')[1].split(' (')[0]
    # print score
    Benchmarks.objects.update_or_create(deck_id=deck_id, defaults={'deck_id': deck_id, 'score': score})
