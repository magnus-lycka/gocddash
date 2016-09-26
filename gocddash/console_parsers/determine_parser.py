from .characterize_console_parser import TexttestConsoleParser
from .junit_report_parser import JunitConsoleParser

parser_info = {'junit': JunitConsoleParser, 'characterize': TexttestConsoleParser}


def get_parser_info(parser_name):
    return parser_info.get(parser_name, JunitConsoleParser)
