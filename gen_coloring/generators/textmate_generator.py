from os.path import join, dirname
from textx import metamodel_from_file
import json
from textx import TextXSemanticError
from ..utils import check_regex, raise_semantic_error, is_keyword,\
    load_jinja2_template, pretty_render
from . import MODULE_DIR_PATH


class TextMatePattern:
    def __init__(self, name):
        self.name = name
        self.statements = []


class TextMateCompoundStatement(TextMatePattern):
    def __init__(self, name, begin_regex, end_regex):
        super().__init__(name)
        self.begin_regex = json.dumps(begin_regex)
        self.end_regex = json.dumps(end_regex)
        self.begin_captures_dict = {}
        self.end_captures_dict = {}

    def __str__(self):
        template = load_jinja2_template("compound_statement.json")
        return template.render(compound_statement=self)


class TextMateIncludeStatement:

    def __init__(self, include_pattern):
        self.include_pattern = include_pattern

    def __str__(self):
        template = load_jinja2_template("include_statement.json")
        return template.render(include_pattern=self.include_pattern)


class TextMateMatchStatement:
    def __init__(self, regex, scope_name):
        self.regex = json.dumps(regex)
        self.scope_name = scope_name

    def __str__(self):
        template = load_jinja2_template("match_statement.json")
        return template.render(match_statement=self)


class TextXMateMatchFromGrammarStatement:

    def __init__(self, matches_from_grammar, root_dir):
        self.grammar_path = join(root_dir, matches_from_grammar.grammar_path)

        self.keyword_match = "keyword"
        self.operator_match = "keyword.other"
        self.string_literal_match = ""
        self.numeric_literal_match = ""

        self._set_match_config(matches_from_grammar)

        textX = metamodel_from_file(join(
            MODULE_DIR_PATH, "..", "grammar", "textX.tx"))
        grammar_model = textX.model_from_file(self.grammar_path)

        terminals = self._get_terminals(grammar_model)
        self.keywords = [x for x in terminals if is_keyword(x)]
        self.operators = [x for x in terminals if not is_keyword(x)]
        self.keywords.sort(key=len, reverse=True)
        self.operators.sort(key=len, reverse=True)
        self.comments = self._get_comments(grammar_model)

        self.statements = [
            TextMateMatchStatement(
                "|".join(self.keywords), self.keyword_match),
            TextMateMatchStatement(
                "|".join(self.operators), self.operator_match),
            TextMateMatchStatement("|".join(self.comments), "comment")
        ]

        if self.string_literal_match:
            self.statements.append(TextMateMatchStatement(
                "\"(\\.|[^\"])*\"", self.string_literal_match))
            self.statements.append(TextMateMatchStatement(
                "\'(\\.|[^\'])*\'", self.string_literal_match))

        if self.numeric_literal_match:
            self.statements.append(TextMateMatchStatement(
                "-?[0-9]+(\\.[0-9]+)?", self.numeric_literal_match))

    def _set_match_config(self, matches_from_grammar):
        for config_statement in matches_from_grammar.config_statements:
            if config_statement.__class__.__name__ == "KeyWordsConfigStatement":
                self.keyword_match = config_statement.regex
            elif config_statement.__class__.__name__ == "OperatorsConfigStatement":
                self.operator_match = config_statement.regex
            elif config_statement.__class__.__name__ == "StringsLiteralConfigStatement":
                self.string_literal_match = config_statement.regex
            elif config_statement.__class__.__name__ == "NumericLiteralsConfigStatement":
                self.numeric_literal_match = config_statement.regex

    def _get_comments(self, grammar_model):
        ret_val = []
        for rule in grammar_model.rules:
            if rule.name == "Comment":
                for sequence in rule.body.sequences:
                    try:
                        for rep_expr in sequence.repeatable_expr:
                            try:
                                re_match = rep_expr.expr.simple_match.re_match
                                regex = re_match.match
                                ret_val.append(regex)
                            except AttributeError:
                                pass
                    except AttributeError:
                        pass
                break
        return ret_val

    def _get_terminals(self, grammar_model):
        ret_val = set()
        for rule in grammar_model.rules:
            try:
                for sequence in rule.body.sequences:
                    try:
                        for rep_expr in sequence.repeatable_expr:
                            try:
                                str_match = rep_expr.expr.simple_match.str_match
                                terminal = str_match.match
                                ret_val.add(terminal)
                            except AttributeError:
                                pass
                    except AttributeError:
                        pass
            except AttributeError:
                pass
        return ret_val

    def __str__(self):
        template = load_jinja2_template("matches_from_grammar_statement.json")
        return template.render(match_from_file_statement=self)


