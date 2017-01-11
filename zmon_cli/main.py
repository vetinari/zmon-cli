import requests

from zmon_cli.cmds import cli
from zmon_cli.output import log_http_exception


def main() -> None:
    try:
        cli()
    except requests.HTTPError as e:
        log_http_exception(e)
