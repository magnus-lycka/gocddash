from .characterize_console_parser import TexttestConsoleParser
from .junit_report_parser import JunitConsoleParser
from gocddash.util.pipeline_config import get_pipeline_config

parser_info = {'junit': JunitConsoleParser, 'characterize': TexttestConsoleParser}


def get_parser_info(parser_name):
    return parser_info.get(parser_name, JunitConsoleParser)


def get_log_parser(pipeline_name):
    parser_name = get_pipeline_config().get_log_parser_name(pipeline_name)
    return get_parser_info(parser_name)
