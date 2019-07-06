
import re

KEYWORD_OPEN = '<keyword>'
KEYWORD_CLOSE = '</keyword>'

IDENTIFIER_OPEN = '<identifier>'
IDENTIFIER_CLOSE = '</identifier>'

SYMBOL_OPEN = '<symbol>'
SYMBOL_CLOSE = '</symbol>'

INT_OPEN = '<integerConstant>'
INT_CLOSE = '</integerConstant>'

STRING_OPEN = '<stringConstant>'
STRING_CLOSE = '</stringConstant>'


class JackTokenizer:

    is_comments = re.compile("(^\s*(/\*.*?(\n.*?)*?\*/))|(^\s*//.*?\n([\n\s]*))")

    is_keyWord = re.compile('^\s*(class|constructor|function|method|field|static|var|int|'
                                 'char|boolean|void|true|false|null|this|let|do|if|else|while|return)\W')
    # The regex capture a one non-word char after the Keyword, add when cutting the string we take care of it

    is_symbol = re.compile('^\s*(\{|\}|\(|\)|\[|\]|\.|\,|\;|\+|\-|\*|\/|\&|\||\<|\>|\=|\~)\s*')
    is_identifier = re.compile('^\s*([a-zA-Z_]\w*)')
    is_str = re.compile('^\s*"([^"]*?)"')
    is_int = re.compile('^\s*(\d+)')

    symbol_dict = {'<': '&lt;', '>': '&gt;', '&':'&amp;'}

    def __init__(self, jack_string):
        self.row_string = jack_string
        self.token_list = []

    def parse_jack(self):
        while self.row_string:

            find_comment = JackTokenizer.is_comments.match(self.row_string)
            if find_comment:
                self.row_string = self.row_string[find_comment.end():]
                continue


            find_keyWord = JackTokenizer.is_keyWord.match(self.row_string)
            if find_keyWord:
                xml_line = (KEYWORD_OPEN, find_keyWord.group(1), KEYWORD_CLOSE)
                self.token_list.append(xml_line)
                self.row_string = self.row_string[find_keyWord.end() - 1:]

                continue


            find_symbol = JackTokenizer.is_symbol.match(self.row_string)
            if find_symbol:
                symbol = find_symbol.group(1)
                if symbol in self.symbol_dict:
                    symbol = self.symbol_dict[symbol]
                xml_line = (SYMBOL_OPEN, symbol, SYMBOL_CLOSE)
                self.token_list.append(xml_line)
                self.row_string = self.row_string[find_symbol.end():]
                continue

            find_identifier = JackTokenizer.is_identifier.match(self.row_string)
            if find_identifier:
                identifier = find_identifier.group(1)
                xml_line = (IDENTIFIER_OPEN, identifier, IDENTIFIER_CLOSE)
                self.token_list.append(xml_line)
                self.row_string = self.row_string[find_identifier.end():]
                continue

            find_int = JackTokenizer.is_int.match(self.row_string)
            if find_int:
                xml_line = (INT_OPEN, find_int.group(1), INT_CLOSE)
                self.token_list.append(xml_line)
                self.row_string = self.row_string[find_int.end():]
                continue

            find_str = JackTokenizer.is_str.match(self.row_string)
            if find_str:
                xml_line = (STRING_OPEN, find_str.group(1), STRING_CLOSE)
                #  the method assume that the input is valid. if we get a line with 3
                #  the method will read the 2 firsts.
                self.token_list.append(xml_line)
                self.row_string = self.row_string[find_str.end():]
                continue

        return

