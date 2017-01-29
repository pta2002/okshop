import os
from setuptools import find_packages, setup
from pip.req import parse_requirements

# TODO: Fix nasty hack ;_;
install_reqs = parse_requirements(os.path.join(os.path.dirname(__file__), 'requirements.txt'), session='hack')
reqs = [str(ir.req) for ir in install_reqs]

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
	README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
	name='django-okshop',
	version='0.1',
	packages=find_packages(),
	install_requires=reqs,
	include_package_data=True,
	license='MIT License',
	description='An ebay-like marketplace for okcash',
	long_description=README,
	author='Pedro Alves',
	author_email='pta2002@pta2002.com',
	classifiers=[
		'Environment :: Web Environment',
		'Framework :: Django',
		'Framework :: Django :: 1.10',
		'License :: MIT License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
	])