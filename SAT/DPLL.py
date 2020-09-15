from SAT.base_SAT_heuristic import Base_SAT_Heuristic_Solver
from collections import OrderedDict


class DPLL_Solver(Base_SAT_Heuristic_Solver):
    def __init__(self, formula):
        super().__init__(formula)

    def compute(self) -> bool:
        """
        Computes DPLL algorithm
        The basic idea of the algorithm is:

    1. "Guess" a variable
    2. Find all unit clauses created from the last assignment and assign the needed value
    3. Iteratively retry step 2 until there is no change (found transitive closure)
    4. If the current assignment cannot yield true for all clauses - fold back from recursion
    and retry a different assignment
    5. If it can - "guess" another variable (recursively invoke and return to 1)

    Termination:

    1. There is nowhere to go "back to" and change a "guess" (no solution)
    2. All clauses are satisfied (there is a solution, and the algorithm found it)
        """
        curr_variables = OrderedDict()
        pre_given = self.formula.return_unit_clauses_variable([]).keys()
        print("pre give " + str(pre_given))
        for variable in self.formula.variables:
            # print(curr_variables)
            # print()
            # print(len(curr_variables))
            # print("\n**")
            if variable not in curr_variables:
                # print("Adding variable to curr_variables")
                curr_variables[variable] = False
                curr_variables.update(self.formula.return_unit_clauses_variable(curr_variables.keys()))
                # print("added new variable " + str(variable) + " and unit clauses. new length")
                # print(len(curr_variables))

        # print("\n***********************************")
        # print(curr_variables.keys())
        # print("\n\n")
        # print(self.formula.variables)
        # print([var for var in self.formula.variables if var not in curr_variables.keys()])

        total_iterations = (len(curr_variables) - len(pre_given)) ** 2

        while any(curr_variables[var] is False for var in curr_variables):
            # Until there is even a 0 in the sequence, it keeps going.
            # E.g. 000100 --> 100100 --> 010100 --> ... --> 011111 --> 111111
            if total_iterations % 10000 == 0:
                print("remaining " + str(total_iterations) + " iterations")
                print(curr_variables)
                print("\n\n\n")
                input()
            total_iterations = total_iterations - 1
            flag = False

            if self.formula.compute_formula(curr_variables) is True:
                # Tries to compute the formula and check if with the current values it is satisfied
                self.result = curr_variables
                return True

            for updated_var in curr_variables:
                # Updates every element from left to right
                # E.g. 00100.. --> 10100

                if updated_var in pre_given:
                    # If it is a literal part of the given setting, skip it
                    continue

                elif flag is True or curr_variables[updated_var] is False:
                    # If in the previous iterations the variables were like 1110.. here
                    # the sequence will become 0001..
                    # Or if the variable is 0, makes it 1
                    curr_variables[updated_var] = not curr_variables[updated_var]
                    if curr_variables[updated_var] is True:
                        break

                else:
                    # If the current variable is 1, in the next iteration it will become 01
                    curr_variables[updated_var] = False
                    flag = True

                    for prev_variable in curr_variables:
                        # Sets to False any previous variable
                        if prev_variable in pre_given:
                            continue
                        elif prev_variable != updated_var:
                            curr_variables[prev_variable] = False
                        else:
                            break

        if self.formula.compute_formula(curr_variables) is True:
            # Tries to compute the formula and check if with the current values it is satisfied
            self.result = curr_variables
            return True

        print("finished lookup. exiting")
        return False