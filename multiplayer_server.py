
from flask import Flask, request
from mencryption import rsa_fernet_encrypt, rsa_fernet_decrypt, generate_rsa_keys, rsa_fernet_signature
from base64 import urlsafe_b64encode, urlsafe_b64decode
from os.path import exists
from json import dump, dumps, load, loads
from json.decoder import JSONDecodeError
from time import time
from mrandom import randint_except
from mhash import sha256
from mmath import int_to_bytes

#
# import os
# import logging
#
# logging.getLogger('werkzeug').disabled = True
# os.environ['WERKZEUG_RUN_MAIN'] = 'true'
#

app = Flask(__name__)

if not exists('rsa.json'):
    _r = generate_rsa_keys(2048, None)
    e, d, n = _r[0], _r[1], _r[2]
    _x = {'e': e, 'd': d, 'n': n}
    with open('rsa.json', 'w') as _f:
        dump(_x, _f, indent=4)
else:
    with open('rsa.json', 'r') as _f:
        _x = load(_f)
    e, d, n = _x['e'], _x['d'], _x['n']

if not exists('games.json'):
    g = {}
    with open('games.json', 'w') as _f:
        dump(g, _f, indent=4)
else:
    with open('games.json', 'r') as _f:
        g = load(_f)

if not exists('accounts.json'):
    a = {}
    with open('accounts.json', 'w') as _f:
        dump(a, _f, indent=4)
else:
    with open('accounts.json', 'r') as _f:
        a = load(_f)


def get_account_name(rsa_n):
    for i in a.keys():
        if a[i]['n'] == rsa_n:
            return i
    return None


def re(data: dict, status: int, a_e: int, a_n: int):
    global e, d, n
    cipher = rsa_fernet_encrypt(dumps(data).encode(), a_e, a_n, e, d, n)
    return {'data': urlsafe_b64encode(cipher), 'app': 'mmL-Game'}, status


