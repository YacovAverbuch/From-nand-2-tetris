
import os, sys, re
from JackAnalyzer import JackAnalyzer
from JackTokenizer import JackTokenizer

def list_of_files(path):
    files_list = []
    if os.path.isfile(path):
        files_list.append(path)
    elif os.path.isdir(path):
        for file in os.listdir(path):
            if file.endswith(".jack"):
                files_list.append(os.path.join(path, file))
    else:
        print('ERROR: No such file or directory')
        sys.exit()
    return files_list


def parse_data(filepath):
    with open(filepath) as data_file:
        data = data_file.read()
    return data


def create_output(list_of_xml_lists):
    """
    :param list_of_xml_lists: list of lists of xml lines
    :param directory
    :return: None
    """
    for file_list in list_of_xml_lists:
        xml_file_name = file_list[0][:-4] + 'vm'
        output_file = open(xml_file_name, 'w')

        for line in file_list[1]:
            output_file.write(line)
            output_file.write("\n")
        output_file.close()
    return


def all_files_to_VM(path):
    """
    Iterate over all the jack files in path (or the only file if path is a file)
    translate every file into a list of vm strings. then call the function to create the output
    from the list of the lists
    :param path: the path argument
    :return: None
    """
    path = os.path.abspath(path)
    files_list = list_of_files(path)
    list_of_VM_files = []
    # each 'file' in the list, should be a tuple of two objects. the first is a string represent the name of
    # the origin file and the second is a list of strings
    for file_name in files_list:
        jack_lines = parse_data(file_name)
        # list of jack lines. include empty lines and comments
        token_lines = JackTokenizer(jack_lines)
        token_lines.parse_jack()

        analyzer = JackAnalyzer(token_lines.token_list)
        analyzer.parse_class_tokens()
        list_of_VM_files.append((file_name, analyzer.VM_lines))
    create_output(list_of_VM_files)
    return


if __name__ == "__main__":
    all_files_to_VM(sys.argv[1])


