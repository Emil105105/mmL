from flask import Flask
from mencryption import rsa_fernet_encrypt, rsa_fernet_decrypt, generate_rsa_keys, rsa_fernet_signature
from base64 import urlsafe_b64encode, urlsafe_b64decode
from os.path import exists
from json import dump, load
from time import time
from mrandom import randint_except
from ast import literal_eval

#
# import os
# import logging
#
# logging.getLogger('werkzeug').disabled = True
# os.environ['WERKZEUG_RUN_MAIN'] = 'true'
#

_legal_characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@.-_/äöüÄÖÜßàâéèêëËœïîôùûçÇ&'
_provider = 'Martin Merkli <martin.merkli@protonmail.com>'
_privacy = 'We do NOT send any data about our users to any third party. You can contact us via e-mail <martin.merkli@' \
           'protonmail.com> about concerns and requests about deleting your account. We collect the following data ab' \
           'out you: Account name and public keys. Your IP-address and requested resource will be visible in the cons' \
           'ole of our server, but we do not save that. Messages in games will be deleted after a few days.'
_illegal_names = ['admin', 'martin', 'martinmerkli', 'martinsmerkli', 'martin.merkli']

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

if not exists('accounts.json'):
    a = {}
    with open('accounts.json', 'w') as _f:
        dump(a, _f, indent=4)
else:
    with open('accounts.json', 'r') as _f:
        a = load(_f)

g = {}


def log(x):
    print(x)


def get_account_name(rsa_n):
    global a
    for i in a.keys():
        if a[i]['n'] == rsa_n:
            return i
    return None


def decode(cipher):
    global d, n
    return rsa_fernet_decrypt(urlsafe_b64decode(cipher), d, n).decode()


def get_sender(cipher):
    global d, n
    signature = rsa_fernet_signature(urlsafe_b64decode(cipher), d, n)
    return signature[1], signature[2]


def re(data, p_e, p_n):
    return urlsafe_b64encode(rsa_fernet_encrypt(data.encode(), p_e, p_n, e, d, n)).decode()


class MultiGame:

    def __init__(self, host, max_players, h_e, h_n, banned_ids, game, public):
        self.host = host
        self.max_players = max_players
        self.players = {host: {'e': h_e, 'n': h_n}}
        self.banned_ids = banned_ids
        self.game = game
        self.created = time()
        self.log = {str(self.created): {'action': 'init', 'player': get_account_name(h_n), 'data': ''}}
        self.ended = None
        if public:
            self.status = 1
        else:
            self.status = 2

    def has_ended(self):
        return not (self.ended is None)

    def is_running(self):
        return self.ended is None

    def is_banned(self, p_n):
        return p_n in self.banned_ids

    def is_part(self, player):
        return player in self.players

    def is_host(self, player):
        return player == self.host

    def is_game(self, game):
        return game == self.game

    def is_public_game(self, game):
        return self.status == 1 and self.game == game and self.is_running()

    def is_open(self):
        return self.status < 3 and self.is_running()

    def is_full(self):
        return self.max_players <= len(self.players) and self.is_running()

    def join(self, p_e, p_n):
        self.log[str(time())] = {'action': 'join', 'player': get_account_name(p_n), 'data': ''}
        self.players[get_account_name(p_n)] = {'e': p_e, 'n': p_n}

    def leave(self, p_n):
        self.log[str(time())] = {'action': 'disconnect', 'player': get_account_name(p_n), 'data': 'disconnected'}
        del self.players[get_account_name(p_n)]
        if get_account_name(p_n) == self.host:
            self.ended = time()
            self.status = 3

    def message(self, p_n, data):
        self.log[str(time())] = {'action': 'message', 'player': get_account_name(p_n), 'data': data}

    def ban(self, player, reason):
        self.log[str(time())] = {'action': 'disconnect', 'player': player, 'data': 'Banned by host due to ' + reason}
        p_n = self.players[player]['n']
        del self.players[player]
        self.banned_ids.append(p_n)

    def kick(self, player, reason):
        self.log[str(time())] = {'action': 'disconnect', 'player': player, 'data': 'Kicked by host due to ' + reason}
        del self.players[player]

    def set_status(self, new_status):
        self.log[str(time())] = {'action': 'disconnect', 'player': self.host, 'data': 'set to ' + str(new_status)}
        self.status = new_status

    def get(self, admin=False):
        r = {'players': self.players, 'log': self.log, 'host': self.host, 'max_players': self.max_players,
             'game': self.game, 'status': self.status, 'created': self.created}
        if admin:
            r['ended'] = self.ended
            r['banned_ids'] = self.banned_ids
        return r

    def get_messages(self):
        r = {}
        for i in self.log:
            if self.log[i]['action'] == 'message':
                r[i] = self.log[i]
        return r

    def get_public(self, game):
        if (not self.is_public_game(game)) or self.is_full() or self.has_ended():
            return None
        else:
            return {'current_players': len(self.players), 'host': self.host, 'max_players': self.max_players}


