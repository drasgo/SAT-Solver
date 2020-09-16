from SAT.base_SAT_heuristic import Base_SAT_Heuristic_Solver
from collections import OrderedDict


class DPLL_Solver(Base_SAT_Heuristic_Solver):
    def __init__(self, formula):
        super().__init__(formula)

    def compute(self) -> bool:
        """
        Computes DPLL algorithm
        The basic idea of the algorithm is:

    1. "Guess" a variable
    2. Find all unit clauses created from the last assignment and assign the needed value
    3. Iteratively retry step 2 until there is no change (found transitive closure)
    4. If the current assignment cannot yield true for all clauses - fold back from recursion
    and retry a different assignment
    5. If it can - "guess" another variable (recursively invoke and return to 1)

    Termination:

    1. There is nowhere to go "back to" and change a "guess" (no solution)
    2. All clauses are satisfied (there is a solution, and the algorithm found it)
        """
        #


        # if self.formula.compute_formula(curr_variables) is True:
        #     Tries to compute the formula and check if with the current values it is satisfied
            # self.result = curr_variables
            # return True

        # Check for tautologies in formula and removes clauses when tautologies appear
        self.formula = self.check_tautology(self.formula)
        self.result = {self.formula.variables[0]:True}

        flag = self.dpll_recursive(self.formula, [self.formula.variables[0], True])

        if flag is False:
            self.result = {self.formula.variables[0]: True}
            flag = self.dpll_recursive(self.formula, [self.formula.variables[1], False])

        if flag is False:
            self.result = {}

        print("finished lookup. exiting")
        return flag

    def dpll_recursive(self, formula, chosen_literal: list):
        # chosen_literal = [literal_name, literal_value]
        self.result[chosen_literal[0]] = chosen_literal[1]
        # shorten clauses in formula containing negative literal
        formula = DPLL_Solver.shorten_formula(formula, chosen_literal)
        # remove clauses in formula containing positive literal
        formula = DPLL_Solver.remove_clauses(formula, chosen_literal)
        # check for pure literals in formula
        formula, pure_literals = self.check_pure_literals(formula)
        # check for unit clauses
        formula, unit_literals = self.check_unit_clauses(formula)

        pure_literals.update(unit_literals)
        # for element in pure_literals:
        if any(element in self.result and pure_literals[element] is not self.result[element] for element in pure_literals):
                return False

        self.result.update(pure_literals)
        # Check if formula is empty
        if len(formula) == 0:
            return True
        # Check if there are any empty clauses
        if any(len(clause) == 0 for clause in formula):
            return False
        # choose another literal in formula
        next_literal = [var for var in formula.variables if var not in self.result][0]
        # Compute next iteration
        if self.dpll_recursive(formula, [next_literal, False]) is True:
            return True
        return self.dpll_recursive(formula, [next_literal, True])

    @staticmethod
    def check_pure_literals(formula):
        pure_variables = {}
        temp = [literal
                for disjunction in formula
                for literal in disjunction
                if all(
                    literal.get_name() != other_literal.get_name() or
                    (literal.get_name() == other_literal.get_name() and
                     literal.positive is other_literal.positive)
                    for other_disjunction in formula.disjunctions
                    for other_literal in other_disjunction)]

        for literal in temp:
            pure_variables[literal.get_name()] = literal.positive
            formula = DPLL_Solver.shorten_formula(formula, [literal.get_name(), literal.positive])
            formula = DPLL_Solver.remove_clauses(formula, [literal.get_name(), literal.positive])
        return formula, pure_variables

    @staticmethod
    def check_unit_clauses(formula):
        unit_variables = {}
        disjunctions_remove = []

        for disjunction in formula.disjunctions:
            if len(disjunction.literals) == 1:
                unit_variables[disjunction.literals[0].get_name()] = disjunction.literals[0].positive
                disjunctions_remove.append(disjunction)

        for ready_disj in disjunctions_remove:
            formula.disjunctions.pop(ready_disj)

        for unit_var in unit_variables:
            DPLL_Solver.shorten_formula(formula, [unit_var, unit_variables[unit_var]])
            DPLL_Solver.remove_clauses(formula, [unit_var, unit_variables[unit_var]])

        return formula, unit_variables

    @staticmethod
    def check_tautology(formula):
        for disjunction in formula.disjunctions[:]:
            if any(
                   lit1.get_name() == lit2.get_name() and
                   lit1.get_value(True) is not lit2.get_value(True)
                   for lit1 in disjunction.literals
                   for lit2 in disjunction.literals
            ):
                formula.disjunctions.pop(disjunction)
        return formula

    @staticmethod
    def shorten_formula(formula, chosen_literal: list):
        for disjunction in formula.disjunctions:
            for literal in disjunction.literals:
                if literal.get_name() == chosen_literal[0] and literal.get_value(chosen_literal[1]) is False:
                    disjunction.literals.pop(literal)
                    break
        return formula

    @staticmethod
    def remove_clauses(formula, chosen_literal: list):
        for disjunction in formula.disjunctions[:]:
            if any(
                    literal.get_name() == chosen_literal[0] and
                    literal.get_value(chosen_literal[1]) is True
                    for literal in disjunction.literals
            ):
                formula.disjunctions.pop(disjunction)
        return formula