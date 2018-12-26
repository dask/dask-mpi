Dask-MPI with Batch Jobs
========================

Dask, with Dask Distributed, is an incredibly powerful engine behind interactive sessions
(see :ref:`interactive`).  However, there are many scenarios where your work is pre-defined
and you do not need an interactive session to execute your tasks.  In these cases, running
in *batch-mode* is best.

Dask-MPI makes running in batch-mode in an MPI environment easy by providing an API to the
same functionality created for the ``dask-mpi`` :ref:`cli`.  However, in batch mode, you
need the script running your Dask Client to run in the same environment in which your Dask
cluster is constructed, and you want your Dask cluster to shut down after your Client script
has executed.

To make this functionality possible, Dask-MPI provides the ``initialize()`` method as part of
its :ref:`api`.  The ``initialize()`` function, when run from within an MPI environment (i.e.,
created by the use of ``mpirun`` or ``mpiexec``), launches the Dask Scheduler on MPI rank 0
and the Dask Workers on MPI ranks 2 and above.  On MPI rank 1, the ``initialize()`` function
"passes through" to the Client script, running the Dask-based Client code the user wishes to
execute.

For example, if you have a Dask-based script named ``myscript.py``, you would be able to
run this script in parallel, using Dask, with the following command.

.. code-block:: bash

   mpirun -np 4 python myscript.py

This will run the Dask Scheduler on MPI rank 0, the user's Client code on MPI rank 1, and
2 workers on MPI rank 2 and MPI rank 3.  To make this work, the ``myscript.py`` script must
have (presumably near the top of the script) the following code in it.

.. code-block:: python

   from dask_mpi import initialize
   initialize()

   from distributed import Client
   client = Client()

The Dask Client will automatically detect the location of the Dask Scheduler running on MPI
rank 0 and connect to it.

When the Client code is finished executing, the Dask Scheduler and Workers (and, possibly,
Nannies) will be terminated.

.. tip:: **Running Batch Jobs with Job Schedulers**

   It is common in High-Performance Computing (HPC) environments to request the necessary
   computing resources with a job scheduler, such LSF, PBS, or SLURM.  In such environments,
   is is advised that the ``mpirun ... python myscript.py`` command be placed in a job
   submission script such that the resources requested from the job scheduler match the
   resources used by the ``mpirun`` command.

For more details on the ``initialize()`` method, see the :ref:`api`.
