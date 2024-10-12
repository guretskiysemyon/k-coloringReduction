from cvc5 import Kind
import math


class ColorerCVC5:
    """
    Base class for graph coloring strategies using CVC5 SMT solver.

    This class provides a framework for implementing various graph coloring
    strategies. Subclasses should implement the create_color_constraints method.

    Attributes:
        num_colors (int): The number of colors to use for graph coloring.
        vertex_symbols (dict): A dictionary mapping graph vertices to their corresponding SMT symbols.
        solver: The CVC5 solver instance.
        color_constraints (list): A list to store the color constraints.
    """
    def __init__(self, num_colors, solver):
        """
        Initialize the ColorerCVC5 instance.

        Args:
            num_colors (int): The number of colors to use for graph coloring.
            solver: The CVC5 solver instance.
        """
        self.num_colors = num_colors
        self.vertex_symbols = {}
        self.solver = solver
        self.color_constraints = []
        
    def create_color_constraints(self, nodes):
        """
        Create color constraints for the given nodes.

        This method should be implemented by subclasses to define the specific
        coloring strategy.

        Args:
            nodes: An iterable of graph nodes.
        
        Returns:
            list : list of the constraints for nodes.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

    def get_vertex_symbols(self):
        """
        Get the dictionary of vertex symbols.

        Returns:
            dict: A dictionary mapping graph vertices to their corresponding SMT symbols.
        """
        return self.vertex_symbols





class LIAColorerCVC5(ColorerCVC5):
    """
    Linear Integer Arithmetic (LIA) colorer for CVC5.

    This class implements a graph coloring strategy using Linear Integer Arithmetic.
    The coloring constraint ensures that each vertex is assigned an integer value
    between 0 and k-1, where k is the number of colors.

    Formula: Forall vi in V: 0 <= vi <= k-1
    """
    def create_color_constraints(self, nodes):
        """
        Create color constraints using Linear Integer Arithmetic.

        Args:
            nodes: An iterable of graph nodes.

        Returns:
            list: A list of CVC5 terms representing the color constraints.
        """

       # If already created then return member color_constraints.
        if self.color_constraints:
            return self.color_constraints
        
        for v in nodes:
            vertex = self.solver.mkConst(self.solver.getIntegerSort(), f"v_{v}")
            self.vertex_symbols[v] = vertex         # save symbol for edge constraints creation and solution computation.


            constraint = self.solver.mkTerm(
                Kind.AND,
                self.solver.mkTerm(Kind.GEQ, vertex, self.solver.mkInteger(0)),
                self.solver.mkTerm(Kind.LEQ, vertex, self.solver.mkInteger(self.num_colors - 1))
            )
            self.color_constraints.append(constraint)

        return self.color_constraints



class NLAColorerCVC5(ColorerCVC5):
    """
    Non-Linear Arithmetic (NLA) colorer for CVC5.

    This class implements a graph coloring strategy using Non-Linear Arithmetic.
    The coloring constraint ensures that the product of the differences between
    each vertex value and the possible color values is zero.

    Formula: Forall vi in V: vi(vi-1)...(vi-(k-1)) = 0
    """
    def create_color_constraints(self, nodes):
        # If already created then return member color_constraints.
        if self.color_constraints :
            return self.color_constraints
        
        for v in nodes:
            vertex = self.solver.mkConst(self.solver.getIntegerSort(), f"v_{v}")
            self.vertex_symbols[v] = vertex # save symbol for edge constraints creation and solution computation.
            
            # create (vi-i) for each i in range
            colorer_vi = []
            for i in range(self.num_colors):
                colorer_vi.append(
                    self.solver.mkTerm(Kind.SUB, vertex, self.solver.mkInteger(i)))
                
            # Muiltiply all constraints.
            self.color_constraints.append(
                self.solver.mkTerm(
                    Kind.EQUAL,
                    self.solver.mkTerm(Kind.MULT, *colorer_vi),
                    self.solver.mkInteger(0)                  
                    ))
            
        return self.color_constraints




# Formula: For each v in V:
#           A_0 = array
#           A_1 = A_0[i_1 <- 0]
#           ...
#           A_k = A_(k-1)[i_(k-1) <- k-1]
#           v = A_k[i_1]

class ArrayINTColorerCVC5(ColorerCVC5):
    """
    Array with Integer (ArrayINT) colorer for CVC5.

    This class implements a graph coloring strategy using Arrays with Integers.
    The coloring constraint uses a series of array operations to assign colors to vertices.

    Formula: For each v in V:
             A_0 = array
             A_1 = A_0[i_1 <- 0]
             ...
             A_k = A_(k-1)[i_(k-1) <- k-1]
             v = A_k[i_1]
    """

    def create_color_constraints(self, nodes):
        """
        Create color constraints using Arrays with Integers.

        Args:
            nodes: An iterable of graph nodes.

        Returns:
            list: A list of CVC5 terms representing the color constraints.
        """
        # If already created then return member color_constraints.
        if self.color_constraints:
            return self.color_constraints
        
        int_sort = self.solver.getIntegerSort()
        array_sort = self.solver.mkArraySort(int_sort, int_sort)

        for v in nodes:
            # Create variable for this vertex
            vertex = self.solver.mkConst(int_sort, f"v_{v}")
            self.vertex_symbols[v] = vertex  # save symbol for edge constraints creation and solution computation.

            # Create array for constraints of this vertex
            ass_vi = []

            # Create base array
            arr1 = self.solver.mkConst(array_sort, f"arr0_v{v}")

            # First iteration out of loop since we will need an i1, and this helps not to use if inside.
            i1 = self.solver.mkConst(int_sort, f"i1_v{v}")
            prev_arr = self.solver.mkConst(array_sort, f"arr1_v{v}")
            ass_vi.append(self.solver.mkTerm(Kind.EQUAL, prev_arr, 
                          self.solver.mkTerm(Kind.STORE, arr1, i1, self.solver.mkInteger(0))))

            for i in range(2, self.num_colors + 1):
                # Create new variable, create new array using cur_arr = prev_arr[i <- i]
                cur_i = self.solver.mkConst(int_sort, f"i{i}_v{v}")
                cur_arr = self.solver.mkConst(array_sort, f"arr{i}_v{v}")
                ass_vi.append(self.solver.mkTerm(Kind.EQUAL, cur_arr, 
                              self.solver.mkTerm(Kind.STORE, prev_arr, cur_i, self.solver.mkInteger(i-1))))
                prev_arr = cur_arr

            # Value of v1 is last array[i1]
            ass_vi.append(self.solver.mkTerm(Kind.EQUAL, vertex, 
                          self.solver.mkTerm(Kind.SELECT, prev_arr, i1)))

            self.color_constraints.extend(ass_vi)

        return self.color_constraints
    


class ArrayBVColorerCVC5(ColorerCVC5):
    """
    Array with Bit-Vector (ArrayBV) colorer for CVC5.

    This class implements a graph coloring strategy using Arrays with Bit-Vectors.
    The coloring constraint uses a series of array operations with bit-vectors to assign colors to vertices.

    Formula: For each v in V:
             A_0 = array
             A_1 = A_0[i_1 <- 0]
             ...
             A_k = A_(k-1)[i_(k-1) <- k-1]
             v = A_k[i_1]
    """

    def create_color_constraints(self, nodes):
        """
        Create color constraints using Arrays with Bit-Vectors.

        Args:
            nodes: An iterable of graph nodes.

        Returns:
            list: A list of CVC5 terms representing the color constraints.
        """
        # If already created then return member color_constraints.
        if self.color_constraints:
            return self.color_constraints
        
        num_bits = math.ceil(math.log2(self.num_colors))
        bv_sort = self.solver.mkBitVectorSort(num_bits)
        array_sort = self.solver.mkArraySort(bv_sort, bv_sort)

        for v in nodes:
            # Create variable for this vertex
            vertex = self.solver.mkConst(bv_sort, f"v_{v}")
            self.vertex_symbols[v] = vertex  # save symbol for edge constraints creation and solution computation.

            # Create array for constraints of this vertex
            ass_vi = []

            # Create base array
            arr1 = self.solver.mkConst(array_sort, f"arr0_v{v}")

            # First iteration out of loop
            i1 = self.solver.mkConst(bv_sort, f"i1_v{v}")
            prev_arr = self.solver.mkConst(array_sort, f"arr1_v{v}")
            ass_vi.append(self.solver.mkTerm(Kind.EQUAL, prev_arr, 
                          self.solver.mkTerm(Kind.STORE, arr1, i1, self.solver.mkBitVector(num_bits, 0))))

            for i in range(2, self.num_colors + 1):
                cur_i = self.solver.mkConst(bv_sort, f"i{i}_v{v}")
                cur_arr = self.solver.mkConst(array_sort, f"arr{i}_v{v}")
                ass_vi.append(self.solver.mkTerm(Kind.EQUAL, cur_arr, 
                              self.solver.mkTerm(Kind.STORE, prev_arr, cur_i, self.solver.mkBitVector(num_bits, i-1))))
                prev_arr = cur_arr

            # Value of vertex is last array[i1]
            ass_vi.append(self.solver.mkTerm(Kind.EQUAL, vertex, 
                          self.solver.mkTerm(Kind.SELECT, prev_arr, i1)))

            self.color_constraints.extend(ass_vi)

        return self.color_constraints

    

class ArrayUFColorerCVC5(ColorerCVC5):
    """
    Array with Uninterpreted Functions (ArrayUF) colorer for CVC5.

    This class implements a graph coloring strategy using Arrays with Uninterpreted Functions.
    It creates distinct color symbols and uses array operations to assign these colors to vertices.

    Formula: For each v in V:
             A_0 = array
             A_1 = A_0[i_1 <- 0]
             ...
             A_k = A_(k-1)[i_(k-1) <- k-1]
             v = A_k[i_1]
    """

    def __init__(self, num_colors, solver):
        """
        Initialize the ArrayUFColorerCVC5 instance.

        Args:
            num_colors (int): The number of colors to use for graph coloring.
            solver: The CVC5 solver instance.
        """
        super().__init__(num_colors, solver)
        self.color_symbols = {}

    def get_color_symbols(self):
        """
        Get the dictionary of color symbols.

        Returns:
            dict: A dictionary mapping color identifiers to their corresponding SMT symbols.
        """
        return self.color_symbols

    def create_color_constraints(self, nodes):
        """
        Create color constraints using Arrays with Uninterpreted Functions.

        Args:
            nodes: An iterable of graph nodes.

        Returns:
            list: A list of CVC5 terms representing the color constraints.
        """
        # If already created then return member color_constraints.
        if self.color_constraints:
            return self.color_constraints

        # Define sorts
        IndexType = self.solver.mkUninterpretedSort("IndexType")
        ElementType = self.solver.mkUninterpretedSort("ColorType")
        ArrayType = self.solver.mkArraySort(IndexType, ElementType)

        # Create color symbols
        for i in range(1, self.num_colors + 1):
            self.color_symbols[f"c_{i}"] = self.solver.mkConst(ElementType, f"c_{i}")

        # Create constraints to ensure colors are different
        for i in range(1, self.num_colors):
            for j in range(i + 1, self.num_colors + 1):
                self.color_constraints.append(
                    self.solver.mkTerm(Kind.DISTINCT, 
                                       self.color_symbols[f"c_{i}"], 
                                       self.color_symbols[f"c_{j}"])
                )

        for v in nodes:
            vertex = self.solver.mkConst(ElementType, f"v_{v}")
            self.vertex_symbols[v] = vertex  # save symbol for edge constraints creation and solution computation.

            ass_vi = []
            arr1 = self.solver.mkConst(ArrayType, f"arr0_v{v}")

            i1 = self.solver.mkConst(IndexType, f"i1_v{v}")
            prev_arr = self.solver.mkConst(ArrayType, f"arr1_v{v}")
            ass_vi.append(
                self.solver.mkTerm(Kind.EQUAL, 
                                   prev_arr, 
                                   self.solver.mkTerm(Kind.STORE, arr1, i1, self.color_symbols[f"c_1"]))
            )

            for i in range(2, self.num_colors + 1):
                cur_i = self.solver.mkConst(IndexType, f"i{i}_v{v}")
                cur_arr = self.solver.mkConst(ArrayType, f"arr{i}_v{v}")
                ass_vi.append(
                    self.solver.mkTerm(Kind.EQUAL,
                        cur_arr,
                        self.solver.mkTerm(Kind.STORE, prev_arr, cur_i, self.color_symbols[f"c_{i}"])
                    )
                )
                prev_arr = cur_arr

            ass_vi.append(
                self.solver.mkTerm(Kind.EQUAL, 
                                   vertex, 
                                   self.solver.mkTerm(Kind.SELECT, prev_arr, i1))
            )
            self.color_constraints.extend(ass_vi)

        return self.color_constraints




class SetUFColorerCVC5(ColorerCVC5):
    """
    Set with Uninterpreted Functions (SetUF) colorer for CVC5.

    This class implements a graph coloring strategy using Sets with Uninterpreted Functions.
    It's designed to work only when the number of colors is a power of 2.

    Formula:
        color_set = {c1,...,c _log(k)}
        For each v in V:
            v is subset of color_set

    Note: This colorer only works when the number of colors is a power of 2.
    """

    def __init__(self, num_colors, solver):
        """
        Initialize the SetUFColorerCVC5 instance.

        Args:
            num_colors (int): The number of colors to use for graph coloring. Must be a power of 2.
            solver: The CVC5 solver instance.
        """
        condition = (num_colors <= 0) or (num_colors & (num_colors - 1)) != 0
        if condition:
            self.object = None
        else:
            super().__init__(num_colors, solver)
            self.color_symbols = []

    def create_color_constraints(self, nodes):
        """
        Create color constraints using Sets with Uninterpreted Functions.

        Args:
            nodes: An iterable of graph nodes.

        Returns:
            list: A list of CVC5 terms representing the color constraints.
        """
        # If already created then return member color_constraints.
        if self.color_constraints:
            return self.color_constraints
        
        set_power = int(math.log2(self.num_colors))

        # Create an uninterpreted sort for colors
        ElementType = self.solver.mkUninterpretedSort("ColorType")
        set_sort = self.solver.mkSetSort(ElementType)

        # Create color symbols
        for i in range(set_power):
            self.color_symbols.append(self.solver.mkConst(ElementType, f"c_{i}"))
        
        # Create constraints to ensure colors are different
        for i in range(set_power):
            for j in range(i + 1, set_power):
                self.color_constraints.append(
                    self.solver.mkTerm(Kind.DISTINCT, 
                                       self.color_symbols[i], 
                                       self.color_symbols[j])
                )
        # Create set with elements
        set_term = self.solver.mkEmptySet(set_sort)
        for c in self.color_symbols:
            set_term = self.solver.mkTerm(Kind.SET_INSERT, c, set_term)

        # For each node vi is subset of set_term
        for v in nodes:
            vertex = self.solver.mkConst(set_sort, f"v_{v}")
            self.vertex_symbols[v] = vertex  # save symbol for edge constraints creation and solution computation.

            self.color_constraints.append(
                self.solver.mkTerm(Kind.SET_SUBSET, vertex, set_term)
            )
        
        return self.color_constraints
        


class SetINTColorerCVC5(ColorerCVC5):
    """
    Set with Integers (SetINT) colorer for CVC5.

    This class implements a graph coloring strategy using Sets with Integers.
    It's designed to work only when the number of colors is a power of 2.

    Formula:
        color_set = {c1,...,c _log(k)}
        For each v in V:
            v is subset of color_set

    Note: This colorer only works when the number of colors is a power of 2.
    """

    def __init__(self, num_colors, solver):
        """
        Initialize the SetINTColorerCVC5 instance.

        Args:
            num_colors (int): The number of colors to use for graph coloring. Must be a power of 2.
            solver: The CVC5 solver instance.
        """
        condition = (num_colors <= 0) or (num_colors & (num_colors - 1)) != 0
        if condition:
            self.object = None
        else:
            super().__init__(num_colors, solver)

    def create_color_constraints(self, nodes):
        """
        Create color constraints using Sets with Integers.

        Args:
            nodes: An iterable of graph nodes.

        Returns:
            list: A list of CVC5 terms representing the color constraints.
        """
        # If already created then return member color_constraints.
        if self.color_constraints:
            return self.color_constraints
        
        set_power = int(math.log2(self.num_colors))

        int_sort = self.solver.getIntegerSort()
        set_sort = self.solver.mkSetSort(int_sort)
        
        # Create set with elements
        set_term = self.solver.mkEmptySet(set_sort)
        for i in range(set_power):
            set_term = self.solver.mkTerm(Kind.SET_INSERT, self.solver.mkInteger(i), set_term)

        # For each node vi is subset of set_term
        for v in nodes:
            vertex = self.solver.mkConst(set_sort, f"v_{v}")
            self.vertex_symbols[v] = vertex  # save symbol for edge constraints creation and solution computation.

            self.color_constraints.append(
                self.solver.mkTerm(Kind.SET_SUBSET, vertex, set_term)
            )
        
        return self.color_constraints



class SetBVColorerCVC5(ColorerCVC5):
    """
    Set with Bit-Vectors (SetBV) colorer for CVC5.

    This class implements a graph coloring strategy using Sets with Bit-Vectors.
    It's designed to work only when the number of colors is a power of 2.

    Formula:
        If k = 2^m
        color_set = {c1,...,cm}
        For each v in V:
            v is subset of color_set

    Note: This colorer only works when the number of colors is a power of 2.
    """

    def __init__(self, num_colors, solver):
        """
        Initialize the SetBVColorerCVC5 instance.

        Args:
            num_colors (int): The number of colors to use for graph coloring. Must be a power of 2.
            solver: The CVC5 solver instance.
        """
        condition = (num_colors <= 0) or (num_colors & (num_colors - 1)) != 0
        if condition:
            self.object = None
        else:
            super().__init__(num_colors, solver)

    def create_color_constraints(self, nodes):
        """
        Create color constraints using Sets with Bit-Vectors.

        Args:
            nodes: An iterable of graph nodes.

        Returns:
            list: A list of CVC5 terms representing the color constraints.
        """
        # If already created then return member color_constraints.
        if self.color_constraints:
            return self.color_constraints
        
        bv_width = math.ceil(math.log2(self.num_colors))
        set_power = int(math.log2(self.num_colors))

        bv_sort = self.solver.mkBitVectorSort(bv_width)
        set_sort = self.solver.mkSetSort(bv_sort)
        
        # Create set with elements
        set_term = self.solver.mkEmptySet(set_sort)
        for i in range(set_power):
            set_term = self.solver.mkTerm(Kind.SET_INSERT, self.solver.mkBitVector(bv_width, i), set_term)

        # For each node vi is subset of set_term
        for v in nodes:
            vertex = self.solver.mkConst(set_sort, f"v_{v}")
            self.vertex_symbols[v] = vertex  # save symbol for edge constraints creation and solution computation.

            self.color_constraints.append(
                self.solver.mkTerm(Kind.SET_SUBSET, vertex, set_term)
            )
        
        return self.color_constraints
    

  
class BVColorerCVC5(ColorerCVC5):
    """
    Bit-Vector (BV) colorer for CVC5.

    This class implements a graph coloring strategy using Bit-Vectors.
    It's designed to work only when the number of colors is a power of 2.

    Formula:
        If k = 2^m, where k is the number of colors,
        then v is a bit vector with length m for each vertex.

    Note: This colorer only works when the number of colors is a power of 2.
    """

    def __init__(self, num_colors, solver):
        """
        Initialize the BVColorerCVC5 instance.

        Args:
            num_colors (int): The number of colors to use for graph coloring. Must be a power of 2.
            solver: The CVC5 solver instance.
        """
        condition = (num_colors <= 0) or (num_colors & (num_colors - 1)) != 0
        if condition:
            self.object = None
        else:
            super().__init__(num_colors, solver)

    def create_color_constraints(self, nodes):
        """
        Create color constraints using Bit-Vectors. Check Formula for details.

        Args:
            nodes: An iterable of graph nodes.

        Returns:
            list: An empty list, as no additional constraints are needed.

        Note: By assumption, we have that k = 2^w, where w is the bit-vector length.
        We just want all colors to be different, which is handled by the graph constraints.
        """
        if self.vertex_symbols:
            return []
        

        bv_length = int(math.log2(self.num_colors))
        bv_sort = self.solver.mkBitVectorSort(bv_length)

        # Each v is BV with bv_length
        for v in nodes:
            vertex = self.solver.mkConst(bv_sort, f"v_{v}")
            self.vertex_symbols[v] = vertex  # save symbol for edge constraints creation and solution computation.

        return []