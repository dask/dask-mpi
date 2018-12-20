Installing
==========

You can install dask-mpi with ``pip``, ``conda``, or by installing from source.

Pip
---

Pip can be used to install both dask-mpi and its dependencies (e.g. dask,
distributed,  NumPy, Pandas, etc.) that are necessary for different
workloads.::

   pip install dask_mpi --upgrade   # Install everything from last released version

Conda
-----

To install the latest version of dask-mpi from the
`conda-forge <https://conda-forge.github.io/>`_ repository using
`conda <https://www.anaconda.com/downloads>`_::

    conda install dask-mpi -c conda-forge

Install from Source
-------------------

To install dask-mpi from source, clone the repository from `github
<https://github.com/dask/dask-mpi>`_::

    git clone https://github.com/dask/dask-mpi.git
    cd dask-mpi
    python setup.py install

or use ``pip`` locally if you want to install all dependencies as well::

    pip install -e .

You can also install directly from git master branch::

    pip install git+https://github.com/dask/dask-mpi


Test
----

Test dask-mpi with ``pytest``::

    git clone https://github.com/dask/dask-mpi.git
    cd dask-mpi
    pytest dask_mpi
