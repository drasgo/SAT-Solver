import time


class Base_SAT_Heuristic_Solver:
    def __init__(self, formula, branching: str = ""):
        self.formula = formula
        self.counter = 0
        self.branching = branching
        self.number_backtracking = 0
        self.starting_time = 0
        # self.n_of_backtracking = {}
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

    def counter_proof(self):
        print("Counter proof:")
        for elem in self.formula.variables:
            if elem not in self.result:
                self.result[elem] = False
        if self.formula.compute_formula(self.result) is True:
            print("Good counter proof")
        else:
            print("fuck")

    @staticmethod
    def check_tautology(formula):
        """Check for tautologies in formula and removes clauses when tautologies appear"""
        removed_disjunctions = []
        for disjunction in formula.disjunctions:
            if any(
                    lit1.get_name() == lit2.get_name() and
                    lit1.get_value(True) is not lit2.get_value(True)
                    for lit1 in disjunction.literals
                    for lit2 in disjunction.literals
            ):
                removed_disjunctions.append(disjunction)

        for disjunction in removed_disjunctions:
            formula.disjunctions.remove(disjunction)
        return formula

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
        conflict = ""
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

                if len(disjunction.literals) == 0:
                    conflict = lit.get_name()
        return disjunctions, conflict

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

    @staticmethod
    def simplifications(new_formula, curr_result):
        # If there are pure literals or unit clauses, executes simplifications and re-check for pure literals
        # and/or unit clauses in cascade until there is nothing else to simplify in the current state
        simpl = []
        while True:
            new_formula.disjunctions, conflict = Base_SAT_Heuristic_Solver.shorten_formula(new_formula.disjunctions, curr_result)
            if conflict != "":
                return new_formula, curr_result, conflict, []
            new_formula.disjunctions = Base_SAT_Heuristic_Solver.remove_clauses(new_formula.disjunctions, curr_result)

            simplified_literals = Base_SAT_Heuristic_Solver.check_pure_literals(new_formula.disjunctions, new_formula.get_variables())
            if len(simplified_literals) == 0:
                simplified_literals = Base_SAT_Heuristic_Solver.check_unit_clauses(new_formula.disjunctions)

            if len(simplified_literals) == 0:
                break
            curr_result.update(simplified_literals)
            for elem in simplified_literals:
                simpl.append(elem)
        return new_formula, curr_result, "", simpl

    @staticmethod
    def perform_vsids(formula, n_backtracking: int) -> str:
        threshold = 5
        alpha = 0.5
        occurrences = {}

        for elem in [literal for disjunction in formula.disjunctions for literal in disjunction.literals]:
            if elem.get_name() in occurrences:
                occurrences[elem.get_name()] += 1
            else:
                occurrences[elem.get_name()] = 1

        if n_backtracking % threshold == 0:
            for elem in occurrences:
                occurrences[elem.get_name()] = occurrences[elem.get_name()] * alpha

        max_val = max(occurrences.values())
        highest_literal = [literal for literal in occurrences if occurrences[literal] == max_val][0]
        return highest_literal

    @staticmethod
    def MAXO(formula):
        occurences = {}
        for disjunction in formula.disjunctions:
            for literal in disjunction:
                if literal.get_name() in occurences:
                    occurences[literal.get_name()] += 1
                else:
                    occurences[literal.get_name()] = 1

        return occurences

    @staticmethod
    def MOM(formula):
        k = 3
        occurences = {}
        minimum_clause = min([len(disj.literals) for disj in formula.disjunctions])

        for disjunction in [disjunction for disjunction in formula.disjunctions if len(disjunction) == minimum_clause]:
            # Retrieve the smallest clauses
            for literal in disjunction.literals:
                # Put the literals occurence in the dictionary (dividing positive and negative)
                if literal.get_name() in occurences:
                    if literal.positive is True:
                        occurences[literal.get_name()]["positive"] += 1
                    else:
                        occurences[literal.get_name()]["negative"] += 1
                else:
                    occurences[literal.get_name()] = {
                        "positive": 1 if literal.positive is True else 0,
                        "negative": 1 if literal.positive is False else 0,
                        "score": 0.0
                    }
        result = {}
        for occur in occurences:
            # compute MOM's formula: max(f(x) + f(-x))* 2^k + f(x)*f(-x))
            result[occur] = (occurences[occur]["positive"] + occurences[occur]["negative"]) * 2 ** k + \
                            occurences[occur]["positive"] * occurences[occur]["negative"]

        return occurences

    @staticmethod
    def MAMS(formula):
        mom_score = Base_SAT_Heuristic_Solver.MOM(formula)
        maxo_score = Base_SAT_Heuristic_Solver.MAXO(formula)
        final_score = {}
        for elem in mom_score:
            final_score[elem] = mom_score[elem]

        for elem in maxo_score:
            if elem in final_score:
                final_score[elem] += maxo_score[elem]

        return final_score

    @staticmethod
    def Jeroslaw_Wang(formula):
        occurrences = {}
        for disjunction in formula.disjunctions:
            for literal in disjunction.literals:
                if literal.get_name() in occurrences:
                    occurrences[literal.get_name()] += 2 ** (-len(disjunction.literals))
                else:
                    occurrences[literal.get_name()] = 2 ** (-len(disjunction.literals))
        return occurrences

    @staticmethod
    def UP(formula, literal):
        alpha = 2
        beta = 1

        temp1, conflict = Base_SAT_Heuristic_Solver.shorten_formula(formula.disjunctions[:],
                                                                    {literal.get_name(): False})
        if conflict != "":
            return None
        temp2 = Base_SAT_Heuristic_Solver.remove_clauses(formula.disjunctions[:], {literal.get_name(): False})

        return alpha * (len(formula.disjunctions) - len(temp2)) + \
               beta * (len([literal
                            for disjunction in formula.disjunctions
                            for literal in disjunction]) -
                       len([literal
                            for disjunction in temp1.disjunctions
                            for literal in disjunction]))

    @staticmethod
    def SUP(formula):
        first_candidate = Base_SAT_Heuristic_Solver.perform_MOM(formula)
        second_candidate = Base_SAT_Heuristic_Solver.perform_MAXO(formula)
        third_candidate = Base_SAT_Heuristic_Solver.perform_Jeroslaw_Wang(formula)
        fourth_candidate = Base_SAT_Heuristic_Solver.performs_MAMS(formula)

        occurences = {}
        for literal in [first_candidate, second_candidate, third_candidate, fourth_candidate]:
            temp = Base_SAT_Heuristic_Solver.UP(formula, literal.get_name())
            if temp is None:
                continue
            occurences[literal.get_name()] = temp
        return occurences

    @staticmethod
    def perform_MAXO(formula):
        """This rule selects the literal with the maximum number of occurrences in the formula"""
        score = Base_SAT_Heuristic_Solver.MAXO(formula)
        highest_occ = max(score.values())
        maximum_literal = [lit for lit in score if score[lit] == highest_occ][0]
        return maximum_literal

    @staticmethod
    def perform_MOM(formula) -> str:
        """it counts only occurrences of literals in minimum size clauses"""
        score = Base_SAT_Heuristic_Solver.MOM(formula)
        highest_occ = max(score.values())
        maximum_literal = [lit for lit in score if score[lit] == highest_occ][0]
        return maximum_literal

    @staticmethod
    def performs_MAMS(formula):
        """
        The idea is that it is desirable to satisfy as many
        clauses as possible (MAXO(l)), but also to create as many clauses of minimum size as possible (MOMS(¯l))
        """
        score = Base_SAT_Heuristic_Solver.MAMS(formula)
        highest_occ = max(score.values())
        maximum_literal = [lit for lit in score if score[lit] == highest_occ][0]
        return maximum_literal

    @staticmethod
    def perform_Jeroslaw_Wang(formula):
        """
        The Jeroslaw-Wang rule combines the ideas behind
        MAXO and MOMS using exponential weighting
        """
        score = Base_SAT_Heuristic_Solver.Jeroslaw_Wang(formula)
        highest_occ = max(score.values())
        maximum_literal = [lit for lit in score if score[lit] == highest_occ][0]
        return maximum_literal

    @staticmethod
    def perform_UP(formula):
        """
        This rule probes the search by making a trial assignment to each free literal and counting the number of
        triggered unit propagations due to that assignment
        """
        occurences = {}
        for literal in formula.get_variables():
            temp = Base_SAT_Heuristic_Solver.UP(formula, literal.get_name())
            if temp is None:
                continue
            occurences[literal.get_name()] = temp
        highest_occ = max(occurences.values())
        maximum_literal = [lit for lit in occurences if occurences[lit] == highest_occ][0]
        return maximum_literal

    @staticmethod
    def perform_SUP(formula):
        """
        SUP runs first the four inexpensive rules (MAXO, MOMS,
        MAMS, and JW), which suggest up to four distinct literals and then it
        selects among them using the UP scoring function
        """
        occurences = Base_SAT_Heuristic_Solver.SUP(formula)
        if len(occurences) == 0:
            occurences = Base_SAT_Heuristic_Solver.MOM(formula)
        highest_occ = max(occurences.values())
        maximum_literal = [lit for lit in occurences if occurences[lit] == highest_occ][0]
        return maximum_literal
