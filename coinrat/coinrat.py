import datetime
import json
import logging
import uuid

import dateutil.parser
import click
import sys
from typing import Tuple, Dict, NoReturn, Union
from os.path import join, dirname

from click import Context
from dotenv import load_dotenv

from coinrat.domain import ForEndUserException, DateTimeInterval
from coinrat.domain.candle import CandleExporter
from coinrat.domain.candle.null_candle_storage import NullCandleStorage
from coinrat.domain.market import Market
from coinrat.domain.order import OrderExporter
from coinrat.domain.pair import Pair
from coinrat.domain.strategy import StrategyRun, StrategyRunMarket
from coinrat.event.null_event_emitter import NullEventEmitter
from coinrat.market_plugins import MarketNotProvidedByPluginException, MarketPluginSpecification, \
    MarketPluginDoesNotExistsException
from coinrat.strategy_plugins import StrategyNotProvidedByAnyPluginException
from coinrat.thread_watcher import ThreadWatcher
from .db_migrations import run_db_migrations
from .di_container_coinrat import DiContainerCoinrat

dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("werkzeug").setLevel(logging.WARNING)
logging.getLogger("pika").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("engineio").setLevel(logging.WARNING)
logging.getLogger("socketio").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

di_container = DiContainerCoinrat()


@click.group('coinrat')
@click.version_option(version='0.1')
@click.help_option()
@click.pass_context
def cli(ctx: Context) -> None:
    pass


@cli.command(help='Shows available markets.')
def markets() -> None:
    click.echo('Available markers:')
    for plugin in di_container.market_plugins.get_available_market_plugins():
        click.echo('  - {}: {}'.format(plugin.get_name(), plugin.get_description()))
        for market_name in plugin.get_available_markets():
            click.echo('    - {}'.format(market_name))


@cli.command(help='Shows market plugin detail.')
@click.argument('market_name', nargs=1)
@click.option(
    '--market_plugin',
    help='Specify the name of plugin used for communication with stockmarket.',
    required=True
)
def market(market_name: str, market_plugin: str) -> None:
    try:
        market_plugin_obj: MarketPluginSpecification = di_container.market_plugins.get_plugin(market_plugin)
    except MarketPluginDoesNotExistsException as e:
        print_error_and_terminate(str(e))

    try:
        market_obj = market_plugin_obj.get_market_class(market_name)
    except MarketNotProvidedByPluginException as e:
        print_error_and_terminate(str(e))

    click.echo('Markets configuration structure:')
    print_structure_configuration(market_obj.get_configuration_structure())
    click.echo()


@cli.command(help='Shows available synchronizers.')
def synchronizers() -> None:
    synchronizer_plugins = di_container.synchronizer_plugins

    click.echo('Available synchronizers and markets supported by them:')
    for synchronizer_name in synchronizer_plugins.get_available_synchronizers():
        click.echo('  - {}'.format(synchronizer_name))
        synchronizer = synchronizer_plugins.get_synchronizer(synchronizer_name, NullCandleStorage(), NullEventEmitter())
        for market_name in synchronizer.get_supported_markets():
            click.echo('    - {}'.format(market_name))


@cli.command(help='Shows available candle storages.')
def candle_storages() -> None:
    click.echo('Available candle storages:')
    for storage_name in di_container.candle_storage_plugins.get_available_candle_storages():
        click.echo('  - {}'.format(storage_name))


@cli.command(help='Shows available order storages.')
def order_storages() -> None:
    click.echo('Available order storages:')
    for storage_name in di_container.order_storage_plugins.get_available_order_storages():
        click.echo('  - {}'.format(storage_name))


@cli.command(help='Shows available portfolio snapshot storages.')
def portfolio_snapshots() -> None:
    click.echo('Available portfolio snapshot storages:')
    for storage_name in di_container.portfolio_snapshot_storage_plugins.get_available_portfolio_snapshot_storages():
        click.echo('  - {}'.format(storage_name))


@cli.command(help='Shows available strategies.')
def strategies() -> None:
    click.echo('Available strategies:')
    for strategy_name in di_container.strategy_plugins.get_available_strategies():
        click.echo('  - {}'.format(strategy_name))


