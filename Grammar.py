import re

from ConstTree import ConstTree


class Grammar(object):
    """
    Grammars like:
    S -> NP: (^ SUBJ) = !, VP: ^ = !
    NP -> (Det: ^ = !), N: ^ = !
    VP -> V: ^ = !, (PP: (^ OBL_LOC) = !)
    """

    def __init__(self, parent_tag, rule):
        """
        construct grammar from signature and rule_dict
        :param parent_tag: the tag of parent
        :param rule: list of rules: [{'tag': subnode_tag, 'rule': xxx, 'optional': 'bool'}]
        """
        self.parent_tag = parent_tag
        self.rule = rule

    def match(self, node):
        """
        test weather a ConstTree node match this grammar.
        If it matches, :return: a list of ConcreteGrammar.
        Otherwise :return: None.
        """
        assert isinstance(node, ConstTree)
        if node.tag.upper() != self.parent_tag.upper():
            return None
        child_list = [{'tag': i.tag, 'node': i}
                      for i in node.child if isinstance(i, ConstTree)]
        i = 0
        j = 0
        result = []
        while i < len(self.rule) and j < len(child_list):
            while self.rule[i]['tag'].upper() != child_list[j]['tag'].upper() and \
                    self.rule[i]['optional']:
                i += 1
                continue
            if self.rule[i]['tag'].upper() != child_list[j]['tag'].upper() and \
                    not self.rule[i]['optional']:
                return None
            if self.rule[i]['tag'].upper() == child_list[j]['tag'].upper():
                result.append(ConcreteGrammar(self.rule[i]['rule'],
                                              node,
                                              child_list[j]['node']))
                i += 1
                j += 1

        while i < len(self.rule):
            if not self.rule[i]['optional']:
                return False
            i += 1

        return result

    @staticmethod
    def from_string(s):
        """
        Load Grammar from string.
        :param s: like "S -> NP: (^ SUBJ) = !, VP: ^ = !"
        :return: grammar object
        """
        r_rule = re.compile("^(\w+): (.*)$")
        try:
            parent_tag, rules_string = s.split(" -> ")
            rules = []
            for i in rules_string.split(","):
                optional = i.strip().startswith("(")
                match = r_rule.match(i.strip().strip("()"))
                assert match
                tag, rule = match.groups()
                rules.append(
                    {"optional": optional, "tag": tag, "rule": rule})
            return Grammar(parent_tag, rules)
        except (ValueError, AssertionError):
            raise Exception("Can not parse.")


class ConcreteGrammar(object):
    """
    Grammar corresponding to specific ConstTree node.
    """

    def __init__(self, grammar, parent, child):
        self.grammar = grammar
        self.parent = parent
        self.child = child


    def __repr__(self):
        """
        print in the console
        """
        return u"<ConcreteGramar: {}, {}, {}>".format(
            self.grammar, self.parent.tag, self.child.tag)