from SAT.base_SAT_heuristic import Base_SAT_Heuristic_Solver
from SAT.DIMACS_decoder import Formula
import time


class CDCL_Solver(Base_SAT_Heuristic_Solver):
    def __init__(self, formula):
        super().__init__(formula)

    def compute(self) -> bool:
        """
        Computes CDCL algorithm
        """
        self.formula = self.check_tautology(self.formula)
        self.starting_time = time.perf_counter()


        return False