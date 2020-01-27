from textx import TextXSemanticError
from ..utils import check_regex, raise_semantic_error, is_keyword, load_jinja2_template
import json
from textx import metamodel_from_file
from os.path import join, dirname


class FromTextXGrammarGenerator:

    def __init__(self, grammar_path, grammar_pattern_rep):
        self.grammar_path = grammar_path
        self.rep = grammar_pattern_rep
        textX = metamodel_from_file("grammar/textX.tx")
        grammar_model = textX.model_from_file(self.grammar_path)

        terminals = self._get_terminals(grammar_model)
        self.keywords = [x for x in terminals if is_keyword(x)]
        self.operators = [x for x in terminals if not is_keyword(x)]
        self.keywords.sort(key=len, reverse=True)
        self.operators.sort(key=len, reverse=True)
        self.comments = self._get_comments(grammar_model)
        # print(self.keywords)

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
        ret_val = []
        for rule in grammar_model.rules:
            try:
                for sequence in rule.body.sequences:
                    try:
                        for rep_expr in sequence.repeatable_expr:
                            try:
                                str_match = rep_expr.expr.simple_match.str_match
                                terminal = str_match.match
                                ret_val.append(terminal)
                            except AttributeError:
                                pass
                    except AttributeError:
                        pass
            except AttributeError:
                pass
        return ret_val

    def _generate_keywords_and_operators(self):
        keyword_regex = "|".join(self.keywords)
        operator_regex = "|".join(self.operators)

        if not "repository" in self.rep:
            self.rep["repository"] = {}

        self.rep["patterns"].append({
            "include": "#keywords"
        })
        self.rep["patterns"].append({
            "include": "#operators"
        })

        self.rep["repository"]["keywords"] = {
            "match": keyword_regex, "name": "keyword"}
        self.rep["repository"]["operators"] = {
            "match": operator_regex, "name": "keyword.other"}

    def _generate_comments(self):

        for ind, comment in enumerate(self.comments):
            self.rep["patterns"].append({
                "include": "#comment"+str(ind+1)
            })

            self.rep["repository"]["comment"+str(ind+1)] = {
                "match": comment, "name": "comment"}

    def generate(self):
        self._generate_keywords_and_operators()
        self._generate_comments()


class TextMateMatchStatement:
    def __init__(self, regex, scope_name):
        self.regex = json.dumps(regex)
        self.scope_name = scope_name


class TextMateCompoundStatement:
    def __init__(self, name, begin_regex, end_regex):
        self.name = name
        self.begin_regex = json.dumps(begin_regex)
        self.end_regex = json.dumps(end_regex)
        self.begin_captures_dict = {}
        self.end_captures_dict = {}


class TextMatePattern:
    def __init__(self, name):
        self.name = name
        self.include_statements = []
        self.match_statements = []
        self.compound_statements = []


class TextMateGrammarGenerator:

    def __init__(self, model):
        self.model = model

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
            pattern.include_statements.append(include.pattern)

    def _generate_match_from_file_statement(self, match_from_file, patterns):
        FromTextXGrammarGenerator(
            match_from_file.grammar_path, patterns).generate()

    def _generate_match_statement(self, match, pattern):
        check_regex(match.regex, ast_node=match, model=self.model)
        pattern.match_statements.append(
            TextMateMatchStatement(match.regex, match.scope_name))

    def _generate_captures(self, captures_dict, names):
        for i in range(len(names)):
            captures_dict[str(i+1)] = names[i]

    def _generate_compound_statement(self, label_set, compound, pattern):
        check_regex(compound.begin_regex,
                    ast_node=compound, model=self.model)
        check_regex(compound.end_regex,
                    ast_node=compound, model=self.model)
        compound_statement = TextMateCompoundStatement(
            compound.scope_name, compound.begin_regex, compound.end_regex)
        pattern.compound_statements.append(compound_statement)

        self._generate_captures(
            compound_statement.begin_captures_dict, compound.begin_names)
        self._generate_captures(
            compound_statement.end_captures_dict, compound.end_names)

        for statement in compound.statements:
            if statement.include:
                pass
                # self._generate_include_statement(
                # label_set, statement.include, )
            elif statement.match:
                pass
                # self._generate_match_statement(
                # statement.match, )

    def _generate_repository_patterns(self, label_set):
        all_patterns = []
        for grammar_pattern in self.model.grammar_patterns:

            all_patterns.append(TextMatePattern(grammar_pattern.name))

            for statement in grammar_pattern.statements:
                if statement.include:
                    self._generate_include_statement(
                        label_set, statement.include, all_patterns[-1])
                elif statement.match:
                    self._generate_match_statement(
                        statement.match, all_patterns[-1])
                elif statement.compound:
                    self._generate_compound_statement(label_set,
                                                      statement.compound, all_patterns[-1])
                elif statement.match_from_file:
                    pass
                    # self._generate_match_from_file_statement(
                    # statement.match_from_file, repository[grammar_pattern.name])
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
        template = load_jinja2_template("static/syntaxes/language.json")
        start_patterns = self._generate_start_patterns(label_set)
        all_patterns = self._generate_repository_patterns(label_set)
        return template.render(
            name=self.model.scope_name,
            start_patterns=start_patterns,
            all_patterns=all_patterns)