@cli.command(help='Shows strategy detail.')
@click.argument('strategy_name', nargs=1)
def strategy(strategy_name) -> None:
    try:
        strategy_obj: Market = di_container.strategy_plugins.get_strategy_class(strategy_name)
    except StrategyNotProvidedByAnyPluginException as e:
        print_error_and_terminate(str(e))

    click.echo('Strategy configuration structure:')
    print_structure_configuration(strategy_obj.get_configuration_structure())
    click.echo()
    click.echo(click.style(
        'You can provide this configuration via JSON file into `run_strategy` command using -c argument.\n',
        fg="green"
    ))


@cli.command(help="""
Exports candles into JSON file. Interval must be in UTC. \n\nExample: \n\n
    "python -m coinrat export_candles bittrex USD BTC \'2017-12-02T00:00:00\' \'2017-12-03T00:00:00\' output.json"
""")
@click.argument('market_name', nargs=1)
@click.argument('pair', nargs=2)
@click.argument('interval', nargs=2)
@click.argument('output_file', nargs=1)
@click.option('--candle_storage', help='Specify candle storage to be exported from.', required=True)
@click.pass_context
def export_candles(
    ctx: Context,
    market_name,
    pair: Tuple[str, str],
    interval: Tuple[str, str],
    output_file: str,
    candle_storage: str
) -> None:
    storage = di_container.candle_storage_plugins.get_candle_storage(candle_storage)
    pair_obj = Pair(pair[0], pair[1])
    interval_obj = DateTimeInterval(
        dateutil.parser.parse(interval[0]).replace(tzinfo=datetime.timezone.utc),
        dateutil.parser.parse(interval[1]).replace(tzinfo=datetime.timezone.utc)
    )
    exporter = CandleExporter(storage)
    exporter.export_to_file(output_file, market_name, pair_obj, interval_obj)


@cli.command(help="""
Exports orders into JSON file. Interval must be in UTC.

Example:
    "python -m coinrat export_orders bittrex USD BTC \'2017-12-02T00:00:00\' \'2017-12-03T00:00:00\' output.json --order_storage influx_db_orders-A"
""")
@click.argument('market_name', nargs=1)
@click.argument('pair', nargs=2)
@click.argument('interval', nargs=2)
@click.argument('output_file', nargs=1)
@click.option('--order_storage', help='Specify order storage to be exported from.', required=True)
@click.pass_context
def export_orders(
    ctx: Context,
    market_name,
    pair: Tuple[str, str],
    interval: Tuple[str, str],
    output_file: str,
    order_storage: str
) -> None:
    storage = di_container.order_storage_plugins.get_order_storage(order_storage)
    pair_obj = Pair(pair[0], pair[1])
    interval_obj = DateTimeInterval(
        dateutil.parser.parse(interval[0]).replace(tzinfo=datetime.timezone.utc),
        dateutil.parser.parse(interval[1]).replace(tzinfo=datetime.timezone.utc)
    )
    exporter = OrderExporter(storage)
    exporter.export_to_file(output_file, market_name, pair_obj, interval_obj)


@cli.command(help="""
Runs synchronization process. Synchronizes data from market into local database for analysis and strategies.

Example:
    python -m coinrat synchronize cryptocompare USD BTC
""")
@click.argument('synchronizer_name', nargs=1)
@click.argument('market', nargs=1)
@click.argument('pair', nargs=2)
@click.option('--candle_storage', help='Specify candle storage to be synced into.', required=True)
@click.pass_context
def synchronize(ctx: Context, synchronizer_name: str, market: str, pair: Tuple[str, str], candle_storage: str) -> None:
    pair_obj = Pair(pair[0], pair[1])

    synchronizer = di_container.synchronizer_plugins.get_synchronizer(
        synchronizer_name,
        market,
        di_container.candle_storage_plugins.get_candle_storage(candle_storage),
        di_container.event_emitter
    )

    available_markets = synchronizer.get_supported_markets()
    if market not in available_markets:
        print_error_and_terminate('Market "{}" is not supported by plugin "{}".'.format(market, synchronizer_name))

    synchronizer.synchronize(market, pair_obj)


