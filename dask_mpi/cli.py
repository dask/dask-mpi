import click
from distributed.cli.utils import check_python_3

from .core import MPIRunner


@click.command()
@click.option(
    "--scheduler-file",
    type=str,
    default="scheduler.json",
    help="Filename to JSON encoded scheduler information.",
)
@click.option(
    "--scheduler-port",
    default=0,
    type=int,
    help="Specify scheduler port number.  Defaults to random.",
)
@click.option(
    "--interface", type=str, default=None, help="Network interface like 'eth0' or 'ib0'"
)
@click.option(
    "--protocol", type=str, default="tcp", help="Network protocol to use like TCP"
)
@click.option("--nthreads", type=int, default=1, help="Number of threads per worker.")
@click.option(
    "--memory-limit",
    default="auto",
    help="Number of bytes before spilling data to disk. "
    "This can be an integer (nbytes) "
    "float (fraction of total memory) "
    "or 'auto'",
)
@click.option(
    "--local-directory", default=None, type=str, help="Directory to place worker files"
)
@click.option(
    "--scheduler/--no-scheduler",
    default=True,
    help=(
        "Whether or not to include a scheduler. "
        "Use --no-scheduler to increase an existing dask cluster"
    ),
)
@click.option(
    "--nanny/--no-nanny",
    default=True,
    help="Start workers in nanny process for management (deprecated use --worker-class instead)",
)
@click.option(
    "--worker-class",
    type=str,
    default="distributed.Nanny",
    help="Class to use when creating workers",
)
@click.option(
    "--worker-options",
    type=str,
    default=None,
    help="JSON serialised dict of options to pass to workers",
)
@click.option(
    "--dashboard-address",
    type=str,
    default=":8787",
    help="Address for visual diagnostics dashboard",
)
def main(
    scheduler_file,
    interface,
    nthreads,
    local_directory,
    memory_limit,
    scheduler,
    dashboard_address,
    nanny,
    worker_class,
    worker_options,
    scheduler_port,
    protocol,
):
    scheduler_options = {
        "scheduler_file": scheduler_file,
        "interface": interface,
        "protocol": protocol,
        "dashboard_address": dashboard_address,
    }
    worker_options = {
        "scheduler_file": scheduler_file,
        "interface": interface,
        "protocol": protocol,
        "nthreads": nthreads,
        "memory_limit": memory_limit,
        "local_directory": local_directory,
    }
    worker_class = "dask.distributed.Nanny" if nanny else "dask.distributed.Worker"
    MPIRunner(
        scheduler=scheduler,
        scheduler_options=scheduler_options,
        worker_class=worker_class,
        worker_options=worker_options,
        client=False,
    )


def go():
    check_python_3()
    main()


if __name__ == "__main__":
    go()
