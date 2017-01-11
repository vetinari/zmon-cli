import click

from typing import Optional, Any


def highlight(msg: str, **kwargs: Optional[Any]) -> None:
    click.secho(' {}'.format(msg), fg='cyan', nl=False, bold=True, **kwargs)
