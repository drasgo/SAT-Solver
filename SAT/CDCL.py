from SAT.base_SAT_heuristic import Base_SAT_Heuristic_Solver
from SAT.DIMACS_decoder import Formula, Disjunction
import time
try:
    import cPickle as pickle
except ImportError:
    import pickle


class CDCL_Solver(Base_SAT_Heuristic_Solver):
    def __init__(self, formula):
        super().__init__(formula)

    def compute(self) -> bool:
        """
        Computes CDCL algorithm
        """
        self.formula = self.check_tautology(self.formula)
        self.starting_time = time.perf_counter()

        flag, _, _ = self.cdcl_recursive(pickle.dumps(self.formula), [self.formula.variables[0], False], {}, self.counter,
                                   pickle.dumps([]))
        if flag is False:
            flag = self.cdcl_recursive(pickle.dumps(self.formula), [self.formula.variables[0], True], {}, self.counter,
                                       pickle.dumps([]))

        self.counter_proof()

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
        assert isinstance(temporal_step, list)
        # Used for debugging for looking at the number of clauses before modification
        print("* Recursion n°: " + str(recursion_index) + ". Number of clauses bef.: " + str(
            len(new_formula.disjunctions)) + " Curr literal " + chosen_literal[0])

        # simplifications
        if chosen_literal[0] not in curr_result:
            curr_result[chosen_literal[0]] = chosen_literal[1]
            temporal_step.append(chosen_literal[0])
            new_formula, curr_result, conflict = CDCL_Solver.simplifications(new_formula, curr_result)

        print("Number of clauses after " + str(len(new_formula.disjunctions)) + " clauses.  Num of known literals: " +
              str(len(curr_result)) + "\n")

        # check if end (positive or negative)
        if len(new_formula.disjunctions) == 0:
            print(curr_result)
            self.result = curr_result
            return True, None, None

        if conflict != "":
        #     Check for the formulas in which that variable initially appeared
            return self.prepare_backtracking(conflict, temporal_step)

        new_variables = new_formula.get_variables()
        next_literal = [var for var in new_variables][0]

        while True:
            flag, back_state, new_clause = self.cdcl_recursive(pickle.dumps(new_formula), [next_literal, False],
                                                               curr_result.copy(), recursion_index,
                                                               pickle.dumps(temporal_step))
            print()
            print("giungere a " + str(back_state))
            print("arrivato a " + chosen_literal[0])
            if flag is True:
                return flag, None, None
            elif back_state != chosen_literal[0]:
                return flag, back_state, new_clause
            elif len(new_clause.literals) == 0:
                break
            else:
                print("new clause")
                print(new_clause.to_string() + ". old formula length " + str(len(new_formula.disjunctions)))
                new_formula.disjunctions.append(new_clause)
                print("new formula length " + str(len(new_formula.disjunctions)))
                new_formula, curr_result, conflict = CDCL_Solver.simplifications(new_formula, curr_result)

        print("**Back to recursion n° " + str(recursion_index) + "\n")

        return self.cdcl_recursive(pickle.dumps(new_formula), [next_literal, True], curr_result.copy(),
                                   recursion_index, pickle.dumps(temporal_step))

    def prepare_backtracking(self, conflict_variable: str, temporal_step: list):
        disjunction = Disjunction()
        back_state = ""
        print("conflict variable: " + conflict_variable)
        for clause in [cl for cl in self.formula.disjunctions if conflict_variable in
                                                                 [literal.get_name() for literal in cl.literals]]:
            print(clause.to_string())
            for literal in clause.literals:
                if literal not in disjunction.literals and literal.get_name() != conflict_variable:
                    literal.positive = not literal.positive
                    disjunction.literals.append(literal)


        print("num involved literals: " + str(len(disjunction.literals)))

        print("temporal steps")
        for step in temporal_step:
            if any(step == literal.get_name() for literal in disjunction.literals):
                back_state = step
                print("found step: " + step)
                break

        return False, back_state, disjunction
