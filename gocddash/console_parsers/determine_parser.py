from .characterize_console_parser import TexttestConsoleParser
from .default_console_parser import DefaultConsoleParser
from .junit_report_parser import JunitConsoleParser

parser_info = {'junit': JunitConsoleParser, 'characterize': TexttestConsoleParser}


def get_parser_info(parser):
    if parser in parser_info:
        return parser_info[parser]
    return DefaultConsoleParser
