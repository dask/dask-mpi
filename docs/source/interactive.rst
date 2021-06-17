.. _interactive:

Dask-MPI with Interactive Jobs
==============================

Dask-MPI can be used to easily launch an entire Dask cluster in an existing MPI environment,
and attach a client to that cluster in an interactive session.

In this scenario, you would launch the Dask cluster using the Dask-MPI command-line interface
(CLI) ``dask-mpi``.

.. code-block:: bash

   mpirun -np 4 dask-mpi --scheduler-file scheduler.json

In this example, the above code will use MPI to launch the Dask Scheduler on MPI rank 0 and
Dask Workers (or Nannies) on all remaining MPI ranks.

It is advisable, as shown in the previous example, to use the ``--scheduler-file`` option when
using the ``dask-mpi`` CLI.  The ``--scheduler-file`` option saves the location of the Dask
Scheduler to a file that can be referenced later in your interactive session.  For example,
the following code would create a Dask Client and connect it to the Scheduler using the
scheduler JSON file.

.. code-block:: python

   from distributed import Client
   client = Client(scheduler_file='/path/to/scheduler.json')

As long as your interactive session has access to the same filesystem where the scheduler JSON
file is saved, this procedure will let you run your interactive session easily attach to your
separate ``dask-mpi`` job.

After a Dask cluster has been created, the ``dask-mpi`` CLI can be used to add more workers to
the cluster by using the ``--no-scheduler`` option.

.. code-block:: bash

   mpirun -n 5 dask-mpi --scheduler-file scheduler.json --no-scheduler

In this example (above), 5 more workers will be created and they will be registered with the
Scheduler (whose address is in the scheduler JSON file).

.. tip:: **Running with a Job Scheduler**

   In High-Performance Computing environments, job schedulers, such as LSF, PBS, or SLURM, are
   commonly used to request the necessary resources needed for an MPI job, such as the number
   of CPU cores, the total memory needed, and/or the number of nodes over which to spread out
   the MPI job.  In such a case, it is advisable that the user place the ``mpirun ... dask-mpi ...``
   command in a job submission script, with the number of MPI ranks (e.g., ``-np 4``) matches the
   number of cores requested from the job scheduler.

.. warning:: **MPI Jobs and Dask Nannies**

   It is many times useful to launch your Dask-MPI cluster (using ``dask-mpi``) with Dask Nannies
   (i.e., with the ``--worker-class distributed.Nanny`` option), rather than strictly with Dask Workers.
   This is because the Dask Nannies can relaunch a worker when a failure occurs. However, in some MPI
   environments, Dask Nannies will not be able to work as expected.  This is because some installations
   of MPI may restrict the number of actual running processes from exceeding the number of MPI ranks
   requested.  When using Dask Nannies, the Nanny process is executed and runs in the background
   after forking a Worker process.  Hence, one Worker process will exist for each Nanny process.
   Some MPI installations will kill any forked process, and you will see many errors arising from
   the Worker processes being killed.  If this happens, disable the use of Nannies with the
   ``--worker-class distributed.Worker`` option to ``dask-mpi``.

For more details on how to use the ``dask-mpi`` command, see the :ref:`cli`.
