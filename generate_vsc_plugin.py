from gen_coloring.generators.plugin_generator import VSCPluginGenerator
from gen_coloring.input.command_arguments import CommandArguments


if __name__ == '__main__':
    args = CommandArguments().parse_args()
    plugin_generator = VSCPluginGenerator(args)
    plugin_generator.generate()