@cli.command(help="""
Starts trading with given strategy.

Example:
    python -m coinrat run_strategy double_crossover bittrex
""")
@click.argument('strategy_name', nargs=1)
@click.argument('pair', nargs=2)
@click.argument('market_names', nargs=-1)
@click.option(
    '-c',
    '--configuration_file',
    help='Configuration file with JSON configuration for strategy.' \
         + ' Run `python -m coinrat strategy <strategy name>` to see the structure' \
         + 'You can check if strategy module has `example_configuration.json` bundled.',
    default=None
)
@click.option('--candle_storage', help='Specify candle storage to be used in this run.', required=True)
@click.option('--order_storage', help='Specify order storage to be used in this run.', required=True)
@click.option(
    '--market_plugin',
    help='Specify the name of plugin used for communication with stockmarket.',
    required=True
)
@click.pass_context
def run_strategy(
    ctx: Context,
    strategy_name: str,
    pair: Tuple[str, str],
    market_names: Tuple[str],
    configuration_file: Union[str, None],
    candle_storage: str,
    order_storage: str,
    market_plugin: str
) -> None:
    pair_obj = Pair(pair[0], pair[1])
    strategy_configuration: Dict = {}
    if configuration_file is not None:
        strategy_configuration = load_configuration_from_file(configuration_file)

    strategy_run_at = di_container.datetime_factory.now()

    strategy_run = StrategyRun(
        uuid.uuid4(),
        strategy_run_at,
        pair_obj,
        [StrategyRunMarket(market_plugin, market_name, {}) for market_name in market_names],
        strategy_name,
        strategy_configuration,
        DateTimeInterval(strategy_run_at, None),
        candle_storage,
        order_storage
    )
    di_container.strategy_run_storage.insert(strategy_run)
    di_container.event_emitter.emit_new_strategy_run(strategy_run)

    try:
        di_container.strategy_standard_runner.run(strategy_run)

    except StrategyNotProvidedByAnyPluginException as e:
        _terminate_strategy_run(strategy_run)
        print_error_and_terminate(str(e))

    except ForEndUserException as e:
        _terminate_strategy_run(strategy_run)
        print_error_and_terminate(str(e))

    except KeyboardInterrupt:
        _terminate_strategy_run(strategy_run)
        pass


def _terminate_strategy_run(strategy_run: StrategyRun) -> None:
    closed_interval = strategy_run.interval.with_till(di_container.datetime_factory.now())
    strategy_run.interval = closed_interval
    di_container.strategy_run_storage.update(strategy_run)


def load_configuration_from_file(configuration_file: str) -> Dict:
    with open(configuration_file) as json_file:
        return json.load(json_file)


@cli.command(help="Starts an socket server for communication with frontend.")
@click.pass_context
def start_server(ctx: Context):
    di_container.socket_server.start()

    def on_exception(exception: Exception):
        logger.critical('RABBIT CONSUMER RESTART: Got exception %r', exception)
        di_container.create_rabbit_consumer(ThreadWatcher(on_exception)).start()

    di_container.create_rabbit_consumer(ThreadWatcher(on_exception)).start()


@cli.command(help="Runs consumer of planned tasks.")
@click.pass_context
def start_task_consumer(ctx: Context):
    di_container.task_consumer.run()


@cli.command(help="Runs migrations, make schema up-to date.")
@click.pass_context
def database_migrate(ctx: Context):
    run_db_migrations(di_container.mysql_connection)


def print_structure_configuration(structure: Dict) -> None:
    if structure == {}:
        click.echo('    This market has no configuration.')
        return

    click.echo('    {:<40} {:<20} <title> (<unit>) - <description>'.format('<name>:<type>', '<default_value>', ))

    for key, value in structure.items():
        if 'hidden' in value and value['hidden'] is True:
            continue

        title = value['title'] if 'title' in value else ''
        description = ' - ' + value['description'] if 'description' in value else ''
        unit = ' ({})'.format(value['unit']) if 'unit' in value and value['unit'] != '' else ''

        click.echo('    {:<40} {:<20} {}{}{}'.format(
            key + ':' + value['type'],
            value['default'],
            title,
            unit,
            description
        ))


def print_error_and_terminate(error_message: str) -> NoReturn:
    click.echo(click.style('ERROR: {}\n'.format(error_message), fg='red'), err=True)
    sys.exit(1)


def main():
    cli(obj={})
