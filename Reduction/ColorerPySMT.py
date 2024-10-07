from pysmt.shortcuts import (
    Symbol, Int, And, LE, GE, Minus, Equals, Times, Store, Select, BV, Not
)
from pysmt.typing import INT, ArrayType, BVType, Type
import math

class ColorerPySMT:
    """
    Base class for graph coloring strategies using pySMT.

    This class provides a framework for implementing various graph coloring
    strategies. Subclasses should implement the create_color_constraints method.

    Attributes:
        num_colors (int): The number of colors to use for graph coloring.
        vertex_symbols (dict): A dictionary mapping graph vertices to their corresponding pySMT symbols.
        color_constraints (list): A list to store the color constraints.
    """

    def __init__(self, num_colors):
        """
        Initialize the ColorerPySMT instance.

        Args:
            num_colors (int): The number of colors to use for graph coloring.
        """
        self.num_colors = num_colors
        self.vertex_symbols = {}      
        self.color_constraints = []
        
    def create_color_constraints(self, nodes):
        """
        Create color constraints for the given nodes.

        This method should be implemented by subclasses to define the specific
        coloring strategy.

        Args:
            nodes: An iterable of graph nodes.

        Returns:
            list: A list of pySMT formulas representing the color constraints.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

    def get_vertex_symbols(self):
        """
        Get the dictionary of vertex symbols.

        Returns:
            dict: A dictionary mapping graph vertices to their corresponding pySMT symbols.
        """
        return self.vertex_symbols


class LIAColorerPySMT(ColorerPySMT):
    """
    Linear Integer Arithmetic (LIA) colorer for pySMT.

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
            list: A list of pySMT formulas representing the color constraints.
        """
        if self.color_constraints:
            return self.color_constraints
        
        for v in nodes:
            vertex = Symbol(f"v_{v}", INT)
            self.vertex_symbols[v] = vertex
            self.color_constraints.append(
                And(GE(vertex, Int(0)), LE(vertex, Int(self.num_colors - 1)))
            )
        
        return self.color_constraints


class NLAColorerPySMT(ColorerPySMT):
    """
    Non-Linear Arithmetic (NLA) colorer for pySMT.

    This class implements a graph coloring strategy using Non-Linear Arithmetic.
    The coloring constraint ensures that the product of the differences between
    each vertex value and the possible color values is zero.

    Formula: Forall vi in V: vi(vi-1)...(vi-(k-1)) = 0
    """

    def create_color_constraints(self, nodes):
        """
        Create color constraints using Non-Linear Arithmetic.

        Args:
            nodes: An iterable of graph nodes.

        Returns:
            list: A list of pySMT formulas representing the color constraints.
        """
        if self.color_constraints:
            return self.color_constraints
        
        for v in nodes:
            vertex = Symbol(f"v_{v}", INT)
            self.vertex_symbols[v] = vertex
            colorer_vi = []
            for i in range(self.num_colors):
                colorer_vi.append(Minus(vertex, Int(i)))
            self.color_constraints.append(Equals(Times(colorer_vi), Int(0)))
        return self.color_constraints


class ArrayUFColorerPySMT(ColorerPySMT):
    """
    Array with Uninterpreted Functions (ArrayUF) colorer for pySMT.

    This class implements a graph coloring strategy using Arrays with Uninterpreted Functions.
    It creates distinct color symbols and uses array operations to assign these colors to vertices.

    Formula: For each v in V:
             A_0 = array
             A_1 = A_0[i_1 <- c_1]
             ...
             A_k = A_(k-1)[i_k <- c_k]
             v = A_k[i_1]
    """

    def __init__(self, num_colors):
        """
        Initialize the ArrayUFColorerPySMT instance.

        Args:
            num_colors (int): The number of colors to use for graph coloring.
        """
        super().__init__(num_colors)
        self.color_symbols = {}

    def get_color_symbols(self):
        """
        Get the dictionary of color symbols.

        Returns:
            dict: A dictionary mapping color identifiers to their corresponding pySMT symbols.
        """
        return self.color_symbols

    def create_color_constraints(self, nodes):
        """
        Create color constraints using Arrays with Uninterpreted Functions.

        Args:
            nodes: An iterable of graph nodes.

        Returns:
            list: A list of pySMT formulas representing the color constraints.
        """
        if self.color_constraints:
            return self.color_constraints

        IndexType = Type("IndexType")
        ElementType = Type("ElementType")
 
        # Create color symbols
        for i in range(1, self.num_colors+1):
            self.color_symbols[f"c_{i}"] = Symbol(f"c_{i}", ElementType)

        # Ensure all colors are different
        for i in range(1, self.num_colors+1):
            for j in range(i+1, self.num_colors+1):
                self.color_constraints.append(
                    Not(Equals(self.color_symbols[f"c_{i}"], self.color_symbols[f"c_{j}"]))
                )

        for v in nodes:
            vertex = Symbol(f"v_{v}", ElementType)
            self.vertex_symbols[v] = vertex

            ass_vi = []
            arr1 = Symbol(f"arr0_v{v}", ArrayType(IndexType, ElementType))
            
            i1 = Symbol(f"i1_v{v}", IndexType)
            prev_arr = Symbol(f"arr1_v{v}", ArrayType(IndexType, ElementType))
            ass_vi.append(Equals(prev_arr, Store(arr1, i1, self.color_symbols[f"c_{1}"])))
          
            for i in range(2, self.num_colors+1):
                cur_i  = Symbol(f"i{i}_v{v}", IndexType)
                cur_arr = Symbol(f"arr{i}_v{v}", ArrayType(IndexType, ElementType))
                ass_vi.append(
                    Equals(
                        cur_arr, 
                        Store(prev_arr, cur_i, self.color_symbols[f"c_{i}"])))
                prev_arr = cur_arr 

            ass_vi.append(Equals(vertex, Select(prev_arr, i1)))
            self.color_constraints.extend(ass_vi)
        return self.color_constraints


class ArrayINTColorerPySMT(ColorerPySMT):
    """
    Array with Integer (ArrayINT) colorer for pySMT.

    This class implements a graph coloring strategy using Arrays with Integers.
    The coloring constraint uses a series of array operations to assign colors to vertices.

    Formula: For each v in V:
             A_0 = array
             A_1 = A_0[i_1 <- 0]
             ...
             A_k = A_(k-1)[i_k <- k-1]
             v = A_k[i_1]
    """

    def create_color_constraints(self, nodes):
        """
        Create color constraints using Arrays with Integers.

        Args:
            nodes: An iterable of graph nodes.

        Returns:
            list: A list of pySMT formulas representing the color constraints.
        """
        if self.color_constraints:
            return self.color_constraints
    
        for v in nodes:
            vertex = Symbol(f"v_{v}", INT)
            self.vertex_symbols[v] = vertex

            ass_vi = []
            arr1 = Symbol(f"arr0_v{v}", ArrayType(INT, INT))
            
            i1 = Symbol(f"i1_v{v}", INT)
            prev_arr = Symbol(f"arr1_v{v}", ArrayType(INT, INT))
            ass_vi.append(Equals(prev_arr, Store(arr1, i1, Int(1))))
          
            for i in range(2, self.num_colors + 1):
                cur_i  = Symbol(f"i{i}_v{v}", INT)
                cur_arr = Symbol(f"arr{i}_v{v}", ArrayType(INT, INT))
                ass_vi.append(Equals(cur_arr, Store(prev_arr, cur_i, Int(i))))
                prev_arr = cur_arr 

            ass_vi.append(Equals(vertex, Select(prev_arr, i1)))

            self.color_constraints.extend(ass_vi)
        return self.color_constraints


class ArrayBVColorerPySMT(ColorerPySMT):
    """
    Array with Bit-Vector (ArrayBV) colorer for pySMT.

    This class implements a graph coloring strategy using Arrays with Bit-Vectors.
    The coloring constraint uses a series of array operations with bit-vectors to assign colors to vertices.

    Formula: For each v in V:
             A_0 = array
             A_1 = A_0[i_1 <- 0]
             ...
             A_k = A_(k-1)[i_k <- k-1]
             v = A_k[i_1]
    """

    def create_color_constraints(self, nodes):
        """
        Create color constraints using Arrays with Bit-Vectors.

        Args:
            nodes: An iterable of graph nodes.

        Returns:
            list: A list of pySMT formulas representing the color constraints.
        """
        if self.color_constraints:
            return self.color_constraints
    
        num_bits = math.ceil(math.log2(self.num_colors))

        for v in nodes:
            vertex = Symbol(f"v_{v}", BVType(num_bits))
            self.vertex_symbols[v] = vertex

            ass_vi = []
            arr1 = Symbol(f"arr0_v{v}", ArrayType(BVType(num_bits), BVType(num_bits)))
            
            i1 = Symbol(f"i1_v{v}", BVType(num_bits))
            prev_arr = Symbol(f"arr1_v{v}", ArrayType(BVType(num_bits), BVType(num_bits)))
            ass_vi.append(Equals(prev_arr, Store(arr1, i1, BV(0, num_bits))))
          
            for i in range(2, self.num_colors + 1):
                cur_i  = Symbol(f"i{i}_v{v}", BVType(num_bits))
                cur_arr = Symbol(f"arr{i}_v{v}", ArrayType(BVType(num_bits), BVType(num_bits)))
                ass_vi.append(Equals(cur_arr, Store(prev_arr, cur_i, BV(i-1, num_bits))))
                prev_arr = cur_arr 

            ass_vi.append(Equals(vertex, Select(prev_arr, i1)))

            self.color_constraints.extend(ass_vi)
        return self.color_constraints


class BVColorerPySMT(ColorerPySMT):
    """
    Bit-Vector (BV) colorer for pySMT.

    This class implements a graph coloring strategy using Bit-Vectors.
    It's designed to work only when the number of colors is a power of 2.

    Formula:
        If k = 2^m, where k is the number of colors,
        then v is a bit vector with length m for each vertex.

    Note: This colorer only works when the number of colors is a power of 2.
    """

    def __init__(self, num_colors):
        """
        Initialize the BVColorerPySMT instance.

        Args:
            num_colors (int): The number of colors to use for graph coloring. Must be a power of 2.
        """
        condition = (num_colors <= 0) or (num_colors & (num_colors - 1)) != 0
        if condition:
            self.object = None
        else:
            super().__init__(num_colors)
    
    def create_color_constraints(self, nodes):
        """
        Create color constraints using Bit-Vectors. Check formula for details

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

        for v in nodes:
            vertex = Symbol(f"v_{v}", BVType(bv_length))
            self.vertex_symbols[v] = vertex
        
        return []