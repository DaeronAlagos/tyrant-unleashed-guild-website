import urlparse
import urllib
import urllib2
import json
import time
import hashlib
import os
from xml.etree import cElementTree as Et
import re
import glob
from jedisite.models import TyrantSettings
from django.conf import settings


class TyrantAPI(object):

    def __init__(self):

        self.settings = dict(TyrantSettings.objects.values_list('name', 'value'))
        self.TOurl = 'http://mobile.tyrantonline.com/api.php'  # Tyrant Unleashed Web URL
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36 OPR/34.0.2036.25',
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

    def get_postdata_params(self, postdata):

        postdata_params = urlparse.parse_qs(postdata)
        return postdata_params

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
        url = '{0}?message={1}&user_id={2}'.format(self.TOurl, message, self.user_id)
        request = urllib2.Request(url, new_postdata, self.header)
        response = urllib2.urlopen(request)
        response_data = json.loads(response.read())

        return response_data

    def create_conquest_zone_request(self, message, zone_id, postdata):

        postdata_params = urlparse.parse_qs(postdata)
        timestamp = int(time.time())
        self.user_id = int(postdata_params['user_id'][0])
        new_postdata_params = {'password': str(postdata_params['password'][0]),
                               'unity': str(self.settings['unity']),
                               'client_version': str(self.settings['client_version']),
                               'api_stat_name': 'getConquestUpdate',
                               'api_stat_time': '',
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
                               # 'os_version': str(self.settings['os_version']),
                               # 'udid': '',
                               # 'device_type': str(self.settings['device_type'])
                               'zone_id': zone_id
                               }

        new_postdata = urllib.urlencode(new_postdata_params)
        # print("New Postdata:", new_postdata)
        url = '{0}?message={1}&user_id={2}'.format(self.TOurl, message, self.user_id)
        # print("URL:", url)
        request = urllib2.Request(url, new_postdata, self.header)
        response = urllib2.urlopen(request)
        response_data = json.loads(response.read())

        return response_data

    def calculateMD5Hash(self, timestamp):
        return hashlib.md5('{0}{1}{2}'.format(self.settings['salt'], self.user_id, int(timestamp))).hexdigest()


class AccountDetails(object):

    def __init__(self, postdata):

        self.postdata = postdata
        self.owned_cards = self.get_owned_cards()
        self.unit_data = {}

    def get_owned_cards(self):

        tyrant_api = TyrantAPI()
        response_data = tyrant_api.create_request('init', self.postdata)

        # print("response data:", response_data)

        inventory = {
            "owned": [],
            "salvaged": []
        }

        for (cid, value) in response_data['user_cards'].items():
            if int(value['num_owned']) > 0:
                inventory["owned"].append(
                    {
                        "card_id": cid,
                        "quantity": value["num_owned"]
                    }
                )

        for card_id, data in response_data['buyback_data'].items():
            if int(data['number']) > 0:
                inventory["salvaged"].append(
                    {
                        "card_id": card_id,
                        "quantity": data["number"]
                    }
                )

        return inventory

    def format_inventory(self):

        card_faction = ['Imperial', 'Raider', 'Bloodthirsty', 'Xeno', 'Righteous', 'Progenitor']

        card_reader = CardReader()
        inventory_items = list()

        for idx, faction in enumerate(card_faction):
            inventory_items.append(
                '// {faction_name} //'.format(
                    faction_name=faction
                )
            )
            for card in self.owned_cards["owned"]:
                card_data = card_reader.card_id_to_name(int(card["card_id"]))
                quantity = card["quantity"]

                if int(card_data['card_type']) == idx + 1:
                    if int(quantity) > 1:
                        if card_data['card_rarity'] == 1 and card_data['card_level'] < 3 or \
                                                card_data['card_rarity'] == 2 and card_data['card_level'] < 4 or \
                                                card_data['card_rarity'] > 2 and card_data['card_level'] < 6:
                            inventory_items.append("{card_name}-{card_level} #{quantity}".format(
                                card_name=card_data['card_name'],
                                card_level=card_data['card_level'],
                                quantity=quantity))
                        else:
                            inventory_items.append("{card_name} #{card_quantity}".format(
                                card_name=card_data['card_name'],
                                card_quantity=quantity
                            ))
                    elif int(quantity) == 1:
                        if card_data['card_rarity'] == 1 and card_data['card_level'] < 3 or \
                                                card_data['card_rarity'] == 2 and card_data['card_level'] < 4 or \
                                                card_data['card_rarity'] > 2 and card_data['card_level'] < 6:
                            inventory_items.append("{card_name}-{card_level}".format(
                                card_name=card_data['card_name'],
                                card_level=card_data['card_level']
                            ))
                        else:
                            inventory_items.append("{card_name}".format(
                                card_name=card_data['card_name']
                            ))

        inventory_items.append("// Salvaged Cards //")

        for card in self.owned_cards["salvaged"]:
            card_data = card_reader.card_id_to_name(int(card['card_id']))
            quantity = card["quantity"]

            inventory_items.append("// {card_name}-{card_level} #{quantity}".format(
                card_name=card_data['card_name'],
                card_level=card_data['card_level'],
                quantity=quantity
            ))

        # print "cards list:", inventory_items
        return inventory_items

    def get_brawl_status(self, postdata):

        tyrant_api = TyrantAPI()
        response_data = tyrant_api.create_request('init', postdata)
        # print "Response Data:", response_data

        brawl_rank = {'brawl_name': response_data['user_data']['name']}
        for key, value in response_data['player_brawl_data'].iteritems():
            brawl_rank[key] = value

        return brawl_rank


