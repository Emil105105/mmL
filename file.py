

NT_CONFIG = 'AppData/Local'
POSIX_CONFIG = '.config'
OTHER_CONFIG = 'config'

NT_APP = 'C:/Apps'
POSIX_APP = '/opt'
OTHER_APP = '/opt'

NT_PROGRAM = 'C:/Program Files'
POSIX_PROGRAM = '/usr/share'
OTHER_PROGRAM = '/usr/share'


def create_directories(absolute_path: str) -> None:
    """
    creates all parent directories

    :param absolute_path: absolute file path (including file)
    """
    from pathlib import Path as lib_Path
    from os.path import dirname
    lib_Path(dirname(absolute_path)).mkdir(parents=True, exist_ok=True)


def config_path(path: str) -> str:
    """
    get the absolute path of a config file

    :param path: the relative file path (WITHOUT the / at the start!)
    :return: the absolute path
    """
    from pathlib import Path as lib_Path
    from os import name as os_name
    from os.path import join as path_join
    p = str(str(lib_Path.home()).replace('\\', '/'))
    if os_name == 'posix':
        p = path_join(p, POSIX_CONFIG, path)
    elif os_name == 'nt':
        p = path_join(p, NT_CONFIG, path)
    else:
        p = path_join(p, OTHER_CONFIG, path)
    return p


def write_config(path: str, data: bytes) -> None:
    """
    write to a config file

    :param path: the relative file path (WITHOUT the / at the start!)
    :param data: Data bytes
    """
    p = config_path(path)
    create_directories(p)
    with open(p, 'wb') as f:
        f.write(data)


def read_config(path: str) -> bytes:
    """
    read a config file

    :param path: the relative file path (WITHOUT the / at the start!)
    :return: the contents of the file
    """
    p = config_path(path)
    create_directories(p)
    with open(p, 'rb') as f:
        data = f.read()
    return data


def app_path(path: str) -> str:
    """
    get the absolute path of an app file

    :param path: the relative file path (WITHOUT the / at the start!)
    :return: the absolute path
    """
    from pathlib import Path as lib_Path
    from os import name as os_name
    from os.path import join as path_join
    p = str(str(lib_Path.home()).replace('\\', '/'))
    if os_name == 'posix':
        p = path_join(p, POSIX_APP, path)
    elif os_name == 'nt':
        p = path_join(p, NT_APP, path)
    else:
        p = path_join(p, OTHER_APP, path)
    return p


def write_app(path: str, data: bytes) -> None:
    """
    write to an app file (this recommended over program because it doesn't require admin or root powers)

    :param path: the relative file path (WITHOUT the / at the start!)
    :param data: Data bytes
    """
    p = app_path(path)
    create_directories(p)
    with open(p, 'wb') as f:
        f.write(data)


def read_app(path: str) -> bytes:
    """
    read an app file

    :param path: the relative file path (WITHOUT the / at the start!)
    :return: the contents of the file
    """
    p = app_path(path)
    create_directories(p)
    with open(p, 'rb') as f:
        data = f.read()
    return data


def program_path(path: str) -> str:
    """
    get the absolute path of a program file

    :param path: the relative file path (WITHOUT the / at the start!)
    :return: the absolute path
    """
    from pathlib import Path as lib_Path
    from os import name as os_name
    from os.path import join as path_join
    p = str(str(lib_Path.home()).replace('\\', '/'))
    if os_name == 'posix':
        p = path_join(p, POSIX_PROGRAM, path)
    elif os_name == 'nt':
        p = path_join(p, NT_PROGRAM, path)
    else:
        p = path_join(p, OTHER_PROGRAM, path)
    return p


def write_program(path: str, data: bytes) -> None:
    """
    write to a program file (might require root or admin permissions)

    :param path: the relative file path (WITHOUT the / at the start!)
    :param data: Data bytes
    """
    p = program_path(path)
    create_directories(p)
    with open(p, 'wb') as f:
        f.write(data)


def read_program(path: str) -> bytes:
    """
    read a config file (might require root or admin permissions)

    :param path: the relative file path (WITHOUT the / at the start!)
    :return: the contents of the file
    """
    p = program_path(path)
    create_directories(p)
    with open(p, 'rb') as f:
        data = f.read()
    return data
