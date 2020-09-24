from SAT.base_SAT_heuristic import Base_SAT_Heuristic_Solver
from SAT.DIMACS_decoder import Formula
import time
# import threading
import psutil
import multiprocessing
try:
    import cPickle as pickle
except ImportError:
    import pickle

MAX_THREADS = 4
result = multiprocessing.Manager().dict()
flag = multiprocessing.Value("i", 0)
num_recursion = multiprocessing.Value("i", 0)
num_backtracking = multiprocessing.Value("i",0)
num_threads = multiprocessing.Value("i", 2)
threads_available = multiprocessing.Value("i", MAX_THREADS)
class DPLL_Solver(Base_SAT_Heuristic_Solver):
    def __init__(self, formula, branching: str = ""):
        self.lock = multiprocessing.Lock()
        super().__init__(formula, branching)

    def compute(self) -> bool:
        """
        Computes DPLL algorithm with parallel implementation
        """
        global threads_available
        self.formula = self.check_tautology(self.formula)
        self.starting_time = time.perf_counter()
        first_literal = self.choose_branching(self.formula)
        self.max_num_threads = multiprocessing.Value = 2
        self.result = multiprocessing.Manager().dict()
        print("Starting.")

        thread1 = multiprocessing.Process(target=self.dpll_recursive, args=(pickle.dumps(self.formula), [first_literal, False], {}, self.counter))
        thread2 = multiprocessing.Process(target=self.dpll_recursive, args=(pickle.dumps(self.formula), [first_literal, True], {}, self.counter))
        threads_available.value -= 2

        thread1.start()
        thread2.start()
        time.sleep(1)
        while (thread1.is_alive() or thread2.is_alive()) and flag.value == 0:
            pass
        if flag.value == 1:
            # print("out********************")
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
            # print("in****************")
            # if thread1.is_alive():
            thread1.join()
            # if thread2.is_alive():
            thread2.join()
            # print("POst****************")

        self.result = result
        self.number_backtracking = num_backtracking.value
        self.max_num_threads = num_threads.value
        self.counter = num_recursion.value
        # final_flag = True if flag.value == 1 else False
        final_flag = self.counter_proof()
        print("Finished lookup.\n")
        self.summary_information(final_flag)
        return final_flag

    def dpll_recursive(self, formula, chosen_literal: list, curr_result: dict, recursion_index):
        # chosen_literal = [literal_name, literal_value]
        # Used for keeping track of the current recursion index
        global num_backtracking
        global num_recursion
        global num_threads
        global result
        global flag
        global threads_available
        recursion_index += 1
        num_recursion.value = max(num_recursion.value, recursion_index)
        new_formula = pickle.loads(formula)
        assert isinstance(new_formula, Formula)
        old_disjunctions = str(len(new_formula.disjunctions))

        if flag.value == 1:
            return

        # If the literal chosen in the previous recursive state is not in the curr_result after the simplification
        # add it to the curr_result and redo the simplifications
        if chosen_literal[0] not in curr_result:
            curr_result[chosen_literal[0]] = chosen_literal[1]
            new_formula, curr_result, empty_clause, _ = DPLL_Solver.simplifications(new_formula, curr_result)

        if flag.value == 1:
            return

        self.lock.acquire()
        print("* Recursion n°: " + str(recursion_index) + ". Number of clauses bef.: " +
              old_disjunctions + ". Number of clauses after " + str(len(new_formula.disjunctions)) +
              ". Curr literal " + chosen_literal[0] + ". Num of known literals: " +
              str(len(curr_result)) + ". Num of threads: " + str(num_threads.value) + "\n")
        self.lock.release()

        if len(new_formula.disjunctions) == 0:
            # Check if formula is empty
            result.update(curr_result.copy())
            flag.value = 1
            print("FOUND SOLUTION!")
            return True

        if empty_clause != "":
            # Check if there is any empty clauses
            print("error")
            num_backtracking.value += 1
            return False

        next_literal = self.choose_branching(new_formula)
        self.lock.acquire()
        if threads_available.value > 0:
            threads_available.value -= 1
            self.lock.release()
            num_threads.value += 1
            thread1 = multiprocessing.Process(target=self.dpll_recursive,
                                              args=(pickle.dumps(new_formula), [next_literal, False], curr_result.copy(),
                                                    recursion_index))
            thread = True
            thread1.start()
        else:
            self.lock.release()
            thread = False
            if self.dpll_recursive(pickle.dumps(new_formula), [next_literal, False], curr_result.copy(), recursion_index) is True:
                return True

        if self.dpll_recursive(pickle.dumps(new_formula), [next_literal, True], curr_result.copy(), recursion_index) is True:
            return True

        if thread is True:
            try:
                while thread1.is_alive() and flag.value == 0:
                    pass
                if thread1.is_alive():
                    thread1.terminate()
                thread1.join()
                num_threads.value -= 1
                threads_available.value += 1
            except UnboundLocalError:
                pass
