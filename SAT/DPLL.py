from SAT.base_SAT_heuristic import Base_SAT_Heuristic_Solver
from SAT.DIMACS_decoder import Formula
import time


class DPLL_Solver(Base_SAT_Heuristic_Solver):
    def __init__(self, formula):
        super().__init__(formula)

    def compute(self) -> bool:
        """
        Computes DPLL algorithm
        """
        self.formula = self.check_tautology(self.formula)
        self.starting_time = time.perf_counter()

        flag = self.dpll_recursive(self.formula.to_string(), [self.formula.variables[0], False], {}, self.counter)
        if flag is False:
            flag = self.dpll_recursive(self.formula.to_string(),[self.formula.variables[0], True], {}, self.counter)

        print("Counter proof:")
        for elem in self.formula.variables:
            if elem not in self.result:
                self.result[elem] = False
        if self.formula.compute_formula(self.result) is True:
            print("Good counter proof")
        else:
            print("fuck")

        print("Finished lookup.\n")
        self.summary_information(flag)
        return flag

    def dpll_recursive(self, disjunctions: str, chosen_literal: list, curr_result: dict, recursion_index):
        # chosen_literal = [literal_name, literal_value]
        # Used for keeping track of the current recursion index
        recursion_index += 1
        # Counter for total number of recursions
        self.counter = recursion_index
        # Create a new formula from the string disjunctions
        new_formula = Formula(str_logic=disjunctions)
        # Used for debugging for looking at the number of clauses before modification
        print("* Recursion n°: " + str(recursion_index) + ". Number of clauses bef.: " + str(len(new_formula.disjunctions))
              + " Curr literal " + chosen_literal[0])

        # First iteration for check of pure literals or unit clauses
        simplified_literals = DPLL_Solver.check_pure_literals(new_formula.disjunctions, new_formula.get_variables())
        if len(simplified_literals) == 0:
            simplified_literals = DPLL_Solver.check_unit_clauses(new_formula.disjunctions)

        if len(simplified_literals) > 0:
            curr_result.update(simplified_literals)
            # Executes all the simplifications and add all the simplifiable literals to curr_result
            new_formula, curr_result = DPLL_Solver.simplifications(new_formula, curr_result)

        # If the literal chosen in the previous recursive state is not in the curr_result after the simplification
        # add it to the curr_result and redo the simplifications
        if chosen_literal[0] not in curr_result:
            curr_result[chosen_literal[0]] = chosen_literal[1]
            new_formula, curr_result = DPLL_Solver.simplifications(new_formula, curr_result)
        # Gets new literal from the formula
        print("Number of clauses after " + str(len(new_formula.disjunctions)) + " clauses.  Num of known literals: " + str(len(curr_result)) + "\n")

        if len(new_formula.disjunctions) == 0:
            # Check if formula is empty
            print(curr_result)
            self.result = curr_result
            return True

        if any(len(elem.literals) == 0 for elem in new_formula.disjunctions):
            # Check if there is any empty clauses
            print("error")
            self.number_backtracking += 1
            return False

        new_variables = new_formula.get_variables()
        next_literal = [var for var in new_variables][0]
        # Compute the method recursively (first with the negated literal and then with the positive literal
        if self.dpll_recursive(new_formula.to_string(), [next_literal, False], curr_result.copy(), recursion_index) is True:
            return True

        print("**Back to recursion n° " + str(recursion_index) + "\n")
        return self.dpll_recursive(new_formula.to_string(), [next_literal, True], curr_result.copy(), recursion_index)

    @staticmethod
    def simplifications(new_formula, curr_result):
        # If there are pure literals or unit clauses, executes simplifications and re-check for pure literals
        # and/or unit clauses in cascade until there is nothing else to simplify in the current state
        while True:
            new_formula.disjunctions = DPLL_Solver.shorten_formula(new_formula.disjunctions, curr_result)
            new_formula.disjunctions = DPLL_Solver.remove_clauses(new_formula.disjunctions, curr_result)

            simplified_literals = DPLL_Solver.check_pure_literals(new_formula.disjunctions, new_formula.get_variables())
            if len(simplified_literals) == 0:
                simplified_literals = DPLL_Solver.check_unit_clauses(new_formula.disjunctions)

            if len(simplified_literals) == 0:
                break
            curr_result.update(simplified_literals)
        return new_formula, curr_result
