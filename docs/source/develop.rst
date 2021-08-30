Development Guidelines
======================

This repository is part of the Dask_ projects.  General development guidelines
including where to ask for help, a layout of repositories, testing practices,
and documentation and style standards are available at the `Dask developer
guidelines`_ in the main documentation.

.. _Dask: https://dask.org
.. _`Dask developer guidelines`: https://docs.dask.org/en/latest/develop.html

Install
-------

After setting up an environment as described in the `Dask developer
guidelines`_ you can clone this repository with git::

   git clone git@github.com:dask/dask-mpi.git

and install it from source::

   cd dask-mpi
   python setup.py install

Test
----

Test using ``pytest``::

   py.test dask_mpi --verbose

Build docs
----------

To build docs site after cloning and installing from sources use::

    cd dask-mpi/docs
    make html

Output will be placed in ``build`` directory.
Required dependencies for building docs can be found in ``dask-mpi/docs/environment.yml``.
