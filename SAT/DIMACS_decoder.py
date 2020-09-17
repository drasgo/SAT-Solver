class Formula:
    def __init__(self, formula: str="", str_logic= "", disjunctions=None):
        self.disjunctions = []
        if formula != "":
            formula = self.remove_comments(formula)
            self.num_variables, self.num_clauses, formula = self.variables_and_clauses(formula)
            self.str_formula = self.convert_DIMACS_to_str(formula)
            self.convert_to_logic()
        elif str_logic != "":
            self.str_formula = str_logic
            self.convert_to_logic()
        else:
            self.disjunctions = disjunctions
        self.variables = self.get_variables()

    @staticmethod
    def remove_comments(formula: str) -> str:
        final = []
        for line in formula.split("\n"):
            if line.split(" ")[0] != "c":
                final.append(line)
        return "\n".join(final)

    @staticmethod
    def variables_and_clauses(formula: str):
        variables_temp = 0
        clauses_temp = 0
        dim = formula.split("\n")
        for line in dim:
            characters = line.split(" ")
            if characters[0] == "p" and characters[1] == "cnf" and len(characters) == 4:
                variables_temp = characters[2]
                clauses_temp = characters[3]
                dim.remove(line)
                break
        if variables_temp != 0 and clauses_temp != 0:
            return variables_temp, clauses_temp, "\n".join(dim)
        else:
            print("Error reading clauses and/or variable in DIMACS input file")
            exit()

    @staticmethod
    def convert_DIMACS_to_str(formula: str) -> str:
        """
        This function converts a DIMACS set of rules in a string where the variables are divided by ORs and
        the clauses are divided by ANDs.
        E.g.    -111 -112 0
                -113 -115 0
                    ||
                    V
        (-111OR-112)AND(-113OR-115)
         """
        converted_logic = ""

        for line in formula.split("\n"):
            converted_line = ""
            split_line = line.split(" ")

            for var in split_line:
                if var == "0":
                    break
                converted_line = converted_line + ("OR" if converted_line != "" else "") + var

            converted_line = ("(" + converted_line + ")" if converted_line != "" else "")
            if converted_line != "":
                converted_logic = converted_logic + ("AND" if converted_logic != "" else "") + converted_line

        return converted_logic

    def convert_to_logic(self):
        for disjunction in self.string_to_conjunctions(self.str_formula):
            self.disjunctions.append(Disjunction(disjunction))

    @staticmethod
    def string_to_conjunctions(elements: str) -> list:
        return elements.split("AND")

    def to_string(self) -> str:
        formula = ""
        for disjunction in self.disjunctions:
            formula = formula + ("AND" if formula != "" else "") + "(" + disjunction.to_string() + ")"
        return formula

    def get_disjunctions(self) -> list:
        return self.disjunctions

    def get_variables(self) -> list:
        temp_vars = set()
        for disj in self.disjunctions:
            for lit in disj.get_literals():
                temp_vars.add(lit.get_name())
        return list(temp_vars)

    def compute_formula(self, values: dict) -> bool:
        # print("values: " + str(len(values)) + ", num_vars: " + str(len(self.variables)))
        if len(values) == len(self.variables):
            if all(disjunction.compute_disjunction(values) is True for disjunction in self.disjunctions):
                return True
        return False

    def return_unit_clauses_variable(self, guessed_variables: dict) -> dict:
        unit_clauses = {}

        for disj in self.disjunctions:
            missing = [lit for lit in disj.literals if lit.get_name() not in guessed_variables]

            if len(missing) == 1:
                temp_disj = [lit for lit in disj.literals if lit.get_name() in guessed_variables]

                if all(lit.get_name() not in guessed_variables or
                       (lit.get_name() in guessed_variables and
                       lit.get_value(guessed_variables[lit.get_name()]) is False)
                       for lit in temp_disj):
                    unit_clauses[missing[0].get_name()] = True if disj.literals[
                                                                      disj.literals.index(missing[0])].get_value(
                        True) is True else False
                else:
                    unit_clauses[missing[0].get_name()] = None

        return unit_clauses


class Disjunction:
    def __init__(self, elements: str):
        self.literals = []
        if elements != "":
            self.convert_to_logic(elements)

    def convert_to_logic(self, elements: str):
        for literal in Disjunction.string_to_disjunctions(elements.translate(str.maketrans("", "", "()"))):
            self.literals.append(Literal(literal))

    @staticmethod
    def string_to_disjunctions(elements: str) -> list:
        return elements.split("OR")

    def to_string(self) -> str:
        disjunction = ""
        for literal in self.literals:
            disjunction = disjunction + ("OR" if disjunction != "" else "") + literal.to_string()
        return disjunction

    def get_literals(self) -> list:
        return self.literals

    def compute_disjunction(self, values: dict) -> bool:
        if all(lit.get_name() in values for lit in self.literals):
            if any(literal.get_value(values[literal.get_name()]) is True for literal in self.literals):
                return True
            return False
        else:
            print("Variable(s) not in disjunction " + self.to_string() + " != " +str(values.keys()))
            return False


class Literal:
    def __init__(self, literal):
        lit = literal.split("-")
        self.positive = True if len(lit) == 1 else False
        self.name = lit[-1]

    def to_string(self) -> str:
        return ("" if self.positive is True else "-") + self.name

    def get_name(self):
        return self.name

    def get_value(self, boolean: bool = True) -> bool:
        if self.positive:
            return boolean
        else:
            return not boolean