@app.route('/api/game/about', methods=['GET'])
def handler_0():
    global _privacy, _provider, e, n
    return {'Creator': 'Martin Merkli <https://github.com/Emil105105>',
            'License': 'https://unlicense.org/',
            'app': 'mmL-GameServer',
            'Privacy_Policy': _privacy,
            'Provider': _provider,
            'e': e, 'n': n}, 200


@app.route('/api/game/create_account/<cipher>', methods=['GET'])
def handler_1(cipher):
    global a, _legal_characters, _illegal_names
    log({'cipher': cipher})
    try:
        data = decode(cipher)
        p_e, p_n = get_sender(cipher)
    except KeyboardInterrupt:
        return {'error': 'could not decode your request', 'code': 2}, 400
    log({'data': data, 'p_e': p_e, 'p_n': p_n})
    if len(data) < 2:
        return {'error': 'name is too short', 'code': 100}, 400
    if len(data) > 32:
        return {'error': 'name is too long', 'code': 101}, 400
    if get_account_name(p_n) is not None:
        return {'error': 'you already have an account', 'code': 102}
    for i in range(len(data)):
        if data[i] not in _legal_characters:
            return {'error': 'name contains illegal characters', 'code': 103}, 400
    if data.lower() in _illegal_names:
        return {'error': 'name is already in use', 'code': 104}, 400
    if data in a.keys():
        return {'error': 'name is already in use', 'code': 104}, 400
    a[data] = {'e': p_e, 'n': p_n}
    with open('accounts.json', 'w') as f:
        dump(a, f, indent=4)
    log({'a': a})
    return {'success': 'Your account was created', 'e': p_e, 'n': p_n, 'name': re(data, p_e, p_n)}, 200


@app.route('/api/game/init/<cipher>', methods=['GET'])
def handler_2(cipher):
    # game\max_players\[banned_ids]\public[0/1]
    try:
        data = decode(cipher).split('\\')
        p_e, p_n = get_sender(cipher)
    except Exception:
        return {'error': 'could not decode your request', 'code': 2}, 400
    if get_account_name(p_n) is None:
        return {'error': 'you do not have an account', 'code': 10}, 400
    if len(data) != 4:
        return {'error': 'too few or too many parameters', 'code': 105}, 400
    if len(data[0]) < 2 or len(data[0]) > 32:
        return {'error': 'too long or too short game name', 'code': 106}, 400
    try:
        max_players = int(data[1])
    except Exception:
        return {'error': 'max_players is not an integer', 'code': 107}, 400
    if max_players < 2 or max_players > 32:
        return {'error': 'number of maximum players not supported', 'code': 108}, 400
    try:
        banned_ids = literal_eval(data[2])
    except Exception:
        return {'error': 'banned_ids is not a list', 'code': 109}, 400
    if not isinstance(banned_ids, list):
        return {'error': 'banned_ids is not a list', 'code': 109}, 400
    if data[3] == '0':
        public = False
    elif data[3] == '1':
        public = True
    else:
        return {'error': 'public is neither 0 nor 1', 'code': 110}, 400
    used_codes = [int(i) for i in g.keys()]
    code = str(randint_except(100000, 999999, used_codes))
    g[code] = MultiGame(get_account_name(p_n), max_players, p_e, p_n, banned_ids, data[0], public)
    log({'g': g})
    return {'success': 'The game was created', '_code': re(code, p_e, p_n)}, 200


