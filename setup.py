from setuptools import setup, find_packages

setup(
    name='autobetsi',
    version='0.1',
    description='Automaticly apply BETSI criteria to isotherms in a directory',
    url='https://github.com/sblanky/autobetsi',
    install_requires=[],
    author_email='leo.blankenship1@nottingham.ac.uk',
    packages=find_packages(),
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "autobetsi=autobetsi.__main__:main"
        ]
    }
)
