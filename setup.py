from setuptools import setup
from setuptools import find_packages

setup(name='Distant Viewing Toolkit',
      version='0.1.0',
      description='Cultural Analysis of Moving Images',
      long_description="""Distant Viewing uses and develops computational techniques to analyse moving image culture on a large scale. The project is currently in active development.""",
      author='Taylor Anold',
      author_email='taylor.arnold@acm.org',
      url='https://github.com/statsmaths/dvt',
      license='GPL-2',
      install_requires=['numpy>=1.14.0',
                        'keras>=2.1.4',
                        'face_recognition>=0.1.0',
                        'six>=1.11.0',
                        'h5py>=2.7.1'],
      extras_require={
          'tests': ['pytest',
                    'pytest-pep8',
                    'pytest-xdist',
                    'pytest-cov'],
      },
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'Intended Audience :: Education',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
          'Programming Language :: Python :: 3.6',
          'Topic :: Multimedia :: Video',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ],
      packages=find_packages())
