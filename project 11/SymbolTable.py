

ARG = 'argument'
VAR = 'var'
STATIC = 'static'
FIELD = 'field'


class ClassSymbolTable:

    def __init__(self, class_name):
        self.class_name = class_name
        # each object in the dictionary the key is string represent the var name and the value is tuple of
        # (string, string, int) represent the (var_type, var_visible, var_number)
        #
        # var visible is stored in jack term - so when compiling we translate the value to VM terms in
        # symbol_string_for_vm method
        self.table = {}
        self.method_table = {}
        self.static_count = 0
        self.field_count = 0
        self.arg_count = 0
        self.var_count = 0

    def add_symbol(self, var_name, var_type, var_visible):
        """
        :param var_name: name
        :param var_type: int\ bool\ char or class_name
        :param var_visible: static\ field\ argument \var
        :return:
        """
        num = 0
        if var_visible == STATIC:
            num = self.static_count
            self.static_count += 1
        elif var_visible == FIELD:
            num = self.field_count
            self.field_count += 1
        elif var_visible == ARG:
            num = self.arg_count
            self.arg_count += 1
        elif var_visible == VAR:
            num = self.var_count
            self.var_count += 1

        if var_visible in [STATIC, FIELD]:
            self.table[var_name] = (var_type, var_visible, num)

        elif var_visible in [ARG, VAR]:
            self.method_table[var_name] = (var_type, var_visible, num)


    def find_symbol(self, var_name):
        if var_name in self.method_table:
            return self.method_table[var_name]
        if var_name in self.table:
            return self.table[var_name]
        return None


    def symbol_string_for_vm(self, var_name):
        values = self.find_symbol(var_name)
        if not values:
            print('ERROR')
            return 'ERROR'

        var_visible = values[1]
        if var_visible == VAR:
            var_visible = 'local'
        if var_visible == FIELD:
            var_visible = 'this'

        return var_visible + ' ' + str(values[2])



    def start_method(self):
        self.method_table.clear()
        self.var_count = 0
        self.arg_count = 1
        self.method_table['this'] = (self.class_name, ARG, 0)


    def start_function(self):
        self.method_table.clear()
        self.var_count = 0
        self.arg_count = 0




