# EasyColorLang - Writing of TextMate grammars made easy

## Intro

EasyColorLang is a domain specific language (DSL) which enables you to generate [TextMate](https://macromates.com/manual/en/language_grammars) grammars used for
language coloring. Although the json format of these grammars is fairly flexible and readable, they tend to get complex relatively quickly.
This makes expanding and maintaining them much harder. Some solutions have been proposed, with the main one being converting the grammar to [Yaml](https://yaml.org/).
Afterwards, one could do the required editing, then convert back. In order to further cut the development time and costs, this DSL has been developed.
It uses [textX](https://github.com/textX/textX), a meta language for writing DSLs, for parsing and AST generating. [Jinja2](https://jinja.palletsprojects.com/en/2.11.x/), a template language,
is used to generate properly formatted json.

## Examples

EasyColorLang language files typically have .eclr extension. They are composed of one or more patterns. Each pattern has one or more statements.
There are different types of statements which will be discussed below. At the end of every file there is a special start statement. In this statement, it
is possible to specify scope name, as well as starting patterns for matching.

```
#main:
    begin: "entity" names: "keyword"
    end: "{" names: "keyword.other"
    (match: "[a-zA-Z][a-zA-Z_0-9]*" name: "support.class")

    begin: "[a-zA-Z][a-zA-Z_0-9]*" names: "markup.italic"
    end: "[a-zA-Z][a-zA-Z_0-9]*" names: "entity.name.function"
    (match:"\s*:\s*" name:"keyword.other")

    matches_from_grammar: "entity.tx"
start entity(main)
```

The example above compiles to the following json:

```javascript
{
    "name": "entity",
    "scopeName": "source.entity",
    "patterns": [
        {
            "include": "#main"
        }
    ],
    "repository": {
        "main": {
            "patterns": [
                {
                    "begin": "entity",
                    "end": "{",
                    "beginCaptures": {
                        "0": {
                            "name": "keyword"
                        }
                    },
                    "endCaptures": {
                        "0": {
                            "name": "keyword.other"
                        }
                    },
                    "patterns": [
                        {
                            "match": "[a-zA-Z][a-zA-Z_0-9]*",
                            "name": "support.class"
                        }
                    ]
                },
                {
                    "begin": "[a-zA-Z][a-zA-Z_0-9]*",
                    "end": "[a-zA-Z][a-zA-Z_0-9]*",
                    "beginCaptures": {
                        "0": {
                            "name": "markup.italic"
                        }
                    },
                    "endCaptures": {
                        "0": {
                            "name": "entity.name.function"
                        }
                    },
                    "patterns": [
                        {
                            "match": "\\s*:\\s*",
                            "name": "keyword.other"
                        }
                    ]
                },
                {
                    "match": "entity|type",
                    "name": "keyword"
                },
                {
                    "match": "}|{|:",
                    "name": "keyword.other"
                },
                {
                    "match": "\\/\\/.*$",
                    "name": "comment"
                }
            ]
        }
    }
}
```

An example file in this _Entity_ language looks like this in IDE (Visual Studio Code):

![Error](https://raw.githubusercontent.com/IgorMaj/SyntaxColoring/master/art/entity_example.PNG)

## Setup and use

After cloning/downloading the repository, the easiest way is to run the following script:

`python generate_vsc_plugin.py examples/color/color.eclr EasyColorLang .eclr`

This will generate the whole Visual Studio Code plugin for syntax highlighting. The IDE will need
to be restarted in order for changes to take effect. Required positional arguments are: _path to the eclr grammar file_,
_language name_ and _language file extension_. There are also optional arguments such as _-description_. You can call the script with
_-h_ argument to see them all.
This project was developed using _textX_ and it is possible to register it as its language and textmate generator.
One easy way to do this is to run the following command in the project directory:

`pip install .`

Afterwards, it is possible to check if textX can find the language and generator:

```
   textx list-generators
   textx list-languages
```

To generate the textmate json you can run the following command:

```
textX generate --target textmate ./examples/color/color.eclr --output-path output.json
```

See the [docs](https://textx.github.io/textX/stable/registration/) for more details.

## Language grammar

EasyColorLang has a relatively simple, yet flexible grammar. A typical file is composed of one or more patterns with the following
syntax:

```
#pattern_example:
  statements...
```

Defining the same pattern (same name) twice will result in a semantic error.
At the end of the file there is a special start statement which specifies scope name, as well as starting patterns:

```
start scope_name(start_pattern1,start_pattern2...)
```

### Comments

EasyColorLang supports single line comments `//` as well as multi-line (block) comments `/* example content */`.

### Pattern statements

There are several types of pattern statements. Include statements can include other pattern references in their parent pattern.

```
include: other_pattern_name
```

Referencing non existing pattern name will result in a semantic error.

Match statement takes scope name and Ruby regular expression:

```
match: "some_regex" name: "some.textmate.scope"
```

Matches from grammar is a special kind of statement designed to speed up grammar development, if _textX_ grammar
is already available. It automatically extracts keywords, operators and comments:

```
matches_from_grammar: "robot.tx" (
        keywords: "keyword"
        operators: "keyword.other"
        //string_literals: "string"
        numeric_literals: "constant.numeric"
    ) // Paren config expression is optional
      // this is also valid -> matches_from_grammar: "robot.tx"

```

As can be seen it is possible to specify scope name for keywords, operators and literals. Keywords and operators have default scopes,
while literals need to be specified if one wants them highlighted at all.

Compound statements are composed out of other statements. They have a beginning and an end match. Other statements can be nested inside them, including other compound statements. The have the following syntax:

```
    begin: "regex1" names: "name1","name2"...
    end: "regex2" names: "name1","name2"...
    name: "keyword"? (
        statements
    )?
```

The _?_ sign means that the statement part is optional. In this example _name_ part and paren expression _()_ which contains other statements are optional.

## License

This project is licensed under the MIT License
