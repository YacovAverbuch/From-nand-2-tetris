
from SymbolTable import *
import JackTokenizer


binary_operators = ['+', '-', '*', '/', '&amp;', '|', '&lt;', '&gt;', '=']
unary_op = ['-', '~']

IDENTIFIER = '<identifier>'


class JackAnalyzer:
    class_name = ''
    class_symbol_table = None

    def __init__(self, tokens_list):
        self.list_of_tokens = tokens_list
        self.VM_lines = []
        self.cur_token = 0

        self.if_counter = 0
        self.while_counter = 0



    def parse_class_tokens(self):
        self.eat_token_string('class')
        self.class_name = self.extruct_token_with_type(IDENTIFIER)
        self.eat_token_string('{')

        self.class_symbol_table = ClassSymbolTable(self.class_name)

        while self.list_of_tokens[self.cur_token][1] in [STATIC, FIELD]:
            self.compile_class_var_one_dec()

        while self.list_of_tokens[self.cur_token][1] in ['constructor', 'method', 'function']:
            self.compile_one_subroutine()

        self.eat_token_string('}')
        return


    def compile_one_subroutine(self):
        con_func_method = self.extruct_general_token()
        if con_func_method in ['constructor', 'function']:
            self.class_symbol_table.start_function()
        elif con_func_method == 'method':
            self.class_symbol_table.start_method()

        ret_val = self.extruct_general_token()   # never used ?

        func_name = self.extruct_token_with_type(IDENTIFIER)

        self.eat_token_string('(')
        self.compile_parameter_list_in_func_declaretion()
        self.eat_token_string(')')
        self.eat_token_string('{')

        while self.list_of_tokens[self.cur_token][1] == 'var':
            self.compile_func_one_var_dec()

        if con_func_method == 'constructor':
            self.VM_lines.append('function ' + self.class_name + '.'
                                 + 'new ' + str(self.class_symbol_table.var_count))
            self.VM_lines.append('push constant ' + str(self.class_symbol_table.field_count))
            self.VM_lines.append('call Memory.alloc 1')
            self.VM_lines.append('pop pointer 0')

        if con_func_method == 'function':
            self.VM_lines.append('function ' + self.class_name + '.'
                                 + func_name + ' ' + str(self.class_symbol_table.var_count))

        if con_func_method == 'method':
            self.VM_lines.append('function ' + self.class_name + '.'
                                 + func_name + ' ' + str(self.class_symbol_table.var_count))
            self.VM_lines.append('push argument 0')
            self.VM_lines.append('pop pointer 0')

        self.compile_multyple_statment()
        self.eat_token_string('}')
        return




    def compile_parameter_list_in_func_declaretion(self):
        if self.list_of_tokens[self.cur_token][1] != ')':
            param_type = self.extruct_general_token()  # int\ bool\ char or class_name
            param_name = self.extruct_token_with_type(IDENTIFIER)
            self.class_symbol_table.add_symbol(param_name, param_type, ARG)

        while self.list_of_tokens[self.cur_token][1] != ')':
            # try this only if has one parameter already
            self.eat_token_string(',')
            param_type = self.extruct_general_token()  # int\ bool\ char or class_name
            param_name = self.extruct_token_with_type(IDENTIFIER)
            self.class_symbol_table.add_symbol(param_name, param_type, ARG)


    def compile_class_var_one_dec(self):
        """
        we call this function only if there is a declaration
        :return:
        """
        stat_field = self.extruct_general_token()
        var_type = self.extruct_general_token()
        var_name = self.extruct_token_with_type(IDENTIFIER)
        self.class_symbol_table.add_symbol(var_name, var_type, stat_field)

        while self.list_of_tokens[self.cur_token][1] == ',':
            self.eat_general_token()  # the ','
            var_name = self.extruct_token_with_type(IDENTIFIER)
            self.class_symbol_table.add_symbol(var_name, var_type, stat_field)

        self.eat_token_string(';')


    def compile_func_one_var_dec(self):
        """
        we call this function only if there is a declaration in the method
        :return:
        """
        self.eat_general_token()  # the 'var'
        var_type = self.extruct_general_token()
        var_name = self.extruct_token_with_type(IDENTIFIER)
        self.class_symbol_table.add_symbol(var_name, var_type, VAR)

        while self.list_of_tokens[self.cur_token][1] == ',':
            self.eat_general_token()  # the ','
            var_name = self.extruct_token_with_type(IDENTIFIER)
            self.class_symbol_table.add_symbol(var_name, var_type, VAR)
        self.eat_token_string(';')


    def compile_multyple_statment(self):
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
        return


    def compile_let_statment(self):
        assign_to_array = False
        self.eat_general_token()  # the 'let'
        var_name = self.extruct_token_with_type(IDENTIFIER)

        if self.list_of_tokens[self.cur_token][1] == '[':  # var_name is an array
            assign_to_array = True
            self.eat_general_token()  # the '['

            self.VM_lines.append('push ' + self.class_symbol_table.symbol_string_for_vm(var_name))
            self.compile_expression()   # leaves on teh stuck the index we operate on
            self.VM_lines.append('add')  # now the must top value is the RAM we want to edit
            self.eat_token_string(']')

        self.eat_token_string('=')
        self.compile_expression()  # leave on the stuck the desire value
        self.eat_token_string(';')

        if assign_to_array:
            self.VM_lines.append('pop temp 0')  # pop the desire value
            self.VM_lines.append('pop pointer 1')  # set that to be the RAM we edit
            self.VM_lines.append('push temp 0')
            self.VM_lines.append('pop that 0')
            return
        else:
            self.VM_lines.append('pop' + ' ' + self.class_symbol_table.symbol_string_for_vm(var_name))


    def compile_if(self):
        if_num = self.if_counter
        self.if_counter += 1

        self.eat_general_token()  # the 'if'
        self.eat_token_string('(')
        self.compile_expression()  # leave on the stuck a boolean value

        self.VM_lines.append('not')  # negate the boolean value
        self.VM_lines.append('if-goto IF_FALSE' + str(if_num))  # if false - jump to end (or to else if exist)

        self.eat_token_string(')')

        self.eat_token_string('{')
        self.compile_multyple_statment()
        self.eat_token_string('}')

        if self.list_of_tokens[self.cur_token][1] == 'else':

            self.VM_lines.append('goto IF_END' + str(if_num))  # if true it will go to end

            self.VM_lines.append('label IF_FALSE' + str(if_num))  # if false it jump to here

            self.eat_general_token()  # the 'else'
            self.eat_token_string('{')
            self.compile_multyple_statment()
            self.eat_token_string('}')

            self.VM_lines.append('label IF_END' + str(if_num))

        else:  # there is no else in code
            self.VM_lines.append('label IF_FALSE' + str(if_num))  # if false it jump to here


    def compile_while(self):
        while_num = self.while_counter
        self.while_counter += 1

        self.eat_general_token()  # the 'while'
        self.eat_token_string('(')

        self.VM_lines.append('label WHILE_TRUE' + str(while_num))
        
        self.compile_expression()  # leave on the stuck a boolean value

        self.VM_lines.append('not')  # negate the boolean value
        self.VM_lines.append('if-goto WHILE_FALSE' + str(while_num))  # if false - jump to end (or to else if exist)

        self.eat_token_string(')')
        self.eat_token_string('{')

        self.compile_multyple_statment()

        self.eat_token_string('}')

        self.VM_lines.append('goto ' + 'WHILE_TRUE' + str(while_num))

        self.VM_lines.append('label WHILE_FALSE' + str(while_num))  # if false it jump to here




    def compile_do(self):
        self.eat_general_token()  # the 'do'
        self.compile_subroutine_call()  # create the actual vm code
        self.eat_token_string(';')

        self.VM_lines.append('pop temp 0')  # pop the return value of the function




    def compile_return(self):

        self.eat_general_token()  # the 'return'
        if self.list_of_tokens[self.cur_token][1] == ';':
            self.VM_lines.append('push constant 0')  # add a dammy value to the stuck

        else:  # there is values
            if self.list_of_tokens[self.cur_token][1] == 'this':
                self.eat_general_token()  # the this
                self.VM_lines.append('push pointer 0')
            else:
                self.compile_expression()   # leave on the stuck a value

        self.eat_token_string(';')
        self.VM_lines.append('return')






    def compile_expression_list(self):
        """
        This function called even if it is not sure there is expressionList at all
        compile all the parameters in the list without the ')'
        :return: num of exp in the list
        """
        num_of_expression = 0
        if self.list_of_tokens[self.cur_token][1] != ')':
            self.compile_expression()
            num_of_expression += 1

            while self.list_of_tokens[self.cur_token][1] == ',':
                self.eat_token_string(',')
                self.compile_expression()
                num_of_expression += 1

        return num_of_expression



    def compile_expression(self):
        """
        when we call this function we know already that there is expression
        :return:
        """
        self.compile_one_term()

        while self.list_of_tokens[self.cur_token][1] in binary_operators:
            # in this implement, we do the operator right after the second value is on the stack
            # so, [4 * 5 + 3 / 2] is equal to (((4 * 5) + 3) / 2)
            operator = self.extruct_general_token()
            self.compile_one_term()
            if operator == '+':
                self.VM_lines.append('add')
            if operator == '-':
                self.VM_lines.append('sub')
            if operator == '*':
                self.VM_lines.append('call Math.multiply 2')
            if operator == '/':
                self.VM_lines.append('call Math.divide 2')
            if operator == '&amp;':
                self.VM_lines.append('and')
            if operator == '|':
                self.VM_lines.append('or')
            if operator == '&lt;':
                self.VM_lines.append('lt')
            if operator == '&gt;':
                self.VM_lines.append('gt')
            if operator == '=':
                self.VM_lines.append('eq')

        return


    def compile_one_term(self):

        if self.list_of_tokens[self.cur_token][1] == '(':  # start of another expression
            self.eat_general_token()   # the '('
            self.compile_expression()
            self.eat_token_string(')')

        elif self.list_of_tokens[self.cur_token][1] in unary_op:  # start wih '~' or '-'
            operator_unary = self.extruct_token_with_type('<symbol>')
            self.compile_one_term()
            if operator_unary == '~':
                self.VM_lines.append('not')
            elif operator_unary == '-':
                self.VM_lines.append('neg')

        elif self.list_of_tokens[self.cur_token + 1][1] in ['.', '(']:   # its a subroutine call
            self.compile_subroutine_call()

        elif self.list_of_tokens[self.cur_token + 1][1] == '[':  # its an array term
            array_name = self.extruct_general_token()
            self.VM_lines.append('push ' + self.class_symbol_table.symbol_string_for_vm(array_name))

            self.eat_token_string('[')
            self.compile_expression()  # one exp. leave on the stuck the index we want to extruct
            self.eat_token_string(']')
            self.VM_lines.append('add')
            self.VM_lines.append('pop pointer 1')  # set that to be the RAM location we want
            self.VM_lines.append('push that 0')

        else:
            token = self.list_of_tokens[self.cur_token]  # an int, string, keyword or var_name
            self.cur_token += 1

            if token[0] == JackTokenizer.INT_OPEN:
                self.VM_lines.append('push constant ' + token[1])

            if token[0] == JackTokenizer.STRING_OPEN:
                cur_str = token[1]
                self.VM_lines.append('push constant ' + str(len(cur_str)))
                self.VM_lines.append('call String.new 1')
                for char in cur_str:
                    char = ord(char)
                    self.VM_lines.append('push constant ' + str(char))
                    self.VM_lines.append('call String.appendChar 2')

            if token[0] == JackTokenizer.KEYWORD_OPEN:
                if token[1] in ['null', 'false']:
                    self.VM_lines.append('push constant 0')
                if token[1] == 'true':
                    self.VM_lines.append('push constant 0')
                    self.VM_lines.append('not')
                    #todo its 'neg' or 'not'
                if token[1] == 'this':
                    self.VM_lines.append('push pointer 0')

            if token[0] == JackTokenizer.IDENTIFIER_OPEN:  # it is a var name
                var_representation = self.class_symbol_table.symbol_string_for_vm(token[1])
                self.VM_lines.append('push ' + var_representation)




    def compile_subroutine_call(self):

        subroutine_name = self.extruct_token_with_type(IDENTIFIER)
        subroutine_sufix = ''

        num_of_args = 0

        if self.list_of_tokens[self.cur_token][1] == '.':
            # its an outer class subroutine call, static or method. or its a static in this class
            subroutine_sufix += self.extruct_general_token()  # the dot
            subroutine_sufix += self.extruct_general_token()  # subroutine_name

            ob_symbol = self.class_symbol_table.find_symbol(subroutine_name)
            if not ob_symbol:  # it is a static call
                subroutine_name = subroutine_name + subroutine_sufix

            elif ob_symbol:   # the subroutine_name is an object so it is a method
                num_of_args += 1
                self.VM_lines.append('push ' + self.class_symbol_table.symbol_string_for_vm(subroutine_name))
                subroutine_name = ob_symbol[0] + subroutine_sufix

        elif self.list_of_tokens[self.cur_token][1] == '(':  # its an inside class method subroutine call
            num_of_args += 1
            subroutine_name = self.class_name + '.' + subroutine_name
            self.VM_lines.append('push pointer 0')

        self.eat_token_string('(')
        num_of_args = num_of_args + self.compile_expression_list()  # leaves on the VM_lines the parameters expressions
        self.eat_token_string(')')
        self.VM_lines.append('call ' + subroutine_name + ' ' + str(num_of_args))




    def eat_token_string(self, string_to_eat):
        if self.list_of_tokens[self.cur_token][1] != string_to_eat:
            print('STRING ERROR ' + 'string to eat = ' + string_to_eat + ', got: ' + self.list_of_tokens[self.cur_token][1] )
            print('counter: '+str(self.cur_token)+' the token: ',self.list_of_tokens[self.cur_token], '\n')
        self.cur_token += 1

    def eat_token_type(self, type_to_eat):
        if self.list_of_tokens[self.cur_token][0] != type_to_eat:
            print('TYPE ERROR')
            print('type to eat = ' + type_to_eat + ', got: ' + self.list_of_tokens[self.cur_token][0])
        self.cur_token += 1

    def eat_general_token(self):
        self.cur_token += 1

    def extruct_token_with_type(self, type_to_eat):
        if self.list_of_tokens[self.cur_token][0] != type_to_eat:
            print('TYPE ERROR:' + 'type to eat = ' + type_to_eat + ', got: ' + self.list_of_tokens[self.cur_token][0] + '\n')
        self.cur_token += 1
        return self.list_of_tokens[self.cur_token - 1][1]

    def extruct_general_token(self):
        self.cur_token += 1
        return self.list_of_tokens[self.cur_token - 1][1]

