from setuptools import setup, find_packages

with open('README.rst') as f:
    long_description = ''.join(f.readlines())

setup(
    name='coinrat',
    version='0.0.1',
    description='Modular auto-trading crypto-currency platform.',
    long_description=long_description,
    author='Petr Hejna',
    author_email='hejna.peter@gmail.com',
    keywords='cryptocurency,crypto,bitcoin,trading,autotrading,tradingbot',
    license='MIT',
    url='https://github.com/achse/coinrat',
    packages=find_packages(),
    classifiers=[
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Natural Language :: English',
        'Environment :: Web Environment',
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'coinrat = coinrat.coinrat:main',
        ],
        'coinrat_market_plugins': [
            'coinrat_bittrex = coinrat_bittrex:market_plugin',
        ],
        'coinrat_storage_plugins': [
            'coinrat_influx_db_storage = coinrat_influx_db_storage:storage_plugin',
        ],
        'coinrat_synchronizer_plugins': [
            'coinrat_cryptocompare = coinrat_cryptocompare:synchronizer_plugin',
        ],
    },
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'coinrat'],
)
