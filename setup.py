from setuptools import find_packages, setup

setup(
    name='django-fallthrough-cache',
    version='0.1.0',
    description='A Django cache backend ',
    long_description=open('README.md').read(),
    author='Dan Tao',
    author_email='daniel.tao@gmail.com',
    url='https://bitbucket.org/dtao/django-fallthrough-cache',
    license='MIT',
    packages=find_packages()
)