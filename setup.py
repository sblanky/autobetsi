from setuptools import setup, find_packages
import codecs
import os.path

def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

setup(
    name='autobetsi',
    version=get_version('autobetsi/__init__.py'),
    description='Automaticly apply BETSI criteria to isotherms in a directory',
    url='https://github.com/sblanky/autobetsi',
    install_requires=[],
    author='L. Scott Blankenship',
    author_email='leo.blankenship1@nottingham.ac.uk',
    packages=find_packages(),
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "autobetsi=autobetsi.__main__:main"
        ]
    }
)
