
import sys
import os
import time
from multiprocessing import Process, Queue  # Import necessary modules for multiprocessing
from networkx.drawing.nx_pydot import read_dot
from reduction import create_reduction, SOLVER_THEORY_MAP




def create_and_solve(reduc_input, output_queue):
    """
    Create a graph encoding reduction, solve it, and put the results in the output queue.

    Args:
        reduc_input (tuple): A tuple containing (solver, theory, num_colors, graph, ret_mod, no_formula),
                         where 'model' is an argument for the cvc5 solver that specifies whether
                         a model should be generated or not. This determines if a solution or
                         only a binary result is needed.
        output_queue (Queue): A multiprocessing Queue to store the results.

    The function puts a tuple in the output_queue containing:
    (result, solution_list, formula, reduction_time, process_time, total_time)
    """
    
    graph_enc = create_reduction(reduc_input[0], 
                                    reduc_input[1],
                                    reduc_input[2],
                                    reduc_input[3],
                                    reduc_input[4],
                                    )
    

    start_reduction_t = time.time()
    if reduc_input[5]:
        formula = graph_enc.get_formula_assertions()
    else:
        graph_enc.get_formula_assertions()
        formula = None
        
    end_reduction_t = time.time()

    
    # Time processing
    start_process = time.time()
    result = graph_enc.solve()
    end_process = time.time()


    reduction_time = end_reduction_t - start_reduction_t
    process_time = end_process - start_process
    total_time = process_time + reduction_time

   
    solution_list = []
    if result and reduc_input[4]:
        try:
            solution  = graph_enc.get_solution()
            sorted_nodes = sorted(solution.keys(), key=lambda x: int(x) if x.isdigit() else x)
            for v in sorted_nodes:
                solution_list.append(f"{v}: {solution[v]}")
        except Exception as e:
            print(f"{e}")
    
        


    output_queue.put((result, solution_list, formula, reduction_time, process_time, total_time))



def process_with_timeout(reduc_input, timeout):
    """
    Run the graph coloring process with a specified timeout.

    Args:
        reduc_input (tuple): A tuple containing (solver, theory, num_colors, graph, model).
        timeout (int): The maximum time in seconds to wait for the process to complete.

    Returns:
        tuple: A tuple containing (result, solution, formula, reduction_time, process_time, total_time).
               Returns (None, "Timeout.", None, None, None, None) if the process times out.
               Returns (None, "Error: No output for process.", None, None, None, None) if there was problem with queue.
    """
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
        return None, "Timeout.", None,  None, None, None
    else:
        if output_queue.empty():
            # Handle cases where no output was put into the queue
            return None, "Error: No output for process.", None, None, None, None
        result = output_queue.get()
        return result
        




def args_validation():
    """
    Validate command-line arguments and prepare input for the solver.

    Returns:
        tuple: A tuple containing:
            - graph_data (dict): A dictionary with keys 'V' (number of vertices),
                                 'E' (number of edges), and 'time' (time to read the graph).
            - timeout (int): The timeout value in seconds.
            - reduct_input (tuple): A tuple containing (solver, theory, num_colors, graph, ret_mod).

    Raises:
        SystemExit: If the arguments are invalid or the input file is not accessible.
    """

    # Not enough arguments
    if len(sys.argv) < 5:
        print("Usage: python reduction <path_to_dot_file> <num_colors> <solver> <theory> [--ret_mod] [--no-formula]")
        sys.exit(1)

    # File is not accessible
    graph_path = sys.argv[1]
    if not (os.path.isfile(graph_path) and os.access(graph_path, os.R_OK)):
        print(f"Error: The file '{graph_path}' does not exist or is not accessible.")
        sys.exit(1)
    
    # Wrong type of argument number colors.
    try:
        num_colors = int(sys.argv[2])
        if num_colors < 3:
            raise ValueError
    except ValueError:
        print("The number of colors must be an integer and must be greater than or equal to 3.")
        sys.exit(1)
    

    
    solver = sys.argv[3]
    theory = sys.argv[4]
    # If need a solution or only result.
    ret_mod = not("--no-model" in sys.argv)
    no_formula = not("--no-formula" in sys.argv)
    timeout = 0

    # take a timeout argument
    try:
        for a in sys.argv:
            if "--t-" in a:
                timeout = int(a.split('-')[-1])
    except:
        print("Wrong timeout format.")
        exit(1)
    

    # There is noe such solver
    if solver not in SOLVER_THEORY_MAP:
        print("Wrong value for solver.")
        exit(1)

    # Check if theory is implemented in choosen colder.
    if theory not in SOLVER_THEORY_MAP[solver]:
        print(f"This theory is not implemented in {solver}")
        exit(1)

    # number of colors must be power of 2 for some theories.
    if theory[0] == "S" or theory[0] == "B":
        power_of_two  = (num_colors <= 0) or (num_colors & (num_colors - 1)) != 0
        if power_of_two:
            print("Number of colors must be power of 2")
            exit(1)

    # rread graph
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

    reduct_input = (solver, theory, num_colors, graph, ret_mod, no_formula)
    
    return graph_data, timeout, reduct_input
   



 # Define some ANSI escape codes for colors
TEXT_COLORS_CLI = {
    "RED" : '\033[91m',
    "GREEN" : '\033[92m',
    "YELLOW" : '\033[93m',
    "BLUE" : '\033[94m',
    "MAGENTA" : '\033[95m',
    "CYAN" : '\033[96m',
    "RESET" : '\033[0m'
}

TEXT_COLORS_FILE = {
    "RED" : '',
    "GREEN" : '',
    "YELLOW" : '',
    "BLUE" :'',
    "MAGENTA" : '',
    "CYAN" : '',
    "RESET" : ''
}

ROUND_PLACE = 6

if __name__=="__main__":
    
    graph_data, timeout, reduct_input = args_validation()
   
    result, solution, formula, reduction_time, process_time, total_time = process_with_timeout(reduct_input, timeout)
    
    if sys.stdout.isatty():
        text_color = TEXT_COLORS_CLI
    else:
        text_color = TEXT_COLORS_FILE
    
    if result == None:
        print(text_color["RED"] + solution + text_color["RESET"])
        exit(1)

    if reduct_input[5]:
        print(text_color["CYAN"] + "\n== Formula ==" + text_color["RESET"])
        for assertion in formula:
            print(assertion)

    print(text_color["GREEN"] + "\n== Output ==" + text_color["RESET"])
    if result:
        for ass in solution:
            print(ass)
        print(f"Result: {text_color['GREEN']}Colorable{text_color['RESET']}")
    else:
        print(f"Result: {text_color['GREEN']}Not Colorable{text_color['RESET']}")



    print(text_color["CYAN"] + "\n== Graph Details ==" + text_color["RESET"])
    print(f"Number of nodes: {text_color['MAGENTA']}{graph_data['V']}{text_color['RESET']}")
    print(f"Number of edges: {text_color['MAGENTA']}{graph_data['E']}{text_color['RESET']}")

    print(text_color["YELLOW"] + "\n== Performance Timings ==" + text_color["RESET"])
    print(f"Read file time          : {text_color['BLUE']}{round(graph_data['time'],ROUND_PLACE)} seconds{text_color['RESET']}")
    print(f"Reduction creation time : {text_color['BLUE']}{round(reduction_time,ROUND_PLACE)} seconds{text_color['RESET']}")
    print(f"Solving time            : {text_color['BLUE']}{round(process_time,ROUND_PLACE)} seconds{text_color['RESET']}")
    print(f"Total time              : {text_color['BLUE']}{round(total_time,ROUND_PLACE)} seconds{text_color['RESET']}")