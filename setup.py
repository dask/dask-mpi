import versioneer
import yaml
from six import string_types

from os.path import exists
from setuptools import setup


def environment_dependencies(obj, dependencies: list = None):
    if dependencies is None:
        dependencies = []
    if isinstance(obj, string_types):
        dependencies.append(obj)
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
      url='https://github.com/dask/dask-mpi',
      license='BSD 3-Clause',
      packages=['dask_mpi'],
      include_package_data=True,
      install_requires=install_requires,
      tests_require=['pytest >= 2.7.1'],
      long_description=long_description,
      zip_safe=False)
