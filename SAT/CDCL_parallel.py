from SAT.base_SAT_heuristic import Base_SAT_Heuristic_Solver
from SAT.DIMACS_decoder import Formula, Disjunction, Literal
from SAT.CDCL import CDCL_Solver
from collections import OrderedDict
import multiprocessing
import psutil
import time
import ctypes
import os
try:
    import cPickle as pickle
except ImportError:
    import pickle


MAX_THREADS = 4
result = multiprocessing.Manager().dict()
num_recursion = multiprocessing.Value("i", 0)
flag = multiprocessing.Value("i", 0)
num_backtracking = multiprocessing.Value("i",0)
num_threads = multiprocessing.Value("i", 0)
shared_formula = multiprocessing.Manager().dict({0:""})
class CDCL_Solver(Base_SAT_Heuristic_Solver):
    def __init__(self, formula, branching: str = ""):
        self.lock = multiprocessing.Lock()
        super().__init__(formula, branching)

    def compute(self) -> bool:
        """
        Computes CDCL algorithm
        """
        global num_threads
        self.formula = self.check_tautology(self.formula)
        self.starting_time = time.perf_counter()
        threads = []

        for index in range(0, MAX_THREADS, 2):
            first_literal = self.choose_branching(self.formula, int(index/2))
            if index == MAX_THREADS - 1:
                threads.append(multiprocessing.Process(target=self.cdcl_recursive,
                                                       args=(pickle.dumps(self.formula),
                                                             [first_literal, False],
                                                             {},
                                                             0,
                                                             pickle.dumps(OrderedDict()),
                                                             "")))
                num_threads.value += 1
            else:
                threads.append(multiprocessing.Process(target=self.cdcl_recursive,
                                                       args=(pickle.dumps(self.formula),
                                                             [first_literal, False],
                                                             {},
                                                             0,
                                                             pickle.dumps(OrderedDict()),
                                                             "")))
                threads.append(multiprocessing.Process(target=self.cdcl_recursive,
                                                       args=(pickle.dumps(self.formula),
                                                             [first_literal, True],
                                                             {},
                                                             0,
                                                             pickle.dumps(OrderedDict()),
                                                             "")))
                num_threads.value += 2

        for thread in threads:
            thread.start()

        while any(thread.is_alive() for thread in threads) and flag.value == 0:
            pass
        if flag.value == 1:
            for th in [thread for thread in threads if thread.is_alive()]:
                parent = psutil.Process(th.pid)
                for child in parent.children(recursive=True):
                    child.terminate()
                parent.terminate()

        else:
            for th in [thread for thread in threads if thread.is_alive()]:
                th.join()

        self.number_backtracking = num_backtracking.value
        self.max_num_threads = num_threads.value
        self.counter = num_recursion.value
        self.result = result
        final_flag = True if flag.value == 1 else False
        final_flag = self.counter_proof()
        print("Finished lookup.\n")
        self.summary_information(final_flag)
        return final_flag

    def cdcl_recursive(self, formula, chosen_literal: list, curr_result: dict, recursion_index, temporal_step, added_clause):
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
        old_disjunction_length = str(len(new_formula.disjunctions))

        if chosen_literal[0] not in curr_result:
            curr_result[chosen_literal[0]] = chosen_literal[1]
            temporal_step[chosen_literal[0]] = []

        while True:
            if flag.value == 1:
                psutil.Process(os.getpid()).terminate()
                return True, None, None

            if  added_clause != shared_formula[0]:
                print("Added new clause")
                added_clause = shared_formula[0]
                temp_formula = Formula(str_logic=shared_formula[0])
                diff = [disj for disj in temp_formula.disjunctions if
                        all(disj.to_string() != orig_disj.to_string
                            for orig_disj in new_formula.disjunctions)]
                new_formula.disjunctions += diff

            # simplifications
            new_formula, curr_result, conflict, added_literals = CDCL_Solver.simplifications(new_formula, curr_result)
            temporal_step[chosen_literal[0]] += added_literals
            if flag.value == 1:
                psutil.Process(os.getpid()).terminate()
                return True, None, None
            self.lock.acquire()
            print("* Recursion n°: " + str(recursion_index) + ". Number of clauses bef.: " + old_disjunction_length +
                  ". Curr literal " + chosen_literal[0] + ". Number of clauses after " +
                  str(len(new_formula.disjunctions)) + " clauses.  Num of known literals: " +
                  str(len(curr_result)) + ". Num of threads: " + str(num_threads.value) + "\n")
            self.lock.release()

            # check if end (positive or negative)
            if len(new_formula.disjunctions) == 0:
                # self.lock.acquire()
                print("FOUND SOLUTION!")
                result.update(curr_result.copy())
                flag.value = 1
                return True, None, None

            if conflict != "":
                print("Conflict for variable " + conflict)
                return self.prepare_backtracking(conflict, temporal_step)

            next_literal = self.choose_branching(new_formula)
            temp_flag, back_state, new_clause = self.cdcl_recursive(pickle.dumps(new_formula), [next_literal, False],
                                                               curr_result.copy(), recursion_index,
                                                               pickle.dumps(temporal_step),
                                                               added_clause)

            if flag.value == 1:
                psutil.Process(os.getpid()).terminate()
                return True, None, None

            elif back_state != chosen_literal[0]:
                return temp_flag, back_state, new_clause

            else:
                print("Back to " + str(recursion_index) + " recursion state")
                new_formula.disjunctions.append(new_clause)
                temp_f =Formula(disjunctions=[new_clause])
                shared_formula[0] = temp_f.to_string()
