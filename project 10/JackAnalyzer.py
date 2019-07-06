

class JackAnalyzer:

    binary_operators = ['+', '-', '*', '/', '&amp;', '|', '&lt;', '&gt;', '=']
    unary_op = ['-', '~']
    build_in_types = ['int', 'char', 'boolean']


    def __init__(self, tokens_list):
        self.list_of_tokens = tokens_list
        self.XML_lines = []
        self.tab_counter = 0
        self.cur_token = 0


    def parse_class_tokens(self):
        self.XML_lines.append('\t' * self.tab_counter + '<class>')
        self.tab_counter += 1
        self.eat_token_string('class')
        self.eat_token_type('<identifier>')
        self.eat_token_string('{')

        while self.list_of_tokens[self.cur_token][1] in ['static', 'field']:
            self.compile_class_var_one_dec()

        while self.list_of_tokens[self.cur_token][1] in ['constructor', 'method', 'function']:
            self.compile_one_subroutine()

        self.eat_token_string('}')
        self.tab_counter -= 1
        self.XML_lines.append('\t' * self.tab_counter + '</class>')

        return



    def compile_one_subroutine(self):
        self.XML_lines.append('\t' * self.tab_counter + '<subroutineDec>')
        self.tab_counter += 1

        self.eat_general_token()  # the cont/ func / method
        self.eat_general_token()  # void or type
        self.eat_token_type('<identifier>')  # the name of the func

        self.eat_token_string('(')
        self.compile_parameter_list()
        self.eat_token_string(')')
        self.XML_lines.append('\t' * self.tab_counter + '<subroutineBody>')
        self.tab_counter += 1
        self.eat_token_string('{')

        while self.list_of_tokens[self.cur_token][1] == 'var':
            self.compile_func_one_var_dec()

        self.compile_multyple_statment()

        self.eat_token_string('}')
        self.tab_counter -= 1
        self.XML_lines.append('\t' * self.tab_counter + '</subroutineBody>')
        self.tab_counter -= 1
        self.XML_lines.append('\t' * self.tab_counter + '</subroutineDec>')

        return


    def compile_parameter_list(self):
        self.XML_lines.append('\t' * self.tab_counter + '<parameterList>')
        self.tab_counter += 1
        if self.list_of_tokens[self.cur_token][1] != ')':
            self.eat_general_token()
            self.eat_token_type('<identifier>')
        while self.list_of_tokens[self.cur_token][1] != ')':
            # try this only if has one parameter already
            self.eat_token_string(',')
            self.eat_general_token()  # the 'type'
            self.eat_token_type('<identifier>')  # var_name

        self.tab_counter -= 1
        self.XML_lines.append('\t' * self.tab_counter + '</parameterList>')



    def compile_class_var_one_dec(self):
        """
        we call this function only if there is a declaration
        :param is_static:
        :return:
        """
        self.XML_lines.append('\t' * self.tab_counter + '<classVarDec>')
        self.tab_counter += 1

        self.eat_general_token()  # the static/ field
        self.eat_general_token()  # the type
        self.eat_token_type('<identifier>')

        while self.list_of_tokens[self.cur_token][1] == ',':
            self.eat_general_token()  # the ','
            self.eat_token_type('<identifier>')

        self.eat_token_string(';')
        self.tab_counter -= 1
        self.XML_lines.append('\t' * self.tab_counter + '</classVarDec>')


    def compile_func_one_var_dec(self):
        """
        we call this function only if there is a declaration in the method
        :return:
        """
        self.XML_lines.append('\t' * self.tab_counter + '<varDec>')
        self.tab_counter += 1

        self.eat_general_token()  # the 'var'
        self.eat_general_token()  # the type
        self.eat_token_type('<identifier>')  # the var_name

        while self.list_of_tokens[self.cur_token][1] == ',':
            self.eat_general_token()  # the ','
            self.eat_token_type('<identifier>')

        self.eat_token_string(';')

        self.tab_counter -= 1
        self.XML_lines.append('\t' * self.tab_counter + '</varDec>')



    def compile_multyple_statment(self):
        self.XML_lines.append('\t' * self.tab_counter + '<statements>')
        self.tab_counter += 1

        while True:
            cur_statment = self.list_of_tokens[self.cur_token][1]
            if cur_statment == 'if':
                self.compile_if()
                continue
            if cur_statment == 'while':
                self.compile_while()
                continue
            if cur_statment == 'let':
                self.compile_let_statment()
                continue
            if cur_statment == 'do':
                self.compile_do()
                continue
            if cur_statment == 'return':
                self.compile_return()
                continue
            break

        self.tab_counter -= 1
        self.XML_lines.append('\t' * self.tab_counter + '</statements>')


    def compile_let_statment(self):
        self.XML_lines.append('\t' * self.tab_counter + '<letStatement>')
        self.tab_counter += 1

        self.eat_general_token()  # the 'let'
        self.eat_token_type('<identifier>')

        if self.list_of_tokens[self.cur_token][1] == '[':  # var_name is an array
            self.eat_general_token()  # the '['
            self.compile_expression()
            self.eat_token_string(']')

        self.eat_token_string('=')
        self.compile_expression()
        self.eat_token_string(';')

        self.tab_counter -= 1
        self.XML_lines.append('\t' * self.tab_counter + '</letStatement>')


    def compile_if(self):
        self.XML_lines.append('\t' * self.tab_counter + '<ifStatement>')
        self.tab_counter += 1

        self.eat_general_token()  # the 'if'
        self.eat_token_string('(')
        self.compile_expression()
        self.eat_token_string(')')

        self.eat_token_string('{')
        self.compile_multyple_statment()
        self.eat_token_string('}')

        if self.list_of_tokens[self.cur_token][1] == 'else':
            self.eat_general_token()  # the 'else'
            self.eat_token_string('{')
            self.compile_multyple_statment()
            self.eat_token_string('}')


        self.tab_counter -= 1
        self.XML_lines.append('\t' * self.tab_counter + '</ifStatement>')


    def compile_while(self):
        self.XML_lines.append('\t' * self.tab_counter + '<whileStatement>')
        self.tab_counter += 1

        self.eat_token_string('while')
        self.eat_token_string('(')
        self.compile_expression()
        self.eat_token_string(')')

        self.eat_token_string('{')
        self.compile_multyple_statment()
        self.eat_token_string('}')

        self.tab_counter -= 1
        self.XML_lines.append('\t' * self.tab_counter + '</whileStatement>')


    def compile_do(self):
        self.XML_lines.append('\t' * self.tab_counter + '<doStatement>')
        self.tab_counter += 1
        self.eat_token_string('do')
        self.compile_subroutine_call()
        self.eat_token_string(';')
        self.tab_counter -= 1
        self.XML_lines.append('\t' * self.tab_counter + '</doStatement>')


    def compile_return(self):
        self.XML_lines.append('\t' * self.tab_counter + '<returnStatement>')
        self.tab_counter += 1
        self.eat_general_token()  # the 'return'
        if self.list_of_tokens[self.cur_token][1] != ';':
            self.compile_expression()
        self.eat_token_string(';')
        self.tab_counter -= 1
        self.XML_lines.append('\t' * self.tab_counter + '</returnStatement>')



    def compile_expression_list(self):
        """
        This function called even if it is not shore there is expressionList at all
        :return:
        """
        self.XML_lines.append('\t' * self.tab_counter + '<expressionList>')
        self.tab_counter += 1

        if self.list_of_tokens[self.cur_token][1] != ')':
            self.compile_expression()
        while self.list_of_tokens[self.cur_token][1] == ',':
            self.eat_token_string(',')
            self.compile_expression()

        self.tab_counter -= 1
        self.XML_lines.append('\t' * self.tab_counter + '</expressionList>')


    def compile_expression(self):
        """
        when we call this function we know already that there is expression
        :return:
        """
        self.XML_lines.append('\t' * self.tab_counter + '<expression>')
        self.tab_counter += 1
        self.compile_one_term()

        while self.list_of_tokens[self.cur_token][1] in JackAnalyzer.binary_operators:
            self.eat_general_token()  # the operator
            self.compile_one_term()

        self.tab_counter -= 1
        self.XML_lines.append('\t' * self.tab_counter + '</expression>')


    def compile_one_term(self):
        self.XML_lines.append('\t' * self.tab_counter + '<term>')
        self.tab_counter += 1

        if self.list_of_tokens[self.cur_token][1] == '(':  # start of another expression
            self.eat_general_token()   # the '('
            self.compile_expression()
            self.eat_token_string(')')

        elif self.list_of_tokens[self.cur_token][1] in JackAnalyzer.unary_op: # start wih '~' or '-'
            self.eat_token_type('<symbol>')
            self.compile_one_term()

        elif self.list_of_tokens[self.cur_token + 1][1] in ['.', '(']:   # its a subroutine call
            self.compile_subroutine_call()

        elif self.list_of_tokens[self.cur_token + 1][1] == '[':  # its an array term
            self.eat_general_token()   # the array name
            self.eat_token_string('[')
            self.compile_expression()
            self.eat_token_string(']')

        else:
            self.eat_general_token()  # an int, string, keyword or var_name

        self.tab_counter -= 1
        self.XML_lines.append('\t' * self.tab_counter + '</term>')


    def compile_subroutine_call(self):
        self.eat_general_token()  # subroutine_name
        if self.list_of_tokens[self.cur_token][1] == '.':
            self.eat_general_token()  # eat the '.'
            self.eat_general_token()  # subroutine_name

        self.eat_token_string('(')
        self.compile_expression_list()
        self.eat_token_string(')')


    def eat_token_string(self, string_to_eat):
        #this code is for jack syntax error. but we assum the input is valid
        #if self.list_of_tokens[self.cur_token][1] != string_to_eat:
        #    print('ERROR')
        self.eat_general_token()


    def eat_token_type(self, type_to_eat):
        #this code is for jack syntax error. but we assum the input is valid
        #if self.list_of_tokens[self.cur_token][0] != type_to_eat:
        #    print('ERROR')
        self.eat_general_token()

    def eat_general_token(self):
        self.XML_lines.append('\t' * self.tab_counter + ' '.join(self.list_of_tokens[self.cur_token]))
        self.cur_token += 1
        return
