from textx import TextXSemanticError
from code.utils import check_regex, raise_semantic_error
import json


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

    def _generate_include_statement(self, label_set, include, patterns):
        if include.pattern not in label_set:
            raise_semantic_error(
                "Non existing pattern referenced: "+include.pattern,
                ast_node=include, model=self.model)
        else:
            patterns.append({
                "include": "#"+include.pattern
            })

    def _generate_match_statement(self, match, patterns):
        check_regex(match.regex, ast_node=match, model=self.model)
        patterns.append({"match": match.regex, "name": match.scope_name})

    def _generate_captures(self, captures_dict, names):
        for i in range(len(names)):
            captures_dict[str(i+1)] = {"name": names[i]}

    def _generate_compound_statement(self, label_set, compound, grammar_pattern_rep):
        grammar_pattern_rep["name"] = compound.scope_name

        check_regex(compound.begin_regex, ast_node=compound, model=self.model)
        grammar_pattern_rep["begin"] = compound.begin_regex

        check_regex(compound.end_regex, ast_node=compound, model=self.model)
        grammar_pattern_rep["end"] = compound.end_regex

        grammar_pattern_rep["beginCaptures"] = {}
        grammar_pattern_rep["endCaptures"] = {}
        self._generate_captures(
            grammar_pattern_rep["beginCaptures"], compound.begin_names)
        self._generate_captures(
            grammar_pattern_rep["endCaptures"], compound.end_names)

        for statement in compound.statements:
            if statement.include:
                self._generate_include_statement(
                    label_set, statement.include, grammar_pattern_rep["patterns"])
            elif statement.match:
                self._generate_match_statement(
                    statement.match, grammar_pattern_rep["patterns"])

    def _generate_repository(self, label_set, grammar_pattern, repository):
        repository[grammar_pattern.name] = {"patterns": []}
        for statement in grammar_pattern.statements:
            if statement.include:
                self._generate_include_statement(
                    label_set, statement.include, repository[grammar_pattern.name]["patterns"])
            elif statement.match:
                self._generate_match_statement(
                    statement.match, repository[grammar_pattern.name]["patterns"])
            elif statement.compound:
                self._generate_compound_statement(label_set,
                                                  statement.compound, repository[grammar_pattern.name])

    def _generate_start_patterns(self, data_dict, label_set):
        data_dict["scopeName"] = "source."+self.model.scope_name
        for start_expression in self.model.start_expressions:
            if start_expression not in label_set:
                raise_semantic_error(
                    "Non existing pattern referenced: "+start_expression,
                    ast_node=start_expression, model=self.model)
            data_dict["patterns"].append({
                "include": "#"+start_expression
            })

    def generate(self):
        label_set = self._get_label_set()
        ret_val = {
            "scopeName": "",
            "patterns": [],
            "repository": {
            }
        }
        for grammar_pattern in self.model.grammar_patterns:
            self._generate_repository(
                label_set, grammar_pattern, ret_val["repository"])
        self._generate_start_patterns(ret_val, label_set)
        return json.dumps(ret_val, indent=4)
