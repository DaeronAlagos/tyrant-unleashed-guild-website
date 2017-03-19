from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import utils.tyrant_utils as tyrant_utils
from jedisite.forms import UserForm, UserProfileForm, GameAccountForm, GameAccountBasicForm, DeckForm, \
    UserIsActiveForm, AllowCommandForm, PasswordChangeForm, UploadInventoryForm, ChangeGuildForm
from jedisite.models import GameAccount, User, Decks, ActionLog, Benchmarks, WarStats
from jedisite.serializers import DecksSerializer, ForceAuthSerializer, AccountsSerializer, InventorySerializer
from .tasks import benchmark_offense_sim, benchmark_defense_sim, check_war_status


# Check if account is in the Officers user group
def is_officer(user):
    return user.groups.filter(name='Officers').exists()


# Check if account is in the Force users group
def is_force_user(user):
    return user.groups.filter(name='Force').exists()


# Home page route
def index(request):
    return render(request, "index.html", {})


# Registration page route
def register(request):
    registered = False

    # If form is submitted
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)
            user.is_active = False
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            registered = True

        else:
            print user_form.errors

    else:
        user_form = UserForm()

    # Render page with custom complete message
    return render(request,
                  'register.html',
                  {'user_form': user_form, 'registered': registered, 'register_success':
                      'Registration Complete! Please notify an officer on LINE.'}
                  )


# Log in page route
def user_login(request):
    # If form is submitted
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:

            if user.is_active:
                login(request, user)
                # Redirect to users settings page
                return HttpResponseRedirect('/profile/settings/')
            else:
                # If account exists by has not been activated by admin
                return render(request, 'login.html',
                              {'disabled': 'Your Jedi account is disabled. Please contact an officer on LINE'})

        else:

            # print("Invalid login details: {0} {1}".format(username, password))
            # If account log in details are invalid
            return render(request, 'login.html', {'invalid_login': 'Invalid login details supplied'})

    # Return login page
    else:
        return render(request, 'login.html', {})


# Log out route (must already be logged in)
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


# User settings route (CSRF protect enabled as page includes password change form)
@login_required
@csrf_protect
@sensitive_post_parameters('old_password', 'new_password1', 'new_password2')
def user_settings(request):
    token = None

    try:
        token = Token.objects.filter(user=request.user)

    except Token.DoesNotExist:
        pass

    # If form is submitted
    if request.method == "POST":
        password_change_form = PasswordChangeForm(user=request.user, data=request.POST)
        if password_change_form.is_valid():
            password_change_form.save()
            # Updating the password logs out all other sessions for the user
            # except the current one.
            update_session_auth_hash(request, password_change_form.user)
            return render(request, 'user_settings.html', {'token': token,
                                                          'change_success': "Password changed successfully"})
    else:
        password_change_form = PasswordChangeForm(user=request.user)

    # Display user settings page
    return render(request, 'user_settings.html', {'token': token,
                                                  'password_change_form': password_change_form
                                                  })


# Delete account page (uses GET method so it can't be issued using POST, profile must also own game account to access)
@login_required
def delete_account(request):
    if request.method == 'GET':
        if 'account_name' in request.GET:
            account_name = request.GET['account_name']

            try:
                account = GameAccount.objects.get(name=account_name)

                if account.user_id == request.user.id:
                    account.delete()
                    return redirect('/profile/accounts/')

            except GameAccount.DoesNotExist:
                pass

    return redirect('/profile/accounts/')


@login_required
def update_postdata(request):
    if request.method == 'GET':

        if 'account_name' in request.GET:

            # check_war_status.delay()  # For testing Celery Schedules
            account_name = request.GET['account_name']

            try:
                account = GameAccount.objects.get(name=account_name)

                if account.user_id == request.user.id:

                    tyrant_api = tyrant_utils.TyrantAPI()
                    canvas_params = tyrant_api.get_canvas_params(account.canvas)
                    account.kong_name = str(canvas_params['kongregate_username'][0])
                    account.postdata = tyrant_api.get_postdata(account.canvas)
                    account_params = tyrant_api.create_request('init', account.postdata)
                    account.name = str(account_params['user_data']['name'])
                    try:
                        account.guild = str(account_params['faction']['name'])
                    except KeyError:
                        account.guild = ''
                    account.user_id = request.user
                    account.save()

                    return HttpResponseRedirect('/profile/accounts/')

            except GameAccount.DoesNotExist:
                pass

    return redirect('/profile/accounts')


