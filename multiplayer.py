import requests
from mencryption import rsa_fernet_encrypt, rsa_fernet_decrypt, rsa_fernet_signature
from base64 import urlsafe_b64encode, urlsafe_b64decode
from json import dumps, loads


server_list = {'192.168.1.134:8187/api/game': {'e': 150217567738312485551917130257762861258235221512867788713554770212038617340168087528169028306535620890890610233065984374537212185875523354794127504929468595269641670246418331678328590391097361240430243265600070863509974028879445579691519652569495170191345529602525246308630579553639444666996629696229254949571,
                                               'n': 16081851274739252063581690036118574640860532126091046929507122825565601083706274573750384634579337493839382544749514713758657208089245718294364937848858819453707226054549638124775135994036540198296573970847363611349877552574587070456877408396900133925515992713006187509898020472362199408053631005324416080783194439934892756914019290993005676543067987800962596545841898980290493349929842873911710030501545232149065036507008196661546963918563737317442450340605604636264642707617293716244057412875527656229847319434350987301204253787758529828164490026931498419587259261778923126349905750327786976931573098782899077143251}
               }


def _send_request(data: dict, e: int, d: int, n: int, server: str, server_e: int, server_n: int):
    encrypted_data = rsa_fernet_encrypt(dumps(data).encode(), server_e, server_n, e, d, n)

    try:
        r = requests.post('http://' + server, json={'data': urlsafe_b64encode(encrypted_data)}, verify=False)
    except Exception:
        raise ServerNotFound('could not connect to server: http://' + server)
    try:
        response = r.json()
    except Exception:
        raise ConnectionIssue('JSON could not be parsed')

    if 'app' not in response.keys():
        raise ServerNotFound(server + ' is not a mmL-Game server.')
    if response['app'] != 'mmL-Game':
        raise ServerNotFound(server + ' is not a mmL-Game server.')
    if 'error' in response.keys():
        raise ConnectionIssue(str(response['error']))
    if r.status_code != 200:
        raise ConnectionIssue('unknown error')

    try:
        decrypted = loads(rsa_fernet_decrypt(urlsafe_b64decode(response['data']), d, n).decode())
    except Exception:
        raise ConnectionIssue('could not decrypt message')

    if 'error' in decrypted.keys():
        raise ConnectionIssue(str(response['error']))

    signature = rsa_fernet_signature(response, d, n)

    if (not signature[0]) or server_e != signature[1] or server_n != signature[2]:
        raise ConnectionIssue('invalid signature')
    return decrypted['data']


def create_account(name: str, e: int, d: int, n: int, server: str = '188.63.49.183:8187/api/game', server_e: int = None, server_n: int = None) -> None:
    """
    Creates a new account. Can be used for all games on a server.

    :param name: preferred name (allowed characters: 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@.-_/äöüÄÖÜßàâéèêëœïîôùûç&'
    :param e: own RSA key
    :param d: own RSA key
    :param n: own RSA key
    :param server: IP-address (including port number) of the server
    :param server_e: public RSA key of the server (this may be None, if the server is on the list)
    :param server_n: public RSA key of the server (this may be None, if the server is on the list)
    """
    if (server_e is None) or (server_n is None):
        try:
            server_e = server_list[server]['e']
            server_n = server_list[server]['n']
        except Exception:
            raise ServerNotOnList()

    data = {'action': 'create_account', 'value': name}
    _send_request(data, e, d, n, server, server_e, server_n)


def get_game_list(game: str, e: int, d: int, n: int, server: str = '188.63.49.183:8187/api/game', server_e: int = None, server_n: int = None) -> dict:
    """
    Looks for public games.

    :param game: Name of the game which is played
    :param e: own RSA key
    :param d: own RSA key
    :param n: own RSA key
    :param server: IP-address (including port number) of the server
    :param server_e: public RSA key of the server (this may be None, if the server is on the list)
    :param server_n: public RSA key of the server (this may be None, if the server is on the list)
    :return: A dictionary with all games: {str('code'): {'current_players': int, 'max_players': int, 'host': str}}
    """
    if (server_e is None) or (server_n is None):
        try:
            server_e = server_list[server]['e']
            server_n = server_list[server]['n']
        except Exception:
            raise ServerNotOnList()

    data = {'action': 'public', 'game': game}
    return _send_request(data, e, d, n, server, server_e, server_n)


