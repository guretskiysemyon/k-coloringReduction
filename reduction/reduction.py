from cvc5 import Solver as cvc5_solver
from pysmt.shortcuts import Solver as pysmt_solver
import ColorerPySMT
import ColorerCVC5
import GraphEncPySMT
import GraphEncCVC5
import sys
import os
import time
from multiprocessing import Process, Queue  # Import necessary modules for multiprocessing
from networkx.drawing.nx_pydot import read_dot




SOLVER_THEORY_MAP = {
    "msat" : {"LIA", "AUF", "AINT", "ABV", "BV"},
    "z3": {"LIA", "NLA", "AUF", "AINT", "ABV", "BV"},
    "yices": {"LIA"}, 
    # "btor" : {"BV", "ABV"}, 
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



# (solver, theory, num_colors, graph, model)
def create_and_solve(reduc_input, output_queue):
    
    graph_enc = create_reduction(reduc_input[0], reduc_input[1], reduc_input[2], reduc_input[3], reduc_input[4] )
    # reset_env()
    start_reduction_t = time.time()
    graph_enc.get_formula()
    end_reduction_t = time.time()

    formula = graph_enc.get_formula_assertions()
    # Time processing
    start_process = time.time()
    res = graph_enc.solve()
    end_process = time.time()


    reduction_time = end_reduction_t - start_reduction_t
    process_time = end_process - start_process
    total_time = process_time + reduction_time

    
    solution_list = []
    if res and reduc_input[4]:
        try:
            solution  = graph_enc.get_solution()
            sorted_nodes = sorted(solution.keys(), key=lambda x: int(x) if x.isdigit() else x)
            for v in sorted_nodes:
                solution_list.append(f"{v}: {solution[v]}")
        except Exception as e:
            print(f"{e}")


    output_queue.put((solution_list, formula, reduction_time, process_time, total_time))



def process_with_timeout(reduc_input, timeout):
    output_queue = Queue()  # Create a Queue to receive results
    process = Process(target=create_and_solve, args=(reduc_input, output_queue))
    process.start()  # Start the process

    if timeout == 0:
        process.join()
    else:
        process.join(timeout)  # Wait for the process to finish or timeout

    if process.is_alive():
        # If the process is still running, terminate it
        process.terminate()
        process.join()
        return None, "Timeot.", None,  None, None
    else:
        if output_queue.empty():
            # Handle cases where no output was put into the queue
            return None, "Error: No output for process.", None, None, None
        result = output_queue.get()
        return result
        




def args_validation():
    if len(sys.argv) < 5:
        print("Usage: python script.py <path_to_dot_file> <num_colors> <solver> <theory> [--ret_mod]")
        sys.exit(1)

    graph_path = sys.argv[1]
    if not (os.path.isfile(graph_path) and os.access(graph_path, os.R_OK)):
        print(f"Error: The file '{graph_path}' does not exist or is not accessible.")
        sys.exit(1)
    

    try:
        num_colors = int(sys.argv[2])
        if num_colors < 3:
            raise ValueError
    except ValueError:
        print("The number of colors must be an integer and must be greater than or equal to 3.")
        sys.exit(1)
    

    
    solver = sys.argv[3]
    theory = sys.argv[4]
    ret_mod = not("--no-model" in sys.argv)
    timeout = 0

    try:
        for a in sys.argv:
            if "--t-" in a:
                timeout = int(a.split('-')[-1])
    except:
        print("Wrong timeout format.")
    

    if solver not in SOLVER_THEORY_MAP:
        print("Wrong value for solver.")
        exit(1)

    # Check if theory is implemented in choosen colder.
    if theory not in SOLVER_THEORY_MAP[solver]:
        print(f"This theory is not implemented in {solver}")
        exit(1)

    if theory[0] == "S" or theory[0] == "B":
        power_of_two  = (num_colors <= 0) or (num_colors & (num_colors - 1)) != 0
        if power_of_two:
            print("Number of colors must be power of 2")


    try:
        read_time_start = time.time()
        graph = read_dot(graph_path)
        read_time_end = time.time()
    except Exception as e:
        print("Error in reading file.")
        print(f"{e}")
    
    num_vertices = graph.number_of_nodes()
    num_edges = graph.number_of_edges()

    graph_data = {
        "V" : num_vertices,
        "E": num_edges, 
        "time" : read_time_end - read_time_start
    }

    reduct_input = (solver, theory, num_colors, graph, ret_mod)
    
    return graph_data, timeout, reduct_input
   






if __name__=="__main__":
    
    graph_data, timeout, reduct_input = args_validation()
   
    solution, formula, reduction_time, process_time, total_time = process_with_timeout(reduct_input, timeout)
        
    
    if isinstance(formula,str):
        print(formula)
        exit(1)
    
    if solution != []:
        print(f"Result: Colorable")
    else:
        print(f"Result: Not Colorable")
    
    print("Formula:")
    for assertion in formula:
        print(assertion)


    for ass in solution:
        print(ass)
            
        
    
    print(f"Number of nodes: {graph_data['V']}")
    print(f"Number of edges: {graph_data['E']}")
    print(f"Read file time: {graph_data['time']}")
    print(f"Reduction creattion time: {reduction_time}")
    print(f"Solving time: {process_time}")
    print(f"Total time: {total_time}")






