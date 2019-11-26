import subprocess

from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open("README.md") as f:
    readme = f.read()

def get_git_version(abbrev=7):
    def is_dirty():
        ## Check for dirty version
        try:
            p = subprocess.Popen(["git", "diff-index", "--name-only", "HEAD"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.stderr.close()
            lines = p.stdout.readlines()
            return len(lines) > 0
        except:
            return False

    ## Call 'git describe --abbrev'
    try:
        p = subprocess.Popen(['git', 'describe', '--tags', '--abbrev=%d' % abbrev],
                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.stderr.close()
        line = p.stdout.readlines()[0].decode('utf-8')

        version = line.strip()
        if is_dirty():
            version+= "-dirty"
        return version

    except Exception as e:
        print(e)
        return None

setup(
    name='mylinky',
    version=get_git_version(),
    url='https://github.com/x3n1x/linky',
    license='MIT',
    author='Lionel Molinier',
    author_email='lionel@molinier.eu',
    description='Linky utility to grab your power consumption from ENEDIS',
    long_description = readme,
    long_description_content_type = "text/markdown",

    install_requires=required,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*"]),

    entry_points = {
		"console_scripts": [
			"mylinky = mylinky.entrypoint:main"
		]
	},
)
