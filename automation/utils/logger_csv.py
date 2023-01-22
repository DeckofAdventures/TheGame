#!/usr/bin/python3

import logging

from csv_logger import CsvLogger

delimiter = ","
size_limit = 8192  # 8 kilobytes
drawheader = [
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

drawlog = CsvLogger(
    filename="./automation/_output/log_draws.csv",
    delimiter=delimiter,
    level=logging.INFO,
    # add_level_names=["check", "save"],
    add_level_nums=None,
    fmt=f"%(asctime)s{delimiter}%(message)s",
    datefmt="%m/%d %H:%M:%S",
    max_size=size_limit,
    max_files=4,  # 4 rotating files
    header=drawheader,
)

# drawlog.check([int,str,DR,type,mod,upper_lower,draw_n])
# restlog.before([type,discards,hand,HP,AP,PP,RestCards])

restheader = [
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

restlog = CsvLogger(
    filename="./automation/_output/log_rests.csv",
    delimiter=delimiter,
    level=logging.INFO,
    # add_level_names=["before", "after"],
    add_level_nums=None,
    fmt=f"%(asctime)s{delimiter}%(message)s",
    datefmt="%m/%d %H:%M:%S",
    max_size=size_limit,
    max_files=4,  # 4 rotating files
    header=restheader,
)