class TextMateGrammarGenerator:

    def __init__(self, model):
        self.model = model
        self.model_file_dir = dirname(model._tx_filename)

    def _get_label_set(self):
        ret_val = set()
        for grammar_pattern in self.model.grammar_patterns:
            if grammar_pattern.name in ret_val:
                raise_semantic_error(
                    "Duplicate grammar pattern definition: "+grammar_pattern.name,
                    ast_node=grammar_pattern, model=self.model)
            ret_val.add(grammar_pattern.name)
        return ret_val

    def _generate_include_statement(self, label_set, include, pattern):
        if include.pattern not in label_set:
            raise_semantic_error(
                "Non existing pattern referenced: "+include.pattern,
                ast_node=include, model=self.model)
        else:
            pattern.statements.append(
                TextMateIncludeStatement(include.pattern))

    def _generate_matches_from_grammar_statement(self, matches_from_grammar, pattern):
        statement = TextXMateMatchFromGrammarStatement(
            matches_from_grammar, self.model_file_dir)
        pattern.statements.append(statement)

    def _generate_match_statement(self, match, pattern):
        check_regex(match.regex, ast_node=match, model=self.model)
        pattern.statements.append(
            TextMateMatchStatement(match.regex, match.scope_name))

    def _generate_captures(self, captures_dict, names):
        for i in range(len(names)):
            captures_dict[str(i)] = names[i]

    def _generate_compound_statement(self, label_set, compound, pattern):
        check_regex(compound.begin_regex,
                    ast_node=compound, model=self.model)
        check_regex(compound.end_regex,
                    ast_node=compound, model=self.model)
        compound_statement = TextMateCompoundStatement(
            compound.scope_name, compound.begin_regex, compound.end_regex)
        pattern.statements.append(compound_statement)

        self._generate_captures(
            compound_statement.begin_captures_dict, compound.begin_names)
        self._generate_captures(
            compound_statement.end_captures_dict, compound.end_names)

        self._generate_statements(label_set, compound, compound_statement)

    def _generate_statements(self, label_set, statement_container, pattern):
        for statement in statement_container.statements:
            if statement.include:
                self._generate_include_statement(
                    label_set, statement.include, pattern)
            elif statement.match:
                self._generate_match_statement(
                    statement.match, pattern)
            elif statement.compound:
                self._generate_compound_statement(label_set,
                                                  statement.compound, pattern)
            elif statement.matches_from_grammar:
                self._generate_matches_from_grammar_statement(
                    statement.matches_from_grammar, pattern)

    def _generate_repository_patterns(self, label_set):
        all_patterns = []
        for grammar_pattern in self.model.grammar_patterns:
            all_patterns.append(TextMatePattern(grammar_pattern.name))
            self._generate_statements(
                label_set, grammar_pattern, all_patterns[-1])
        return all_patterns

    def _generate_start_patterns(self, label_set):
        ret_val = []
        for start_expression in self.model.start_expressions:
            if start_expression not in label_set:
                raise_semantic_error(
                    "Non existing pattern referenced: "+start_expression,
                    ast_node=start_expression, model=self.model)
            ret_val.append(start_expression)
        return ret_val

    def generate(self):
        label_set = self._get_label_set()
        template = load_jinja2_template("language.json")
        start_patterns = self._generate_start_patterns(label_set)
        all_patterns = self._generate_repository_patterns(label_set)
        return pretty_render(template.render(
            name=self.model.scope_name,
            start_patterns=start_patterns,
            all_patterns=all_patterns))
