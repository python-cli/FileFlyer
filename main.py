#!/usr/bin/env python

import coloredlogs, logging, logging.config
import os
import os.path
import shutil
import click

from git import Repo

from fileflyer.config import *
from fileflyer.utility import *

# Refer to
#   1. https://stackoverflow.com/a/7507842/1677041
#   2. https://stackoverflow.com/a/49400680/1677041
#   3. https://docs.python.org/2/library/logging.config.html
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'colored': {
            '()': 'coloredlogs.ColoredFormatter',
            'format': "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            'datefmt': '%H:%M:%S',
        }
    },
    'handlers': {
        'default': {
            'level': 'DEBUG' if __debug__ else 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
        'console': {
            'level': 'DEBUG' if __debug__ else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'colored',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': 'main.log',
            'maxBytes': 1024 * 1024,
            'backupCount': 10
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        },
        '__main__': {  # if __name__ == '__main__'
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'fileflyer': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

def check_repo_status() -> bool:
    base_url = get_repo_url()
    root_path = get_repo_path()
    repo = Repo(root_path)
    branch_name = get_repo_branch()
    remote_name = get_repo_remote_name()

    if base_url is None or len(base_url) <= 0:
        logger.error('No github repository\'s base url found.')
        return False

    if len(branch_name) > 0:
        if branch_name == repo.active_branch.name:
            logger.debug(f'It\'s in the expected branch: {branch_name}.')
        else:
            logger.error('Not in target branch.')
            return False
    else:
        logger.warn('Skip the branch match.')

    if repo.is_dirty():
        logger.warn('Repo is under the dirty state.')
        return False

    remotes = list(map(lambda r: r.name, repo.remotes))

    if remote_name is None or len(remote_name) <= 0:
        logger.error('The target remote doesn\'t specify.')
        return False

    if remote_name not in remotes:
        logger.error('The target remote doesn\'t exist.')
        return False

    return True

def walk_files_recursively(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            yield file_path

@click.group()
@click.option('--debug/--no-debug', default=False, help='Enable logger level to DEBUG')
def cli(debug):
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    debug and click.echo('Debug mode is on')

@cli.command()
def configure():
    '''
    Show the current configurations.
    '''
    logger.info('\n%s' % get_raw_config())

@cli.command()
def repo():
    '''
    Check the repo's status.
    '''
    if check_repo_status():
        logger.info('The file hosting repository looks good!')
    else:
        logger.error('Something wrong should be resolved first!')

@cli.command()
@click.argument('items', type=click.Path(exists=True, resolve_path=True), nargs=-1)
@click.option('--folder', type=click.STRING, default='default', help='Which folder will the files be.')
@click.option('--origin/--raw', default=False, help='Show the original source file path or raw file path in the end.')
@click.option('--plain/--json', default=True, help='Show the result with plain text or json format.')
def upload(items, folder, origin, plain):
    '''
    Upload the files to github repository.
    '''
    if len(items) <= 0:
        logger.info('Missing files!')
        return

    root_path = get_repo_path()

    if check_repo_status() is not True:
        logger.error('Abort the upload before resolving the repo\'s status.')
        return

    repo = Repo(root_path)
    folder_name = resolve_folder_name(get_folder_name(folder))
    root_folder = os.path.join(root_path, folder_name)

    if not os.path.exists(root_folder):
        os.makedirs(root_folder)
        logger.debug(f'Created folder {folder_name}')

    total_files = []

    for item in items:
        dest_path = os.path.join(root_folder, os.path.basename(item))

        if os.path.isdir(item):
            shutil.copytree(item, dest_path)
            for file in walk_files_recursively(dest_path):
                total_files.append(file.replace(root_path, ''))
        else:
            shutil.copy2(item, dest_path)
            total_files.append(dest_path.replace(root_path, ''))

        repo.index.add(dest_path)

    total_files_desc = '\n'.join(total_files)
    repo.index.commit(f'[FileFlyer] Add {len(total_files)} file(s).\n\n{total_files_desc}')

    origin_remote = list(filter(lambda r: r.name == get_repo_remote_name(), repo.remotes))[0]
    origin_remote.push()

    base_url = get_repo_url()
    branch_name = get_repo_branch() or repo.active_branch.name
    json_result = {}

    for file in total_files:
        option = '' if origin is True else '?raw=true'
        share_url = f'{base_url}/blob/{branch_name}{file}{option}'

        if plain:
            print(f'{file}:\n\t{share_url}\n')
        else:
            json_result[file] = share_url

    if not plain:
        print(pretty_json_string(json_result))

if __name__ == '__main__':
    cli()
