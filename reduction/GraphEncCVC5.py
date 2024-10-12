from cvc5 import Kind
from GraphEnc import GraphEnc
import ColorerCVC5

class GraphEncCVC5(GraphEnc):
    """
    A class that encodes k-coloring problems for undirected graphs using SMT formulas with CVC5.

    This class extends GraphEnc to work with CVC5 for solving graph coloring problems.
    It provides implementation for adding constraints, generating formulas, and solving the coloring problem.

    Methods:
        - add_constraints()
        - get_formula()
        - get_formula_assertions()
        - create_reduction()
        - get_solution()
        - solve()

    Attributes:
        Inherits all attributes from GraphEnc.
    """

    def add_constraints(self):
        """
        Add graph constraints ensuring no two connected vertices share the same color.

        This method creates constraints for each edge in the graph, ensuring that
        the vertices connected by the edge have different colors.

        Returns:
            list: A list of edge constraints (CVC5 term objects).
        """
        vertex_symbols = self.colorer.get_vertex_symbols()
        edges = self.graph.edges()
        
        for e in edges:
            self.graph_constraints.append(
                self.solver.mkTerm(
                    Kind.DISTINCT,
                    vertex_symbols[e[0]],
                    vertex_symbols[e[1]]))

        return self.graph_constraints

    def get_formula(self):
        """
        Get the complete formula for the graph coloring problem.

        This method combines all constraints into a single AND formula.

        Returns:
            cvc5.Term: The AND of all constraints in the formula.
        """
        formula = super().get_formula()  # Calls the superclass method to get constraints.
        return self.solver.mkTerm(Kind.AND, *formula)


    def get_formula_assertions(self):
        """
        Get the formula assertions.

        This method returns the formula assertions as CVC5 terms.

        Returns:
            list: A list of CVC5 term objects representing the assertions.
        """
        formula = super().get_formula()
        ass_list = []
        for assertion in formula:
            ass_list.append(str(assertion))
        return ass_list
    




    def get_solution(self):
        """
        Get the solution for the graph coloring problem.

        This method solves the problem and retrieves the coloring solution.
        It handles different types of colorers (LIA, NLA, and others) and assigns colors accordingly.

        Returns:
            dict or None: A dictionary mapping nodes to colors if a solution is found, 
                          or None if no solution exists.
                          Colors are encoded as integer numbers.

        Note: All exceptions that can be raised in CVC5 are not caught and will be raised as well.
        """
        symbols = self.colorer.get_vertex_symbols()
        nodes = self.graph.nodes()

        if not self.solver.checkSat().isSat():
            return None
        
        # In case the theory works with integers, we use a direct approach.
        if isinstance(self.colorer, (ColorerCVC5.LIAColorerCVC5, ColorerCVC5.NLAColorerCVC5)):
            return {n: self.solver.getValue(symbols[n]) for n in nodes}

        # Otherwise, we go through all assignments and create a symbol-integer map ourselves.
        solution = {}
        color_map = {}
        next_color = 0
        for n in self.graph.nodes():
            term_str = str(self.solver.getValue(symbols[n]))
            if term_str not in color_map:
                color_map[term_str] = next_color
                next_color += 1
            solution[n] = color_map[term_str]
        return solution

    def solve(self):
        """
        Solve the graph coloring problem.

        This method adds the formula to the solver and attempts to solve it.

        Returns:
            bool: True if a solution is found, False otherwise.
        """
        # Add color constraints from the colorer and call the solver's solve function.
        self.solver.assertFormula(self.get_formula())
        return self.solver.checkSat().isSat()