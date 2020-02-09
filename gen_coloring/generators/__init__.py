from os.path import dirname, abspath, join
from textx import metamodel_from_file
from ..obj_preprocessors import match_from_file_preprocessor


MODULE_DIR_PATH = (dirname(abspath(__file__)))


def load_metamodel():
    meta_model = metamodel_from_file(
        join(MODULE_DIR_PATH, "..", "grammar", "coloring.tx"))
    meta_model.register_obj_processors(
        {'QuotedScopeName': lambda scope: scope.scopeName,
         'PatternId': lambda id: id[1:],  # to  remove '#'
         'MatchFromGrammarConfig': lambda config: config.statements,
         'MatchFromGrammarStatement': match_from_file_preprocessor
         })
    return meta_model
