from sage.all import *
import sys
import os
import time
from networkx.drawing.nx_pydot import read_dot
from sage.graphs.graph_coloring import chromatic_number
from multiprocessing import Process, Queue  # Import necessary modules for multiprocessing
from networkx.drawing.nx_pydot import read_dot


def read_and_process(graph, output_queue):

    # Time reading
    # reset_env()
    start_red_t = time.time()
    G = Graph(graph, multiedges=False, loops=False)
    
    end_red_t = time.time()

    # Time processing
    start_process = time.time()
    res = chromatic_number(G)
    end_process = time.time()

    # del reduction_graph

    reduction_time = end_red_t - start_red_t
    process_time = end_process - start_process
    total_time = process_time + reduction_time

    # Store the results in the output queue
    output_queue.put((res, reduction_time, process_time, total_time))


def process_with_timeout(graph, timeout):
    output_queue = Queue()  # Create a Queue to receive results
    process = Process(target=read_and_process, args=(graph, output_queue))
    process.start()  # Start the process

    process.join(timeout)  # Wait for the process to finish or timeout

    if process.is_alive():
        # If the process is still running, terminate it
        process.terminate()
        process.join()
        print(f"Timeout")
        return None, None, None, None
    else:
        # If the process finished in time, get the result
        if output_queue.empty():
            # Handle cases where no output was put into the queue
            print(f"Error: No output from read_and_process")
            return None, None, None, None
        result = output_queue.get()
        return result




# Main script setup
path_to_files = sys.argv[1]
path_to_directory = sys.argv[2]
output_file = sys.argv[3]

# path_to_files = "/home/semyon/CodeProjects/FinalProject/t.txt"
# path_to_directory = "/home/semyon/CodeProjects/FinalProject/COLOR02.30.04/Small_ones/DOT"
# solver_name = "z3"
# theory_name = "AUF"
# output_file = "res.csv"



timeout_seconds = 10  # Set your desired timeout in seconds

counter = 1

with open(output_file, "w") as res:
    res.write("File name, Read_Time, k, reduction_time, process_time, total_time\n")
    with open(path_to_files, 'r') as file_list:
        for filename in file_list:
            filename = filename.strip()  # Remove any leading/trailing whitespace

            # Skip empty lines
            if not filename:
                continue

            file_path = os.path.join(path_to_directory, filename)
            # Check if the file exists
            if not os.path.isfile(file_path):
                print(f"Warning: File not found: {file_path}")
                continue

            print(f"Processing {counter}: {filename}")

            start_read = time.time()
            graph = read_dot(file_path)
            end_read = time.time()
            read_time = end_read - start_read

            res.write(f"{filename}, {read_time}")
           
            result, reduction_time, process_time, total_time = process_with_timeout(graph, timeout_seconds)

            if result is None:
                # Handle timeout case
                res.write(f", T, T, T, T\n")
            else:
                res.write(f", {result}, {reduction_time}, {process_time}, {total_time}\n")
            
            res.flush()
            print(f"{counter}: {filename} Finished!")
            sys.stdout.flush()
            counter += 1
            del graph
