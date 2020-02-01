import argparse


class CommandArguments:

    def __init__(self):
        self._args = None
        self._parser = argparse.ArgumentParser(
            description="Command-line argument processor. The program should be used \
            according to the following instructions:")
        self._parser.add_argument(
            "grammar_path", metavar="Grammar path", help="Path to the grammar", type=str)
        self._parser.add_argument(
            "name", metavar="Name", help="Name of the new language", type=str)
        self._parser.add_argument(
            "extension", metavar="Extension", help="Language file extension", type=str)

        self._parser.add_argument(
            "-display_name", metavar="Display name", type=str, default=None,
            help="Name of the language(to display). If omitted same as language name.")
        self._parser.add_argument(
            "-description", metavar="Description", type=str, default=None,
            help="Language description")
        self._parser.add_argument(
            "-language", metavar="Language", type=str, default=None,
            help="Language grammar name. If omitted, same as language name")

    def parse_args(self):
        self._args = vars(self._parser.parse_args())
        return self

    def __getattr__(self, name):
        return self._args[name]

    def __getitem__(self, key):
        return self._args[key]


if __name__ == '__main__':
    cmd_args = CommandArguments()
    cmd_args.parse_args()
    print(cmd_args.grammar_path)
    print(cmd_args.name)
    print(cmd_args.extension)
