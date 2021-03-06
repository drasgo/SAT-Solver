from SAT.base_SAT_heuristic import Base_SAT_Heuristic_Solver
from SAT.DIMACS_decoder import Formula
import time
try:
    import cPickle as pickle
except ImportError:
    import pickle


class DPLL_Solver(Base_SAT_Heuristic_Solver):
    def __init__(self, formula, branching: str = ""):
        super().__init__(formula, branching)

    def compute(self) -> bool:
        """
        Computes DPLL algorithm
        """
        self.formula = self.check_tautology(self.formula)
        self.starting_time = time.perf_counter()
        first_literal = self.choose_branching(self.formula)

        flag = self.dpll_recursive(pickle.dumps(self.formula), [first_literal, False], {}, 0)
        if flag is False:
            flag = self.dpll_recursive(pickle.dumps(self.formula),[first_literal, True], {}, 0)

        flag = self.counter_proof()

        print("Finished lookup.\n")
        self.summary_information(flag)
        return flag

    # def dpll_recursive(self, disjunctions: str, chosen_literal: list, curr_result: dict, recursion_index):
    def dpll_recursive(self, formula, chosen_literal: list, curr_result: dict, recursion_index):
        # chosen_literal = [literal_name, literal_value]
        # Used for keeping track of the current recursion index
        recursion_index += 1
        # Counter for total number of recursions
        self.counter += 1
        # Create a new formula from the string disjunctions
        new_formula = pickle.loads(formula)
        assert isinstance(new_formula, Formula)
        # Used for debugging for looking at the number of clauses before modification
        print("* Recursion n°: " + str(recursion_index) + ". Number of clauses bef.: " +
              str(len(new_formula.disjunctions)) + " Curr literal " + chosen_literal[0])

        # If the literal chosen in the previous recursive state is not in the curr_result after the simplification
        # add it to the curr_result and redo the simplifications

        if chosen_literal[0] not in curr_result:
            curr_result[chosen_literal[0]] = chosen_literal[1]
            new_formula, curr_result, empty_clause, _ = DPLL_Solver.simplifications(new_formula, curr_result)

        print("Number of clauses after " + str(len(new_formula.disjunctions)) + " clauses.  Num of known literals: " +
              str(len(curr_result)) + "\n")

        if len(new_formula.disjunctions) == 0:
            # Check if formula is empty
            print(curr_result)
            self.result = curr_result
            return True

        if empty_clause != "":
            # Check if there is any empty clauses
            print("error")
            self.number_backtracking += 1
            return False

        next_literal = self.choose_branching(new_formula)
        if self.dpll_recursive(pickle.dumps(new_formula), [next_literal, False], curr_result.copy(), recursion_index) is True:
            return True

        print("**Back to recursion n° " + str(recursion_index) + "\n")
        return self.dpll_recursive(pickle.dumps(new_formula), [next_literal, True], curr_result.copy(), recursion_index)
