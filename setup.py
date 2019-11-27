from setuptools import setup, find_packages
import os


def read(fname):
	"""
	Returns path to README
	"""
	return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='dotpy',
	version = '1.0.0',
	author = 'Rubbie Kelvin',
	author_email = 'rubbiekelvinvoltsman@gmail.com',
	url = 'https://github.com/rubbiekelvin/Dotpy',
	description = 'Multithreaded TCP server/client',
	long_description = read('README.md'),
	long_description_content_type='text/markdown',
	license = 'MIT',
	keywords = 'socket client server multithreaded', 
	packages = find_packages()
)