Dask-MPI
========

*Easily deploy Dask using MPI*


The Dask-MPI project makes it easy to deploy Dask from within an existing MPI
environment, such as one created with the common MPI command-line launchers
``mpirun`` or ``mpiexec``.  Such environments are commonly found in high performance
supercomputers, academic research institutions, and other clusters where MPI
has already been installed.  Dask-MPI provides a convenient interface for
launching your cluster either from within a batch script or directly from the
command-line.

Example:
--------

You can launch a Dask cluster directly from the command-line using the ``dask-mpi``
command and specifying a scheduler JSON file.

.. code-block:: bash

   mpirun -np 4 dask-mpi --scheduler-file /path/to/scheduler.json

You can then access this cluster from a batch script or an interactive session
(such as a Jupyter Notebook) by referencing the scheduler file.

.. code-block:: python

   from dask.distributed import Client
   client = Client(scheduler_file='/path/to/scheduler.json')


Example:
--------

Alternatively, you can turn your batch Python script into an MPI executable
simply by using the ``initialize`` function.

.. code-block:: python

   from dask_mpi import initialize
   initialize()

   from dask.distributed import Client
   client = Client()  # Connect this local process to remote workers

which makes your Python script launchable directly with ``mpirun`` or ``mpiexec``.

.. code-block:: bash

   mpirun -np 4 python my_client_script.py

.. toctree::
   :maxdepth: 1
   :caption: Getting Started

   install
   interactive
   batch

.. toctree::
   :maxdepth: 1
   :caption: Detailed use

   cli
   api

.. toctree::
   :maxdepth: 1
   :caption: Help & Reference

   howitworks
   develop
   history
