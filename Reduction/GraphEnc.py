

"""
GraphEnc Module

This module defines an abstract base class for encoding k-coloring problem for undirected graph 
in the logic formula.

Classes:
    GraphEnc: An abstract base class for graph encoding.

"""

class GraphEnc:
    """
    An abstract base class for encoding k-coloring problem for undirected graph 
    in the logic formula.


    Methods:
        - add_constraints()
        - get_formula()
        - create_reduction()
        - get_formula_assertions()
        - get_solution()
        - solve()

    Attributes:
        graph: The graph to be colored.
        colorer: The coloring strategy to be used. It changes in context of theory.
        solver: The solver instance to be used for finding a solution.
        graph_constraints (list): A list to store constraints of fomula.

    """
    def __init__(self, graph, colorer, solver):
        """
        Initialize a new GraphEnc instance.

        Args:
            graph: The graph to be colored.
            colorer: The coloring strategy to be used. It changes in context of theory.
            solver: The solver instance to be used for finding a solution.
        """
        self.graph = graph
        self.colorer = colorer
        self.solver = solver
        self.graph_constraints = []
    

    def __enter__(self):
        """
        Enter the runtime context related to this object.

        Returns:
            self: The instance itself.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the runtime context related to this object.

        This method cleans up resources by exiting the solver and deleting attributes.

        Args:
            exc_type: The exception type, if any.
            exc_val: The exception value, if any.
            exc_tb: The exception traceback, if any.
        """
        # Clean up resources
        self.solver.exit()
        del self.colorer
        del self.solver
        del self.graph_constraints


    def add_constraints(self):
        """
        Add constraints to the graph encoding.

        This method should be overridden by subclasses to implement
        specific constraint addition logic.

        Raises:
            NotImplementedError: If this method is not overridden by a subclass.
        """
        raise NotImplementedError("This method should be overridden by subclasses")


    def get_formula(self):
        """
        Get the complete formula for the graph coloring problem.

        This method combines color constraints and graph-specific constraints.

        Returns:
            Formula: With all constraints
        """
        formula = self.colorer.create_color_constraints(self.graph.nodes()) # create colors and vertecies constraints
        if self.graph_constraints == []:
            self.add_constraints()                  # If not created yes, crete esges contraints
        formula.extend(self.graph_constraints)
        return formula
    

    def get_formula_assertions(self):
        """
        Get the formula assertions.

        This method should be overridden by subclasses to implement
        specific logic for obtaining formula assertions.

        Return:
            list: list of constraints in string format.
        Raises:
            NotImplementedError: If this method is not overridden by a subclass.
        """
        raise NotImplementedError("This method should be overridden by subclasses")


    def get_solution(self):
        """
        Get the solution for the graph coloring problem.

        This method should be overridden by subclasses to implement
        specific logic for obtaining the solution.

        Return:
            If there is solution returns dictionary with vertecies symbols and their assignments,
            and return None otherwise.
        Raises:
            NotImplementedError: If this method is not overridden by a subclass.
        """
        raise NotImplementedError("This method should be overridden by subclasses")


    def solve(self):
        """
        Solve the graph coloring problem.

        This method should be overridden by subclasses to implement
        specific solving logic.

        Returns:
            True if there is solution and False otherwise.

        Raises:
            NotImplementedError: If this method is not overridden by a subclass.
        """
        raise NotImplementedError("This method should be overridden by subclasses")
    

    def get_solver(self):
        """
        Get the solver instance associated with this graph encoding.

        Returns:
            Solver: The solver instance (either CVC5 or pySMT) used for this graph encoding.
        """
        return self.solver
