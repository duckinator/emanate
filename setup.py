from setuptools import setup

setup(
    name='emanate',
    version='1.0.0',
    description='Symlink files from one directory to another, similarly to Effuse and Stow.',
    author='Ellen Marie Dash',
    author_email='me@duckie.co',
    url='https://github.com/duckinator/emanate',
    license='MIT',
    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    entry_points={
        'console_scripts': [
            'emanate=emanate:main',
        ],
    },
    packages=['emanate'],
    python_requires='>=3.0',
)
