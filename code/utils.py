import re
from textx import TextXSemanticError
import pathlib
from pathlib import Path
import shutil
import os
import json


def is_regex_valid(regex):
    try:
        re.compile(regex)
        return True
    except re.error:
        return False


def check_regex(regex, ast_node, model):
    if not is_regex_valid(regex):
        raise raise_semantic_error(
            "Regex is not valid: "+regex, ast_node, model)


def mkdirs(file_path):
    path = pathlib.Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)


def remove_dir(dir_path):
    try:
        shutil.rmtree(dir_path)
    except FileNotFoundError:
        pass


def copy_file(from_path, to_path):
    in_file = open(from_path, "r")
    dump_to_file(in_file.read(), to_path)
    in_file.close()


def get_filename_no_ext(path):
    try:
        return os.path.basename(path).split(".")[0]
    except IndexError:
        return os.path.basename(path)


def load_json_file(path):
    file = open(path, "r")
    ret_val = json.loads(file.read())
    file.close()
    return ret_val


def value_or_default_if_none(value1, value2):
    return value1 if value1 is not None else value2


def get_home_dir():
    return str(Path.home()).replace("\\", "/")


def dump_to_file(obj_string, file_path):
    mkdirs(file_path)
    file = open(file_path, "w")
    file.write(obj_string)
    file.close()


def raise_semantic_error(error_msg, ast_node, model):
    line, col = model._tx_parser.pos_to_linecol(
        ast_node._tx_position)
    raise TextXSemanticError(error_msg, line=line, col=col)
