from os import makedirs
from os.path import join, exists, expanduser, realpath
import yaml
import json

_root = expanduser('~/.config/fileflyer')
exists(_root) or makedirs(_root)

_config = None

CONFIG_FILE = join(_root, 'config.yaml')

_SECTION_GITHUB = 'github'
_SECTION_FOLDERS = 'folders'

def _load_config():
    global _config

    if _config is not None:
        return _config

    if exists(CONFIG_FILE):
        with open(CONFIG_FILE) as file:
            _config = yaml.load(file, Loader=yaml.FullLoader)
    else:
        _config = {
            _SECTION_GITHUB: {
                'url': 'https://github.com/username/repo-name',
                'remote': 'origin',
                'path': '/local/path/to/repo',
                'branch': 'master',
                'token': '',
            },
            _SECTION_FOLDERS: {
                'default': {
                    'format': 'files/{date}/{XXXXXXXX}'
                }
            }
        }

        with open(CONFIG_FILE, 'w') as file:
            yaml.dump(_config, file)

    return _config

def pretty_json_string(dic):
    return json.dumps(dic, sort_keys=True, indent=4)

def get_raw_config():
    config = _load_config()
    output = pretty_json_string(config)
    output += '\n\nPATH: %s' % CONFIG_FILE

    return output

def get_repo_url():
    return _load_config().get(_SECTION_GITHUB).get('url')

def get_repo_remote_name():
    return _load_config().get(_SECTION_GITHUB).get('remote')

def get_repo_path():
    path = _load_config().get(_SECTION_GITHUB).get('path')
    return realpath(path) if path is not None else None

def get_repo_branch():
    return _load_config().get(_SECTION_GITHUB).get('branch')

def get_folder_name(name):
    return _load_config().get(_SECTION_FOLDERS).get(name).get('format')
