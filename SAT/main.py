import sys
import os
from SAT.DIMACS_decoder import Formula


def execute_main(args: list):
    technique_number, input_file = grab_input_parameters(args)
    result_file_path = "./" + input_file[input_file.rfind("/"):input_file.rfind(".")] + ".out"
    check_file_exists(input_file)
    formula = Formula(read_DIMACS_input_file(input_file))

    if technique_number == 1:
        from SAT.DPLL import DPLL_Solver
        solver = DPLL_Solver(formula)
    elif technique_number == 2:
        from SAT.CDCL import CDCL_Solver
        solver = CDCL_Solver(formula)
    elif technique_number == 3:
        from SAT.DPLL import DPLL_Solver
        solver = DPLL_Solver(formula, branching="VSIDS")
    elif technique_number == 4:
        from SAT.DPLL import DPLL_Solver
        solver = DPLL_Solver(formula, branching="MOM")
    elif technique_number == 5:
        from SAT.DPLL import DPLL_Solver
        solver = DPLL_Solver(formula, branching="MAXO")
    elif technique_number == 6:
        from SAT.DPLL import DPLL_Solver
        solver = DPLL_Solver(formula, branching="MAMS")
    elif technique_number == 7:
        from SAT.DPLL import DPLL_Solver
        solver = DPLL_Solver(formula, branching="JW")
    elif technique_number == 8:
        from SAT.DPLL import DPLL_Solver
        solver = DPLL_Solver(formula, branching="UP")
    elif technique_number == 9:
        from SAT.DPLL import DPLL_Solver
        solver = DPLL_Solver(formula, branching="SUP")
    elif technique_number == 10:
        from SAT.CDCL import CDCL_Solver
        solver = CDCL_Solver(formula, branching="VSIDS")
    elif technique_number == 11:
        from SAT.CDCL import CDCL_Solver
        solver = CDCL_Solver(formula, branching="MOM")
    elif technique_number == 12:
        from SAT.CDCL import CDCL_Solver
        solver = CDCL_Solver(formula, branching="MAXO")
    elif technique_number == 13:
        from SAT.CDCL import CDCL_Solver
        solver = CDCL_Solver(formula, branching="MAMS")
    elif technique_number == 14:
        from SAT.CDCL import CDCL_Solver
        solver = CDCL_Solver(formula, branching="JW")
    elif technique_number == 15:
        from SAT.CDCL import CDCL_Solver
        solver = CDCL_Solver(formula, branching="UP")
    elif technique_number == 16:
        from SAT.CDCL import CDCL_Solver
        solver = CDCL_Solver(formula, branching="SUP")
    else:
        print("Number " + str(technique_number) + " not recognized. Check --help for more informations.")
        exit()

    solver.compute()
    with open(result_file_path, "w") as fp:
        fp.write(solver.get_result())


def grab_input_parameters(args: list):
    tech = None
    if "--help" in args:
        print("""
SAT solver written in Python. Commands available:
\t-S1 : DPLL
\t-S2 : CDCL
\t-S3 : DPLL + VSIDS
\t-S4 : DPLL + MOM
\t-S5 : DPLL + MAXO
\t-S6 : DPLL + MAMS
\t-S7 : DPLL + Jeroslaw-Wang
\t-S8 : DPLL + UP
\t-S9 : DPLL + SUP
\t-S10 : CDCL + VSIDS
\t-S11 : CDCL + MOM
\t-S12 : CDCL + MAXO
\t-S13 : CDCL + MAMS
\t-S14 : CDCL + Jeroslaw-Wang
\t-S15 : CDCL + UP
\t-S16 : CDCL + SUP
Example command: main.py -S1 "input_file_path"
        """)

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
