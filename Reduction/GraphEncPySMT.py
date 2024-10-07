from pysmt.shortcuts import  And, Equals, Not
from .GraphEnc import GraphEnc
from .ColorerPySMT import ArrayUFColorerPySMT, BVColorerPySMT, ArrayBVColorerPySMT
from pysmt.solvers.msat import MathSAT5Solver



class GraphEncPySMT(GraphEnc):
    """
    A class that encodes k-coloring problems for undirected graphs using SMT formulas with pySMT.

    This class extends GraphEnc to work with pySMT for solving graph coloring problems.
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
            list: A list of edge constraints (pySMT formula nodes).
        """
       
        vertex_symbols = self.colorer.get_vertex_symbols()
        edges = self.graph.edges()

        for e in edges:
            self.graph_constraints.append(
                Not(Equals(vertex_symbols[e[0]], vertex_symbols[e[1]]))
            )
        return self.graph_constraints


    def get_formula(self):
        """
        Get the complete formula for the graph coloring problem.

        This method combines all constraints into a single AND formula.

        Returns:
            pysmt.fnode.FNode: The AND of all constraints in the formula.
        """
        formula = super().get_formula() # Calls the superclass method to get constraints and then create a formula using And.
        return And(formula)
    
    
    def get_formula_assertions(self):
        """
        Get the formula assertions as serialized strings.

        This method converts each assertion in the formula to a serialized string representation.

        Returns:
            list: A list of serialized assertions (strings).
        """
        formula = super().get_formula()     # Get all assertions.
        ass_list = []

        # Create a list of assertions represented as strings.
        for assertion in formula:
            ass_list.append(assertion.serialize())
        return ass_list
        
    

    def get_solution(self):
        """
        Get the solution for the graph coloring problem.

        This method solves the problem and retrieves the coloring solution.
        It handles different types of colorers (ArrayUF, BV, ArrayBV) and solvers.

        Returns:
            dict or None: A dictionary mapping nodes to colors if a solution is found, 
                          or None if no solution exists.
                          Colors are encoded as integer numbers.

        Raises:
            Exception: If MathSAT5Solver is used with ArrayUFColorerPySMT, which is an unsupported combination.
            Since MathSAT can solve formulas with custom types, but cannot return it's assignment.
            Note: All exceptions that can be raised in pysmt (like NotImplemented) are not caught, and will be raised as well.

        """
        # get nodes data
        vertex_symbols = self.colorer.get_vertex_symbols()
        nodes = self.graph.nodes()

        # If there is no solution return None
        if not self.solve():
            return None

        # Check if the solver can provide a model
        if isinstance(self.solver, MathSAT5Solver) and isinstance(self.colorer, ArrayUFColorerPySMT):
            raise Exception("MathSAT5Solver cannot access assigned values for custom types")
        else:
            model = self.solver.get_model()

        result = {}

        # Z3 can work with custom types in arrays, but cannot return its model either. But it can be solved
        # as solving another formula in context of the model. 
        # Therefore, we iterate over all vertices and all color symbols and check if vi=cj.
        # If result is True then color of vi is cj.
        if isinstance(self.colorer, ArrayUFColorerPySMT):
            color_symbols = self.colorer.get_color_symbols()
            for n in nodes:
                for i, c in enumerate(color_symbols, start=0):
                    if model.get_value(Equals(vertex_symbols[n], color_symbols[c])).is_true():
                        result[n] = i
                        break
            return result
        
        # In the case of BV, we want to represent the bit vector as an integer.
        elif isinstance(self.colorer, (BVColorerPySMT, ArrayBVColorerPySMT)):
            for n in nodes:
                bv_value = model.get_value(vertex_symbols[n])
                result[n] = bv_value.constant_value()

        # In case that theory works with integers" to "In case the theory works with integers.
        else:
            result = {n: model.get_value(vertex_symbols[n]).constant_value() for n in nodes}
        return result
        


    def solve(self):
        """
        Solve the graph coloring problem.

        This method adds the formula to the solver and attempts to solve it.

        Returns:
            bool: True if a solution is found, False otherwise.
        """
        # Add color constraints from the colorer and call the solver's solve function.
        self.solver.add_assertion(self.get_formula())
        return self.solver.solve()

