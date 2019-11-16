from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='linky',
    version='0.1',
    url='https://github.com/x3n1x/linky',
    license='MIT',
    author='Lionel Molinier',
    author_email='lionel@molinier.eu',
    description='Linky utility to grab your power consumption from ENEDIS',

    install_requires=required,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*"]),

    entry_points = {
		"console_scripts": [
			"linky = linky.entrypoint:main"
		]
	},
)
