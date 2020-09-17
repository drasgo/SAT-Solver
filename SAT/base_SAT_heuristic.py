import time


class Base_SAT_Heuristic_Solver:
    def __init__(self, formula):
        self.formula = formula
        self.counter = 0
        self.number_backtracking = 0
        self.starting_time = 0
        self.result = {}

    def compute(self) -> bool:
        pass

    def get_result(self) -> str:
        return " ".join([lit for lit in self.result if self.result[lit] is True]).strip()

    def summary_information(self, flag):
        print("**********")
        print("Satisfiable" if flag is True else "Unsatisfiable")
        print("Number of recursions: " + str(self.counter))
        print("Number of backtracking: " + str(self.number_backtracking))
        print("Time passed: " + str(round((time.perf_counter() - self.starting_time), 2)) + " seconds")
        print("Number of known literals: " + str(len([var for var in self.formula.disjunctions if len(var.literals) == 1])))
        print("**********")

    @staticmethod
    def check_pure_literals(disjunctions, variables):
        """check for pure literals in formula"""
        pure_variables = {}
        # do iteration over difference between all variables and curr_result
        for variable in variables:
            if all(
                variable != var.get_name() or
                (variable == var.get_name() and
                var.positive is False)
                for disjunction in disjunctions
                for var in disjunction.literals
            ):
                # If all variables with the same name are False
                pure_variables[variable] = False

            elif all(
                variable != var.get_name() or
                (variable == var.get_name() and
                var.positive is True)
                for disjunction in disjunctions
                for var in disjunction.literals
            ):
                # If all variables with the same name are True
                pure_variables[variable] = True

        return pure_variables

    @staticmethod
    def check_unit_clauses(disjunctions):
        """check for unit clauses"""
        unit_variables = {}

        for disjunction in disjunctions:
            if len(disjunction.literals) == 1:
                unit_variables[disjunction.literals[0].get_name()] = disjunction.literals[0].positive

        return unit_variables

    @staticmethod
    def shorten_formula(disjunctions, chosen_literal: dict):
        """shorten clauses in formula containing negative literal"""
        for disjunction in disjunctions:
            removed_literals = []
            for literal in disjunction.literals:
                if any(
                        literal.get_name() == lit and
                        literal.get_value(chosen_literal[lit]) is False
                        for lit in chosen_literal
                       ):
                    removed_literals.append(literal)

            for lit in removed_literals:
                disjunction.literals.remove(lit)
        return disjunctions

    @staticmethod
    def remove_clauses(disjunctions, chosen_literal: dict):
        """remove clauses in formula containing positive literal"""
        removed_clauses = []
        for disjunction in disjunctions:
            if any(
                    literal.get_name() == lit and
                    literal.get_value(chosen_literal[lit]) is True
                    for literal in disjunction.literals
                    for lit in chosen_literal
            ):
                removed_clauses.append(disjunction)

        for disj in removed_clauses:
            disjunctions.remove(disj)
        return disjunctions