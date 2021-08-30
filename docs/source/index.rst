Dask-MPI
========

*Easily deploy Dask using MPI*


The Dask-MPI project makes it easy to deploy Dask from within an existing MPI
environment, such as one created with the common MPI command-line launchers
``mpirun`` or ``mpiexec``.  Such environments are commonly found in high performance
supercomputers, academic research institutions, and other clusters where MPI
has already been installed.

Dask-MPI provides two convenient interfaces to launch Dask, either from within
a batch script or directly from the command-line.

Batch Script Example
--------------------

You can turn your batch Python script into an MPI executable
with the ``dask_mpi.initialize`` function.

.. code-block:: python

   from dask_mpi import initialize
   initialize()

   from dask.distributed import Client
   client = Client()  # Connect this local process to remote workers

This makes your Python script launchable directly with ``mpirun`` or ``mpiexec``.

.. code-block:: bash

   mpirun -np 4 python my_client_script.py

This deploys the Dask scheduler and workers as well as the user's Client
process within a single cohesive MPI computation.


Command Line Example
--------------------

Alternatively you can launch a Dask cluster directly from the command-line
using the ``dask-mpi`` command and specifying a scheduler file where Dask can
write connection information.

.. code-block:: bash

   mpirun -np 4 dask-mpi --scheduler-file ~/dask-scheduler.json

You can then access this cluster either from a separate batch script or from an
interactive session (such as a Jupyter Notebook) by referencing the same scheduler
file that ``dask-mpi`` created.

.. code-block:: python

   from dask.distributed import Client
   client = Client(scheduler_file='~/dask-scheduler.json')


Use Job Queuing System Directly
-------------------------------

You can also use `Dask Jobqueue <https://jobqueue.dask.org>`_ to deploy Dask
directly on a job queuing system like SLURM, SGE, PBS, LSF, Torque, or others.
This can be especially nice when you want to dynamically scale your cluster
during your computation, or for interactive use.


.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Getting Started

   install
   batch
   interactive
   gpu

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Detailed use

   cli
   api

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Help & Reference

   howitworks
   develop
   history
