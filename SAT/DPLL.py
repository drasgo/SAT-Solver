from SAT.base_SAT_heuristic import Base_SAT_Heuristic_Solver
from SAT.DIMACS_decoder import Formula
import time


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
        # print(self.formula.to_string())
        start_time = time.perf_counter()

        flag = self.dpll_recursive(self.formula.to_string(), [self.formula.variables[0], False], {}, self.counter)
        if flag is False:
            flag = self.dpll_recursive(self.formula.to_string(),[self.formula.variables[0], True], {}, self.counter)
        delta_time = time.perf_counter() - start_time

        print("Counter proof:")
        for elem in self.formula.variables:
            if elem not in self.result:
                self.result[elem] = False
        if self.formula.compute_formula(self.result) is True:
            print("Good counter proof")
        else:
            print("fuck")

        print("Finished lookup.")
        print("Number of recursions: " + str(self.counter))
        print("Time passed: " + str(round(delta_time, 2)) + " seconds")
        print("Number of known literals: " + str(len([var for var in self.formula.disjunctions if len(var.literals) == 1])))
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

    def dpll_recursive(self, disjunctions: str, chosen_literal: list, curr_result: dict, recursion_index):
        # chosen_literal = [literal_name, literal_value]
        # Used for keeping track of the current recursion index
        recursion_index += 1
        # Counter for total number of recursions
        self.counter = recursion_index
        # Create a new formula from the string disjunctions
        new_formula = Formula(str_logic=disjunctions)
        # Used for debugging for looking at the number of clauses before modification
        print("*Recursion n°: " + str(recursion_index) + ". Number of clauses bef.: " + str(len(new_formula.disjunctions))
              + " Curr literal " + chosen_literal[0])

        # First iteration for check of pure literals or unit clauses
        simplified_literals = DPLL_Solver.check_pure_literals(new_formula.disjunctions, new_formula.get_variables())
        if len(simplified_literals) == 0:
            simplified_literals = DPLL_Solver.check_unit_clauses(new_formula.disjunctions)

        if len(simplified_literals) > 0:
            curr_result.update(simplified_literals)
            # Executes all the simplifications and add all the simplifiable literals to curr_result
            new_formula, curr_result = DPLL_Solver.simplifications(new_formula, curr_result)

        # If the literal chosen in the previous recursive state is not in the curr_result after the simplification
        # add it to the curr_result and redo the simplifications
        if chosen_literal[0] not in curr_result:
            curr_result[chosen_literal[0]] = chosen_literal[1]
            new_formula, curr_result = DPLL_Solver.simplifications(new_formula, curr_result)
        # else:
            # print("literal " + chosen_literal[0] + " already in curr_results with value " + str(chosen_literal[1])
            #       + " (current value: " + str(curr_result[chosen_literal[0]]) + ")")

        # Gets new literal from the formula
        print("After " + str(len(new_formula.disjunctions)) + " clauses.  Num of known literals: " + str(len(curr_result)) + "\n")

        if len(new_formula.disjunctions) == 0:
            # Check if formula is empty
            print(curr_result)
            self.result = curr_result
            return True

        if any(len(elem.literals) == 0 for elem in new_formula.disjunctions):
            # Check if there is any empty clauses
            print("error")
            return False

        new_variables = new_formula.get_variables()
        next_literal = [var for var in new_variables][0]
        # Compute the method recursively (first with the negated literal and then with the positive literal
        if self.dpll_recursive(new_formula.to_string(), [next_literal, False], curr_result.copy(), recursion_index) is True:
            return True

        print("**Back to recursion n° " + str(recursion_index) + "\n")
        return self.dpll_recursive(new_formula.to_string(), [next_literal, True], curr_result.copy(), recursion_index)

    @staticmethod
    def simplifications(new_formula, curr_result):
        # If there are pure literals or unit clauses, executes simplifications and re-check for pure literals
        # and/or unit clauses in cascade until there is nothing else to simplify in the current state
        while True:
            new_formula.disjunctions = DPLL_Solver.shorten_formula(new_formula.disjunctions, curr_result)
            new_formula.disjunctions = DPLL_Solver.remove_clauses(new_formula.disjunctions, curr_result)

            simplified_literals = DPLL_Solver.check_pure_literals(new_formula.disjunctions, new_formula.get_variables())
            if len(simplified_literals) == 0:
                simplified_literals = DPLL_Solver.check_unit_clauses(new_formula.disjunctions)

            if len(simplified_literals) == 0:
                break
            curr_result.update(simplified_literals)
        return new_formula, curr_result

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
                # print("pure literal " + variable + " found with value " + str(False))
                pure_variables[variable] = False

            elif all(
                variable != var.get_name() or
                (variable == var.get_name() and
                var.positive is True)
                for disjunction in disjunctions
                for var in disjunction.literals
            ):
                # If all variables with the same name are True
                # print("pure literal " + variable + " found with value " + str(True))
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