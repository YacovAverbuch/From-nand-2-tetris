

import os, sys, re
import Basic_Command
import Function_Commands

INPUT_FILE_OR_DIR = 1


def list_of_files(path):
    #gets a path and returns a list of asm file names
    files_list=[]
    #if the path is a file name, returns a list of a single file name
    if os.path.isfile(path):
        files_list.append(path)
    #if the path is a directory name, returns a list of all the file names anded with .vm
    else:
        for file in os.listdir(path):
            if file.endswith(".vm"):
                files_list.append(os.path.join(path, file))
    return files_list


def parse_data(filepath):
    with open(filepath) as data_file:
        lines = []
        for line in data_file:
            lines.append(line)
    return lines


def ignore_comments_and_empty_lines(asm_lines_list):
    for line_num, line in enumerate (asm_lines_list):
        ignore_line  = re.match('^\s*(//|$)', line)
        if ignore_line:
            asm_lines_list[line_num] = None
            continue
    return


def translate_to_asm(text_lines, file_path):
    """
    :return list of asm commands strings
    """
    file_name = os.path.split(file_path)[1]
    asm_code_list = []
    for line in text_lines:
        if not line:
            continue

        pos = line.find('//')
        if pos != -1:
            line = line[:pos]  # clear the string after the '//'

        asm_code_list.append(['\n// ' + line[:-1]])

        push_pop_command = re.match('^\s*(push|pop)\s+(\S+)\s+(\d+)', line)
        if push_pop_command:
            p_func = Basic_Command.VM_functions_dict[push_pop_command.group(1)]
            asm_code_list.append(p_func(push_pop_command.group(2), push_pop_command.group(3),file_name[:-2]))
            continue


        label_command = re.match('^\s*(goto|if-goto|label)\s+(\S+)', line)
        if label_command:
            asm_code_list.append(Basic_Command.get_label_command(label_command.group(1), label_command.group(2)))
            continue

        function_command = re.match('^\s*(function|call)\s+(\S+)?\s+(\d+)?', line)
        if function_command:
            asm_code_list.append(Function_Commands.get_function_commands(function_command.group(1),function_command.group(2),
                                                                         function_command.group(3), file_name[:-2]))
            continue

        if(re.match('^\s*return', line)):
            asm_code_list.append(Function_Commands.get_function_commands('return', None, None, None))
            continue

        VM_command = re.match('^\s*([a-z]+)', line)
        if VM_command:
            asm_code_list.append(Basic_Command.VM_functions_dict[VM_command.group(1)]())
            continue

    return asm_code_list



def create_output(list_of_asm, vm_file_path):
    """
    :param list_of_asm: list of lists of asm commands
    :param vm_file_path: the path argument
    :return: None
    """
    if os.path.isfile(vm_file_path):
        asm_file_name = vm_file_path[:-2]+'asm'
    else:
        dir_name = os.path.split(vm_file_path)[1]
        separator = vm_file_path[-len(dir_name) - 1: -len(dir_name)]
        asm_file_name = vm_file_path + separator + dir_name + '.asm'

    output_file = open(asm_file_name, 'w')

    for i, file in enumerate(list_of_asm):
        list_of_asm[i] = "\n".join(file)

    output_file.write("\n".join(list_of_asm))
    output_file.close()
    return


def translate_all_files(path):
    """
    Iterate over all the files in path (or the only file if path is a file)
    translate every file into a list of asm strings. then call the function to create the output
    from the list of the lists
    :param path: the path argument
    :return: None
    """
    path = os.path.abspath(path)
    files_list = list_of_files(path)
    list_of_asm_files = []
    list_of_asm_files.append(['@256','D=A','@SP','M=D']+
                             Function_Commands.get_function_commands('call', 'Sys.init', 0, 'initialize.program.call'))
    for file in files_list:
        VM_lines = parse_data(file)  # list of VM commands
        ignore_comments_and_empty_lines(VM_lines)
        asm_lines = translate_to_asm(VM_lines, file)  # a list of lists of commands
        list_of_asm_files.extend(asm_lines)

    create_output(list_of_asm_files, path)
    return


if __name__ == "__main__":
    file_or_dir = sys.argv[INPUT_FILE_OR_DIR]
    translate_all_files(file_or_dir)