@app.route('/api/game', methods=['POST'])
def handle_request():
    global e, d, n, a, g
    if request.is_json:
        try:
            enc_data = urlsafe_b64decode(request.json['data'])
            try:
                str_data = rsa_fernet_decrypt(enc_data, d, n, False).decode()
                signature = rsa_fernet_signature(enc_data, d, n)
            except ValueError:
                return {'error': 'Could not decrypt the request :101', 'app': 'mmL-Game'}, 400

            a_e = signature[1]
            a_n = signature[2]
            account_ns = [i['n'] for i in a.values()]

            try:
                data = loads(str_data)
            except JSONDecodeError:
                return {'error': 'The encrypted data must be JSON :102', 'app': 'mmL-Game'}, 400

            if data['action'] == 'create_account':
                if a_n in account_ns:
                    return re({'error': 'You already have an account :103'}, 400, a_e, a_n)
                if data['value'] in a.keys():
                    return re({'error': 'An account with this name already exists :104'}, 400, a_e, a_n)
                if data['value'] > 32:
                    return re({'error': 'Name is too long :120'}, 400, a_e, a_n)
                legal_characters = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@.-_/äöüÄÖÜßàâéèêëœïîôùûç&')
                for i in range(len(data['value'])):
                    if data['value'] not in legal_characters:
                        return re({'error': 'Name contains illegal/not supported characters :121'}, 400, a_e, a_n)
                a[data['value']] = {'e': a_e, 'n': a_n, 'time': time()}
                with open('accounts.json', 'w') as f:
                    dump(a, f, indent=4)
                return re({'success': 'you created a new account'}, 200, a_e, a_n)

            if data['action'] == 'init':
                if signature[2] not in account_ns:
                    return re({'error': 'You do not have an account :105'}, 400, a_e, a_n)
                if data['max_players'] < 2 or data['max_players'] > 32:
                    return re({'error': 'Number of maximum players not supported :114'}, 400, a_e, a_n)
                g_code = randint_except(10 ** 5, 10 ** 6, list(g.keys()))
                game = {'max_players': data['max_players'], 'banned_ids': data['banned_ids'], 'game': data['game'],
                        'players': {get_account_name(a_n): {'e': a_e, 'n': a_n}},
                        'created': time(), 'ended': None, 'host': get_account_name(a_n),
                        'log': {str(time()): {'action': 'init',
                                              'player': get_account_name(a_n), 'data': 'Created game'},
                                str(time() + 0.005): {'action': 'join', 'player': get_account_name(a_n), 'data': ''}}}
                if data['public']:
                    game['status'] = 1
                else:
                    game['status'] = 2
                g[str(g_code)] = game
                with open('games.json', 'w') as f:
                    dump(g, f, indent=4)
                return re({'success': 'The game was created', 'data': str(g_code)}, 200, a_e, a_n)

            if data['action'] == 'join':
                if a_n not in account_ns:
                    return re({'error': 'You do not have an account :105'}, 400, a_e, a_n)
                if data['code'] not in g.keys():
                    return re({'error': 'Game code is not valid :106'}, 400, a_e, a_n)
                if g[data['code']]['ended'] is not None:
                    return re({'error': 'This game does not exist anymore :107'}, 400, a_e, a_n)
                if g[data['code']]['status'] == 3:
                    return re({'error': 'You cannot join this game :116'}, 400, a_e, a_n)
                user_id = urlsafe_b64encode(sha256(int_to_bytes(signature[1]) + int_to_bytes(signature[2]))).decode()
                if user_id in g[data['code']]['banned_ids']:
                    return re({'error': 'You are banned from this game :108'}, 400, a_e, a_n)
                if len(g[data['code']]['players'].values()) >= g[data['code']]['max_players']:
                    return re({'error': 'Game is full :109'}, 400, a_e, a_n)
                g[data['code']]['players'][get_account_name(a_n)] = {'e': a_e, 'n': a_n}
                g[data['code']]['log'][str(time())] = {'action': 'join', 'player': get_account_name(a_n), 'data': ''}
                with open('games.json', 'w') as f:
                    dump(g, f, indent=4)
                return re({'success': 'You have joined this game'}, 200, a_e, a_n)

            if data['action'] == 'ban':
                if a_n not in account_ns:
                    return re({'error': 'You do not have an account :105'}, 400, a_e, a_n)
                if data['code'] not in g.keys():
                    return re({'error': 'Game code is not valid :106'}, 400, a_e, a_n)
                if g[data['code']]['ended'] is not None:
                    return re({'error': 'This game does not exist anymore :107'}, 400, a_e, a_n)
                if get_account_name(a_n) != g[data['code']]['host']:
                    return re({'error': 'You are not host :112'}, 400, a_e, a_n)
                if data['player'] not in g[data['code']]['players'].keys():
                    return re({'error': 'Player not found :110'}, 400, a_e, a_n)
                if not data['kick']:
                    g[data['code']]['banned_ids'].append(urlsafe_b64encode(sha256(int_to_bytes(signature[1]) +
                                                                                  int_to_bytes(signature[2]))).decode())
                del g[data['code']]['players'][data['player']]
                g[data['code']]['log'][str(time())] = {'action': 'disconnect', 'player': data['player'], 'data': 'ban'}
                with open('games.json', 'w') as f:
                    dump(g, f, indent=4)
                return re({'success': 'The player has been removed'}, 200, a_e, a_n)

            if data['action'] == 'disconnect':
                if a_n not in account_ns:
                    return re({'error': 'You do not have an account :105'}, 400, a_e, a_n)
                if data['code'] not in g.keys():
                    return re({'error': 'Game code is not valid :106'}, 400, a_e, a_n)
                if g[data['code']]['ended'] is not None:
                    return re({'error': 'This game does not exist anymore :107'}, 400, a_e, a_n)
                name = get_account_name(a_n)
                if name not in g[data['code']]['players']:
                    return re({'error': 'You are not part of this game :113'}, 400, a_e, a_n)
                if name == g[data['code']]['host']:
                    g[data['code']]['ended'] = time()
                del g[data['code']]['players'][name]
                g[data['code']]['log'][str(time())] = {'action': 'disconnect', 'player': name, 'data': 'left'}
                with open('games.json', 'w') as f:
                    dump(g, f, indent=4)
                return re({'success': 'You disconnected'}, 200, a_e, a_n)

            if data['action'] == 'status':
                if a_n not in account_ns:
                    return re({'error': 'You do not have an account :105'}, 400, a_e, a_n)
                if data['code'] not in g.keys():
                    return re({'error': 'Game code is not valid :106'}, 400, a_e, a_n)
                if g[data['code']]['ended'] is not None:
                    return re({'error': 'This game does not exist anymore :107'}, 400, a_e, a_n)
                if get_account_name(a_n) != g[data['code']]['host']:
                    return re({'error': 'You are not host :112'}, 400, a_e, a_n)
                if data['status'] < 1 or data['status'] > 3:
                    return re({'error': 'Invalid status :115'}, 400, a_e, a_n)
                g[data['code']]['status'] = data['status']
                g[data['code']]['log'][str(time())] = {'action': 'status', 'player': get_account_name(a_n),
                                                       'data': 'set to ' + ['public', 'private', 'not accessible']
                                                       [data['status'] - 1]}
                with open('games.json', 'w') as f:
                    dump(g, f, indent=4)
                return re({'success': 'The status was updated'}, 200, a_e, a_n)

            if data['action'] == 'message':
                if a_n not in account_ns:
                    return re({'error': 'You do not have an account :105'}, 400, a_e, a_n)
                if data['code'] not in g.keys():
                    return re({'error': 'Game code is not valid :106'}, 400, a_e, a_n)
                if g[data['code']]['ended'] is not None:
                    return re({'error': 'This game does not exist anymore :107'}, 400, a_e, a_n)
                if get_account_name(a_n) not in g[data['code']]['players'].keys():
                    return re({'error': 'You are not part of this game :113'}, 400, a_e, a_n)
                if len(data['message']) > 65536:
                    return re({'error': 'Message too long :116'}, 400, a_e, a_n)
                g[data['code']]['log'][str(time())] = {'action': 'status', 'player': get_account_name(a_n),
                                                       'data': data['message']}
                with open('games.json', 'w') as f:
                    dump(g, f, indent=4)
                return re({'success': 'The message was sent'}, 200, a_e, a_n)

            if data['action'] == 'log':
                if a_n not in account_ns:
                    return re({'error': 'You do not have an account :105'}, 400, a_e, a_n)
                if data['code'] not in g.keys():
                    return re({'error': 'Game code is not valid :106'}, 400, a_e, a_n)
                if g[data['code']]['ended'] is not None:
                    return re({'error': 'This game does not exist anymore :107'}, 400, a_e, a_n)
                if get_account_name(a_n) not in g[data['code']]['players'].keys():
                    return re({'error': 'You are not part of this game :113'}, 400, a_e, a_n)
                return re({'success': 'We sent the log to you', 'data': g[data['code']]['log']}, 200, a_e, a_n)

            if data['action'] == 'public':
                if a_n not in account_ns:
                    return re({'error': 'You do not have an account :105'}, 400, a_e, a_n)
                r = {}
                for i in g.keys():
                    if g[i]['status'] == 1 and data['game'] == g[i]['game'] and (g[i]['endend'] is not None):
                        r[i] = {'host': g[i]['host'], 'max_players': g[i]['max_players'],
                                'current_players': len(g[i]['players'].keys())}
                return re({'success': 'We sent a list of all public games to you', 'data': r}, 200, a_e, a_n)

            if data['action'] == 'player_list':
                if a_n not in account_ns:
                    return re({'error': 'You do not have an account :105'}, 400, a_e, a_n)
                if data['code'] not in g.keys():
                    return re({'error': 'Game code is not valid :106'}, 400, a_e, a_n)
                if g[data['code']]['ended'] is not None:
                    return re({'error': 'This game does not exist anymore :107'}, 400, a_e, a_n)
                if get_account_name(a_n) not in g[data['code']]['players'].keys():
                    return re({'error': 'You are not part of this game :113'}, 400, a_e, a_n)
                r = g[data['code']]['players']
                return re({'success': 'We sent a list of all players to you', 'data': r}, 200, a_e, a_n)

        except BaseException:
            return {'error': 'An unknown error occurred during the handling of your request :111', 'app': 'mmL-Game'}, 400
    else:
        return {'error': 'Request must be JSON :100', 'app': 'mmL-Game'}, 400


@app.errorhandler(405)
@app.errorhandler(404)
def error(f=None):
    return {'error': 'not found :404'}, 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8187, debug=False)
