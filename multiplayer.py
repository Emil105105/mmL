

server_list = {'192.168.1.134:8187/api/game': {'e': 150217567738312485551917130257762861258235221512867788713554770212038617340168087528169028306535620890890610233065984374537212185875523354794127504929468595269641670246418331678328590391097361240430243265600070863509974028879445579691519652569495170191345529602525246308630579553639444666996629696229254949571,
                                               'n': 16081851274739252063581690036118574640860532126091046929507122825565601083706274573750384634579337493839382544749514713758657208089245718294364937848858819453707226054549638124775135994036540198296573970847363611349877552574587070456877408396900133925515992713006187509898020472362199408053631005324416080783194439934892756914019290993005676543067987800962596545841898980290493349929842873911710030501545232149065036507008196661546963918563737317442450340605604636264642707617293716244057412875527656229847319434350987301204253787758529828164490026931498419587259261778923126349905750327786976931573098782899077143251},
               '127.0.0.1:8187/api/game': {'e': 150217567738312485551917130257762861258235221512867788713554770212038617340168087528169028306535620890890610233065984374537212185875523354794127504929468595269641670246418331678328590391097361240430243265600070863509974028879445579691519652569495170191345529602525246308630579553639444666996629696229254949571,
                                           'n': 16081851274739252063581690036118574640860532126091046929507122825565601083706274573750384634579337493839382544749514713758657208089245718294364937848858819453707226054549638124775135994036540198296573970847363611349877552574587070456877408396900133925515992713006187509898020472362199408053631005324416080783194439934892756914019290993005676543067987800962596545841898980290493349929842873911710030501545232149065036507008196661546963918563737317442450340605604636264642707617293716244057412875527656229847319434350987301204253787758529828164490026931498419587259261778923126349905750327786976931573098782899077143251}
               }


def check_server(server: str):
    import requests
    try:
        r = requests.get('http://' + server + '/about')
    except Exception:
        return False
    if r.status_code != 200:
        return False
    if r.json()['app'] != 'mmL-GameServer':
        return False
    return True


def get_server_keys(server: str):
    import requests
    try:
        r = requests.get('http://' + server + '/about')
        response = r.json()
    except Exception:
        raise ConnectionIssue()
    if r.status_code != 200:
        raise ConnectionIssue()
    if ('e' not in response) or ('n' not in response):
        raise ConnectionIssue()
    return {'e': response['e'], 'n': response['n']}


def _decode(cipher, d, n):
    try:
        from mencryption import rsa_fernet_decrypt
    except ModuleNotFoundError:
        from mmL.mencryption import rsa_fernet_decrypt
    from base64 import urlsafe_b64decode
    return rsa_fernet_decrypt(urlsafe_b64decode(cipher), d, n).decode()


def _send_request(data: str, e: int, d: int, n: int, server: str, server_e: int, server_n: int, action: str):
    import requests
    try:
        from mencryption import rsa_fernet_encrypt
    except ModuleNotFoundError:
        from mmL.mencryption import rsa_fernet_encrypt
    from base64 import urlsafe_b64encode
    try:
        encrypted = urlsafe_b64encode(rsa_fernet_encrypt(data.encode(), server_e, server_n, e, d, n)).decode()
    except Exception:
        raise EncryptionError()

    try:
        r = requests.get('http://' + server + action + '/' + encrypted)
        response = r.json()
    except Exception:
        raise ConnectionIssue()

    if 'error' in response:
        if 'code' in response:
            if response['code'] == 2:
                raise EncryptionError()
            elif response['code'] == 10:
                raise NoAccount()
            elif response['code'] in [100, 101]:
                raise NameIsInvalid()
            elif response['code'] == 102:
                raise AccountExists()
            elif response['code'] == 103:
                raise NameContainsIllegalCharacters()
            elif response['code'] == 104:
                raise NameIsInUse()
            elif response['code'] == 106:
                raise GameNotSupported()
            elif response['code'] == 108:
                raise MaxPlayersNotSupported()
            elif response['code'] == 111:
                raise InvalidGameCode()
            elif response['code'] == 112:
                raise GameNotAccessible()
            elif response['code'] == 113:
                raise Banned()
            elif response['code'] == 114:
                raise AlreadyJoined()
            elif response['code'] == 115:
                raise GameEnded()
            elif response['code'] == 116:
                raise NotPart()
            elif response['code'] == 117:
                raise GameIsFull()
            elif response['code'] == 119:
                raise CannotBanPlayer()
            elif response['code'] == 120:
                raise BanYourself()
            elif response['code'] == 121:
                raise ReasonTooLong()
            elif response['code'] == 125:
                raise InvalidMessage()
            else:
                raise MultiplayerError()
        else:
            raise ConnectionIssue()
    elif r.status_code == 500:
        raise MultiplayerError()
    elif r.status_code in [404, 405]:
        raise ConnectionIssue()
    elif r.status_code != 200:
        raise ConnectionIssue()
    else:
        return response


