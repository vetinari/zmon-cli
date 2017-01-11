import os
import logging

from typing import Optional

import yaml
import click
import clickclick
import zign.api
import requests

from clickclick import Action, error


DEFAULT_CONFIG_FILE = '~/.zmon-cli.yaml'


def configure_logging(loglevel: int) -> None:
    # configure file logger to not clutter stdout with log lines
    logging.basicConfig(level=loglevel, filename='/tmp/zmon-cli.log',
                        format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
    logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.WARNING)


def get_config_data(config_file: Optional[str]=DEFAULT_CONFIG_FILE) -> dict:
    fn = os.path.expanduser(config_file)
    data = {}  # type: dict

    try:
        if os.path.exists(fn):
            with open(fn) as fd:
                data = yaml.safe_load(fd)
        else:
            clickclick.warning('No configuration file found at [{}]'.format(config_file))

            data['url'] = click.prompt('ZMON Base URL (e.g. https://zmon.example.org/api/v1)')

            # TODO: either ask for fixed token or Zign
            data['user'] = click.prompt('ZMON username', default=os.environ['USER'])

            with open(fn, mode='w') as fd:
                yaml.dump(data, fd, default_flow_style=False,
                          allow_unicode=True,
                          encoding='utf-8')
    except Exception as e:
        error(e)

    return validate_config(data)


def set_config_file(config_file: str, default_url: str) -> None:
    while True:
        url = click.prompt('Please enter the ZMON base URL (e.g. https://demo.zmon.io)', default=default_url)

        with Action('Checking {}..'.format(url)):
            requests.get(url, timeout=5, allow_redirects=False)
            break

    data = {'url': url}

    if click.confirm('Is your ZMON using GitHub for authentication?'):
        token = click.prompt('Your personal access token (optional, only needed for GitHub auth)')
        data['token'] = token

    fn = os.path.expanduser(config_file)
    with Action('Writing configuration to {}..'.format(fn)):
        with open(fn, 'w') as fd:
            yaml.safe_dump(data, fd, default_flow_style=False)


def validate_config(data: dict) -> dict:
    """
    >>> validate_config({'url': 'foo', 'token': '123'})['url']
    'foo'
    """
    if not data.get('url'):
        raise Exception('Config file improperly configured: key "url" is missing')

    if 'token' not in data:
        data['token'] = zign.api.get_token('zmon', ['uid'])

    return data
