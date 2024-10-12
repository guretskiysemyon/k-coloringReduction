


import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Reduction import reduction
from Reduction.ColorerPySMT import LIAColorerPySMT,ArrayBVColorerPySMT, ArrayUFColorerPySMT,ArrayINTColorerPySMT, BVColorerPySMT, NLAColorerPySMT
from Reduction.GraphEncPySMT import GraphEncPySMT
from networkx.drawing.nx_pydot import read_dot
from pysmt.shortcuts import Solver
from pysmt.environment import reset_env


file_path = "./Examples/graph.dot"
k = 4

graph = read_dot(file_path)

print("z3 and LIA")
solver = Solver(name = "z3")
colorer = LIAColorerPySMT(k)
reduction_graph = GraphEncPySMT(graph, colorer, solver)


if reduction_graph.solve():
    solution = reduction_graph.get_solution()
    for v in solution:
        print(f"{v} : {solution[v]}")
else:
    print("Not colorable")


for assertion in reduction_graph.get_formula_assertions():          
    print(assertion)
# Delete the solver
del solver

# Reset the environment to clear all symbols and formulas
reset_env()


print("*****************************************\n\n")



print("z3 and Array UF")
solver = Solver(name = "z3")
colorer = ArrayUFColorerPySMT(k)
reduction_graph = GraphEncPySMT(graph, colorer, solver)


if reduction_graph.solve():
    solution = reduction_graph.get_solution()
    for v in solution:
        print(f"{v} : {solution[v]}")
else:
    print("Not colorable")


for assertion in reduction_graph.get_formula_assertions():          
    print(assertion)
# Delete the solver
del solver

# Reset the environment to clear all symbols and formulas
reset_env()


print("*****************************************\n\n")



print("msat and BV")
solver = Solver(name = "msat")
colorer = BVColorerPySMT(k)
reduction_graph = GraphEncPySMT(graph, colorer, solver)


if reduction_graph.solve():
    solution = reduction_graph.get_solution()
    for v in solution:
        print(f"{v} : {solution[v]}")
else:
    print("Not colorable")


for assertion in reduction_graph.get_formula_assertions():          
    print(assertion)
# Delete the solver
del solver

# Reset the environment to clear all symbols and formulas
reset_env()


print("*****************************************\n\n")



print("btor and BV")
solver = Solver(name = "btor")
colorer = BVColorerPySMT(k)
reduction_graph = GraphEncPySMT(graph, colorer, solver)


if reduction_graph.solve():
    solution = reduction_graph.get_solution()
    for v in solution:
        print(f"{v} : {solution[v]}")
else:
    print("Not colorable")


for assertion in reduction_graph.get_formula_assertions():          
    print(assertion)
# Delete the solver
del solver

# Reset the environment to clear all symbols and formulas
reset_env()


print("*****************************************\n\n")





print("yices and LIA")
solver = Solver(name = "yices")
colorer = LIAColorerPySMT(k)
reduction_graph = GraphEncPySMT(graph, colorer, solver)


if reduction_graph.solve():
    solution = reduction_graph.get_solution()
    for v in solution:
        print(f"{v} : {solution[v]}")
else:
    print("Not colorable")


for assertion in reduction_graph.get_formula_assertions():          
    print(assertion)
# Delete the solver
del solver

# Reset the environment to clear all symbols and formulas
reset_env()


print("*****************************************\n\n")




print("Using reduction file: \n")
print("LIA")
graph_enc = reduction.createReduction('cvc5', 'LIA', k, graph)
if graph_enc.solve():
    solution  = graph_enc.get_solution()
    for v in solution:
        print(f"{v}: {solution[v]}")
   
else:
    print("Not colorable")

print("Formula:")
formula = graph_enc.get_formula_assertions()
for assertion in formula:
    print(assertion)

