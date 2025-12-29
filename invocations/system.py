import pathlib
import shutil

import invoke


@invoke.task
def copy_vscode_settings(
    context: invoke.Context,
    force_update: bool = False,
) -> None:
    """Copy vscode settings from template.

    Args:
    ----
        context: invoke's context
        force_update: rewrite file if exists or not

    """
    _rewrite_file(
        context=context,
        from_path=".vscode/recommended_settings.json",
        to_path=".vscode/settings.json",
        force_update=force_update,
    )


@invoke.task
def copy_env_file(
    context: invoke.Context,
    force_update: bool = False,
) -> None:
    """Copy .env file from template.

    Args:
    ----
        context: invoke's context
        force_update: rewrite file if exists or not

    """
    _rewrite_file(
        context=context,
        from_path=".env.template",
        to_path=".env",
        force_update=force_update,
    )


def _rewrite_file(
    context: invoke.Context,
    from_path: str,
    to_path: str,
    force_update: bool = False,
) -> None:
    """Copy file to destination."""
    if force_update or not pathlib.Path(to_path).is_file():
        shutil.copy(from_path, to_path)


@invoke.task
def chown(
    context: invoke.Context,
    owner: str = "${USER}",
    path: str = ".",
) -> None:
    """Change ownership of files to user.

    Shortcut for owning apps dir by specified user after some files were
    generated using docker-compose (migrations, new app, etc).

    """
    context.run(f"sudo chown -R {owner}: {path}")


@invoke.task
def create_tmp_folder(context: invoke.Context) -> None:
    """Create folder for temporary files."""
    pathlib.Path(".tmp").mkdir(parents=True, exist_ok=True)
