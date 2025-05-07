from setuptools import setup, find_packages

setup(
    name='chatcli',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'click',
        'requests'
    ],
    entry_points={
        'console_scripts': [
            'chatcli = chatcli.cli:cli',
        ],
    },
    author='Subhobroto Sasmal',
    description='A simple chat CLI for local chat servers',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
