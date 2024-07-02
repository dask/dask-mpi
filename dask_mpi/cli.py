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
    "--scheduler-rank",
    default=0,
    type=int,
    help="The MPI rank on which the scheduler will launch.  Defaults to 0.",
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
    "--exclusive-workers/--inclusive-workers",
    default=True,
    help=(
        "Whether to force workers to run on unoccupied MPI ranks.  If false, "
        "then a worker will be launched on the same rank as the scheduler."
    ),
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
    scheduler_port,
    scheduler_rank,
    interface,
    protocol,
    nthreads,
    memory_limit,
    local_directory,
    scheduler,
    dashboard,
    dashboard_address,
    nanny,
    exclusive_workers,
    worker_class,
    worker_options,
    name,
):
    comm = MPI.COMM_WORLD

    world_size = comm.Get_size()
    min_world_size = 1 + scheduler * max(scheduler_rank, exclusive_workers)
    if world_size < min_world_size:
        raise WorldTooSmallException(
            f"Not enough MPI ranks to start cluster with exclusive_workers={exclusive_workers} and "
            f"scheduler_rank={scheduler_rank}, found {world_size} MPI ranks but needs {min_world_size}."
        )

    rank = comm.Get_rank()

    try:
        worker_options = json.loads(worker_options)
    except TypeError:
        worker_options = {}

    async def run_worker():
        WorkerType = import_term(worker_class)
        if not nanny:
            WorkerType = Worker
            raise DeprecationWarning(
                "Option --no-nanny is deprectaed, use --worker-class instead"
            )
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

    async def run_scheduler(launch_worker=False):
        async with Scheduler(
            interface=interface,
            protocol=protocol,
            dashboard=dashboard,
            dashboard_address=dashboard_address,
            scheduler_file=scheduler_file,
            port=scheduler_port,
        ) as scheduler:
            comm.Barrier()

            if launch_worker:
                asyncio.get_event_loop().create_task(run_worker())

            await scheduler.finished()

    if rank == scheduler_rank and scheduler:
        asyncio.get_event_loop().run_until_complete(
            run_scheduler(launch_worker=not exclusive_workers)
        )
    else:
        comm.Barrier()

        asyncio.get_event_loop().run_until_complete(run_worker())


if __name__ == "__main__":
    main()
