from setuptools import setup, find_packages
from codecs import open
from os import path
from sas_select.version import VERSION

# Get the long description from the README file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='sas_select',
    version=VERSION,
    description='Web based search facility for products on the Stoma Appliance Schedule',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/timcu/sas-select',
    author="D Tim Cummings",
    author_email='tim@triptera.com.au',  # Optional
    license='MIT',
    classifiers=[ 
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Topic :: Health',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    keywords='bpss flask stoma medicare',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    python_requires='>=3',
    install_requires=['flask_bootstrap', 'pandas', 'xlrd'],
    include_package_data=True,
)
