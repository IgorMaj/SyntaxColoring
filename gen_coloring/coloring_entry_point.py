from textx import LanguageDesc, GeneratorDesc
from .generators import load_metamodel
from .generators.textmate_generator import TextMateGrammarGenerator


def easy_clr_metamodel():
    return load_metamodel()


def fast_textmate_generator(metamodel, model, output_path, overwrite, debug, **custom_args):
    return TextMateGrammarGenerator(model).generate()


easy_coloring_lang = LanguageDesc('EasyColorLang',
                                  pattern='*.eclr',
                                  description='Language made for easier writing of TextMate grammars',
                                  metamodel=easy_clr_metamodel)

textmate_gen_coloring = GeneratorDesc(
    language='EasyColorLang',
    target='textmate',
    description='Language made for easier writing of TextMate grammars',
    generator=fast_textmate_generator)
