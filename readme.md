
# About
This project is based on the method described in "Colors Make Theories Hard" by Roberto Sebastiani [1](https://www.researchgate.net/publication/303912889_Colors_Make_Theories_Hard), specifically on proving NP-hardness in various theories like arithmetic and arrays through satisfiability problems. The article introduces reductions from the k-color graph problem to satisfiability problems for given theories, providing various algorithms for graph coloring challenges using these reductions. Our work implements these reductions using pysmt and cvc solvers, thus solving the k-colorability problem in this manner.

As part of the project, we have run tests on our tools and SageMath, and and compared the results as described below.


## Implemented Theories
    msat : LIA, AUF, AINT, ABV, BV,
    z3   : LIA, NLA, AUF, AINT, ABV, BV,
    yices: LIA, BV, 
    btor : BV, ABV, 
    cvc5 : LIA, NLA, AUF, AINT, ABV, BV, SUF, SINT, SBV,

where:
    **A** stands for Array and **S** stands for Sets theory (e.g., ABV is array theory with BV to BV arrays).

Note: msat, z3, yices, and btor are implemented using the pysmt API, while cvc5 is implemented using its own library


## Structure of Code

There are different types of Colorers, each representing a specific theory and creating constraints for vertices and colors (You can read more about this in the article). Therefore, there are two abstract classes: ColorerCVC5 and ColorerPySMT. Colorers that extend these classes implement reductions to specific theories (e.g., LIAColorer, BVColorer, etc.).

However, there is one abstract class GraphEnc with GraphEncCVC5 and GraphEncPySMT extending it. The difference between these is only in syntax since one works with the PySMT API and the other with the CVC5 API. Both receive a colorer as an argument and add edge constraints ($v_{i}\ne v_{j}$ if they are connected by an edge).

Additionally, there is a reduction.py file that can create a pair of colorer and graph encoder for your convenience, but you do not need to use it. You can create them yourself. More details could be found in the code documentation.

# Installation:
Since we use pysmt, you first need to install pysmt:

``` bash
pip install pysmt
```
Then, you can install the necessary solvers:

``` bash
pysmt-install --msat --z3 --btor --yices
```
After installation, you can check the setup:

```
pysmt-install --check
```

To install cvc5, run:

```bash
pip install cvc5
```


>[Note] - 
> You can learn more about these tools at the[pysmt](https://github.com/pysmt/pysmt) GitHub repository and [cvc5](https://cvc5.github.io/) website.


We have used the networkx and pydot libraries to read files, which are also compatible with SageMath's input formats. To install these libraries, use the following command:

```bash
pip install networkx pydot
```

After installation, you can run `exampleCVC5.py` and `examplePySMT.py` from Examples directory to ensure that the installation worked.



# Tests

### Benchmarks
We ran tests on the benchmarks which are in the Benchmarks folder, that are sourced from the DIMACS COLOR02.30.04 challenge. You can view the original DIMACS format and the same graphs but translated to .dot format, in the DOT folder.

Additionally, there is a `sorted_graph_data.csv` file that includes all the files we used, sorted by the number of edges. This file also provides information on the number of vertices and edges for each graph.


### Test conditions
In the script we used, we set a 10-second limit for each graph to determine how many each tool could solve. Since our reduction is a decision problem and requires k (the number of colors) as an argument, we ran tests for all k values in the range of 3 to 20 and all k values in [4,8,16,32,64] for BV and Sets.

However, SageMath searches for the minimal k, so the conditions for the tools differ, but we have accounted for it.

### Results files
You can find the results file in the TestsResults folder, divided into cvc5 and pysmt sections and sometimes ordered by theory. Additionally, the 10United folder contains all files consolidated in one place.
As also saved all graphs as images that we used in this readme.



## Results
### First Perspective

We create graphs where the x-axis varies with k (number of colors) and the y-axis represents the number of inputs that each solver-theory pair solved within a given timeout.

Firstly, We show a theory comparison for the cvc5 solver:
![](TestResults/GraphImages/all_counted_only_cvc.jpg)


Next, we do the same for msat and z3:
![](TestResults/GraphImages/all_counted_only_msat.jpg)

![](TestResults/GraphImages/all_counted_only_z3.jpg)

On each of the graphs, a pointed line represents SageMath's results. A reminder that this tool finds the minimal k, so we represent its running time as constant across all k's. The result is 16.

From the graphs, note that in z3, all theories solved more inputs than SageMath. In cvc5, all theories except one outperformed SageMath, and in msat, part of the theories did so. We allow ourselves to make this comparison since there is a possibility to run all k's from 3 to 20 in parallel and solve the graph instances in this way. However, it's important to note that this is not a scalable solution (i.e., we cannot do this for large k).

In the end, we compile all graphs into one image. DDespite that this graph is overloaded with information, it is clear that most solver-theory pairs performed better. The source image is available in the files, you can zoom in for higher resolution.

![](TestResults/GraphImages/all_counted.jpg)


The results for BV and Set are presented below in the same format. The results are the same.
![](TestResults/GraphImages/BV_S_counted.jpg)


### Second Perspective
In the table below, each row corresponds to a specific theory. This enables comparison of the results of different solvers. In this context, the number of inputs is the product of the number of files and the number of k's. For BV and sets, it is $185 \cdot 5 = 925$ and for other cases, it is $185\cdot 18=3330$.


For BV and sets:
| Theory name   |   cvc | msat   | z3   | btor   |
|:--------------|------:|:-------|:-----|:-------|
| BV            |   549 | 561    | 504  | 540    |
| SBV           |    78 | -      | -    | -      |
| SINT          |    76 | -      | -    | -      |
| SUF           |    78 | -      | -    | -      |

where "-" indicates that the theory is not implemented by the solver.

And for other theories:
| Theory name   |   cvc | msat   |   z3 | yices   | btor   |
|:--------------|------:|:-------|-----:|:--------|:-------|
| ABV           |   639 | 789    | 1006 | -       | 1267   |
| AINT          |   533 | 473    | 1278 | -       | -      |
| AUF           |   722 | 1123   | 1339 | -       | -      |
| LIA           |   703 | 1067   |  962 | 1328    | -      |
| NIA           |    27 | -      | 1145 | -       | -      |


From the first table, observe that the results for BV are relatively consistent across the solvers, while the results for Sets are significantly lower, with the best result accounting for about half of all inputs. 

In the second table, z3 generally outperforms cvc5 and msat, with the best result covering about a third of all inputs.


### Third Perspective
In the following graphs, the x-axis corresponds to the range of k's and the y-axis represents the number of inputs solved. However, in this section, each line represents a theory. A theory is considered to solve an input within a given time if at least one solver can solve this input it using this theory. We aggregate the results for clarity. Again, this approach proves to be useful as it is possible to run multiple solvers in parallel.

![](/TestResults/GraphImages/all_aggr.jpg)
In this case, we can see that all theories perform better than the SageMath tool, but it is difficult to discern the relationship between them.

For BV and Sets
![](/TestResults/GraphImages/all_aggr_BV.jpg)

Here, only BV performs better than SageMath, while Sets achieve almost the same results as SageMath.



### Fourth Perspective
In this section, we define that a pair (solver, theory) successfully solves an input if for some k the result is False, but for k+1 it is True. We utilize the advantage of the ability to run all tests (from k=3 to k=20) simultaneously. If a (solver, theory) pair solves an input, we calculate the time by taking the maximum of the times to decide k and k+1.

The following table displays these results:

| File name                   |   k |   Sage Result | cvc-ABV   | cvc-AINT   | cvc-AUF   | cvc-LIA   | msat-ABV   | msat-AINT   | msat-AUF   | msat-LIA   | z3-ABV   | z3-AINT   | z3-AUF   | z3-LIA   | z3-NIA   | yices-LIA   | btor-ABV   |
|:----------------------------|----:|--------------:|:----------|:-----------|:----------|:----------|:-----------|:------------|:-----------|:-----------|:---------|:----------|:---------|:---------|:---------|:------------|:-----------|
| myciel3.dot                 |   4 |       0.01596 | 0.01758   | 0.12347    | 0.01587   | 0.0265    | 0.05747    | 0.04411     | 0.0371     | 0.20305    | 0.05381  | 0.04988   | 0.0488   | 0.35391  | 1.57844  | 0.22048     | 0.10181    |
| myciel4.dot                 |   5 |       0.14637 | 3.53037   | x          | 4.06482   | 9.14237   | 0.13385    | 0.16975     | 0.08435    | 0.7886     | 0.08718  | 0.12075   | 0.0832   | 0.72028  | 5.13743  | 7.372       | 0.04326    |
| 2-Insertions_3.dot          |   4 |       0.40619 | 5.11704   | x          | 4.92877   | 1.42027   | 0.23049    | 0.1561      | 0.07013    | 0.09832    | 0.17066  | 0.09575   | 0.07586  | 0.11299  | 3.46678  | 4.13224     | 0.05006    |
| qwhopt.order5.holes10.1.dot |   5 |       0.0068  | 0.11236   | x          | 0.08096   | 0.17269   | 0.39489    | 0.14027     | 0.06579    | 0.04702    | 0.16375  | 0.05696   | 0.06098  | 0.05771  | 3.34632  | 0.06648     | 0.05276    |
| qwhdec.order5.holes10.1.dot |   5 |       0.00645 | 0.11181   | x          | 0.08125   | 0.17258   | 0.41481    | 0.15542     | 0.08146    | 0.0471     | 0.18188  | 0.07298   | 0.07744  | 0.05749  | 3.34464  | 0.06703     | 0.05259    |
| 1-FullIns_3.dot             |   4 |       0.00679 | 0.05827   | 0.77024    | 0.05726   | 0.07582   | 0.13502    | 0.11414     | 0.06529    | 0.04497    | 0.06169  | 0.0577    | 0.05759  | 0.0664   | 2.34407  | 0.0406      | 0.03417    |
| queen5_5.dot                |   5 |       0.0081  | 0.11755   | 5.89396    | 0.16103   | 0.29072   | 0.42851    | 0.15909     | 0.07526    | 0.07494    | 0.08934  | 0.06414   | 0.06526  | 0.08778  | 3.438    | 0.06827     | 0.08006    |
| jean.dot                    |  10 |       0.02242 | x         | x          | x         | x         | x          | x           | 2.038      | x          | 7.03539  | 0.66042   | 0.53975  | x        | x        | x           | 1.04872    |
| 1-FullIns_4.dot             |   5 |       6.2531  | x         | x          | x         | x         | 5.0504     | 2.13759     | 0.34834    | 1.351      | 1.56639  | 0.188     | 0.21579  | 0.55471  | 3.90635  | x           | 0.23163    |
| huck.dot                    |  11 |       0.02954 | x         | x          | x         | x         | x          | x           | x          | x          | x        | 5.1867    | 3.4922   | x        | x        | x           | 2.2456     |
| miles250.dot                |   8 |       0.02787 | x         | x          | x         | x         | 7.54487    | x           | 1.07705    | 4.60329    | 1.22082  | 0.32859   | 0.31108  | 3.08174  | x        | x           | 0.33705    |
| david.dot                   |  11 |       0.04628 | x         | x          | x         | x         | x          | x           | x          | x          | x        | 7.4241    | 4.74902  | x        | x        | x           | 1.77252    |
| queen7_7.dot                |   7 |       2.61606 | x         | x          | x         | x         | x          | 3.23592     | 0.54408    | x          | x        | 1.3367    | 6.48746  | x        | x        | x           | 1.73852    |
| anna.dot                    |  11 |       0.06383 | x         | x          | x         | x         | x          | x           | x          | x          | x        | x         | 7.10551  | x        | x        | x           | 2.88424    |
| games120.dot                |   9 |       0.06823 | 4.62348   | x          | x         | x         | x          | x           | 1.3028     | x          | x        | 0.5278    | 0.59516  | x        | x        | x           | 0.95879    |
| queen8_12.dot               |  12 |       2.6014  | x         | x          | x         | x         | x          | x           | x          | x          | x        | x         | x        | x        | x        | x           | x          |


where 'x' denotes that the (solver, theory) pair did not solve the input.


Here is a more compact table to show who provided the best result for each file:


| File name                   | Best     | Difference to second   |
|:----------------------------|:---------|:----------------------:|
| myciel3.dot                 | cvc-AUF  | 0.00567                |
| myciel4.dot                 | btor-ABV | 2.3835                 |
| 2-Insertions_3.dot          | btor-ABV | 7.11406                |
| qwhopt.order5.holes10.1.dot | sageMath | 5.91471                |
| qwhdec.order5.holes10.1.dot | sageMath | 6.30233                |
| 1-FullIns_3.dot             | sageMath | 4.0324                 |
| queen5_5.dot                | sageMath | 6.91852                |
| jean.dot                    | sageMath | 23.07449               |
| 1-FullIns_4.dot             | z3-AINT  | 32.26117               |
| huck.dot                    | sageMath | 75.01896               |
| miles250.dot                | sageMath | 10.16182               |
| david.dot                   | sageMath | 37.29991               |
| queen7_7.dot                | msat-AUF | 3.80823                |
| anna.dot                    | sageMath | 44.18628               |
| games120.dot                | sageMath | 6.7356                 |
| queen8_12.dot               | sageMath | -                      |

For inputs that SageMath successfully solves, it often provides better results than our tool. Only in 5 out of 16 inputs, our tool performed better. The last column calculates the difference between SageMath's result to the second-place result, divided by the best result (in cases where SageMath was the best otherwise the comparison is made with the best solver).

The difference between these results is significant, varying from 2 to 75 times the performance of the competing solvers.


### Fifth Perspective
Once again, we evaluate whether a (solver, theory) pair can solve an input using the criteria from the previous case—where k is False and k+1 is True. However, this time we proceed through all files and compare the results excluding those from SageMath.

For each of the 185 files, we determined which (solver, theory) combination yields the best result in terms of time. Afterward, we sorted the (solver, theory) pairs by the frequency with which they achieved the best score. For example, in our analysis, btor using the Array with BV (ABV) theory was found to be the best 15 times across all cases.

The table below summarizes the frequencies with which each solver-theory pair provided the best results:

| Solver name   |   Number of Solved |
|:--------------|-------------------:|
| btor-ABV      |                 15 |
| z3-AUF        |                  6 |
| z3-AINT       |                  5 |
| msat-LIA      |                  2 |
| msat-AUF      |                  2 |
| cvc-AUF       |                  1 |
| z3-NIA        |                  1 |


Note that btor with Arrays with BV (ABV) is the leading pair. Following far behind in second place is z3 with Array with Uninterpreted Functions (AUF). Also, it is noteworthy that a total of 32 inputs were solved, which is twice the number solved by SageMath.

[!Note] In the last two cases, we did not use BV and Sets since the step in k is large, and the same definition of "solved" can not be applied.

# Conclusion:
In some cases, this approach can yield good results. Specifically, the number of solved instances was greater than what the baseline SageMath tool could solve, and in some cases, it even outperformed SageMath. However, in instances that SageMath solved, our tool generally exhibited poorer performance.

## Future work:
Our current implementation is direct and does not utilize any heuristics. Therefore, experimenting with the extension of the formula to include more constraints could potentially yield better results.

Since our reduction addresses a decision problem, it could be interesting to explore converting it into a search problem.

Additionally, there are other tools like SageMath that could be evaluated as well.





