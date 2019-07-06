



def get_push(segment, i, file_name):
    segment, i = get_segment(segment, i, file_name)
    if segment == "constant":
        return ["//push constant " + i, "@"+i, "D=A", "@SP", "A=M", "M=D", "@SP", "M=M+1"]
    if i == 'flag':
        return get_push_with_direct_address(segment)
    else:
        return get_push_with_address_pointer(segment, i)


def get_pop(segment, i, file_name):
    segment, i = get_segment(segment, i, file_name)
    if i == 'flag':
        return get_pop_with_direct_address(segment)
    else:
        return get_pop_with_address_pointer(segment, i)






def get_segment(segment, i, file_name):
    str_i = str(i)
    int_i = int(i)
    dict1 = {"local": ("LCL", str_i), "argument": ("ARG", str_i), "this": ("THIS", str_i),
             "that": ("THAT", str_i)}
    dict2 = {"static": (file_name + str_i), "temp": (5 + int_i), "pointer": (3 + int_i)}

    if segment in dict1:
        segment, i = dict1[segment]
    elif segment in dict2:
        segment = dict2[segment]
        i = 'flag'
    return str(segment), str(i)


def get_push_with_address_pointer(segment, i):
    return ["//push segment i", "@" + i, "D=A", "@"+segment, "A=M+D", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1"]


def get_push_with_direct_address(segment):
    return [ "//push segment i", "@"+segment, "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1"]


def get_pop_with_address_pointer(segment, i):
    return ["//pop segment i", "@"+i, "D=A", "@"+segment, "M=M+D //segment=base+i",
            "@SP", "M=M-1", "A=M", "D=M", "@"+segment, "A=M", "M=D", "@"+i, "D=A",
            "@"+segment, "M=M-D //segment=base+i-i"]


def get_pop_with_direct_address(segment):
    return["//pop segment i", "@SP", "M=M-1", "A=M", "D=M", "@"+segment, "M=D"]




def get_add():
    return["//add", "@SP", "M=M-1", "A=M", "D=M  //D=y", "A=A-1", "M=M+D //x=x+y"]


def get_sub():
    return["//sub", "@SP", "M=M-1", "A=M", "D=M  //D=y", "A=A-1", "M=M-D //x=x-y"]



def get_neg():
    return ["//neg", "@SP", "A=M", "A=A-1", "M=!M", "M=M+1"]


def get_eq():
    """
    :return: list of asm command to calculate if x (SP[-2] == y (SP[-1])
    """
    cur_call = functions_using_counter[get_eq]
    functions_using_counter[get_eq] += 1
    asm_commends = ["// eq",
                "@SP",
                "M = M - 1",
               "A = M",
               "D = M       //D is y",
               "A = A - 1",
               "D = D - M   // D is y - x",
               "M = -1      // define it as true",
               "@EQ.callEnd." + str(cur_call),
               "D;JEQ",
                "@SP",
                "A = M - 1",
               "M = 0       // if didnt JPM then it false",
               "(EQ.callEnd." +  str(cur_call) + ")"]
    return asm_commends



def get_gt():
    """
    :return: list of asm command to calculate if x (SP[-2] > y (SP[-1])
    """
    first_call_asm_commends = ["//gt",
                    "@GT.call.0",
                    "D = A",
                    "(GT)",
                    "@R13",
                    "M=D",

                    "@SP",
                    "M=M-1",
                    "A=M   //points at y",
                    "D=M",
                    "@YPOSITIVE_GT  //if y>0",
                    "D;JGT",

                    "//else y<= 0",
                    "@SP",
                    "A=M-1     //points at x",
                    "D=M",
                    "@COMPARE_GT //if x<=0",
                    "D;JLE ",
                    "@TRUE_GT    //else x>0",
                    "0;JMP       ",

                    "(YPOSITIVE_GT)",
                    "@SP",
                    "A=M-1     //points at x",
                    "D=M     //D=x",
                    "@COMPARE_GT  //if x>0",
                    "D;JGT",
                    "@FALSE_GT    //else",
                    "0;JMP       ",

                    "(COMPARE_GT)",
                    "@SP",
                    "A=M   //points at y",
                    "D=D-M  // D was x, now x - y",
                    "@TRUE_GT // if x-y > o",
                    "D;JGT",
                    "@FALSE_GT//else",
                    "0;JMP",

                    "(FALSE_GT)",
                    "@SP    ",
                    "A=M-1  //points at x",
                    "M=0 ",
                    "@END_GT",
                    "0;JMP",
                    "(TRUE_GT)",
                    "@SP",
                    "A=M-1  //points at x",
                    "M=-1",

                    "(END_GT)",
                    "@R13",
                    "A = M",
                    "0;JMP",
                    "(GT.call.0)"]
    cur_call = functions_using_counter[get_gt]
    functions_using_counter[get_gt] += 1
    if cur_call == 0:
        return first_call_asm_commends
    return [
        "@GT.call." + str(cur_call),
        "D = A",
        "@GT",
        "0;JMP",
        "(GT.call." + str(cur_call) + ")"
    ]


def get_lt():
    """
    :return: list of asm command to calculate if x (SP[-2] < y (SP[-1])
    """
    first_call_asm_commends = ["//lt",
                               "@LT.call.0",
                               "D = A",
                               
                               "(LT)",
                               "@R13",
                               "M = D",

                               "@SP",
                               "M = M - 1",
                               "A = M   //points at y",
                               "D = M",
                               "@Y_POSITIVE_LT  //if y>0",
                               "D;JGT",

                               "//else y<= 0",
                               "@SP",
                               "A = M - 1     //points at x",
                               "D = M",
                               "@COMPARE_LT   //if x <= 0",
                               "D;JLE ",
                               "@FALSE_LT    //else x > 0",
                               "0;JMP       ",

                               "(Y_POSITIVE_LT)",
                               "@SP",
                               "A = M - 1     // points at x",
                               "D = M         // D = x",
                               "@COMPARE_LT   // if x > 0",
                               "D;JGT",
                               "@TRUE_LT      //else",
                               "0;JMP       ",

                               "(COMPARE_LT)",
                               "@SP",
                               "A = M      //points at y",
                               "D = D - M  // D was x, now x - y",
                               "@TRUE_LT   // if x-y < o",
                               "D;JLT",
                               "@FALSE_LT  //else",
                               "0;JMP",

                               "(FALSE_LT)",
                               "@SP    ",
                               "A=M-1  //points at x",
                               "M=0 ",
                               "@END_LT",
                               "0;JMP",

                               "(TRUE_LT)",
                               "@SP",
                               "A=M-1  //points at x",
                               "M=-1",

                               "(END_LT)",
                               "@R13",
                               "A = M",
                               "0;JMP",
                               "(LT.call.0)"]
    cur_call = functions_using_counter[get_lt]
    functions_using_counter[get_lt] += 1
    if cur_call == 0:
        return first_call_asm_commends
    return [
        "@LT.call." + str(cur_call),
        "D = A",
        "@LT",
        "0;JMP",
        "(LT.call." + str(cur_call) + ")"
    ]


functions_using_counter = {get_eq: 0, get_gt: 0, get_lt: 0}


def get_and():
    return["//and", "@SP", "M=M-1", "A=M", "D=M  //D=y", "A=A-1", "M=M&D //x=x&y"]


def get_or():
    return ["//or", "@SP", "M = M - 1", "A = M", "D = M", "A = A - 1", "M = M|D "]



def get_not():
    return ["//neg", "@SP", "A=M", "A=A-1", "M=!M"]


VM_functions_dict = {'push': get_push, 'pop': get_pop, 'add': get_add, 'sub': get_sub, 'neg': get_neg,
             'eq': get_eq, 'gt': get_gt, 'lt': get_lt, 'and': get_and, 'or': get_or, 'not': get_not}
