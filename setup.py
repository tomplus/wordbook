import os
import sys
from setuptools import setup

f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
long_description = f.read()
f.close()

setup(
    name='wordbook',
    version='1.0.0',
    description='Python client for DICT Servers',
    long_description=long_description,
    url='http://github.com/tomplus/wordbook',
    author='Tomasz Prus',
    author_email='tomasz.prus@gmail.com',
    keywords=['DICT', 'dictionary'],
    license='MIT',
    packages=['wordbook'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)

