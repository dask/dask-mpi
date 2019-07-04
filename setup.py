import versioneer
import yaml

from six import string_types
from os.path import exists
from setuptools import setup


def environment_dependencies(obj, dependencies=None):
    if dependencies is None:
        dependencies = []
    # if isinstance(obj, string_types):
    #     dependencies.append(obj.replace('=', '=='))
    elif isinstance(obj, dict):
        if 'dependencies' in obj:
            environment_dependencies(obj['dependencies'], dependencies=dependencies)
        elif 'pip' in obj:
            environment_dependencies(obj['pip'], dependencies=dependencies)
    elif isinstance(obj, list):
        for d in obj:
            environment_dependencies(d, dependencies=dependencies)
    return dependencies


with open('environment.yml') as f:
    install_requires = environment_dependencies(yaml.safe_load(f))

if exists('README.rst'):
    with open('README.rst') as f:
        long_description = f.read()
else:
    long_description = ''

setup(name='dask-mpi',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Deploy Dask using mpi4py',
      url='https://github.com/dask/dask-mpi',  # TODO: Update to docs when docs complete
      maintainer='Kevin Paul',
      maintainer_email='kpaul@ucar.edu',
      license='BSD 3-Clause',
      include_package_data=True,
      install_requires=install_requires,
      python_requires=">=3.5",
      packages=['dask_mpi'],
      long_description=long_description,
      entry_points="""
            [console_scripts]
            dask-mpi=dask_mpi.cli:go
            """,
      zip_safe=False)