@app.route('/api/game/join/<cipher>', methods=['GET'])
def handler_3(cipher):
    try:
        data = decode(cipher)
        p_e, p_n = get_sender(cipher)
    except Exception:
        return {'error': 'could not decode your request', 'code': 2}, 400
    name = get_account_name(p_n)
    if name is None:
        return {'error': 'you do not have an account', 'code': 10}, 400
    if data not in g:
        return {'error': 'invalid game code', 'code': 111}, 400
    if not g[data].is_open():
        return {'error': 'game is not accessible', 'code': 112}, 400
    if g[data].is_banned(p_n):
        return {'error': 'you are banned from this game', 'code': 113}, 400
    if g[data].is_part(name):
        return {'error': 'you have already joined this game', 'code': 114}, 400
    if g[data].has_ended():
        return {'error': 'the game has already ended', 'code': 115}, 400
    if g[data].is_full():
        return {'error': 'the game is full', 'code': 117}, 400
    g[data].join(p_e, p_n)
    return {'success': 'you are now part of this game', '_code': re(data, p_e, p_n)}, 200


@app.route('/api/game/disconnect/<cipher>', methods=['GET'])
def handler_4(cipher):
    try:
        data = decode(cipher)
        p_e, p_n = get_sender(cipher)
    except Exception:
        return {'error': 'could not decode your request', 'code': 2}, 400
    name = get_account_name(p_n)
    if name is None:
        return {'error': 'you do not have an account', 'code': 10}, 400
    if data not in g:
        return {'error': 'invalid game code', 'code': 111}, 400
    if g[data].has_ended():
        return {'error': 'the game has already ended', 'code': 115}, 400
    if not g[data].is_part(name):
        return {'error': 'you are not part of this game', 'code': 116}, 400
    g[data].leave(p_n)
    return {'success': 'you left the game', 'host': g[data].is_host(name), '_code': re(data, p_e, p_n)}, 200


@app.route('/api/game/kick/<cipher>', methods=['GET'])
def handler_5(cipher):
    # game\name\ban[0/1]\reason
    try:
        data = decode(cipher).split('\\')
        p_e, p_n = get_sender(cipher)
    except Exception:
        return {'error': 'could not decode your request', 'code': 2}, 400
    name = get_account_name(p_n)
    if name is None:
        return {'error': 'you do not have an account', 'code': 10}, 400
    if len(data) != 4:
        return {'error': 'too few or too many parameters', 'code': 105}, 400
    if data[0] not in g:
        return {'error': 'invalid game code', 'code': 111}, 400
    if g[data[0]].has_ended():
        return {'error': 'the game has already ended', 'code': 115}, 400
    if not g[data[0]].is_part(name):
        return {'error': 'you are not part of this game', 'code': 116}, 400
    if not g[data[0]].is_host(name):
        return {'error': 'you are not host', 'code': 118}, 400
    if not g[data[0]].is_part(data[1]):
        return {'error': 'player is not part of this game', 'code': 119}, 400
    if name == data[1]:
        return {'error': 'you cannot kick yourself', 'code': 120}, 400
    if len(data[3]) > 64:
        return {'error': 'reason is too long', 'code': 121}, 400
    if data[2] == '0':
        g[data[0]].kick(data[1], data[3])
    elif data[2] == '1':
        g[data[0]].kick(data[1], data[3])
    else:
        return {'error': 'ban is neither 0 nor 1', 'code': 122}, 400
    return {'success': 'the player got kicked', 'player': re(data[1], p_e, p_n)}, 200


