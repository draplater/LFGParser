"""
Lexicon like:
lion: N, [(^ PRED) = 'lion', (^ NUM) = PL]
lions: 'lion', 'infl_N', []
live: V, [(^ PRED) = 'live<...>', (^ TENSE) = PRES, (^ SUBJ) = !]
lives: 'live',  'infl_V", [(! PRES) = 3, (! NUM) = SG]
"""
import re
import traceback

from Grammar import ConcreteGrammar


class Lexicon(object):
    lexicon_dict = {}

    def __init__(self, word, word_type, rules):
        self.tag = u'"{}"'.format(word)
        self.word = word
        self.type = word_type
        self.rules = rules
        Lexicon.lexicon_dict[self.word] = self

    def instantiation(self, parent):
        return [ConcreteGrammar(i, parent, self) for i in self.rules]

    @staticmethod
    def from_string(s):
        """
        Load lexicon from string like N, [(^ PRED) = 'lion', (^ NUM) = PL]
        :param s:
        :return:
        """
        r_inflection = re.compile(ur"^(\w+) -> (.+)$")
        r_lexicon = re.compile(ur"(\w+) - (.+)")
        try:
            word_info, rules_string = s.split(":")
            rules = [i.strip() for i in rules_string.split(",")]
            match = r_inflection.match(word_info.strip())
            if match:
                original, word = match.groups()
                return Inflection(Lexicon.lexicon_dict[original], word, rules)
            match = r_lexicon.match(word_info.strip())
            assert match
            _type, word = match.groups()
            return Lexicon(word, _type, rules)
        except (ValueError, AssertionError) as e:
            traceback.print_exc()
            raise Exception("Can not parse.")


class Inflection(Lexicon):
    """
    Inflection of words. such as live -> lives
    """

    def __init__(self, original, word, rules):
        super(Inflection, self).__init__(word, original.type, rules)
        self.original = original
        self.tag = original.tag

    def instantiation(self, parent):
        return [ConcreteGrammar(i, parent, self)
                for i in self.rules + self.original.rules]
