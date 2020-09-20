from SAT.base_SAT_heuristic import Base_SAT_Heuristic_Solver
from SAT.DIMACS_decoder import Formula, Disjunction, Literal
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

        if self.branching == "vsids":
            first_literal = CDCL_Solver.perform_vsids(self.formula, self.number_backtracking)
        else:
            first_literal = self.formula.variables[0]

        flag, _, _ = self.cdcl_recursive(pickle.dumps(self.formula), [first_literal, False], {}, self.counter,
                                   pickle.dumps(OrderedDict()))
        if flag is False:
            flag = self.cdcl_recursive(pickle.dumps(self.formula), [first_literal, True], {}, self.counter,
                                       pickle.dumps(OrderedDict()))

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
        assert isinstance(temporal_step, OrderedDict)
        # Used for debugging for looking at the number of clauses before modification
        print("* Recursion n°: " + str(recursion_index) + ". Number of clauses bef.: " + str(
            len(new_formula.disjunctions)) + " Curr literal " + chosen_literal[0])

        # simplifications
        if chosen_literal[0] not in curr_result:
            curr_result[chosen_literal[0]] = chosen_literal[1]
            temporal_step[chosen_literal[0]] = []
        while True:
            new_formula, curr_result, conflict, added_literals = CDCL_Solver.simplifications(new_formula, curr_result)
            temporal_step[chosen_literal[0]] += added_literals
            print("Number of clauses after " + str(len(new_formula.disjunctions)) + " clauses.  Num of known literals: " +
                  str(len(curr_result)) + "\n")

            # check if end (positive or negative)
            if len(new_formula.disjunctions) == 0:
                print(curr_result)
                self.result = curr_result
                return True, None, None

            if conflict != "":
                # if conflict not in self.n_of_backtracking:
                #     self.n_of_backtracking[conflict] = 1
                # else:
                #     self.n_of_backtracking[conflict] += 1
                #     Check for the formulas in which that variable initially appeared
                return self.prepare_backtracking(conflict, temporal_step)

            new_variables = new_formula.get_variables()

            if self.vsids is True:
                next_literal = self.perform_vsids(new_formula, self.number_backtracking)
            else:
                next_literal = [var for var in new_variables][0]

            flag, back_state, new_clause = self.cdcl_recursive(pickle.dumps(new_formula), [next_literal, False],
                                                               curr_result.copy(), recursion_index,
                                                               pickle.dumps(temporal_step))
            print()
            print("giungere a " + str(back_state))
            print("arrivato a " + chosen_literal[0])

            if flag is True:
                return True, None, None

            elif back_state != chosen_literal[0]:
                return flag, back_state, new_clause

            else:
                print("new clause")
                print(new_clause.to_string() + ". old formula length " + str(len(new_formula.disjunctions)))
                new_formula.disjunctions.append(new_clause)
                print("new formula length " + str(len(new_formula.disjunctions)))

    def prepare_backtracking(self, conflict_variable: str, temporal_step: OrderedDict):
        disjunction = Disjunction()
        self.number_backtracking += 1
        back_state = ""
        print("conflict variable: " + conflict_variable)
        for clause in [cl for cl in self.formula.disjunctions if conflict_variable in
                                                                 [literal.get_name() for literal in cl.literals]]:
            print(clause.to_string())
            for literal in clause.literals:
                # if all(literal.get_name() != lit.get_name() for lit in disjunction.literals) and \
                #         literal.get_name() != conflict_variable:
                temp_literal = Literal()
                temp_literal.name = literal.get_name()
                temp_literal.positive = literal.positive
                disjunction.literals.append(temp_literal)

        print("temporal steps: " + str(temporal_step))

        steps = []

        for elem in temporal_step:
            steps.append(elem)
            for sub_elem in temporal_step[elem]:
                steps.append(sub_elem)

        for step in steps:
            if any(step == literal.get_name() for literal in disjunction.literals):
                if step in temporal_step:
                    back_state = step
                else:
                    for elem in temporal_step:
                        if any(step == sub for sub in temporal_step[elem]):
                            back_state = elem
                            break
                print("found step: " + step)
                break

        flag = False
        while flag is False:
            flag = True
            for literal in disjunction.literals:
                if any(literal != lit and literal.get_name() == lit.get_name() and
                       literal.positive is not lit.positive for lit in disjunction.literals):
                    print("removed positive/negatuve: " + literal.to_string() + " and " + [lit for lit in disjunction.literals if literal != lit and
                                                                                           literal.get_name() == lit.get_name() and
                                                                                           literal.positive is not lit.positive][0].to_string())
                    disjunction.literals.remove(literal)
                    disjunction.literals.remove([lit for lit in disjunction.literals if literal != lit and
                                                 literal.get_name() == lit.get_name() and
                                                 literal.positive is not lit.positive][0])
                    flag = False
                    break
                if any(literal != lit and literal.get_name() == lit.get_name() and
                       literal.positive is lit.positive for lit in disjunction.literals):
                    print("removed literal with same value " + literal.to_string())
                    disjunction.literals.remove(literal)
                    flag = False
                    break

        print("num involved literals: " + str(len(disjunction.literals)))
        print(disjunction.to_string())

        return False, back_state, disjunction


