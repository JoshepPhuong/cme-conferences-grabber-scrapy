import platform

import invoke

from . import pre_commit, printing, system


@invoke.task
def init(context: invoke.Context, update_deps: bool = False) -> None:
    """Build project from scratch."""
    printing.print_success("Initial assembly of all dependencies")
    install_tools(context)

    if update_deps:
        printing.print_success("Update and install dependencies")
        context.run("poetry update")
    else:
        context.run("poetry sync")

    printing.print_success("Setting up vscode settings")
    system.copy_vscode_settings(context)

    printing.print_success("Setting up git")
    git_setup(context)

    printing.print_success("Setup done")


@invoke.task
def install_tools(context: invoke.Context) -> None:
    """Install shell/cli dependencies, and tools needed to install dependencies.

    Define your dependencies here, for example local("sudo npm -g install ngrok")

    Install `poetry-plugin-up` plugin to update major versions of dependencies.

    """
    context.run("poetry self add poetry-plugin-up")


@invoke.task
def git_setup(context: invoke.Context) -> None:
    """Set up git for working."""
    printing.print_success("Setting up git and pre-commit")
    pre_commit.install(context)

    _set_git_setting(
        context,
        setting="merge.ff",
        value="false",
    )
    _set_git_setting(
        context,
        setting="pull.ff",
        value="only",
    )


def _set_git_setting(
    context: invoke.Context,
    setting: str,
    value: str,
) -> None:
    """Set git setting in config."""
    context.run(f"git config --local --add {setting} {value}")
