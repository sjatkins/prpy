__author__ = 'samantha'
from setuptools import setup, find_packages

setup(name='prpy',
      version='0.1',
      description='Perilous Realms',
      author='Samantha Atkins',
      author_email='samantha@conceptwareinc.com',
      license='internal',
      packages=find_packages(exclude=['test']),
      install_requires=['pyparsing', 'requests', 'pyyaml', 'pydantic'],
      zip_safe=False)
