# Path: fastlabio/setup.py
# -*- coding: utf-8 -*-
"""
Setup file for the fastlabio library.

This file is used to package and distribute the fastlabio library.
It follows the structure of the plico_motor library's setup.py.
"""
import os
import sys
from shutil import rmtree

from setuptools import setup, Command

__author__ = 'Your Name' # TODO: Replace with actual author name
__version__ = '0.1.0' # TODO: Replace with actual version
__date__ = '2023-10-27' # TODO: Replace with actual date

NAME = 'fastlabio'
DESCRIPTION = 'Fast Lab IO Library' # TODO: Replace with actual description
URL = 'https://github.com/YourOrg/fastlabio' # TODO: Replace with actual URL
EMAIL = 'your.email@example.com' # TODO: Replace with actual email
AUTHOR = __author__
LICENSE = 'MIT' # TODO: Verify license
KEYWORDS = 'laboratory, instrumentation control' # TODO: Add relevant keywords

here = os.path.abspath(os.path.dirname(__file__))
# Load the package's __version__.py module as a dictionary.
about = {}
# TODO: Create a fastlabio/__version__.py file with a __version__ attribute
# with open(os.path.join(here, NAME, '__version__.py')) as f:
#     exec(f.read(), about)


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\\033[1m{0}\\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system(
            '{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        # os.system('git tag v{0}'.format(about['__version__'])) # Uncomment after creating __version__.py
        os.system('git push --tags')

        sys.exit()


setup(name=NAME,
      description=DESCRIPTION,
      version=__version__, # Using __version__ from this file for now
      classifiers=[
          'Development Status :: 4 - Beta', # TODO: Adjust status
          'Operating System :: OS Independent', # TODO: Adjust OS
          'Programming Language :: Python :: 3',
          # TODO: Add specific Python versions, e.g., 'Programming Language :: Python :: 3.7',
      ],
      long_description=open('README.md').read(), # TODO: Create README.md if it doesn't exist or update it
      long_description_content_type='text/markdown',
      url=URL,
      author_email=EMAIL,
      author=AUTHOR,
      license=LICENSE,
      keywords=KEYWORDS,
      packages=[
          'fastlabio',
          # TODO: Add any subpackages if they exist e.g., 'fastlabio.client',
      ],
      # entry_points={ # Uncomment and modify if there are any scripts to install
      #     'console_scripts': [
      #         'your_script_name=fastlabio.module:main_function',
      #     ],
      # },
      # package_data={ # Uncomment and modify if there are any non-code files to include
      #     'fastlabio': ['path/to/your/data/file'],
      # },
      install_requires=[
          'fastapi',
          'uvicorn[standard]',
          'pydantic',
          'opencv-python',
          'numpy',
          'pysilico',
          'pysilico_server',
          'pytest',
          'pytest-asyncio',
          'httpx',
      ],
      include_package_data=True,
      test_suite='tests', # Assuming tests are in a 'tests' directory
      cmdclass={'upload': UploadCommand, },
      zip_safe=False, # Often necessary for package_data
      ) 