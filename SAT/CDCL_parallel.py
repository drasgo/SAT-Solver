from SAT.base_SAT_heuristic import Base_SAT_Heuristic_Solver
from SAT.DIMACS_decoder import Formula, Disjunction, Literal
from collections import OrderedDict
import multiprocessing
import psutil
import time
try:
    import cPickle as pickle
except ImportError:
    import pickle


MAX_THREADS = 4
result = multiprocessing.Manager().dict()
num_recursion = multiprocessing.Value("i", 0)
flag = multiprocessing.Value("b", False)
num_backtracking = multiprocessing.Value("i",0)
num_threads = multiprocessing.Value("i", 2)
shared_formula = multiprocessing.Value("s", "")
class CDCL_Solver(Base_SAT_Heuristic_Solver):
    def __init__(self, formula, branching: str = ""):
        self.lock = multiprocessing.Lock()
        super().__init__(formula, branching)

    def compute(self) -> bool:
        """
        Computes CDCL algorithm
        """
        self.formula = self.check_tautology(self.formula)
        self.starting_time = time.perf_counter()
        first_literal = self.choose_branching(self.formula)

        thread1 = multiprocessing.Process(target=self.cdcl_recursive, args=(pickle.dumps(self.formula), [first_literal, False], {}, self.counter,
                                   pickle.dumps(OrderedDict())))
        thread2 = multiprocessing.Process(target=self.cdcl_recursive, args=(pickle.dumps(self.formula), [first_literal, True], {}, self.counter,
                                   pickle.dumps(OrderedDict())))

        thread1.start()
        thread2.start()
        while (thread1.is_alive() or thread2.is_alive()) and flag.value is False:
            pass
        if flag.value is True:
            if thread1.is_alive():
                parent = psutil.Process(thread1.pid)
                for child in parent.children(recursive=True):
                    child.kill()
                parent.kill()
            elif thread2.is_alive():
                parent = psutil.Process(thread2.pid)
                for child in parent.children(recursive=True):
                    child.kill()
                parent.kill()
        else:
            if thread1.is_alive():
                thread1.join()
            else:
                thread2.join()

        self.number_backtracking = num_backtracking.value
        self.max_num_threads = num_threads.value
        self.counter = num_recursion.value
        self.result = result
        self.counter_proof()
        print("Finished lookup.\n")
        self.summary_information(flag.value)
        return flag.value

    def cdcl_recursive(self, formula, chosen_literal: list, curr_result: dict, recursion_index, temporal_step, added_clause: str = ""):
        # Used for keeping track of the current recursion index
        global shared_formula
        global num_backtracking
        global num_recursion
        global num_threads
        global result
        global flag
        recursion_index += 1
        # Counter for total number of recursions
        num_recursion.value = max(num_recursion.value, recursion_index)
        new_formula = pickle.loads(formula)
        temporal_step = pickle.loads(temporal_step)
        assert isinstance(new_formula, Formula)
        assert isinstance(temporal_step, OrderedDict)
        # Used for debugging for looking at the number of clauses before modification
        old_disjunction_length = str(len(new_formula.disjunctions))

        if chosen_literal[0] not in curr_result:
            curr_result[chosen_literal[0]] = chosen_literal[1]
            temporal_step[chosen_literal[0]] = []

        while True:
            if flag.value is True:
                return True, None, None

            if  added_clause != shared_formula.value:
                new_formula.disjunctions.append(Disjunction(elements=shared_formula.value))

            # simplifications
            new_formula, curr_result, conflict, added_literals = CDCL_Solver.simplifications(new_formula, curr_result)
            temporal_step[chosen_literal[0]] += added_literals

            self.lock.acquire()
            print("* Recursion n°: " + str(recursion_index) + ". Number of clauses bef.: " + old_disjunction_length +
                  ". Curr literal " + chosen_literal[0] + ". Number of clauses after " +
                  str(len(new_formula.disjunctions)) + " clauses.  Num of known literals: " +
                  str(len(curr_result)) + "\n")
            self.lock.release()

            # check if end (positive or negative)
            if len(new_formula.disjunctions) == 0:
                self.lock.acquire()
                print("FOUND SOLUTION!")
                result.update(curr_result.copy())
                flag.value = True
                return True, None, None

            if conflict != "":
                print("Conflict for variable " + conflict)
                return self.prepare_backtracking(conflict, temporal_step)

            next_literal = self.choose_branching(new_formula)
            flag, back_state, new_clause = self.cdcl_recursive(pickle.dumps(new_formula), [next_literal, False],
                                                               curr_result.copy(), recursion_index,
                                                               pickle.dumps(temporal_step),
                                                               shared_formula.value)

            if flag is True:
                return True, None, None

            elif back_state != chosen_literal[0]:
                return flag, back_state, new_clause

            else:
                print("Back to " + str(recursion_index) + " recursion state")
                new_formula.disjunctions.append(new_clause)

    def prepare_backtracking(self, conflict_variable: str, temporal_step: OrderedDict):
        disjunction = Disjunction()
        self.number_backtracking += 1
        back_state = ""

        for clause in [cl for cl in self.formula.disjunctions if conflict_variable in
                                                                 [literal.get_name() for literal in cl.literals]]:
            # print(clause.to_string())
            for literal in clause.literals:
                temp_literal = Literal()
                temp_literal.name = literal.get_name()
                temp_literal.positive = literal.positive
                disjunction.literals.append(temp_literal)

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
                break

        flag = False
        while flag is False:
            flag = True
            for literal in disjunction.literals:
                if any(literal != lit and literal.get_name() == lit.get_name() and
                       literal.positive is not lit.positive for lit in disjunction.literals):

                    disjunction.literals.remove(literal)
                    disjunction.literals.remove([lit for lit in disjunction.literals if literal != lit and
                                                 literal.get_name() == lit.get_name() and
                                                 literal.positive is not lit.positive][0])
                    flag = False
                    break
                if any(literal != lit and literal.get_name() == lit.get_name() and
                       literal.positive is lit.positive for lit in disjunction.literals):
                    # print("removed literal with same value " + literal.to_string())
                    disjunction.literals.remove(literal)
                    flag = False
                    break

        return False, back_state, disjunction
