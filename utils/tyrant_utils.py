import urlparse
import urllib
import urllib2
import json
import time
import hashlib
import os
import xmltodict
import re
import glob
import datetime
from jedisite.models import TyrantSettings
from django.conf import settings


class TyrantAPI(object):

    def __init__(self):

        #settings = TyrantSettings.objects.all()  # Get values from database
        self.settings = dict(TyrantSettings.objects.values_list('name', 'value'))
        self.TOurl = 'http://mobile.tyrantonline.com/api.php'  # Tyrant Unleashed Web URL
        self.header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36 OPR/34.0.2036.25',
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                           'Accept-Language': 'en-GB,en;q=0.5',
                           'Host': 'mobile.tyrantonline.com',
                           'Content-Type': 'application/x-www-form-urlencoded',
                           'X-Unity-Version': '4.6.6f2',
                           'Connection': 'keep-alive'
                       }
        self.user_id = ''

    def get_canvas_params(self, canvas):  # Parse canvas link

        canvas_params = urlparse.parse_qs(urlparse.urlparse(canvas).query)
        return canvas_params

    def get_postdata(self, canvas):  # Prepare initial postdata to send

        # Get parameters from canvas
        canvas_params = self.get_canvas_params(canvas)

        # Assemble short postdata parameters
        short_postdata_params = dict()
        short_postdata_params.update({'password': ''})  # Don't have this until response. Remove?
        short_postdata_params.update({'unity': self.settings['unity']})
        short_postdata_params.update({'client_version': self.settings['client_version']})
        short_postdata_params.update({'api_stat_name': 'getUserAccount'})
        short_postdata_params.update({'api_stat_time': ''})  # Do I need this?
        short_postdata_params.update({'user_id': ''})  # Don't have this until response. Remove?
        short_postdata_params.update({'timestamp': ''})
        short_postdata_params.update({'hash': ''})  # Made from 'user_id' + 'salt' + 'timestamp'. Probably don't need it.
        short_postdata_params.update({'syncode': ''})  # Don't have this until response. Remove?
        short_postdata_params.update({'client_version': self.settings['client_version']})  # This was in sample data twice. Probably don't need it.
        short_postdata_params.update({'device_type': self.settings['device_type']})
        short_postdata_params.update({'os_version': self.settings['os_version']})
        short_postdata_params.update({'platform': self.settings['platform']})
        short_postdata_params.update({'kong_id': canvas_params['kongregate_user_id'][0]})
        short_postdata_params.update({'kong_token': canvas_params['kongregate_game_auth_token'][0]})
        short_postdata_params.update({'kong_name': canvas_params['kongregate_username'][0].encode('utf-8')})
        short_postdata_params.update({'dummy': 'data'})

        # Encode short postdata parameters to a string
        short_postdata = urllib.urlencode(short_postdata_params)
        # print("Short Postdata", short_postdata)

        short_url = '{0}?message={1}&user_id='.format(self.TOurl, 'getUserAccount')
        request = urllib2.Request(short_url, short_postdata, self.header)
        response = urllib2.urlopen(request)
        response_data = json.loads(response.read())
        # print(response_data)

        self.user_id = int(response_data['new_user'])

        long_postdata_params = {'password': str(response_data['new_password']),
                                'unity': str(self.settings['unity']),
                                'client_version': str(self.settings['client_version']),
                                'user_id': int(response_data['new_user']),
                                'timestamp': int(time.time()),
                                'hash': '',
                                'syncode': str(response_data['new_syncode']),
                                'client_version': str(self.settings['client_version']),
                                'device_type': str(self.settings['device_type']),
                                'os_version': str(self.settings['os_version']),
                                'platform': str(self.settings['platform']),
                                'kong_id': str(canvas_params['kongregate_user_id'][0]),
                                'kong_token': str(canvas_params['kongregate_game_auth_token'][0]),
                                'kong_name': str(canvas_params['kongregate_username'][0]),
                                'os_version': str(self.settings['os_version']),
                                'udid': '',
                                'device_type': str(self.settings['device_type'])
                                }

        long_postdata_params.update({'hash': self.calculateMD5Hash(long_postdata_params['timestamp'])})

        long_postdata = urllib.urlencode(long_postdata_params)
        # print("Long Postdata:", long_postdata)

        return long_postdata

    def create_request(self, message, postdata):

        postdata_params = urlparse.parse_qs(postdata)
        # print(postdata_params)
        timestamp = int(time.time())
        self.user_id = int(postdata_params['user_id'][0])
        new_postdata_params = {'password': str(postdata_params['password'][0]),
                               'unity': str(self.settings['unity']),
                               'client_version': str(self.settings['client_version']),
                               'user_id': self.user_id,
                               'timestamp': timestamp,
                               'hash': self.calculateMD5Hash(timestamp),
                               'syncode': str(postdata_params['syncode'][0]),
                               'client_version': str(self.settings['client_version']),
                               'device_type': str(self.settings['device_type']),
                               'os_version': str(self.settings['os_version']),
                               'platform': str(self.settings['platform']),
                               'kong_id': str(postdata_params['kong_id'][0]),
                               'kong_token': str(postdata_params['kong_token'][0]),
                               'kong_name': str(postdata_params['kong_name'][0]),
                               'os_version': str(self.settings['os_version']),
                               'udid': '',
                               'device_type': str(self.settings['device_type'])
                               }

        new_postdata = urllib.urlencode(new_postdata_params)
        url = '{0}?message={1}&user_id='.format(self.TOurl, message, self.user_id)
        request = urllib2.Request(url, new_postdata, self.header)
        response = urllib2.urlopen(request)
        response_data = json.loads(response.read())

        return response_data

    def calculateMD5Hash(self, timestamp):
        return hashlib.md5('{0}{1}{2}'.format(self.settings['salt'], self.user_id, int(timestamp))).hexdigest()