@app.route('/api/game/status/<cipher>', methods=['GET'])
def handler_6(cipher):
    # game\status[1/2/3]
    try:
        data = decode(cipher).split('\\')
        p_e, p_n = get_sender(cipher)
    except Exception:
        return {'error': 'could not decode your request', 'code': 2}, 400
    name = get_account_name(p_n)
    if name is None:
        return {'error': 'you do not have an account', 'code': 10}, 400
    if len(data) != 2:
        return {'error': 'too few or too many parameters', 'code': 105}, 400
    if data[0] not in g:
        return {'error': 'invalid game code', 'code': 111}, 400
    if g[data[0]].has_ended():
        return {'error': 'the game has already ended', 'code': 115}, 400
    if not g[data[0]].is_part(name):
        return {'error': 'you are not part of this game', 'code': 116}, 400
    if not g[data[0]].is_host(name):
        return {'error': 'you are not host', 'code': 118}, 400
    try:
        status = int(data[1])
    except Exception:
        return {'error': 'status is not an integer', 'code': 123}, 400
    if status < 1 or status > 3:
        return {'error': 'status is not supported', 'code': 124}, 400
    g[data[0]].set_status(status)
    return {'success': 'the status was updated', 'status': re(data[1], p_e, p_n)}, 200


@app.route('/api/game/message/<cipher>', methods=['GET'])
def handler_7(cipher):
    # game\message
    try:
        data = decode(cipher).split('\\')
        p_e, p_n = get_sender(cipher)
    except Exception:
        return {'error': 'could not decode your request', 'code': 2}, 400
    name = get_account_name(p_n)
    if name is None:
        return {'error': 'you do not have an account', 'code': 10}, 400
    if len(data) != 2:
        return {'error': 'too few or too many parameters', 'code': 105}, 400
    if data[0] not in g:
        return {'error': 'invalid game code', 'code': 111}, 400
    if g[data[0]].has_ended():
        return {'error': 'the game has already ended', 'code': 115}, 400
    if not g[data[0]].is_part(name):
        return {'error': 'you are not part of this game', 'code': 116}, 400
    if len(data) < 1 or len(data) > 65535:
        return {'error': 'message is too long or too short', 'code': 125}, 400
    g[data[0]].message(p_n, data)
    return {'success': 'the message was sent'}, 200


@app.route('/api/game/info/<cipher>', methods=['GET'])
def handler_8(cipher):
    try:
        data = decode(cipher)
        p_e, p_n = get_sender(cipher)
    except Exception:
        return {'error': 'could not decode your request', 'code': 2}, 400
    log({'data': data, 'g': g, 'p_e': p_e, 'p_n': p_n})
    name = get_account_name(p_n)
    if name is None:
        return {'error': 'you do not have an account', 'code': 10}, 400
    if data not in g:
        return {'error': 'invalid game code', 'code': 111}, 400
    if g[data].has_ended():
        return {'error': 'the game has already ended', 'code': 115}, 400
    if not g[data].is_part(name):
        return {'error': 'you are not part of this game', 'code': 116}, 400
    return g[data].get(admin=False)


@app.route('/api/game/receive/<cipher>', methods=['GET'])
def handler_9(cipher):
    try:
        data = decode(cipher)
        p_e, p_n = get_sender(cipher)
    except Exception:
        return {'error': 'could not decode your request', 'code': 2}, 400
    name = get_account_name(p_n)
    if name is None:
        return {'error': 'you do not have an account', 'code': 10}, 400
    if data not in g:
        return {'error': 'invalid game code', 'code': 111}, 400
    if g[data].has_ended():
        return {'error': 'the game has already ended', 'code': 115}, 400
    if not g[data].is_part(name):
        return {'error': 'you are not part of this game', 'code': 116}, 400
    return g[data].get_messages()


@app.route('/api/game/public/<cipher>', methods=['GET'])
def handler_10(cipher):
    try:
        data = decode(cipher)
        p_e, p_n = get_sender(cipher)
    except Exception:
        return {'error': 'could not decode your request', 'code': 2}, 400
    name = get_account_name(p_n)
    if name is None:
        return {'error': 'you do not have an account', 'code': 10}, 400
    r = {}
    for i in g.keys():
        info = g[i].get_public(data)
        if info is None:
            pass
        else:
            r[i] = info
    return r


@app.errorhandler(405)
@app.errorhandler(404)
def handler_e(_):
    return {'error': '404 not found'}, 404


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=8187, debug=False)
    except KeyboardInterrupt:
        pass
