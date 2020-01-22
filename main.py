from code.generators.PluginGenerator import PluginGenerator
from code.input.CommandArguments import CommandArguments


if __name__ == '__main__':
    args = CommandArguments().parse_args()
    plugin_generator = PluginGenerator(args)
    plugin_generator.generate()