class AccountDetails(object):

    def __init__(self):

        self.card_list = []
        self.unit_data = {}

    def get_owned_cards(self, postdata):

        tyrant_api = TyrantAPI()
        response_data = tyrant_api.create_request('init', postdata)

        # print("response data:", response_data)

        cards = {}
        for (cid, value) in response_data['user_cards'].items():
            if int(value['num_owned']) > 0:
                cards.update({cid: value['num_owned']})

        card_reader = CardReader()

        card_faction = ['none', 'Imperial', 'Raider', 'Bloodthirsty', 'Xeno', 'Righteous', 'Progenitor']
        get_cards_start = datetime.datetime.now()
        for i in range(1, 7):
            self.card_list.append(['// {0} //'.format(card_faction[i])])
            for (cid, value) in cards.items():
                self.unit_data = card_reader.card_id_to_name(cid)
                print "Unit Data:", self.unit_data
                # TODO: Make this work better
                if not int(cid) == 31184:  # Neocyte Core
                    if int(self.unit_data['type']) == i:
                        if int(value) > 1:
                            #print self.unit_data['card_name']
                            if (int(self.unit_data['rarity']) == 1 and int(self.unit_data['level']) < 3) or (int(self.unit_data['rarity']) == 2 and int(self.unit_data['level']) < 4) or (int(self.unit_data['rarity']) > 2 and int(self.unit_data['level']) < 6):
                                #print "{0}-{1} #{2}".format(self.unit_data['card_name'], self.unit_data['card_level'], value)
                                self.card_list.append(['{0}-{1} #{2}'.format(self.unit_data['name'], self.unit_data['level'], value)])
                            else:
                                #print "{0} #{1}".format(self.unit_data['card_name'], value)
                                self.card_list.append(['{0} #{1}'.format(self.unit_data['name'], value)])
                        else:
                            if (int(self.unit_data['rarity']) == 1 and int(self.unit_data['level']) < 3) or (int(self.unit_data['rarity']) == 2 and int(self.unit_data['level']) < 4) or (int(self.unit_data['rarity']) > 2 and int(self.unit_data['level']) < 6):
                                #print "{0}-{1}".format(self.unit_data['card_name'], self.unit_data['card_level'])
                                self.card_list.append(['{0}-{1}'.format(self.unit_data['name'], self.unit_data['level'])])
                            else:
                                #print "{0}".format(self.unit_data['card_name'])
                                self.card_list.append(['{0}'.format(self.unit_data['name'])])
                else:
                    self.card_list.append(['Neocyte Core-2'])

        get_cards_end = datetime.datetime.now()
        print "Time to get cards: ", get_cards_end - get_cards_start
        return self.card_list

    def get_brawl_status(self, postdata):

        tyrant_api = TyrantAPI()
        response_data = tyrant_api.create_request('init', postdata)
        print "Response Data:", response_data

        brawl_rank = {'brawl_name': response_data['user_data']['name']}
        for key, value in response_data['player_brawl_data'].iteritems():
            brawl_rank[key] = value

        return brawl_rank


