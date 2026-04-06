from setuptools import setup, find_packages

setup(
    name='arxiv-cli',
    version='0.1.0',
    description='CLI tool for working with arXiv scientific preprints',
    author='',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'click>=8.0.0',
        'requests>=2.25.0',
        'feedparser>=6.0.0',
        'python-dateutil>=2.8.0',
    ],
    entry_points={
        'console_scripts': [
            'arxiv=arxiv_cli.cli:cli',
        ],
    },
    python_requires='>=3.8',
)
