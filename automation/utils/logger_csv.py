#!/usr/bin/python3
"""
Provides 2 loggers that send output to CSVs with configs set here.
    draw_log - saves info relevant to draws
    rest_log - saves info before and after rests
"""

import logging

from csv_logger import CsvLogger

delimiter = ","
size_limit = 8192  # 8 kilobytes
draw_header = [
    "date",
    "id",
    "check_save",
    "result_int",
    "result_str",
    "DR",
    "type",
    "mod",
    "upper_lower",
    "draw_n",
]

draw_log = CsvLogger(
    filename="./automation/_output/log_draws.csv",
    delimiter=delimiter,
    level=logging.INFO,
    # add_level_names=["check", "save"],
    add_level_nums=None,
    fmt=f"%(asctime)s{delimiter}%(message)s",
    datefmt="%m/%d %H:%M:%S",
    max_size=size_limit,
    max_files=4,  # 4 rotating files
    header=draw_header,
)

# draw_log.check([int,str,DR,type,mod,upper_lower,draw_n])
# rest_log.before([type,discards,hand,HP,AP,PP,RestCards])

rest_header = [
    "date",
    "id",
    "before_after",
    "type",
    "discards",
    "hand",
    "HP",
    "AP",
    "PP",
    "RestCards",
]

rest_log = CsvLogger(
    filename="./automation/_output/log_rests.csv",
    delimiter=delimiter,
    level=logging.INFO,
    add_level_nums=None,
    fmt=f"%(asctime)s{delimiter}%(message)s",
    datefmt="%m/%d %H:%M:%S",
    max_size=size_limit,
    max_files=4,  # 4 rotating files
    header=rest_header,
)
