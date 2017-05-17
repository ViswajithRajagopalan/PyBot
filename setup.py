
from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

setup(
    name='PyCalendar',
    version='0.1.0',
    description='Discord bot that handle a Google calendar',
    long_description=readme,
    author='Axel Rieben & Johnny Da Costa',
    author_email='axel.rieben@he-arc.ch, johnny.dacosta@he-arc.ch',
    url='https://github.com/johndacost/PyBot',
    license='MIT',
    packages=find_packages(exclude=('tests', 'docs'))
)
