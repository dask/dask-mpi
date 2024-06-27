import asyncio
import json

import click
from distributed import Scheduler, Worker
from distributed.utils import import_term
from mpi4py import MPI

from .exceptions import WorldTooSmallException


@click.command()
@click.argument("scheduler_address", type=str, required=False)
@click.option(
    "--scheduler-file",
    type=str,
    default=None,
    help="Filename to JSON encoded scheduler information.",
)
@click.option(
    "--scheduler-port",
    default=None,
    type=int,
    help="Specify scheduler port number.  Defaults to random.",
)
@click.option(
    "--interface", type=str, default=None, help="Network interface like 'eth0' or 'ib0'"
)
@click.option(
    "--protocol", type=str, default=None, help="Network protocol to use like TCP"
)
@click.option(
    "--nthreads", type=int, default=None, help="Number of threads per worker."
)
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
    "--dashboard/--no-dashboard",
    "dashboard",
    default=True,
    required=False,
    help="Launch the Dashboard [default: --dashboard]",
)
@click.option(
    "--dashboard-address",
    type=str,
    default=None,
    help="Address for visual diagnostics dashboard",
)
@click.option(
    "--name",
    type=str,
    default="dask_mpi",
    help="Name prefix for each worker, to which dask-mpi appends ``-<worker_rank>``.",
)
def main(
    scheduler_address,
    scheduler_file,
    interface,
    nthreads,
    local_directory,
    memory_limit,
    scheduler,
    dashboard,
    dashboard_address,
    nanny,
    worker_class,
    worker_options,
    scheduler_port,
    protocol,
    name,
):
    comm = MPI.COMM_WORLD

    world_size = comm.Get_size()
    if scheduler and world_size < 2:
        raise WorldTooSmallException(
            f"Not enough MPI ranks to start cluster, found {world_size}, "
            "needs at least 2, one each for the scheduler and a worker."
        )

    rank = comm.Get_rank()

    try:
        worker_options = json.loads(worker_options)
    except TypeError:
        worker_options = {}

    if rank == 0 and scheduler:

        async def run_scheduler():
            async with Scheduler(
                interface=interface,
                protocol=protocol,
                dashboard=dashboard,
                dashboard_address=dashboard_address,
                scheduler_file=scheduler_file,
                port=scheduler_port,
            ) as s:
                comm.Barrier()
                await s.finished()

        asyncio.get_event_loop().run_until_complete(run_scheduler())

    else:
        comm.Barrier()

        async def run_worker():
            WorkerType = import_term(worker_class)
            if not nanny:
                raise DeprecationWarning(
                    "Option --no-nanny is deprectaed, use --worker-class instead"
                )
                WorkerType = Worker
            opts = {
                "interface": interface,
                "protocol": protocol,
                "nthreads": nthreads,
                "memory_limit": memory_limit,
                "local_directory": local_directory,
                "name": f"{name}-{rank}",
                "scheduler_file": scheduler_file,
                **worker_options,
            }
            if scheduler_address:
                opts["scheduler_ip"] = scheduler_address
            async with WorkerType(**opts) as worker:
                await worker.finished()

        asyncio.get_event_loop().run_until_complete(run_worker())


if __name__ == "__main__":
    main()
