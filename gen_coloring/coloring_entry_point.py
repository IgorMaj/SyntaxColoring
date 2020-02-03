from textx import LanguageDesc, GeneratorDesc
from .generators import load_metamodel
from .generators.textmate_generator import TextMateGrammarGenerator
from .utils import dump_to_file


def easy_clr_metamodel():
    return load_metamodel()


def fast_textmate_generator(metamodel, model, output_path, overwrite, debug, **custom_args):
    ret_val = TextMateGrammarGenerator(model).generate()
    if not output_path:
        print(ret_val)
    else:
        dump_to_file(ret_val, output_path)
    return ret_val


easy_coloring_lang = LanguageDesc('EasyColorLang',
                                  pattern='*.eclr',
                                  description='Language made for easier writing of TextMate grammars',
                                  metamodel=easy_clr_metamodel)

textmate_gen_coloring = GeneratorDesc(
    language='EasyColorLang',
    target='textmate',
    description='Language made for easier writing of TextMate grammars',
    generator=fast_textmate_generator)
