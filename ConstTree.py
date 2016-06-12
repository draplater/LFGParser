# en    coding: utf-8
import re


class ConstTreeParserError(Exception):
    def __init__(self, message):
        self.message = message

class ConstTree:
    """
    c-structure of LFG.
    """

    def __init__(self, tag):
        self.child = []
        self.tag = tag

    def __repr__(self):
        """
        print tree in the console
        :return: tree
        """
        return u"ConstTree <{}>: [{}]".format(self.tag,
                                             u', '.join([unicode(i) for i in self.child]))

    def __unicode__(self):
        return self.__repr__()

    def __str__(self):
        return self.__unicode__().encode("utf-8")

    def __getitem__(self, item):
        if isinstance(item, (str, unicode)):
            for i in self.child:
                if isinstance(i, ConstTree) and i.tag.upper() == item.upper():
                    return i
        if isinstance(item, int):
            return self.child[item]
        raise KeyError

    @staticmethod
    def from_string(s):
        """
        construct ConstTree from parenthesis representation
        :param s: unicode string of parenthesis representation
        :return: ConstTree root
        """
        assert isinstance(s, unicode)
        # always wrap with __root__
        if not s.startswith(u"( "):
            s = u"( {})".format(s)
        pos = 0
        stack = []
        while pos < len(s):
            if s[pos] == ')':
                pattern_match = re.search("\)+", s[pos:])
                match_string = pattern_match.group(0)
                for i in range(match_string.count(")")):
                    if not stack:
                        raise ConstTreeParserError(
                            'redundant ")" at pos {}.'.format(pos + i))
                    node = stack.pop()
                    if node.tag != '__root__':
                        stack[-1].child.append(node)
                pos += pattern_match.end(0)
                continue
            pattern_match = re.search("[^\s\)]+", s[pos:])
            match_string = pattern_match.group(0)
            if match_string == '(':
                root = ConstTree("__root__")
                stack.append(root)
            elif match_string.startswith('('):
                tag = match_string[1:]
                if not re.match("^\w+$", tag):
                    raise ConstTreeParserError(
                        'Invalid tag "{}" at pos {}.'.format(tag, pos))
                node = ConstTree(tag)
                stack.append(node)
            else:
                stack[-1].child.append(match_string)
            pos += pattern_match.end(0)
        if len(stack) != 0:
            raise ConstTreeParserError('missing ")".')
        return root


if __name__ == '__main__':
    a = ConstTree.from_string(u'( (zj (!dj (np (!rn 我)) (!vp (!vp (!v 病)) (ule 了))) (wfs 。)))')
    print a
    b = ConstTree.from_string(u'( (s (np (n LIONS)) (vp (v lives))))')
    print b
