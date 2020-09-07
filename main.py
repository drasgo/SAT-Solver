import sys
import os

def grab_input_parameters(args: list):
    tech = None
    if "--help" in args:
        print("""SAT solver written in Python. Commands available:
                    \t-S0 : DPLNN
                    \t-S1 : ???
                    \t-S2 : ???
                    Example command: main.py -S1 "input_file_path" """)

    elif len(args) >= 3:
        if "-S" in args[1].upper():
            tech = args[1].split("S")[1]
        path = args[2]
        try:
            return int(tech), path
        except TypeError:
            print("Technique number not specified. Type --help for consulting the technique types and numbers")
    else:
        print("-S+number and/or input file path missing")
    exit()

def check_file_exists(file_path: str):
    if not os.path.exists(file_path):
        print("File " + file_path + " does not exist!")
        exit()

def read_DIMACS_input_file(file_path: str) -> str:
    with open(file_path, "r") as fp:
        dimacs = fp.read()
    return dimacs

def remove_comments(dimacs: str) -> str:
    final = []
    for line in dimacs.split("\n"):
        if line.split(" ")[0] != "c":
            final.append(line)
    return "\n".join(final)

def variables_and_clauses(dimacs: str):
    variables_temp = 0
    clauses_temp = 0
    dim = dimacs.split("\n")
    for line in dim:
        characters = line.split(" ")
        if characters[0] == "p" and characters[1] == "cnf" and len(characters) == 4:
            variables_temp = characters[2]
            clauses_temp = characters[3]
            dim.remove(line)
            break
    if variables_temp != 0 and clauses_temp != 0:
        return variables_temp, clauses_temp, "\n".join(dim)
    else:
        print("Error reading clauses and/or variable in DIMACS input file")
        exit()

def convert_DIMACS_to_logic(dimacs: str) -> str:
    """
    This function converts a DIMACS set of rules in a string where the variables are divided by ORs and
    the clauses are divided by ANDs.
    E.g.    -111 -112 0
            -113 -115 0
                ||
                V
    (-111OR-112)AND(-113OR-115)
     """
    converted_logic = ""

    for line in dimacs.split("\n"):
        converted_line = ""
        split_line = line.split(" ")

        if converted_logic != "":
            converted_logic = converted_logic + "AND"

        for var in split_line:
            if var == "0":
                break

            else:
                if converted_line != "":
                    converted_line = converted_line + "OR"
                converted_line = converted_line + var

        converted_logic = converted_logic + "(" + converted_line + ")"

    return converted_logic

if __name__ == "__main__":
    technique_number, input_file = grab_input_parameters(sys.argv)
    check_file_exists(input_file)
    dimacs_input = remove_comments(read_DIMACS_input_file(input_file))
    variables, clauses, dimacs_input = variables_and_clauses(dimacs_input)
    logic = convert_DIMACS_to_logic(dimacs_input)
    print(logic)