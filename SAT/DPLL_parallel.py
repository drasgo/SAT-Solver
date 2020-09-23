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
flag = False
event = multiprocessing.Event()
result = multiprocessing.Manager().dict()
num_recursion = multiprocessing.Value("i", 0)
num_backtracking = multiprocessing.Value("i",0)
num_threads = multiprocessing.Value("i", 2)
class DPLL_Solver(Base_SAT_Heuristic_Solver):
    def __init__(self, formula, branching: str = ""):
        self.flag = False
        self.lock = multiprocessing.Lock()
        # self.max_threads = multiprocessing.Semaphore(MAX_THREADS)
        self.terminate = multiprocessing.Value = 0
        self.threads_available = multiprocessing.Value = MAX_THREADS
        self.event = multiprocessing.Event()
        super().__init__(formula, branching)

    def compute(self) -> bool:
        """
        Computes DPLL algorithm with parallel implementation
        """
        self.formula = self.check_tautology(self.formula)
        self.starting_time = time.perf_counter()
        first_literal = self.choose_branching(self.formula)
        self.max_num_threads = multiprocessing.Value = 2
        self.result = multiprocessing.Manager().dict()
        print("Starting.")

        thread1 = multiprocessing.Process(target=self.dpll_recursive, args=(pickle.dumps(self.formula), [first_literal, False], {}, self.counter))
        thread2 = multiprocessing.Process(target=self.dpll_recursive, args=(pickle.dumps(self.formula), [first_literal, False], {}, self.counter))
        self.threads_available -= 2

        thread1.start()
        thread2.start()
        while (thread1.is_alive() or thread2.is_alive()) and not self.event.is_set():
            pass
        if self.event.is_set():
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
        self.result = result
        self.number_backtracking = num_backtracking.value
        self.max_num_threads = num_threads.value
        self.counter = num_recursion.value

        print(self.result)
        self.counter_proof()
        print("Finished lookup.\n")
        self.summary_information(self.flag)
        return self.flag

    def dpll_recursive(self, formula, chosen_literal: list, curr_result: dict, recursion_index):
        # chosen_literal = [literal_name, literal_value]
        # Used for keeping track of the current recursion index
        global num_backtracking
        global num_recursion
        global num_threads
        global result
        global event

        recursion_index += 1
        num_recursion.value = max(num_recursion.value, recursion_index)
        new_formula = pickle.loads(formula)
        assert isinstance(new_formula, Formula)
        old_disjunctions = str(len(new_formula.disjunctions))

        if event.is_set():
            # self.lock.acquire()
            return

        # If the literal chosen in the previous recursive state is not in the curr_result after the simplification
        # add it to the curr_result and redo the simplifications
        if chosen_literal[0] not in curr_result:
            curr_result[chosen_literal[0]] = chosen_literal[1]
            new_formula, curr_result, empty_clause, _ = DPLL_Solver.simplifications(new_formula, curr_result)

        if event.is_set():
            # self.lock.acquire()
            return
        self.lock.acquire()
        print("* Recursion n°: " + str(recursion_index) + ". Number of clauses bef.: " +
              old_disjunctions + ". Number of clauses after " + str(len(new_formula.disjunctions)) +
              ". Curr literal " + chosen_literal[0] + ". Num of known literals: " +
              str(len(curr_result)) + ". Num of threads: " + str(num_threads.value) + "\n")
        self.lock.release()

        if len(new_formula.disjunctions) == 0:
            # Check if formula is empty
            self.lock.acquire()
            # print(curr_result)
            result.update(curr_result.copy())
            event.set()
            # self.lock.release()
            print("FOUND SOLUTION!")
            return True

        if empty_clause != "":
            # Check if there is any empty clauses
            print("error")
            num_backtracking.value += 1
            return False

        next_literal = self.choose_branching(new_formula)
        self.lock.acquire()
        if self.threads_available > 0:
            self.threads_available -= 1
            self.lock.release()
            num_threads.value += 1
            # self.max_threads.acquire()
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
        elif thread is True:
            try:
                while thread1.is_alive() and not event.is_set():
                    pass
                if thread1.is_alive():
                    thread1.terminate()
                # self.max_threads.release()
                thread1.join()
                num_threads -= 1
                self.threads_available += 1
            except UnboundLocalError:
                pass