def create_account(name: str, e: int, d: int, n: int, server: str = '188.63.49.183:8187/api/game', server_e: int = None, server_n: int = None) -> None:
    """
    Creates a new account. Can be used for all games on a server.

    :param name: preferred name (allowed characters: 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@.-_/äöüÄÖÜßàâéèêëœïîôùûç&')
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

    _send_request(name, e, d, n, server, server_e, server_n, '/create_account')


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

    return _send_request(game, e, d, n, server, server_e, server_n, '/public')


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
        self.server = server

        self.received = []

        if (server_e is None) or (server_n is None):
            try:
                server_e = server_list[server]['e']
                server_n = server_list[server]['n']
            except Exception:
                raise ServerNotOnList()
        self.server_e = server_e
        self.server_n = server_n

        if banned_ids is None:
            banned_ids = []

        request = game + '\\' + str(max_players) + '\\' + str(banned_ids) + '\\' + str(int(public))
        self.code = _decode(_send_request(request, e, d, n, server, server_e, server_n, '/init')['_code'], d, n)

    def get_code(self) -> str:
        """
        This returns the access code for clients.

        :return: The game code: str('code')
        """
        return self.code

    def set_status(self, status: int) -> None:
        """
        Change the status of the game.
        Players that already have joined the game, will remain in the game.

        :param status: The new status of the game: 1. public; 2. private; 3. not accessible
        """
        _send_request(self.code + '\\' + str(status), self.e, self.d, self.n, self.server, self.server_e, self.server_n, '/status')

    def info(self) -> dict:
        """
        Get info about the game. For example:
        {'players': dict, 'log': dict, 'host': str, 'max_players': int, 'game': str, 'status': int, 'created': float}

        :return: A dictionary with all information
        """
        return _send_request(self.code, self.e, self.d, self.n, self.server, self.server_e, self.server_n, '/info')

    def get_messages(self) -> dict:
        """
        Get a dictionary with the latest messages.

        :return: A dictionary with the latest messages
        """
        from base64 import urlsafe_b64decode
        msg = _send_request(self.code, self.e, self.d, self.n, self.server, self.server_e, self.server_n, '/receive')

        r = {}
        for i in list(msg.keys()):
            if i in self.received:
                pass
            else:
                r[i] = urlsafe_b64decode(msg[i]['data'])

        self.received = list(msg.keys())

        return r

    def ban(self, player_name: str, reason: str = 'banned by the host', kick: bool = False) -> None:
        """
        This will remove the selected player from the game.

        :param player_name: The name of the player
        :param reason: Reason for the ban (or kick)
        :param kick: Only kick player and not ban them
        """
        if kick:
            data = '0'
        else:
            data = '1'
        _send_request(self.code + '\\' + player_name + '\\' + data + '\\' + reason, self.e, self.d, self.n, self.server, self.server_e, self.server_n, '/kick')

    def message(self, data: bytes) -> None:
        """
        Sends a message to all players.

        :param data: Data string
        """
        from base64 import urlsafe_b64encode
        _send_request(self.code + '\\' + urlsafe_b64encode(data).decode(), self.e, self.d, self.n, self.server, self.server_e, self.server_n, '/message')

    def leave(self) -> None:
        """
        Ends the game session
        """
        _send_request(self.code, self.e, self.d, self.n, self.server, self.server_e, self.server_n, '/disconnect')


class Client:

    def __init__(self, e: int, d: int, n: int, code: str, server: str = '188.63.49.183:8187/api/game', server_e: int = None, server_n: int = None) -> None:
        """
        Joins a game.

        :param e: own RSA key
        :param d: own RSA key
        :param n: own RSA key
        :param code: the game code
        :param server: IP-Address (including port number) of the server
        :param server_e: public RSA key of the server (this may be None, if the server is on the list)
        :param server_n: public RSA key of the server (this may be None, if the server is on the list)
        """
        self.code = code
        self.e = e
        self.d = d
        self.n = n
        self.server = server

        self.received = []

        if (server_e is None) or (server_n is None):
            try:
                server_e = server_list[server]['e']
                server_n = server_list[server]['n']
            except Exception:
                raise ServerNotOnList()

        self.server_e = server_e
        self.server_n = server_n

        _send_request(code, e, d, n, server, server_e, server_n, '/join')

    def info(self) -> dict:
        """
        Get info about the game. For example:
        {'players': dict, 'log': dict, 'host': str, 'max_players': int, 'game': str, 'status': int, 'created': float}

        :return: A dictionary with all information
        """
        return _send_request(self.code, self.e, self.d, self.n, self.server, self.server_e, self.server_n, '/info')

    def get_messages(self) -> dict:
        """
        Get a dictionary with the latest messages.

        :return: A dictionary with the latest messages
        """
        from base64 import urlsafe_b64decode
        msg = _send_request(self.code, self.e, self.d, self.n, self.server, self.server_e, self.server_n, '/receive')

        r = {}
        for i in list(msg.keys()):
            if i in self.received:
                pass
            else:
                r[i] = urlsafe_b64decode(msg[i]['data'])

        self.received = list(msg.keys())

        return r

    def message(self, data: bytes) -> None:
        """
        Sends a message to all players.

        :param data: Data string
        """
        from base64 import urlsafe_b64encode
        _send_request(self.code + '\\' + urlsafe_b64encode(data).decode(), self.e, self.d, self.n, self.server,
                      self.server_e, self.server_n, '/info')

    def leave(self) -> None:
        """
        Ends the game session
        """
        _send_request(self.code, self.e, self.d, self.n, self.server, self.server_e, self.server_n, '/disconnect')


class MultiplayerError(Exception):
    """Base exception for other exceptions"""
    pass


class NameIsInvalid(MultiplayerError):
    """Raised if the preferred name is invalid"""
    pass


class AccountExists(MultiplayerError):
    """Raised if you already have an account"""
    pass


class NameContainsIllegalCharacters(MultiplayerError):
    """Raised if the preferred name contains illegal characters"""
    pass


class NameIsInUse(MultiplayerError):
    """Raised if the preferred name is already in use"""
    pass


class NoAccount(MultiplayerError):
    """Raised if you don't have an account"""
    pass


