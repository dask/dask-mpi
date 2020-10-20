How Dask-MPI Works
==================

Dask-MPI works by using the ``mpi4py`` package and using MPI to selectively run
different code on different MPI ranks.  Hence, like any other application of the
``mpi4py`` package, it requires creating the appropriate MPI environment through
the running of the ``mpirun`` or ``mpiexec`` commands.

.. code-block:: bash

   mpirun -np 8 dask-mpi --no-nanny --scheduler-file ~/scheduler.json

or

.. code-block:: bash

   mpirun -np 8 python my_dask_script.py

Using the Dask-MPI CLI
----------------------

By convention, Dask-MPI always launches the Scheduler on MPI rank 0.  When using the CLI
(``dask-mpi``), Dask-MPI launches the Workers (or Nannies and Workers) on the remaining
MPI ranks (MPI ranks 1 and above).  On each MPI rank, a ``tornado`` event loop is started
after the Scheduler and Workers are created.  These event loops continue until a kill
signal is sent to one of the MPI processes, and then the entire Dask cluster (all MPI ranks)
is shut down.

When using the ``--no-scheduler`` option of the Dask-MPI CLI, more workers can be added to
an existing Dask cluster.  Since these two runs will be in separate ``mpirun`` or ``mpiexec``
executions, they will only be tied to each other through the scheduler.  If a worker in the
new cluster crashes and takes down the entire MPI environment, it will not have anything to
do with the first (original) Dask cluster.  Similarly, if the first cluster is taken down,
the new workers will wait for the Scheduler to reactivate so they can re-connect.

Using the Dask-MPI API
----------------------

Again, Dask-MPI always launches the Scheduler on MPI rank 0.  When using the ``initialize()``
method, Dask-MPI runs the Client script on MPI rank 1 and launches the Workers on the
remaining MPI ranks (MPI ranks 2 and above).  The Dask Scheduler and Workers start their
``tornado`` event loops once they are created on their given MPI ranks, and these event
loops run until the Client process (MPI rank 1) sends the termination signal to the
Scheduler.  Once the Scheduler receives the termination signal, it will shut down the
Workers, too.
