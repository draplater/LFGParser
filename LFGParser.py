#!/usr/bin/python
# encoding: utf-8
import re
import json
import sys
from ConstTree import ConstTree
from Grammar import Grammar
from Lexicon import Lexicon
from UFSet import UFSet
import xml.dom.minidom


class LFGParserError(Exception):
    def __init__(self, message):
        self.message = message


def recursive_parse_tree(tree, grammar_list, word_set):
    """
    find suitable grammar for each node of tree recursively.
    :param tree:
    :param grammar_list:
    :param word_set:
    :return: a list of ConcreteGrammar
    """
    result = []
    for i in grammar_list:
        match_result = i.match(tree)
        if match_result:
            result = match_result
            break

    for i in tree.child:
        if isinstance(i, ConstTree):
            result.extend(recursive_parse_tree(i, grammar_list, word_set))
        if isinstance(i, (str, unicode)):
            result.extend(word_set[i.lower()].instantiation(tree))
    return result


def generate_f_strcuture(const_tree, grammar_list, word_set):
    """
    generate f-structure of constituent tree
    :param const_tree:
    :param grammar_list:
    :param word_set:
    :return: the root of f_structure
    """
    # generate ConcreteGrammar rules
    rule_list = recursive_parse_tree(const_tree, grammar_list, word_set)

    # parse '^ = !'
    # use a ufset to union all equivalent nodes
    ufset = UFSet()
    for i in rule_list:
        ufset.add(i.parent)
        ufset.add(i.child)
        if i.grammar == '^ = !':
            ufset.union(i.parent, i.child)

    # init f-structure
    f_struct = {}
    for key, value in ufset.map.items():
        if key == value:
            f_struct[key] = {}

    # convert rules to f-structure
    for i in rule_list:
        # parse (^ xxx) = xxx
        match_1 = re.match(ur'^\(\^ (\w+)\) = (.+)$', i.grammar)
        if match_1:
            tag = match_1.group(1)
            right = match_1.group(2)
            # parse (^ xxx) = !
            if right == '!':
                f_struct[ufset.find(i.parent)][tag] = f_struct[ufset.find(i.child)]
            # parse (^ xxx) = attribute
            else:
                f_struct[ufset.find(i.parent)][tag] = right

    try:
        root = ufset.find(const_tree[0])
        return f_struct[ufset.find(const_tree[0])]
    except KeyError:
        raise LFGParserError("Incomplete f-structure.")


def f_structure_to_xml(const_tree_string, root):
    """
    convert f-structure to LinguaView XML
    :param const_tree_string:
    :param root:
    :return:
    """
    f_structure_to_xml.global_id = 0

    def to_xml(node):
        """
        convert f-structure node to xml recursively
        :param node:
        :return:
        """
        result = ""
        f_structure_to_xml.global_id += 1
        result += u'<fstruct id="{}">\n'.format(f_structure_to_xml.global_id)
        for key, value in node.items():
            if key == 'PRED':
                result += u'<attr name="PRED" valtype="sem"> {} </attr>\n'.format(value)
            elif isinstance(value, dict):
                result += u'<attr name="{}" valtype="fstruct">\n'.format(key)
                result += to_xml(value)
                result += u'</attr>\n'
            else:
                result += u'<attr name="{}" valtype="atomic"> {} </attr>\n'.format(key, value)
        result += u"</fstruct>\n"
        return result

    template = u"""<?xml version="1.0" encoding="utf-8" ?>
    <viewer>
      <sentence id="1">
          <lfg>
              <cstruct> {} </cstruct>
              {}
          </lfg>
      </sentence>
    </viewer>
      """
    output_string = template.format(const_tree_string,
                                    to_xml(root))
    print output_string
    # prettify xml
    dom = xml.dom.minidom.parseString(output_string.encode("utf-8"))
    dom.encoding = "utf-8"
    output_string = dom.toprettyxml(encoding="utf-8")
    # remove empty line
    output_string = "\n".join([ll for ll in output_string.splitlines() if ll.strip()])
    return output_string


def parse_json(json_input):
    """

    :param string:
    :return:
    """
    # load const tree
    const_tree = ConstTree.from_string(json_input['const_tree'])
    # load grammar
    grammar_list = [Grammar.from_string(i) for i in json_input['grammar']]
    # load lexicon list
    for i in json_input['lexicon']:
        Lexicon.from_string(i)
    word_set = Lexicon.lexicon_dict
    root = generate_f_strcuture(const_tree, grammar_list, word_set)
    output_string = f_structure_to_xml(json_input['const_tree'], root)

    return output_string


if __name__ == '__main__':
    # input file
    string_input = sys.stdin.read().decode('utf-8')
    json_object = json.loads(string_input)
    print parse_json(json_object)