class GameNotSupported(MultiplayerError):
    """Raised if the name of the game is either too long or too short"""
    pass


class MaxPlayersNotSupported(MultiplayerError):
    """Raised if max_players is out of reach"""
    pass


class InvalidGameCode(MultiplayerError):
    """Raised if the code is invalid"""
    pass


class GameNotAccessible(MultiplayerError):
    """Raised if the game is not accessible"""
    pass


class Banned(MultiplayerError):
    """Raised if you got banned from a game"""
    pass


class AlreadyJoined(MultiplayerError):
    """Raised if you already have joined this game"""
    pass


class GameEnded(MultiplayerError):
    """Raised if the game has ended"""
    pass


class NotPart(MultiplayerError):
    """Raised if you are not part of the game"""
    pass


class GameIsFull(MultiplayerError):
    """Raised if the maximum number of players is reached"""
    pass


class CannotBanPlayer(MultiplayerError):
    """Raised if you tried to ban a player which is not in the game"""
    pass


class BanYourself(MultiplayerError):
    """Raised if you tried to ban yourself"""
    pass


class ReasonTooLong(MultiplayerError):
    """Raised if the reason is too long"""
    pass


class InvalidMessage(MultiplayerError):
    """Raised if the message is too long or too short"""
    pass


class ConnectionIssue(MultiplayerError):
    """Base exception for all connection related issues and errors"""
    pass


class ServerNotFound(ConnectionIssue):
    """Raised if no connection could be established"""
    pass


class ServerNotOnList(ConnectionIssue):
    """Raised if the cryptographic keys are missing"""
    pass


class EncryptionError(ConnectionIssue):
    """Raised if the encryption or decryption was not possible"""
    pass

