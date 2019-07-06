file_calls_counter={'return' : 0}

def get_function_commands(command, function_name, nArgs, file_name):
    '''
    :param command: string - 'fnction', 'call' or 'return'
    :param function_name: the second string in line
    :param nArgs: the third string
    :return: the asm command appropriate to the VM command
    '''
    if command == 'function':
        # clear nArgs on the stuck for local space for the function and move the SP accordingly
        return['(' + function_name + ')', '@' + str(nArgs) +'//num of locals',
               'D = A', '(' + function_name + '.init.start)',
               '@' + function_name + '.init.end', 'D;JEQ',
               '@SP', 'A = M', 'M = 0', 'D = D - 1', '@SP', 'M = M + 1',
               '@' + function_name + '.init.start', '0;JMP',
               '(' + function_name + '.init.end)']

    if command == 'call':
        if file_name in file_calls_counter:
            file_calls_counter[file_name] += 1
        else:
            file_calls_counter[file_name]=1

        counter = file_calls_counter[file_name]
        return_address = file_name+'$ret.'+str(counter)
        asm_commends = ["@"+return_address+"   //save return address", "D=A", "@SP", "A=M", "M=D", "@SP", "M=M+1",

                        "@LCL  //save caller's LCL", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1",

                        "//save caller's ARG", "@ARG  ", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1",

                        "//save caller's THIS", "@THIS  ", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1",

                        "//save caller's THAT", "@THAT  ", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1",

                        "//reposition ARG", "@5", "D=A", "@"+str(nArgs)+' //num of args', "D=D+A", "@SP", "D=M-D", "@ARG", "M=D",

                        "//reposition LCL", "@SP", "D=M", "@LCL", "M=D",
                        "@"+function_name, "0;JMP",
                        "("+return_address+")"]
        return asm_commends


    if command == 'return':
        # set the last func state and return to the return point
        counter = str(file_calls_counter['return'])
        asm_commends = ['@5','D=A','@LCL','A=M-D','D=M','@R13','M=D',

                        "@SP  // pop the last object on the stuck to the correct location", "A = M - 1", "D = M",

                        "@ARG", "A = M", "M = D", "D = A + 1  // set the new location for the SP", "@SP", "M = D",

                        "@LCL", "A = M - 1", "D = M", "@THAT", "M = D",
                        "@2", "D = A", "@LCL", "A = M - D", "D = M", "@THIS", "M = D",
                        "@3", "D = A", "@LCL", "A = M - D", "D = M", "@ARG", "M = D",
                        "@4", "D = A", "@LCL", "A = M - D", "D = M", "@LCL", "M = D",
                        "@R13", "A=M", "0;JMP"]
        #file_calls_counter['return'] +=1
        return asm_commends


