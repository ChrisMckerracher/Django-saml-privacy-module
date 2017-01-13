"""
Reworked setup module from django_saml2_auth.
See:
https://github.com/fangli/django_saml2_auth
"""

from codecs import open
from setuptools import (setup, find_packages)
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='saml2_login_required',

    version='0.1',

    description="Django decorator mimicking django's login required decorator, but with saml integration",

    long_description=long_description,

    url='https://github.com/ChrisMckerracher/saml2_login_required',

    author='Fang Li, Christopher Mckerracher',
    author_email='surivlee+djsaml2auth@gmail.com, ChrisLMckerracher@gmail.com',

    license='Apache 2.0',

    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: Apache Software License',

        'Framework :: Django :: 1.10',

        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='okta login required',

    packages=find_packages(),

    install_requires=['pysaml2==4.0.5'],
    include_package_data=True,
)
