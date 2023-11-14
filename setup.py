import subprocess
from distutils.core import setup

name = 'taskserver'
version = '0.0.4'

with open("README.md", "r") as fh:
    long_description = fh.read()

print(f'SETUP {name} [{version}]')
setup(
    name=name,
    packages=[
        name,
        f'{name}.app',
        f'{name}.app.config',
        f'{name}.domain',
        f'{name}.domain.models',
        f'{name}.domain.repositories',
        f'{name}.domain.serializers',
        f'{name}.domain.use_cases',
        f'{name}.templates',
    ],
    version=version,
    license='MIT',
    description='Simple task server built on top of Taskfile',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Club404',
    author_email='info@club404.io',
    url='https://github.com/planet-lodder/taskserver.py',
    download_url='https://github.com/planet-lodder/taskserver.py/archive/refs/tags/%s.tar.gz' % version,
    keywords=['taskfile', 'http', 'server'],
    install_requires=[],
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
