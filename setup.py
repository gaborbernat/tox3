from setuptools import find_packages, setup

setup(
    name='tox3',
    description='virtualenv-based automation of test activities',
    url='https://tox.readthedocs.org/',
    use_scm_version=True,
    include_package_data=True,
    license='http://opensource.org/licenses/MIT',
    platforms=['unix', 'linux', 'osx', 'cygwin', 'win32'],
    author='Bernat Gabor',
    author_email='gaborjbernat@gmail.com',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    python_requires='>=3.6',
    setup_requires=['setuptools_scm >= 1.15.6, <2'],
    install_requires=['toml >= 0.9.3, <1',
                      'colorlog >= 3.1.0, <4',
                      'py'],
    extras_require={'testing': ['pytest >= 3.0.0',
                                'pytest-asyncio >= 0.8.0, <1']},
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Operating System :: POSIX',
                 'Operating System :: Microsoft :: Windows',
                 'Operating System :: MacOS :: MacOS X',
                 'Topic :: Software Development :: Testing',
                 'Topic :: Software Development :: Libraries',
                 'Topic :: Utilities'] + [
                    ('Programming Language :: Python :: {}'.format(x)) for x in '3.4 3.5 3.6'.split()]
)
