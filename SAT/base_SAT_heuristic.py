class Base_SAT_Heuristic_Solver:
    def __init__(self, formula):
        self.formula = formula
        self.result = []

    def compute(self) -> bool:
        pass

    def get_result(self) -> str:
        return " ".join(self.result).strip()
