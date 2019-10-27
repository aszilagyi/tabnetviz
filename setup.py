
from setuptools import setup

with open('piplongdesc.md') as f:
    README=f.read()

setup(
  name='tabnetviz',
  version='1.1.0',
  description='Table-based network visualizer',
  long_description=README,
  long_description_content_type='text/markdown',
  url='https://git.io/tabnetviz',
  author='Andras Szilagyi',
  author_email='szilagyi.andras@ttk.hu',
  license='GPLv3',
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3 :: Only',
    'Topic :: Multimedia :: Graphics',
    'Topic :: Scientific/Engineering',
    'Topic :: Scientific/Engineering :: Bio-Informatics',
    'Topic :: Scientific/Engineering :: Information Analysis',
    'Topic :: Scientific/Engineering :: Visualization',
  ],
  packages=['tabnetviz'],
  include_package_data=False,
  install_requires=['pyyaml', 'yamlloader', 'pygraphviz', 'pandas', 'matplotlib',
    'networkx', 'svgwrite'],
  python_requires='>=3.2',
  entry_points={'console_scripts': ['tabnetviz=tabnetviz.__main__:main']}
  )
  
