import sys
import os
from SAT.DIMACS_decoder import Formula


def execute_main(args):
    technique_number, input_file = grab_input_parameters(args)
    check_file_exists(input_file)
    formula = Formula(read_DIMACS_input_file(input_file))
    print(formula.to_string())
    print("\n")
    input()
    print(len(formula.disjunctions))

    print("\n")
    input()
    for dis in formula.disjunctions:
        input()
        print(len(dis.literals))


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


if __name__ == "__main__":
    execute_main(sys.argv)
    exit()