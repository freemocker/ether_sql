import os
from subprocess import call
from click.testing import CliRunner
from ether_sql.cli import cli
from ether_sql.models import (
    base,
    Blocks,
    Transactions,
    Receipts,
    Uncles,
    Logs,
    Traces,
)
from tests.common_tests.expected_data import (
    EXPECTED_BLOCK_PROPERTIES,
    EXPECTED_UNCLE_PROPERTIES,
    EXPEXTED_TRANSACTION_PROPERTIES,
    EXPECTED_RECEIPT_PROPERTIES,
    EXPECTED_LOG_PROPERTIES,
    EXPECTED_TRACE_PROPERTIES,
)


def export_to_csv_single_thread(node_session_block_56160):
    directory = 'test_export'
    call(["rm", "-rf", directory])
    runner = CliRunner()
    result = runner.invoke(cli, ['--settings',
                                 node_session_block_56160.setting_name,
                                 'sql', 'export_to_csv',
                                 '--directory', directory])
    assert result.exit_code == 0
    # match the names of exported tables
    tables_in_sql = list(base.metadata.tables)
    files_in_directory = os.listdir(directory)
    for sql_table in tables_in_sql:
        assert sql_table+'.csv' in files_in_directory
    call(["rm", "-rf", directory])


def verify_block_contents(node_session_block_56160):
    # comparing values of blocks
    node_session_block_56160.setup_db_session()
    block_properties_in_sql = node_session_block_56160.db_session.\
        query(Blocks).filter_by(block_number=56160).first().to_dict()
    assert block_properties_in_sql == EXPECTED_BLOCK_PROPERTIES

    # comparing values of uncles
    uncle_properties_in_sql = node_session_block_56160.db_session.\
        query(Uncles).filter_by(current_blocknumber=56160).first().to_dict()
    assert uncle_properties_in_sql == EXPECTED_UNCLE_PROPERTIES

    # comparing values of transactions
    transaction_properties_in_sql = node_session_block_56160.db_session.\
        query(Transactions).filter_by(block_number=56160).first().to_dict()
    assert transaction_properties_in_sql == EXPEXTED_TRANSACTION_PROPERTIES

    # comparing values of receipts
    receipt_properties_in_sql = node_session_block_56160.db_session.\
        query(Receipts).filter_by(block_number=56160).first().to_dict()
    assert receipt_properties_in_sql == EXPECTED_RECEIPT_PROPERTIES

    # comparing values of logs
    log_properties_in_sql = node_session_block_56160.db_session.\
        query(Logs).filter_by(block_number=56160).first().to_dict()
    assert log_properties_in_sql == EXPECTED_LOG_PROPERTIES

    # comparing values of traces
    if node_session_block_56160.settings.PARSE_TRACE:
        trace_properties_in_sql = node_session_block_56160.\
            db_session.query(Traces).filter_by(block_number=56160).first().\
            to_dict()
        assert trace_properties_in_sql == EXPECTED_TRACE_PROPERTIES


def push_block_range_single_thread(settings_name):
    runner = CliRunner()
    result = runner.invoke(cli, ['--settings', settings_name,
                                 'scrape_block_range',
                                 '--start_block_number', 0,
                                 '--end_block_number', 10])
    assert result.exit_code == 0
