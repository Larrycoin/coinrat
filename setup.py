from setuptools import setup, find_packages

setup(
    name='coinrat',
    version='0.0.1',
    description='Modular auto-trading crypto-currency platform.',
    author='Petr Hejna',
    author_email='hejna.peter@gmail.com',
    keywords='crypto-currency,crypto,bitcoin,trading,auto-trading,trading-bot',
    license='proprietary',
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
            'coinrat_dummy_print = coinrat_dummy_print:market_plugin',
        ],
        'coinrat_candle_storage_plugins': [
            'coinrat_influx_db_storage = coinrat_influx_db_storage:candle_storage_plugin',
        ],
        'coinrat_order_storage_plugins': [
            'coinrat_influx_db_storage = coinrat_influx_db_storage:order_storage_plugin',
        ],
        'coinrat_synchronizer_plugins': [
            'coinrat_bittrex = coinrat_bittrex:synchronizer_plugin',
            'coinrat_cryptocompare = coinrat_cryptocompare:synchronizer_plugin',
        ],
        'coinrat_strategy_plugins': [
            'coinrat_double_crossover_strategy = coinrat_double_crossover_strategy:strategy_plugin',
        ],
    },
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'coinrat'],
)
