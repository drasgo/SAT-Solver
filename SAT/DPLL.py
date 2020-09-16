from SAT.base_SAT_heuristic import Base_SAT_Heuristic_Solver
from collections import OrderedDict
import copy
from SAT.DIMACS_decoder import Formula, Disjunction


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
        self.formula = self.check_tautology(self.formula)
        flag = self.dpll_recursive(self.formula.disjunctions, self.formula.variables, [self.formula.variables[0], False], {})

        if flag is False:
            flag = self.dpll_recursive(self.formula.disjunctions, self.formula.variables,[self.formula.variables[0], True], {})

        print("finished lookup. exiting")
        return flag

    @staticmethod
    def check_tautology(formula):
        """Check for tautologies in formula and removes clauses when tautologies appear"""
        for disjunction in formula.disjunctions[:]:
            if any(
                   lit1.get_name() == lit2.get_name() and
                   lit1.get_value(True) is not lit2.get_value(True)
                   for lit1 in disjunction.literals
                   for lit2 in disjunction.literals
            ):
                formula.disjunctions.remove(disjunction)
        return formula

    def dpll_recursive(self, disjunctions, variables, chosen_literal: list, curr_result: dict):
        # chosen_literal = [literal_name, literal_value]
        curr_result[chosen_literal[0]] = chosen_literal[1]
        current_disjunctions = disjunctions.copy()
        current_disjunctions = DPLL_Solver.shorten_formula(current_disjunctions, chosen_literal)
        current_disjunctions = DPLL_Solver.remove_clauses(current_disjunctions, chosen_literal)
        current_disjunctions, pure_literals = self.check_pure_literals(current_disjunctions, variables)
        current_disjunctions, unit_literals = self.check_unit_clauses(current_disjunctions)
        pure_literals.update(unit_literals)

        curr_result.update(pure_literals)
        print("missing " + str(len(current_disjunctions)) + " clauses")
        if len(current_disjunctions) == 0:
            # Check if formula is empty
            self.result = curr_result
            return True

        if any(len(elem.literals) == 0 for elem in current_disjunctions):
            # Check if there are any empty clauses
            print("error")
            return False

        # choose another literal in formula

        next_literal = [var for var in variables if var not in curr_result]
        if len(next_literal) == 0:
            return self.formula.compute_formula(curr_result)
        else:
            next_literal = next_literal[0]

        # Compute the method recursively (first with the negated literal and then with the positive literal
        if self.dpll_recursive(current_disjunctions, variables, [next_literal, False], curr_result.copy()) is True:
            return True
        return self.dpll_recursive(current_disjunctions, variables, [next_literal, True], curr_result.copy())

    def check_pure_literals(self, disjunctions, variables):
        """check for pure literals in formula"""
        pure_variables = {}
        for variable in variables:
            if variable not in self.result:
                if all(
                    variable != var.get_name() or
                    (variable == var.get_name() and
                    var.positive is False)
                    for disjunction in disjunctions
                    for var in disjunction.literals
                ):
                    # If all variables with the same name are False
                    pure_variables[variable] = False
                    disjunctions = DPLL_Solver.shorten_formula(disjunctions, [variable, False])
                    disjunctions = DPLL_Solver.remove_clauses(disjunctions, [variable, False])

                elif all(
                    variable != var.get_name() or
                    (variable == var.get_name() and
                    var.positive is True)
                    for disjunction in disjunctions
                    for var in disjunction.literals
                ):
                    # If all variables with the same name are True
                    pure_variables[variable] = True
                    disjunctions = DPLL_Solver.shorten_formula(disjunctions, [variable, True])
                    disjunctions = DPLL_Solver.remove_clauses(disjunctions, [variable, True])

        return disjunctions, pure_variables

    @staticmethod
    def check_unit_clauses(disjunctions):
        """check for unit clauses"""
        unit_variables = {}
        disjunctions_remove = []
        for disjunction in disjunctions:
            if len(disjunction.literals) == 1:
                unit_variables[disjunction.literals[0].get_name()] = disjunction.literals[0].positive
            else:
                disjunctions_remove.append(disjunction)

        for unit_var in unit_variables:
            disjunctions_remove = DPLL_Solver.shorten_formula(disjunctions_remove, [unit_var, unit_variables[unit_var]])
            disjunctions_remove = DPLL_Solver.remove_clauses(disjunctions_remove, [unit_var, unit_variables[unit_var]])

        return disjunctions_remove, unit_variables

    @staticmethod
    def shorten_formula(disjunctions, chosen_literal: list):
        """shorten clauses in formula containing negative literal"""
        shortenede_formula = []
        for disjunction in disjunctions:
            for literal in disjunction.literals:
                if literal.get_name() == chosen_literal[0] and literal.get_value(chosen_literal[1]) is False:
                    temp_literals = [lit for lit in disjunction.literals if lit != literal]
                    disjunction = Disjunction("")
                    disjunction.literals = temp_literals
            shortenede_formula.append(disjunction)
        return shortenede_formula

    @staticmethod
    def remove_clauses(disjunctions, chosen_literal: list):
        """remove clauses in formula containing positive literal"""
        removed_clauses = []
        for disjunction in disjunctions[:]:
            if not any(
                    literal.get_name() == chosen_literal[0] and
                    literal.get_value(chosen_literal[1]) is True
                    for literal in disjunction.literals
            ):
                removed_clauses.append(disjunction)
        return removed_clauses