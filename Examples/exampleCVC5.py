from cvc5 import Solver

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Reduction.ColorerCVC5 import (
    LIAColorerCVC5, NLAColorerCVC5, BVColorerCVC5, ArrayUFColorerCVC5
)
from Reduction import reduction
from Reduction.GraphEncCVC5 import GraphEncCVC5
from networkx.drawing.nx_pydot import read_dot




file_path = "./Examples/graph.dot"
k = 4

graph = read_dot(file_path)


print("LIA")
solver = Solver()
# solver.setLogic("QF_LIA")
solver.setOption("produce-models", "true")



colorer = LIAColorerCVC5(k, solver)
reduction_graph = GraphEncCVC5(graph, colorer, solver)


if reduction_graph.solve():
    solution  = reduction_graph.get_solution()
    for v in solution:
        print(f"{v}: {solution[v]}")
   
else:
    print("Not colorable")

print("Formula:")
formula = reduction_graph.get_formula_assertions()
for assertion in formula:
    print(assertion)


print("*****************************************\n\n")




print("Array UF")

solver = Solver()
# solver.setLogic("QF_LIA")
solver.setOption("produce-models", "true")



colorer = ArrayUFColorerCVC5(k, solver)
reduction_graph = GraphEncCVC5(graph, colorer, solver)


if reduction_graph.solve():
    solution  = reduction_graph.get_solution()
    for v in solution:
        print(f"{v}: {solution[v]}")
   
else:
    print("Not colorable")

print("Formula:\n")
formula = reduction_graph.get_formula_assertions()
for assertion in formula:
    print(assertion)


print("*****************************************\n\n")





print("NLA")
solver = Solver()

solver.setOption("produce-models", "true")



colorer = NLAColorerCVC5(k, solver)
reduction_graph = GraphEncCVC5(graph, colorer, solver)


if reduction_graph.solve():
    solution  = reduction_graph.get_solution()
    for v in solution:
        print(f"{v}: {solution[v]}")
   
else:
    print("Not colorable")

print("Formula:")
formula = reduction_graph.get_formula_assertions()
for assertion in formula:
    print(assertion)


print("*****************************************\n\n")






print("BV")
solver = Solver()
solver.setOption("produce-models", "true")



colorer = BVColorerCVC5(k, solver)
reduction_graph = GraphEncCVC5(graph, colorer, solver)


if reduction_graph.solve():
    solution  = reduction_graph.get_solution()
    for v in solution:
        print(f"{v}: {solution[v]}")
   
else:
    print("Not colorable")

print("Formula:")
formula = reduction_graph.get_formula_assertions()
for assertion in formula:
    print(assertion)


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


