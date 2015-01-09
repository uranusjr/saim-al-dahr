#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup


readme = open('README.rst').read()

requirements = open('requirements.txt').read().strip().split('\n')

setup(
    name="Sa'im al-Dahr",
    version='0.1.0',
    description='Run Sphinx doctests in Nose.',
    long_description=readme,
    author='Tzu-ping Chung',
    author_email='uranusjr@gmail.com',
    url='https://github.com/uranusjr/saim-al-dahr',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    license='MIT',
    zip_safe=False,
    keywords=['doctest', 'nose', 'sphinx'],
    entry_points={
        'nose.plugins.0.10': [
            'sphinx = sphinxnose:SphinxDoctest',
        ],
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
