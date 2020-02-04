# EasyColorLang - Writing of TextMate grammars made easy

## Intro

EasyColorLang is a domain specific language (DSL) which enables you to generate [TextMate](https://macromates.com/manual/en/language_grammars) grammars used for
language coloring. Although the json format of these grammars is fairly flexible and readable, they tend to get complex relatively quickly.
This makes expanding and maintaining much harder. Some solutions have been proposed, with the main one being converting the grammar to [Yaml](https://yaml.org/).
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

    match_from_file: "examples/entity/entity.tx"
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

After cloning/downloading the repository...

## Language grammar

//TODO language grammar explanation

## License

This project is licensed under the MIT License
