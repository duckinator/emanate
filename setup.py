from setuptools import setup

setup(
    entry_points={
        'console_scripts': [
            'emanate=emanate.cli:main',
        ],
        'distutils.commands': [
            'release = distutils_twine:release',
        ],
    },
)
