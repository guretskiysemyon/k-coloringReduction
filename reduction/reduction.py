from cvc5 import Solver as cvc5_solver
from pysmt.shortcuts import Solver as pysmt_solver
import ColorerPySMT
import ColorerCVC5
import GraphEncPySMT
import GraphEncCVC5




SOLVER_THEORY_MAP = {
    "msat" : {"LIA", "AUF", "AINT", "ABV", "BV"},
    "z3": {"LIA", "NLA", "AUF", "AINT", "ABV", "BV"},
    "yices": {"LIA"}, 
    "btor" : {"BV", "ABV"}, 
    "cvc5" : {"LIA", "NLA", "AUF", "AINT", "ABV", "BV", "SUF", "SINT", "SBV"},
  }


def create_reduction(solver, theory, k, graph, search_model = True):
    """
    Create a graph encoding reduction based on the specified solver and theory.

    Args:
        solver (str): The name of the solver to use.
        theory (str): The theory to use for graph coloring.
        k (int): The number of colors to use.
        graph: The graph to be colored.

    Returns:
        GraphEnc: An instance of either GraphEncCVC5 or GraphEncPySMT.

    Raises:
        Exception: If an invalid solver is specified.
        NotImplementedError: If the specified theory is not implemented for the given solver.
        Exception: If the number of colors is not a power of 2 for certain theories.
    """

    # Check if solver is legit.
    if solver not in SOLVER_THEORY_MAP:
        raise Exception("Wrong value for solver.")

    # Check if theory is implemented in choosen colder.
    if theory not in SOLVER_THEORY_MAP[solver]:
        raise NotImplementedError(f"This theory is not implemented in {solver}")

    # Check that for BV or Sets k is power of 2.
    if theory[0] == "S" or theory[0] == "B":
        power_of_two  = (k <= 0) or (k & (k - 1)) != 0
        if power_of_two:
            raise Exception("Number of colors must be power of 2")
    
    if solver == "cvc5":
        graph_enc = create_cvc5(theory, k, graph, search_model)

    else:
        graph_enc = create_pysmt(solver,theory, k, graph)
    
    return graph_enc



def create_cvc5(theory, k, graph, search_model = True):
    """
    Create a CVC5-based graph encoding.

    Args:
        theory (str): The theory to use for graph coloring.
        k (int): The number of colors to use.
        graph: The graph to be colored.
        search_model (bool): Whether to produce models. Defaults to True.

    Returns:
        GraphEncCVC5: An instance of GraphEncCVC5 with the appropriate colorer.
    """
    solver = cvc5_solver()
    if search_model:
        solver.setOption("produce-models", "true")
    
    if theory == "LIA":
        colorer = ColorerCVC5.LIAColorerCVC5(k, solver)
    elif theory == "NLA":
        colorer = ColorerCVC5.NLAColorerCVC5(k, solver)
    elif theory == "AUF":
        colorer = ColorerCVC5.ArrayUFColorerCVC5(k, solver)
    elif theory == "AINT":
        colorer = ColorerCVC5.ArrayINTColorerCVC5(k, solver)
    elif theory == "ABV":
        colorer = ColorerCVC5.ArrayBVColorerCVC5(k, solver)
    elif theory == "BV":
        colorer = ColorerCVC5.BVColorerCVC5(k, solver)
    elif theory == "SUF":
        colorer = ColorerCVC5.SetUFColorerCVC5(k, solver)
    elif theory == "SINT":
        colorer = ColorerCVC5.SetINTColorerCVC5(k, solver)
    elif theory == "SBV":
        colorer = ColorerCVC5.SetBVColorerCVC5(k, solver)
    
    graph_enc = GraphEncCVC5.GraphEncCVC5(graph, colorer, solver)

    return graph_enc




def  create_pysmt(solver_name, theory,k, graph):
    """
    Create a pySMT-based graph encoding.

    Args:
        solver_name (str): The name of the pySMT solver to use.
        theory (str): The theory to use for graph coloring.
        k (int): The number of colors to use.
        graph: The graph to be colored.

    Returns:
        GraphEncPySMT: An instance of GraphEncPySMT with the appropriate colorer.
    """
    solver = pysmt_solver(name=solver_name)
    if theory == "LIA":
        colorer = ColorerPySMT.LIAColorerPySMT(k)
    elif theory == "NLA":
        colorer = ColorerPySMT.NLAColorerPySMT(k)
    elif theory == "AUF":
        colorer = ColorerPySMT.ArrayUFColorerPySMT(k)
    elif theory == "AINT":
        colorer = ColorerPySMT.ArrayINTColorerPySMT(k)
    elif theory == "ABV":
        colorer = ColorerPySMT.ArrayBVColorerPySMT(k)
    elif theory == "BV":
        colorer = ColorerPySMT.BVColorerPySMT(k)

    graph_enc = GraphEncPySMT.GraphEncPySMT(graph, colorer, solver)
    return graph_enc