class Host:

    def __init__(self, game: str, e: int, d: int, n: int, max_players: int = 2, public: bool = True, banned_ids: list = None, server: str = '188.63.49.183:8187/api/game', server_e: int = None, server_n: int = None) -> None:
        """
        Creates a new multiplayer game.

        :param game: Defines which game is played
        :param e: own RSA key
        :param d: own RSA key
        :param n: own RSA key
        :param max_players: maximum number of players (including host)
        :param public: The game appears in the public game list
        :param banned_ids: List of banned players
        :param server: IP-Address (including port number) of the server
        :param server_e: public RSA key of the server (this may be None, if the server is on the list)
        :param server_n: public RSA key of the server (this may be None, if the server is on the list)
        """
        self.game = game
        self.e = e
        self.d = d
        self.n = n
        self.log_received = []
        self.server = server
        if (server_e is None) or (server_n is None):
            try:
                server_e = server_list[server]['e']
                server_n = server_list[server]['n']
            except Exception:
                raise ServerNotOnList()
        self.server_e = server_e
        self.server_n = server_n

        data = {'action': 'init', 'game': game, 'max_players': max_players, 'banned_ids': banned_ids, 'public': public}
        self.code = _send_request(data, e, d, n, server, server_e, server_n)

    def code(self) -> str:
        """
        This returns the access code for clients.

        :return: The game code: str('code')
        """
        return self.code

    def player_list(self) -> dict:
        """
        Returns a dictionary with all player IDs.

        :return: List of all players with ID: {str('account_name'): {e: int, n: int}}
        """
        data = {'action': 'player_list', 'code': self.code}
        return _send_request(data, self.e, self.d, self.n, self.server, self.server_e, self.server_n)

    def set_status(self, status: int) -> None:
        """
        Change the status of the game.
        Players that already have joined the game, will remain in the game.

        :param status: The new status of the game: 1. public; 2. private; 3. not accessible
        """
        data = {'action': 'status', 'code': self.code, 'status': status}
        _send_request(data, self.e, self.d, self.n, self.server, self.server_e, self.server_n)

    def latest_log(self) -> dict:
        """
        This returns a dictionary of all new events with time stamps.
        Example: {'192348715': {'action': 'disconnect', 'player': 'Jan_K', 'data': 'banned by Host'}}
        Possible values: {time: {'action': 'join/disconnect/message/status/init', 'player': 'Any', 'data': 'Any'}}

        :return: Dictionary of new events: {str('time'): {'action': str('action'), 'player': str('player_name'),
                 'data': str('data')}}
        """
        data = {'action': 'log', 'code': self.code}
        response = _send_request(data, self.e, self.d, self.n, self.server, self.server_e, self.server_n)

        new = response.keys()

        for i in range(len(self.log_received)):
            response.pop(self.log_received[i], None)

        self.log_received = new
        return response

    def log(self) -> dict:
        """
        This returns a dictionary of all events with time stamps.
        Example: {'192348715': {'action': 'disconnect', 'player': 'Jan_K', 'data': 'banned by Host'}}
        Possible values: {time: {'action': 'join/disconnect/message/status/init', 'player': 'Any', 'data': 'Any'}}

        :return: Dictionary of all events: {str('time'): {'action': str('action'), 'player': str('player_name'),
                 'data': str('data')}}
        """
        data = {'action': 'log', 'code': self.code}
        response = _send_request(data, self.e, self.d, self.n, self.server, self.server_e, self.server_n)

        self.log_received = response.keys()
        return response

    def ban(self, player_name: str, kick: bool = False) -> None:
        """
        This will remove the selected player from the game.

        :param player_name: The name of the player
        :param kick: Only kick player and not ban them
        """
        data = {'action': 'ban', 'player': player_name, 'kick': kick, 'code': self.code}
        _send_request(data, self.e, self.d, self.n, self.server, self.server_e, self.server_n)

    def message(self, data: bytes) -> None:
        """
        Sends a message to all players.

        :param data: Data string
        """
        d = {'action': 'message', 'code': self.code, 'message': urlsafe_b64encode(data).decode()}
        _send_request(d, self.e, self.d, self.n, self.server, self.server_e, self.server_n)

    def leave(self) -> None:
        """
        Ends the game session
        """
        data = {'action': 'disconnect', 'code': self.code}
        _send_request(data, self.e, self.d, self.n, self.server, self.server_e, self.server_n)