class CardReader(object):

    def __init__(self):
        self.cardList = {}

        self.xml_files = glob.glob(os.path.join(settings.BASE_DIR, 'utils/tuo/data/cards_section_?.xml'))
        for self.xml_file in self.xml_files:
            self.xml = open(self.xml_file, 'r')
            self.xml_dict = xmltodict.parse(self.xml, encoding='utf-8')
            for card in self.xml_dict['root']['unit']:
                try:
                    try:
                        self.cardList.update({
                            card['id']: {'name': card['name'], 'rarity': card['rarity'], 'level': unicode(1),
                                         'set': card['set'], 'type': card['type'], 'fusion_level': card['fusion_level']}})
                        try:
                            for level in card['upgrade']:
                                self.cardList.update({
                                    level['card_id']: {'name': card['name'], 'rarity': card['rarity'],
                                                       'level': level['level'],
                                                       'set': card['set'], 'type': card['type'],
                                                       'fusion_level': card['fusion_level']}})
                        except:
                            pass
                    except:
                        self.cardList.update({
                            card['id']: {'name': card['name'], 'rarity': card['rarity'], 'level': unicode(1),
                                         'set': card['set'], 'type': card['type']}})
                        try:
                            for level in card['upgrade']:
                                self.cardList.update({
                                    level['card_id']: {'name': card['name'], 'rarity': card['rarity'],
                                                       'level': level['level'],
                                                       'set': card['set'], 'type': card['type']}})
                        except:
                            pass
                except:
                    self.cardList.update(
                        {card['id']: {'name': card['name'], 'rarity': card['rarity'], 'level': unicode(1),
                                      'type': card['type']}})
                    try:
                        for level in card['upgrade']:
                            self.cardList.update({
                                level['card_id']: {'name': card['name'], 'rarity': card['rarity'],
                                                   'level': level['level'], 'type': card['type']}})
                    except:
                        pass

    def card_id_to_name(self, card_id):

        return self.cardList.get(str(card_id))

    def card_name_to_id(self, card):

        m = re.search(r'^\s?(.*?)-?(\d)?[ ]?#?(\d)?$', card)
        name = unicode(m.group(1))
        cards = []
        for (card_id, unit_data) in self.cardList.items():
            if unit_data['name'] == name:
                if int(unit_data['rarity']) == 1:
                    if m.group(2) is None:
                        level = 3
                    else:
                        level = m.group(2)
                    break
                if int(unit_data['rarity']) == 2:
                    if m.group(2) is None:
                        level = 4
                    else:
                        level = m.group(2)
                    break
                if int(unit_data['rarity']) > 2:
                    if m.group(2) is None:
                        level = 6
                    else:
                        level = m.group(2)
                    break
            if m.group(3) is not None:
                amount = m.group(3)
            else:
                amount = 1

        for i in range(1, int(amount) + 1):
            cards.extend([(card_id, name)])

        # print "Returned Cards:", cards
        return cards

    def get_card_name(self, s):
        m = re.search(r'^\s?(.*?)-?(\d)?[ ]?#?(\d)?$', s)
        mx = [str(m.group(1)), str(m.group(2)), str(m.group(3))]
        print "mx: ", mx
        return mx

    def deck_as_names_to_ids(self, cards_as_name):

        cards = cards_as_name.split(',')
        print cards
        for card, qty in cards:
            return
