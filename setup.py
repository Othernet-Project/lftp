import os
from setuptools import setup, find_packages


def read(fname):
    """ Return content of specified file """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


VERSION = '1.3.dev1'

setup(
    name='lftp',
    version=VERSION,
    license='GPLv3',
    packages=find_packages(),
    include_package_data=True,
    long_description=read('README.rst'),
    install_requires=[
        'librarian',
        'pyftpdlib',
        'pysendfile',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Applicaton',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
