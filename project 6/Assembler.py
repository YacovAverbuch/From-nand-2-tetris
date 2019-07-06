

import os, sys, re

SCRIPT_NAME_LOCATION = 0
INPUT_FILE_OR_DIR = 1


comp_dict = {'D>>': '010010000', 'A>>': '010000000', 'M>>': '011000000', 'D<<': '010110000', 'A<<': '010100000',
             'M<<': '011100000', '0': '110101010', '1': '110111111', '-1': '110111010', 'D': '110001100',
             'A': '110110000', 'M': '111110000', '!D': '110001101', '!A': '110110001', '!M': '111110001',
             '-D': '110001111', '-A': '110110011', '-M': '111110011', 'D+1': '110011111', 'A+1': '110110111',
             'M+1': '111110111', 'D-1': '110001110', 'A-1': '110110010', 'M-1': '111110010', 'D+A': '110000010',
             'D+M': '111000010', 'D-A': '110010011', 'D-M': '111010011',
             'A-D': '110000111',
             'M-D': '111000111', 'M+D': '111000010',
             'D&A': '110000000', 'D&M': '111000000', 'D|A': '110010101', 'D|M': '111010101'}

jump_dict = {None: '000', 'JGT': '001', 'JEQ': '010', 'JGE': '011', 'JLT': '100',
             'JNE': '101', 'JLE': '110', 'JMP': '111'}


def list_of_files(path):
    """gets a path and returns a list of asm file names"""
    files_list=[]
    path = os.path.abspath(path)

    #if the path is a file name, returns a list of a single file name
    if os.path.isfile(path):
        files_list.append(path)
    #if the path is a directory name, returns a list of all the file names anded with .asm
    else:
        for file in os.listdir(path):
            if file.endswith(".asm"):
                files_list.append(os.path.join(path, file))
    return files_list


def parse_data(filepath):
    with open(filepath) as data_file:
        lines = []
        for line in data_file:
            lines.append(line)
    return lines


def init_symbols_dictionary():
    symbols = {'SP' : bin(0)[2:].zfill(15), 'LCL' : bin(1)[2:].zfill(15), 'ARG' : bin(2)[2:].zfill(15),
               'THIS' : bin(3)[2:].zfill(15), 'THAT' : bin(4)[2:].zfill(15),
               'SCREEN' : bin(16384)[2:].zfill(15), 'KBD' : bin(24576)[2:].zfill(15)}
    for i in range(16):
        symbols['R' + str(i)] = bin(i)[2:].zfill(15)
    return symbols


def collect_symbols_and_ignore_coments(asm_lines_list, asm_symbols_dic):
    i = 0
    for line_num, line in enumerate (asm_lines_list):
        ignore_line  = re.match('^\s*(//|$)', line)
        if not line or ignore_line:
            asm_lines_list[line_num] = None
            continue
        lable  = re.match('^\s*\(\s*([\S]+)\)', line)
        if lable:
            asm_symbols_dic[lable.group(1)] = bin(i)[2:].zfill(15)  # gives the line the number of the next line
            asm_lines_list[line_num] = None
            continue
        i = i + 1  # its a command line
    return


def get_dest(text_dest):
    if not text_dest:
        return '000'
    text_dest = text_dest.replace('=', '')
    text_dest = text_dest.replace(' ', '')

    binary_dest = ['0', '0', '0']
    if 'A' in text_dest:
        binary_dest[0] = '1'

    if 'D' in text_dest:
        binary_dest[1] = '1'

    if 'M' in text_dest:
        binary_dest[2] = '1'

    return ''.join(binary_dest)


def translate_to_binary(text_lines, asm_symbols):
    ''':return list of binary strings, containing only 0/1'''
    sel_avaiable = 16
    binary_code_list = []
    for line in text_lines:
        binary_command = '0'
        if not line:
            continue
        A_commmand = re.match('^\s*@(\S+)', line)
        if A_commmand:
            var = A_commmand.group(1)
            if var[0].isdigit():  # it is a number for sel
                binary_command += bin(int(var))[2:].zfill(15)
            else:  # it is a variable
                if var not in asm_symbols:
                    asm_symbols[var] = bin(sel_avaiable)[2:].zfill(15)
                    sel_avaiable += 1
                binary_command += asm_symbols[var]
            binary_code_list.append(binary_command)
            continue

        C_command = re.match('^\s*([AMD\s]+=)?([AMD!&|+\-10\s]+)(\s*;\s*([A-Z]+))?', line)
        binary_command = '1'  # the C_command start with '1'

        comp = C_command.group(2).strip()
        comp = comp_dict[comp]
        dest = get_dest(C_command.group(1))
        jmp = jump_dict[C_command.group(4)]

        binary_command = binary_command + comp + dest + jmp
        binary_code_list.append(binary_command)
    return binary_code_list



def create_output(list_of_bin, asm_file_name):
    hack_file_name = asm_file_name[:-3]+'hack'
    output_file = open(hack_file_name, 'w')
    output_file.write("\n".join(list_of_bin))
    output_file.close()
    return



def path_to_bin_files(path):
    """gets a list of files and..... does everything"""
    files_list=list_of_files(path)
    for file in files_list:
        asm_lines = parse_data(file)
        symbols_dict = init_symbols_dictionary()
        collect_symbols_and_ignore_coments(asm_lines, symbols_dict)
        bin_lines = translate_to_binary(asm_lines, symbols_dict)
        create_output(bin_lines, file)


if __name__ == "__main__":
    script_name = sys.argv[SCRIPT_NAME_LOCATION]
    file_or_dir = sys.argv[INPUT_FILE_OR_DIR]
    path_to_bin_files(file_or_dir)
