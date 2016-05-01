from __future__ import absolute_import

from jediguild.celery import app
from django.conf import settings

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
def benchmark_sim(deck):

    import os
    import subprocess

    tuo = os.path.join(settings.BASE_DIR, 'utils/tuo/tuo.exe')

    result = subprocess.check_output(tuo +
                                     ' "{Seed}" "{GauntletOffense}" gw ordered -t {Threads} sim {Iteration}'.format(
                                         Seed=deck,
                                         GauntletOffense="april_gw_metamorph",
                                         Threads=1,
                                         Iteration=1000),
                                     shell=False, cwd=".\\utils\\tuo").splitlines()
    score = result[-3].split(':')[1].split('(')[0]
    print score