class Client:

    def __init__(self, game: str, e: int, d: int, n: int, code: str, server: str = '188.63.49.183:8187/api/game', server_e: int = None, server_n: int = None) -> None:
        """
        Joins a game.

        :param game: Name of the game which is played
        :param e: own RSA key
        :param d: own RSA key
        :param n: own RSA key
        :param code: the game code
        :param server: IP-Address (including port number) of the server
        :param server_e: public RSA key of the server (this may be None, if the server is on the list)
        :param server_n: public RSA key of the server (this may be None, if the server is on the list)
        """
        self.game = game
        self.code = code
        self.e = e
        self.d = d
        self.n = n
        self.log_received = []
        self.server = server
        if (server_e is None) or (server_n is None):
            try:
                server_e = server_list[server]['e']
                server_n = server_list[server]['n']
            except Exception:
                raise ServerNotOnList()
        self.server_e = server_e
        self.server_n = server_n
        data = {'action': 'join', 'code': code}
        self.code = _send_request(data, e, d, n, server, server_e, server_n)

    def latest_log(self) -> dict:
        """
        This returns a dictionary of all new events with time stamps.
        Example: {'192348715': {'action': 'disconnect', 'player': 'Jan_K', 'data': 'banned by Host'}}
        Possible values: {time: {'action': 'join/disconnect/message/status/init', 'player': 'Any', 'data': 'Any'}}

        :return: Dictionary of new events: {str('time'): {'action': str('action'), 'player': str('player_name'),
                 'data': str('data')}}
        """
        data = {'action': 'log', 'code': self.code}
        response = _send_request(data, self.e, self.d, self.n, self.server, self.server_e, self.server_n)

        new = response.keys()

        for i in range(len(self.log_received)):
            response.pop(self.log_received[i], None)

        self.log_received = new
        return response

    def log(self) -> dict:
        """
        This returns a dictionary of all events with time stamps.
        Example: {'192348715': {'action': 'disconnect', 'player': 'Jan_K', 'data': 'banned by Host'}}
        Possible values: {time: {'action': 'join/disconnect/message/status/init', 'player': 'Any', 'data': 'Any'}}

        :return: Dictionary of all events: {str('time'): {'action': str('action'), 'player': str('player_name'),
                 'data': str('data')}}
        """
        data = {'action': 'log', 'code': self.code}
        response = _send_request(data, self.e, self.d, self.n, self.server, self.server_e, self.server_n)

        self.log_received = response.keys()
        return response

    def player_list(self) -> dict:
        """
        Returns a dictionary with all player IDs

        :return: List of all players with ID: {str('account_name'): {e: int, n: int}}
        """
        data = {'action': 'player_list', 'code': self.code}
        return _send_request(data, self.e, self.d, self.n, self.server, self.server_e, self.server_n)

    def message(self, data: bytes) -> None:
        """
        Sends a message to all players.

        :param data: Data string
        """
        d = {'action': 'message', 'code': self.code, 'message': urlsafe_b64encode(data).decode()}
        _send_request(d, self.e, self.d, self.n, self.server, self.server_e, self.server_n)

    def leave(self) -> None:
        """
        Ends the game session
        """
        data = {'action': 'disconnect', 'code': self.code}
        _send_request(data, self.e, self.d, self.n, self.server, self.server_e, self.server_n)


class MultiplayerError(Exception):
    """Base exception for other exceptions"""
    pass


class NameContainsIllegalCharacters(MultiplayerError):
    """Raised if the preferred name contains illegal characters"""
    pass


class NameIsInUse(MultiplayerError):
    """Raised if the preferred name is already in use"""
    pass


class TimedOut(MultiplayerError):
    """Raised if you didn't respond for a certain time"""
    pass


class Banned(MultiplayerError):
    """Raised if you got banned from a game"""
    pass


class GameEnded(MultiplayerError):
    """Raised if the game has ended"""
    pass


class NoAccount(MultiplayerError):
    """Raised if you don't have an account"""
    pass


class InvalidGameCode(MultiplayerError):
    """Raised if the code is invalid"""
    pass


class ConnectionIssue(MultiplayerError):
    """Base exception for all connection related issues and errors"""


class ServerNotFound(ConnectionIssue):
    """Raised if no connection could be established"""
    pass


class ServerNotOnList(ConnectionIssue):
    """Raised if the cryptographic keys are missing"""



