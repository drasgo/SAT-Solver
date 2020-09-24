from SAT.base_SAT_heuristic import Base_SAT_Heuristic_Solver
from SAT.DIMACS_decoder import Formula
from collections import OrderedDict
import time
try:
    import cPickle as pickle
except ImportError:
    import pickle


class CDCL_Solver(Base_SAT_Heuristic_Solver):
    def __init__(self, formula, branching: str = ""):
        super().__init__(formula, branching)

    def compute(self) -> bool:
        """
        Computes CDCL algorithm
        """
        self.formula = self.check_tautology(self.formula)
        self.starting_time = time.perf_counter()
        first_literal = self.choose_branching(self.formula)

        flag, _, _ = self.cdcl_recursive(pickle.dumps(self.formula), [first_literal, False], {}, self.counter,
                                   pickle.dumps(OrderedDict()))
        if flag is False:
            flag = self.cdcl_recursive(pickle.dumps(self.formula), [first_literal, True], {}, self.counter,
                                       pickle.dumps(OrderedDict()))

        flag = self.counter_proof()

        print("Finished lookup.\n")
        self.summary_information(flag)
        return flag

    def cdcl_recursive(self, formula, chosen_literal: list, curr_result: dict, recursion_index, temporal_step):
        # Used for keeping track of the current recursion index
        recursion_index += 1
        # Counter for total number of recursions
        self.counter = recursion_index
        new_formula = pickle.loads(formula)
        temporal_step = pickle.loads(temporal_step)
        assert isinstance(new_formula, Formula)
        assert isinstance(temporal_step, OrderedDict)
        # Used for debugging for looking at the number of clauses before modification
        old_disjunction_length = str(len(new_formula.disjunctions))

        # simplifications
        if chosen_literal[0] not in curr_result:
            curr_result[chosen_literal[0]] = chosen_literal[1]
            temporal_step[chosen_literal[0]] = []
        while True:
            new_formula, curr_result, conflict, added_literals = CDCL_Solver.simplifications(new_formula, curr_result)
            temporal_step[chosen_literal[0]] += added_literals
            print("* Recursion n°: " + str(recursion_index) + ". Number of clauses bef.: " + old_disjunction_length +
                  ". Curr literal " + chosen_literal[0] + ". Number of clauses after " +
                  str(len(new_formula.disjunctions)) + " clauses.  Num of known literals: " +
                  str(len(curr_result)) + "\n")

            # check if end (positive or negative)
            if len(new_formula.disjunctions) == 0:
                print("SOLUTION!")
                self.result = curr_result
                return True, None, None

            if conflict != "":
                print("Conflict for variable " + conflict)
                return self.prepare_backtracking(conflict, temporal_step)

            next_literal = self.choose_branching(new_formula)
            flag, back_state, new_clause = self.cdcl_recursive(pickle.dumps(new_formula), [next_literal, False],
                                                               curr_result.copy(), recursion_index,
                                                               pickle.dumps(temporal_step))

            if flag is True:
                return True, None, None

            elif back_state != chosen_literal[0]:
                return flag, back_state, new_clause

            else:
                print("Back to " + str(recursion_index) + " recursion state")
                new_formula.disjunctions.append(new_clause)