class ConquestUpdate(object):

    def __init__(self):
        self.tyrant_api = TyrantAPI()

    def getConquestUpdate_data(self, postdata):

        data = self.tyrant_api.create_request('getConquestUpdate', postdata)
        # print "Data:", data

        return data


class CardReader(object):

    def __init__(self):

        self.cards_list = None

        try:
            with open(os.path.join(settings.BASE_DIR, "utils", "tuo", "data", "all_cards.json")) as all_cards_file:
                self.cards_list = json.load(all_cards_file)

        except IOError:

            self.create_all_cards_file()
            with open(os.path.join(settings.BASE_DIR, "utils", "tuo", "data", "all_cards.json")) as all_cards_file:
                self.cards_list = json.load(all_cards_file)

    def create_all_cards_file(self):

        xml_files = glob.glob(os.path.join(settings.BASE_DIR, "utils", "tuo", "data", "cards_section_*.xml"))
        cards_list = list()

        for xml_file in xml_files:
            tree = Et.ElementTree(file=xml_file)

            root = tree.getroot()
            for unit in root:

                cards_list.append(
                    {
                        "card_id": int(unit.find('id').text),
                        "card_name": str(unit.find('name').text),
                        "card_rarity": int(unit.find('rarity').text),
                        "card_type": int(unit.find('type').text),
                        "card_level": int(1)
                    }
                )

                for upgrade in unit.findall('upgrade'):

                    cards_list.append(
                        {
                            "card_id": int(upgrade.find('card_id').text),
                            "card_name": str(unit.find('name').text),
                            "card_rarity": int(unit.find('rarity').text),
                            "card_type": int(unit.find('type').text),
                            "card_level": int(upgrade.find('level').text)
                        }
                    )

        with open(os.path.join(settings.BASE_DIR, "utils", "tuo", "data", "all_cards.json"), "w") as all_cards_file:
            json.dump(cards_list, all_cards_file, indent=4)

    def card_id_to_name(self, card_id):

        # print "Card Data:", [matching for matching in self.cards_list if matching["card_id"] == card_id][0]
        return [matching for matching in self.cards_list if matching["card_id"] == card_id][0]

        # return [matching['card_name'] + '-' + matching['card_level'] for matching in self.cards_list
        #         if matching['card_id'] == card_id]

    def card_name_to_id(self, card_name):
        m = re.search(r"^\s?(.*?[\d]?)(-\d)?[ ]?#?(\d{1,2})?$", card_name)
        name = unicode(m.group(1))
        cards = []

        if m.group(2):
            level = int(m.group(2)[1:])
        else:
            level = max([matching["card_level"] for matching in self.cards_list if matching["card_name"] == name])

        if m.group(3):
            amount = m.group(3)
        else:
            amount = 1

        for i in range(1, int(amount) + 1):
            cards.append(
                ([matching["card_id"] for matching in self.cards_list if
                 (matching["card_name"] == name and matching["card_level"]) == level][0], card_name)
            )

        return cards

    def get_card_name(self, s):
        m = re.search(r'^\s?(.*?)-?(\d)?[ ]?#?(\d)?$', s)
        mx = [str(m.group(1)), str(m.group(2)), str(m.group(3))]
        # print "mx: ", mx
        return mx

    def deck_as_names_to_ids(self, cards_as_name):

        cards = cards_as_name.split(',')
        # print cards
        for card, qty in cards:
            return

    def bge_to_dict(self, bge):

        if not bge:
            bge_list = ["None", "None", "None"]
        else:
            bge_list = bge.split(', ')

        bge_as_dict = {
            "global": {
                "global_id": "",
                "name": ""
            },
            "friendly": {
                "friendly_id": "",
                "name": ""
            },
            "enemy": {
                "enemy_id": "",
                "name": ""
            }
        }

        try:
            bge_as_dict["global"]["name"] = str(bge_list[0])
        except IndexError:
            bge_as_dict["global"]["name"] = "None"

        try:
            bge_as_dict["friendly"]["name"] = str(bge_list[1])
        except IndexError:
            bge_as_dict["friendly"]["name"] = "None"

        try:
            bge_as_dict["enemy"]["name"] = str(bge_list[2])
        except IndexError:
            bge_as_dict["enemy"]["name"] = "None"

        # print "bge_as_dict:", bge_as_dict
        return bge_as_dict
