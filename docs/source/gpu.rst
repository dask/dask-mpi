Dask-MPI with GPUs
==================

When running `dask-mpi` on GPU enabled systems you will be provided with one or more GPUs per MPI rank.

Today Dask assumes one worker process per GPU with workers tied correctly to each GPU. To help with this
the `dask-cuda <https://docs.rapids.ai/api/dask-cuda/nightly/index.html>`_ package exists which contains
cluster and worker classes which are designed to correctly configure your GPU environment.

.. code-block:: bash

    conda install -c rapidsai -c nvidia -c conda-forge dask-cuda
    # or
    python -m pip install dask-cuda

It is possible to leverage ``dask-cuda`` with ``dask-mpi`` by setting the worker class to use ``dask_cuda.CUDAWorker``.

.. code-block:: bash

    mpirun -np 4 dask-mpi --worker-class dask_cuda.CUDAWorker

.. code-block:: python

    from dask_mpi import initialize

    initialize(worker_class="dask_cuda.CUDAWorker")


.. tip::

   If your cluster is configured so that each rank represents one node you may have multiple GPUs
   per node. Workers will be created per GPU, not per rank so ``CUDAWorker`` will create one worker
   per GPU with names following the pattern   ``{rank}-{gpu_index}``. So if you set ``-np 4`` but you
   have four GPUs per node you will end up with   sixteen workers in your cluster.

Additional configuration
------------------------

You may also want to pass additional configuration options to ``dask_cuda.CUDAWorker`` in addition to the ones
supported by ``dask-mpi``. It is common to configure things like memory management and network protocols for
GPU workers.

You can pass any additional options that are accepted by ``dask_cuda.CUDAWorker`` with the worker options paramater.

On the CLI this is expected to be a JSON serialised dictionary of values.

.. code-block:: bash

    mpirun -np 4 dask-mpi --worker-class dask_cuda.CUDAWorker --worker-options '{"rmm_managed_memory": true}'

In Python it is just a dictionary.

.. code-block:: python

    from dask_mpi import initialize

    initialize(worker_class="dask_cuda.CUDAWorker", worker_options={"rmm_managed_memory": True})

.. tip::

    For more information on using GPUs with Dask check out the `dask-cuda documentation
    <https://docs.rapids.ai/api/dask-cuda/nightly/index.html>`_.