@login_required
def download_inventory(request):
    if request.method == 'GET':

        if 'account_name' in request.GET:

            account_name = request.GET['account_name']

            try:
                import csv
                import StringIO

                account = GameAccount.objects.get(name=account_name)

                if account.postdata:
                    account_details = tyrant_utils.AccountDetails(account.postdata)
                    inventory = account_details.format_inventory()
                    # print("Cardlist:", card_list)
                else:
                    inventory = account.inventory
                    # print(card_list)

                f = StringIO.StringIO()
                writer = csv.writer(f)

                for card in inventory:
                    # print(card)
                    writer.writerow([card])

                f.seek(0)
                response = HttpResponse(f, content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename=oc_{0}.txt'.format(account.kong_name)
                return response

            except GameAccount.DoesNotExist:
                pass

    return


@login_required
def user_accounts(request):
    add_account_form = GameAccountForm(prefix='add_account')
    add_account_basic_form = GameAccountBasicForm(prefix='add_account_basic')
    allow_command_form = AllowCommandForm(prefix='allow_command')
    upload_inventory_form = UploadInventoryForm(prefix='upload_inventory')
    change_guild_form = ChangeGuildForm(prefix='change_guild')

    if request.method == 'POST':

        # print(request.POST)

        if 'add_account' in request.POST:
            add_account_form = GameAccountForm(request.POST, prefix='add_account')

            if add_account_form.is_valid():
                # print(add_account_form.errors)
                account = add_account_form.save(commit=False)
                tyrant_api = tyrant_utils.TyrantAPI()
                postdata_params = tyrant_api.get_postdata_params(add_account_form['postdata'].value())
                account.kong_name = str(postdata_params['kong_name'][0])
                account.postdata = add_account_form['postdata'].value()
                account_params = tyrant_api.create_request('init', account.postdata)
                account.name = str(account_params['user_data']['name'].encode('utf-8'))
                try:
                    account.guild = str(account_params['faction']['name'])
                except KeyError:
                    account.guild = ''
                account.user = request.user
                account.save()
                return HttpResponseRedirect('/profile/accounts/')

            add_account_basic_form = GameAccountBasicForm(prefix='add_account_basic')
            allow_command_form = AllowCommandForm(prefix='allow_command')
            upload_inventory_form = UploadInventoryForm(prefix='upload_inventory')
            change_guild_form = ChangeGuildForm(prefix='change_guild')

        elif 'add_account_basic' in request.POST:

            add_account_basic_form = GameAccountBasicForm(request.POST, prefix='add_account_basic')

            if add_account_basic_form.is_valid():
                # print(add_account_basic_form.errors)
                account = add_account_basic_form.save(commit=False)
                account.user = request.user
                account.save()
                return HttpResponseRedirect('/profile/accounts/')

            add_account_form = GameAccountForm(prefix='add_account')
            allow_command_form = AllowCommandForm(prefix='allow_command')
            upload_inventory_form = UploadInventoryForm(prefix='upload_inventory')
            change_guild_form = ChangeGuildForm(prefix='change_guild')

        elif 'allow_command' in request.POST:

            instance = GameAccount.objects.get(kong_name=request.POST['kong_name'])
            allow_command_form = AllowCommandForm(request.POST, prefix='allow_command', instance=instance)

            if allow_command_form.is_valid():
                if request.POST.get('allow_command', False):
                    command_form = allow_command_form.save(commit=False)
                    command_form.allow_command = True
                    command_form.save()
                else:
                    command_form = allow_command_form.save(commit=False)
                    command_form.allow_command = False
                    command_form.save()

                return HttpResponseRedirect('/profile/accounts/')

            add_account_form = GameAccountForm(prefix='add_account')
            add_account_basic_form = GameAccountBasicForm(prefix='add_account_basic')
            upload_inventory_form = UploadInventoryForm(prefix='upload_inventory')
            change_guild_form = ChangeGuildForm(prefix='change_guild')

        elif 'upload_inventory' in request.POST:

            # print(request.POST)

            instance = GameAccount.objects.get(kong_name=request.POST['kong_name'])
            upload_inventory_form = UploadInventoryForm(request.POST, prefix='upload_inventory', instance=instance)

            if upload_inventory_form.is_valid():
                # print(upload_inventory_form.errors)
                upload_inventory_form.save(commit=True)
                #
                # cards_list = upload_inventory_form['inventory'].value().splitlines()
                #
                # inventory_form.inventory = cards_list

                return HttpResponseRedirect('/profile/accounts/')

            add_account_form = GameAccountForm(prefix='add_account')
            add_account_basic_form = GameAccountBasicForm(prefix='add_account_basic')
            allow_command_form = AllowCommandForm(prefix='allow_command')
            change_guild_form = ChangeGuildForm(prefix='change_guild')

        elif 'kong_name' in request.POST:

            # print(request.POST)

            instance = GameAccount.objects.get(kong_name=request.POST['kong_name'])
            change_guild_form = ChangeGuildForm(request.POST, prefix='change_guild', instance=instance)

            if change_guild_form.is_valid():
                guild_form = change_guild_form.save(commit=False)
                guild_form.guild = request.POST['change_guild']
                guild_form.save()

                return HttpResponseRedirect('/profile/accounts')

            else:
                print(change_guild_form.errors)

            add_account_form = GameAccountForm(prefix='add_account')
            add_account_basic_form = GameAccountBasicForm(prefix='add_account_basic')
            allow_command_form = AllowCommandForm(prefix='allow_command')
            upload_inventory_form = UploadInventoryForm(prefix='upload_inventory')

    try:
        accounts = GameAccount.objects.filter(user=request.user).order_by('name')

    except GameAccount.DoesNotExist:
        pass

    return render(request, 'user_accounts.html', {'accounts': accounts,
                                                  'add_account_form': add_account_form,
                                                  'add_account_basic_form': add_account_basic_form,
                                                  'allow_command_form': allow_command_form,
                                                  'upload_inventory_form': upload_inventory_form,
                                                  'change_guild_form': change_guild_form,
                                                  })


@login_required
def user_decks(request):
    structures = [
        'Tesla Coil-4',
        'Minefield-4',
        'Foreboding Archway-4',
        'Forcefield-4',
        'Illuminary Blockade-4',
        'Inspiring Altar-4',
        'Death Factory-4',
        'Lightning Cannon-4',
        'Sky Fortress-4',
        'Mortar Tower-4',
        'Corrosive Spore-4'
    ]
    benchmark_structures = {
        "friendly_offense": "Sky Fortress-4, Sky Fortress-4",
        "friendly_defense": "Foreboding Archway-4",
        "enemy_offense": "Sky Fortress-4, Sky Fortress-4",
        "enemy_defense": "Foreboding Archway-4, Foreboding Archway-4"
    }

    if request.method == 'POST':

        if 'add_deck' in request.POST:
            card_reader = tyrant_utils.CardReader()
            post_name_id = request.POST.get('add_deck-name').encode('utf-8')
            post_name = GameAccount.objects.get(id=post_name_id).name
            post_mode = request.POST.get('add_deck-mode')
            post_type = request.POST.get('add_deck-type')
            post_bge = request.POST.get('add_deck-bge')
            # print "post bge:", post_bge
            post_friendly_structures_list = request.POST.get('add_deck-friendly_structures').split(",")
            for idx, structure in enumerate(post_friendly_structures_list):
                post_friendly_structures_list[idx] = structure.strip().title() + "-4"
            post_enemy_structures_list = request.POST.get('add_deck-enemy_structures').split(",")
            for idx, structure in enumerate(post_enemy_structures_list):
                post_enemy_structures_list[idx] = structure.strip().title() + "-4"

            try:
                instance = Decks.objects.get(
                    name=post_name,
                    mode=post_mode,
                    type=post_type,
                    bge=card_reader.bge_to_dict(post_bge),
                    friendly_structures=", ".join(post_friendly_structures_list),
                    enemy_structures=", ".join(post_enemy_structures_list)
                )
                # print "Instance: ", instance
                add_deck_form = DeckForm(request.POST, user=request.user, prefix='add_deck', instance=instance)
            except Decks.DoesNotExist:
                add_deck_form = DeckForm(request.POST, user=request.user, prefix='add_deck')
                # print "Instance not found"

            if add_deck_form.is_valid():
                # print(add_deck_form.errors)
                deck_form = add_deck_form.save(commit=False)

                # Convert deck string into json format
                cards_as_name = add_deck_form['deck'].value()
                cards_as_name = cards_as_name.split(',')

                deck = {
                    "commander": {
                        "card_id": str(card_reader.card_name_to_id(cards_as_name[0])),
                        "name": str(cards_as_name.pop(0))
                    },
                    "cards": [

                    ]
                }

                for card_name in cards_as_name:
                    # for returned_card_id, returned_card_name in card_reader.card_name_to_id(card_name):
                    returned_card_ids = card_reader.card_name_to_id(card_name)
                    for card_id in returned_card_ids:
                        deck.setdefault("cards").append(
                            {"card_id": int(card_id[0]), "name": str(card_id[1])}
                        )

                # deck = json.dumps(deck)
                deck_form.deck = deck

                deck_form.bge = card_reader.bge_to_dict(add_deck_form['bge'].value())

                guild = GameAccount.objects.filter(name=deck_form.name).values('guild')
                deck_form.guild = guild[0]['guild']

                deck_form.save()
                deck_id = Decks.objects.get(
                    name=deck_form.name.encode('utf-8'),
                    mode=deck_form.mode,
                    type=deck_form.type,
                    bge=card_reader.bge_to_dict(post_bge),
                    friendly_structures=deck_form.friendly_structures,
                    enemy_structures=deck_form.enemy_structures
                )

                if deck_id.type == "Faction" and deck_id.mode == "Offense" and deck_id.bge == {
                    "global": {"global_id": "", "name": "None"},
                    "friendly": {"friendly_id": "", "name": "None"},
                    "enemy": {"enemy_id": "", "name": "None"}} and \
                    deck_id.friendly_structures == benchmark_structures["friendly_offense"] and \
                        deck_id.enemy_structures == benchmark_structures["enemy_defense"]:
                    # print "Benchmark Offense Deck"
                    benchmark_offense_sim.delay(add_deck_form['deck'].value(), deck_id.id)
                if deck_id.type == "Faction" and deck_id.mode == "Defense" and deck_id.bge == {
                    "global": {"global_id": "", "name": "None"},
                    "friendly": {"friendly_id": "", "name": "None"},
                    "enemy": {"enemy_id": "", "name": "None"}} and \
                    deck_id.friendly_structures == benchmark_structures["friendly_defense"] and \
                        deck_id.enemy_structures == benchmark_structures["enemy_offense"]:
                    # print "Benchmark Defense Deck"
                    benchmark_defense_sim.delay(add_deck_form['deck'].value(), deck_id.id)

                return HttpResponseRedirect('/profile/decks/')

    else:

        add_deck_form = DeckForm(prefix='add_deck', user=request.user)

    try:
        accounts = GameAccount.objects.filter(user=request.user).values_list('name'.encode('utf-8'),
                                                                             flat=True).order_by('name')
        # print accounts
        decks = Decks.objects.filter(name__in=accounts).values()

        for deck in decks:
            # print "Deck:", deck

            card_list = [deck['deck']["commander"]["name"]]

            for card in deck['deck']["cards"]:
                card_list.append(card["name"])

            card_names = ', '.join(card_list)
            deck['deck'] = card_names

            bge_names = "Global: " + str(deck["bge"]["global"]["name"] +
                                         ", Friendly: " + str(deck["bge"]["friendly"]["name"] +
                                                              ", Enemy: " + str(deck["bge"]["enemy"]["name"])))

            deck['bge'] = bge_names

    except GameAccount.DoesNotExist, Decks.DoesNotExist:
        pass

    return render(request, 'user_decks.html', {'add_deck_form': add_deck_form,
                                               'accounts': accounts,
                                               'decks': decks})


@login_required
def benchmarks(request):
    benchmarks_queryset = Benchmarks.objects.all()  # Get Database query set

    from collections import defaultdict
    benchmarks_dict = defaultdict(dict)

    for account_name in benchmarks_queryset:

        benchmarks_dict[account_name.deck.name]["guild"] = account_name.deck.guild

        try:

            if account_name.deck.mode == "Offense":

                card_list = [account_name.deck.deck["commander"]["name"]]

                for card in account_name.deck.deck["cards"]:
                    card_list.append(card["name"])

                card_names = ', '.join(card_list)

                benchmarks_dict[account_name.deck.name]["offense_deck"] = card_names
                benchmarks_dict[account_name.deck.name]["offense_score"] = round(float(account_name.score), 2)
                benchmarks_dict[account_name.deck.name]["offense_date"] = account_name.date

            if account_name.deck.mode == "Defense":

                card_list = [account_name.deck.deck["commander"]["name"]]

                for card in account_name.deck.deck["cards"]:
                    card_list.append(card["name"])

                card_names = ', '.join(card_list)

                benchmarks_dict[account_name.deck.name]["defense_deck"] = card_names
                benchmarks_dict[account_name.deck.name]["defense_score"] = round(float(account_name.score), 2)
                benchmarks_dict[account_name.deck.name]["defense_date"] = account_name.date

        except KeyError:

            pass

        try:

            benchmarks_dict[account_name.deck.name]["total"] = \
                round(float((benchmarks_dict[account_name.deck.name]["offense_score"] +
                             benchmarks_dict[account_name.deck.name]["defense_score"]) / 2), 2)

        except KeyError:

            benchmarks_dict[account_name.deck.name]["total"] = 0

    benchmarks_accounts = benchmarks_dict.items()
    benchmarks_accounts.sort(key=lambda x: (x[1]["total"]), reverse=True)

    return render(request, "benchmarks.html", {'benchmarks_accounts': benchmarks_accounts,
                                               })


@login_required
def ranks_war(request):
    from collections import defaultdict

    war_data = WarStats.objects.order_by('date').values()
    stats_construct = defaultdict(list)

    # print("War Data:", war_data)

    for war in war_data:

        member_data = []
        # print "War:", war

        for player in war['data']:

            member = {
                "member_name": player['member_name'],
                "wins": player['wins'],
                "losses": player['losses'],
                "attacks": player['wins'] + player['losses'],
                "defend_wins": player['defend_wins'],
                "defend_losses": player['defend_losses'],
                "attacked": player['defend_wins'] + player['defend_losses']
            }

            try:
                member.update(
                    {'win_percent': round(float(player['wins']) / 20 * 100, 1)}
                )
            except ZeroDivisionError:
                member.update(
                    {'win_percent': 0}
                )
            try:
                member.update(
                    {'defend_percent': round(float(player['defend_wins']) / int(member['attacked']) * 100, 1)}
                )
            except ZeroDivisionError:
                member.update(
                    {'defend_percent': 100.0}
                )

            # member.update({'total_wins': player['wins']})

            member_data.append(member)

        member_data = sorted(member_data, key=lambda k: k['member_name'].lower())

        stats_construct[war['name']].append([war['enemy_guild'], member_data])

    # for war, enemies in stats_construct.items():
    #     print war
    #     member_totals = []
    #     for enemy, player in enemies:
    #         member_totals.append(
    #             {"member_name": player["member_name"], "total_wins": player["wins"]}
    #         )
    #
    #
    # print(stats_construct)

    return render(request, "ranks_war.html", {
        'stats_construct': dict(stats_construct),
    })


@login_required
def ranks_brawl(request):
    return render(request, "ranks_brawl.html", {})


@login_required
@user_passes_test(is_officer)
def members(request):
    try:
        users = User.objects.all()
        users = users.exclude(username="james")
        users = users.order_by("username")
        # print users

    except User.DoesNotExist:
        pass

    if request.method == 'POST':

        if 'is_active' in request.POST:
            post_test = request.POST.get('the_post')
            response_data = {}

            is_active_form = UserIsActiveForm(request.POST, prefix='is_active')

            if is_active_form.is_valid():
                return

    else:
        is_active_form = UserIsActiveForm(prefix='is_active')

    return render(request, "members.html", {'users': users,
                                            'is_active_form': is_active_form,
                                            })


@login_required
@user_passes_test(is_officer)
def accounts_list(request):
    try:
        game_accounts = GameAccount.objects.all().order_by("name")
        action_log = ActionLog.objects.filter(event="Canvas").order_by('target_id', '-date').distinct('target_id')

    except GameAccount.DoesNotExist:
        pass

    return render(request, "accounts.html", {'game_accounts': game_accounts,
                                             'action_log': action_log
                                             })


@login_required
@user_passes_test(is_officer)
def gauntlets(request):
    from datetime import datetime, timedelta
    from collections import Counter

    try:
        expiry_date = datetime.now() - timedelta(days=7)
        decks = Decks.objects.all().exclude(date__lt=expiry_date).order_by("-date").values()
        # decks = Decks.objects.all().order_by("-date").values()
        commander_list = []

        for deck in decks:
            card_list = [deck['deck']["commander"]["name"]]
            commander_list.append(deck['deck']["commander"]["name"].split('-')[0])

            for card in deck['deck']["cards"]:
                card_list.append(card["name"])

            card_names = ', '.join(card_list)
            deck['deck'] = card_names

            bge_names = "Global: " + str(deck['bge']["global"]["name"] + ", Friendly: " + str(
                deck['bge']["friendly"]["name"] + ", Enemy: " + str(deck['bge']["enemy"]["name"])))

            deck['bge'] = bge_names

        commander_count = Counter(commander_list)
        commander_dict = {}
        for commander in commander_count:
            commander_dict.update(
                {str(commander): round(float(commander_count[commander]) / sum(commander_count.itervalues()) * 100, 1)})

    except Decks.DoesNotExist:
        pass

    return render(request, "gauntlets.html", {'decks': decks,
                                              'commander_dict': commander_dict,
                                              })


@login_required
@user_passes_test(is_force_user)
def download(request):
    import os

    filename = "ThePyForce.zip"
    restricted_directory = "/home/daeronalagos/webapps/static_media/restricted_downloads"

    response = HttpResponse(content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    response['X-Sendfile'] = os.path.join(restricted_directory, filename)
    return response


@login_required
def benchmark_gauntlet(request):
    import os

    filename = "customdecks_benchmark.txt"
    directory = "/home/daeronalagos/webapps/static_media/restricted_downloads"

    response = HttpResponse(content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    response['X-Sendfile'] = os.path.join(directory, filename)
    return response


# API VIEWS #

@api_view(['GET', 'POST'])
def deckslist(request):
    if request.method == 'GET':

        if 'guild' and 'battle_type' and 'gbge' in request.GET:

            decks = Decks.objects.filter(
                guild=request.GET['guild'],
                type=request.GET['battle_type'],
                bge__global__name=request.GET['gbge'])
            serializer = DecksSerializer(decks, many=True)
            return Response(serializer.data)

        else:

            decks = Decks.objects.all()
            serializer = DecksSerializer(decks, many=True)
            return Response(serializer.data)

    elif request.method == 'POST':

        # bge = json.loads(request.data['bge'])

        try:
            instance = Decks.objects.get(
                name=request.data['name'],
                mode=request.data['mode'],
                type=request.data['type'],
                bge=request.data['bge'],
                # bge=bge,
                friendly_structures=request.data['friendly_structures'],
                enemy_structures=request.data['enemy_structures']
            )
            serializer = DecksSerializer(instance, data=request.data)

        except Decks.DoesNotExist:
            serializer = DecksSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors)


@api_view(['GET', ])
@user_passes_test(is_force_user)
def force_auth(request):
    if request.method == 'GET':

        if 'account_name' in request.GET:

            try:
                account = GameAccount.objects.get(kong_name=request.GET['account_name'])
            except GameAccount.DoesNotExist:
                content = {status.HTTP_404_NOT_FOUND: 'Game Account Does Not Exist'}
                return Response(content)
            user = request.user
            serializer = ForceAuthSerializer(account)
            if account.user_id == user.id:
                return Response(serializer.data)
            else:
                content = {status.HTTP_403_FORBIDDEN: 'Permission Denied'}
                return Response(content)

    content = {status.HTTP_403_FORBIDDEN: 'Permission Denied'}
    return Response(content)


@api_view(['GET', ])
@user_passes_test(is_officer)
def api_account_list(request):
    if request.method == 'GET':

        decks = Decks.objects.filter(
            mode="Offense").filter(
            type="Faction").filter(
            friendly_structures="Sky Fortress-4, Sky Fortress-4").filter(
            enemy_structures="Foreboding Archway-4, Foreboding Archway-4"
        )
        accounts = GameAccount.objects.filter(name__in=decks.values('name'))

        accounts_to_sim = []

        for account in accounts:

            for deck in decks:

                if deck.name == account.name:

                    card_list = [deck.deck["commander"]["name"]]

                    for card in deck.deck["cards"]:
                        card_list.append(card["name"])

                    card_names = ", ".join(card_list)

                    accounts_to_sim.append(
                        {
                            "account": account.name,
                            "guild": account.guild,
                            "seed": card_names
                        }
                    )

        serializer = AccountsSerializer(accounts_to_sim)
        return Response(serializer.data)

    else:
        content = {status.HTTP_403_FORBIDDEN: 'Permission Denied'}
        return Response(content)


@api_view(['GET', ])
@user_passes_test(is_officer)
def user_inventory(request):

    if "account" in request.GET:

        try:
            account = GameAccount.objects.get(name=request.GET['account'])
        except GameAccount.DoesNotExist:
            content = {status.HTTP_404_NOT_FOUND: 'Game Account Does Not Exist'}
            return Response(content)

        if account.postdata:
            account_details = tyrant_utils.AccountDetails(account.postdata)
            card_list = account_details.format_inventory()
        else:
            card_list = account.inventory

        serializer = InventorySerializer(card_list)
        return Response(serializer.data)

    else:

        content = {status.HTTP_404_NOT_FOUND: 'No game account specified'}
        return Response(content)
