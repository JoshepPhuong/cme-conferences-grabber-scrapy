import platform

from invoke import Collection

import invocations

ns = Collection(
    invocations.grabbers,
    invocations.linters,
    invocations.pre_commit,
    invocations.printing,
    invocations.project,
    invocations.system,
)

# Configurations for run command
# https://github.com/pyinvoke/invoke/issues/561
is_pty_enabled = platform.system() == "Linux"
ns.configure(
    dict(
        run=dict(
            pty=is_pty_enabled,
            echo=True,
        ),
    ),
)
