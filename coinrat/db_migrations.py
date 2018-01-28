import logging
import MySQLdb
import os

logger = logging.getLogger(__name__)
current_directory = os.path.dirname(__file__)

yml_file_template = """databases:
    coinrat:
        engine: mysql
        host: {}
        port: 3306
        user: {}
        password: {}
        db: {}
        path: db_schema/
     
    coinrat_test:
        engine: mysql
        host: {}
        port: 3306
        user: {}
        password: {}
        db: {}
        path: db_schema/
"""


def run_db_migrations(mysql_connection: MySQLdb.Connection, tag='coinrat'):
    create_yml_file_for_migration_lib()
    create_migrations_table_if_not_exists(mysql_connection)
    os.system("dbschema --config db_schema/migrations.yml --tag " + tag)


def create_migrations_table_if_not_exists(mysql_connection: MySQLdb.Connection):
    cursor = mysql_connection.cursor()
    cursor.execute("SHOW TABLES LIKE 'migrations_applied'")
    if cursor.fetchone() is None:
        logger.info('Migrations table: "migrations_applied" does not exists. Creating.')
        cursor.execute(
            """CREATE TABLE `migrations_applied` (
            `id` INT NOT NULL AUTO_INCREMENT,
            `name` VARCHAR(256) NOT NULL,
            `date` DATETIME NOT NULL,
            PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=`utf8`;""")


def create_yml_file_for_migration_lib():
    with open(os.path.join(current_directory, '../db_schema/migrations.yml'), 'w+') as migrations_config:
        migrations_config.write(yml_file_template.format(
            os.environ.get('MYSQL_HOST'),
            os.environ.get('MYSQL_USER'),
            os.environ.get('MYSQL_PASSWORD'),
            os.environ.get('MYSQL_DATABASE'),
            os.environ.get('MYSQL_HOST'),
            os.environ.get('MYSQL_USER'),
            os.environ.get('MYSQL_PASSWORD'),
            os.environ.get('MYSQL_DATABASE') + '_test'
        ))
