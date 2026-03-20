"""TwoPixel CLI entry point"""

import sys

import click

from . import __version__
from .commands import conf, init, plug, run

logo_tmpl = r"""
████████╗██╗    ██╗ ██████╗ ██████╗ ██╗██╗  ██╗███████╗██╗
╚══██╔══╝██║    ██║██╔═══██╗██╔══██╗██║╚██╗██╔╝██╔════╝██║
   ██║   ██║ █╗ ██║██║   ██║██████╔╝██║ ╚███╔╝ █████╗  ██║
   ██║   ██║███╗██║██║   ██║██╔═══╝ ██║ ██╔██╗ ██╔══╝  ██║
   ██║   ╚███╔███╔╝╚██████╔╝██║     ██║██╔╝ ██╗███████╗███████╗
   ╚═╝    ╚══╝╚══╝  ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝
"""


@click.group()
@click.version_option(__version__, prog_name="TwoPixel")
def cli() -> None:
    """The TwoPixel CLI"""
    click.echo(logo_tmpl)
    click.echo("Welcome to TwoPixel CLI!")
    click.echo(f"TwoPixel CLI version: {__version__}")


@click.command()
@click.argument("command_name", required=False, type=str)
def help(command_name: str | None) -> None:
    """Display help information for commands

    If COMMAND_NAME is provided, display detailed help for that command.
    Otherwise, display general help information.
    """
    ctx = click.get_current_context()
    if command_name:
        # Find the specified command
        command = cli.get_command(ctx, command_name)
        if command:
            # Display help for the specific command
            click.echo(command.get_help(ctx))
        else:
            click.echo(f"Unknown command: {command_name}")
            sys.exit(1)
    else:
        # Display general help information
        click.echo(cli.get_help(ctx))


cli.add_command(init)
cli.add_command(run)
cli.add_command(help)
cli.add_command(plug)
cli.add_command(conf)

if __name__ == "__main__":
    cli()
