from setuptools import setup

from cclab import __version__

setup(
    name='cclab',
    version=__version__,
    author='Tao Fei',
    author_email='filia.tao@gmail.com',
    description='Cytocurrency research & expirements',
    license='GPL 3',
    py_modules=['cclab'],
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
    ],
)
