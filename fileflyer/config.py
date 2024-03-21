from os import makedirs
from os.path import join, exists, expanduser
import configparser
import json

_root = expanduser('~/.config/fileflyer')
exists(_root) or makedirs(_root)

_config = None

CONFIG_FILE = join(_root, 'config')

_SECTION_GITHUB = 'Github'

def _load_config():
    global _config

    if _config is None:
        _config = configparser.ConfigParser()

        if exists(CONFIG_FILE):
            _config.read(CONFIG_FILE)
        else:
            _config.add_section(_SECTION_GITHUB)
            _config.set(_SECTION_GITHUB, 'remote', '')
            _config.set(_SECTION_GITHUB, 'local', '')
            _config.set(_SECTION_GITHUB, 'token', '')

            with open(CONFIG_FILE, 'wb') as f:
                _config.write(f)

    return _config

def pretty_json_string(dic):
    return json.dumps(dic, sort_keys=True, indent=4)

def get_raw_config():
    output = ''
    config = _load_config()

    for section in config.sections():
        output += '%s: \n' % section
        output += pretty_json_string(dict(config.items(section)))
        output += '\n\n'

    output += 'PATH: %s' % CONFIG_FILE

    return output

def get_repo_url():
    return _load_config().get(_SECTION_GITHUB, 'remote')

def get_repo_path():
    return _load_config().get(_SECTION_GITHUB, 'local')

def get_repo_token():
    return _load_config().get(_SECTION_GITHUB, 'token')
