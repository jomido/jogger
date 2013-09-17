from setuptools import setup, find_packages

setup(
    name='jogger',
    version='0.1.1',
    description='Navigate log files.',
    long_description=(
        open('README.md').read()
    ),
    url='http://github.com/jomido/jogger/',
    license='MIT',
    author='Jonathan Dobson',
    author_email='jon.m.dobson@gmail.com',
    packages=[
        'jogger'
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Text Processing',
        'Topic :: System :: Logging'
    ],
)