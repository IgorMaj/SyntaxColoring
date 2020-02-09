import json
from .textmate_generator import TextMateGrammarGenerator
from pathlib import Path
from ..utils import get_home_dir, remove_dir, copy_file, dump_to_file, \
    get_filename_no_ext, value_or_default_if_none, load_json_file, extract_relative_path
from . import MODULE_DIR_PATH
from . import load_metamodel
from os.path import join

ROOT_PATH = join(MODULE_DIR_PATH, "..", "static")


class VSCPluginGenerator:

    def __init__(self, args):
        self._meta_model = load_metamodel()
        self._args = args
        self._file_list = self._get_file_list()

    def _get_file_list(self):
        ret_val = []
        for path in Path(ROOT_PATH).rglob("*.*"):
            if not path.is_dir():
                ret_val.append(str(path))
        return ret_val

    def _generate_package_json(self, plugin_path, package_path, scope_name, grammar_path):
        package_json_obj = load_json_file(package_path)

        package_json_obj["name"] = self._args.name
        package_json_obj["displayName"] = value_or_default_if_none(
            self._args.display_name, self._args.name)
        package_json_obj["description"] = value_or_default_if_none(
            self._args.description, "Description of: "+self._args.name)

        package_json_obj["contributes"]["languages"][0]["id"] = self._args.name
        package_json_obj["contributes"]["languages"][0]["aliases"] = [value_or_default_if_none(
            self._args.display_name, self._args.name)]
        package_json_obj["contributes"]["languages"][0]["extensions"] = [
            self._args.extension]

        package_json_obj["contributes"]["grammars"][0]["language"] = value_or_default_if_none(
            self._args.language, self._args.name)
        package_json_obj["contributes"]["grammars"][0]["scopeName"] = scope_name
        package_json_obj["contributes"]["grammars"][0]["path"] = grammar_path

        dump_to_file(json.dumps(package_json_obj, indent=4),
                     join(plugin_path, "package.json"))

    def _generate_syntax(self, plugin_path):
        model = self._meta_model.model_from_file(self._args.grammar_path)
        generator = TextMateGrammarGenerator(model)
        generated_str = generator.generate()
        relative_grammar_path = join("syntaxes",
                                     get_filename_no_ext(self._args.grammar_path)+".tmLanguage.json")
        dump_to_file(generated_str,
                     join(plugin_path, relative_grammar_path))
        return json.loads(generated_str), relative_grammar_path

    def generate(self):
        plugin_path = join(
            get_home_dir(), ".vscode", "extensions", self._args.name)
        remove_dir(plugin_path)
        grammar, grammar_path = self._generate_syntax(plugin_path)
        for file_path in self._file_list:
            if file_path.endswith(join("static", "package.json")):
                self._generate_package_json(
                    plugin_path, file_path, grammar["scopeName"], grammar_path)
            else:
                copy_file(file_path, join(plugin_path,
                                          extract_relative_path(file_path, "static")))
