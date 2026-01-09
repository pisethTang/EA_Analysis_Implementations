# utilities/TSPlib.py
import numpy as np
import math
from typing import Optional 
import logging

from dataclasses import dataclass




@dataclass 
class AlgorithmResult:
    """
    Standardizes return object for algorithms.
    """
    permutation: np.ndarray
    length: float 



class TSPInstance:
    """
    The 'Data Class'. It loads the file ONE time and creates the 
    distance matrix ONE time. All algorithms just look at this.
    """
    def __init__(self, filename: str):
        self.filename = filename
        self.size: int = 0
        self.coords: Optional[np.ndarray] = None
        self.distances: Optional[np.ndarray] = None
        self._setup(filename)

    def _setup(self, filename: str):
        self.__setfile(filename)
        self.__setdist()

    def __setfile(self, filename: str):
        try:
            if(filename is None or filename == ""): raise Exception('Empty filename')
            # Reading the files from the data folder.
            # path = "data/" + filename
            path = "../data/" + filename
            with open(path,'r') as file:
                lines = file.readlines()
            
            # Extract the size of the TSP space.
            numbers = []
            for char in filename:
                if char.isdigit():
                    numbers.append(char)
            # Combine list of char number into a single number 
            self.size = int(''.join(map(str, numbers)))
            
            if(self.size is None): raise Exception('Uninitialised city size')
            self.coords = np.zeros((self.size, 2), dtype=float)
            #The flag being used for starting section of the coordination section
            start = False        
            index = 0
            for line in lines:
                # Remove the leading and trailing spaces
                line = line.strip() 
                # Flag the starting section of the coordination
                if line == "NODE_COORD_SECTION":
                    start = True
                    continue
                # End of file
                elif line == "EOF":
                    break
                # Start the process of the coordination collection
                if start: 
                    seq_num = line.split()
                    if len(seq_num) == 3:
                        x, y = float(seq_num[1]), float(seq_num[2])
                        self.coords[index] = np.array([x, y])
                        index += 1 
        except Exception as e:
            logging.exception(e)
            raise

    def __setdist(self):
        # Init distances
        if self.size is None:
            raise Exception('Uninitialised city size')
        if self.coords is None:
            raise Exception('Uninitialised coordinates')
        self.distances = np.zeros((self.size, self.size), dtype=int) # n x n matrix of distance with row-major style
        # Loop until n - 1 for n as number of coordinations, because we are calculating distance in pair.
        for i in range(self.size):
            for j in range(self.size):
                # Getting difference between x1 and x2 of vector 1 and 2, so forth until coordination of n
                dx = self.coords[j][0] - self.coords[i][0] 
                # Getting difference between y1 and y2 of vector 1 and 2, so forth until coordination of n
                dy = self.coords[j][1] - self.coords[i][1]
                # Euclidean length, rounded to int (Liam said)
                self.distances[i][j] = int(math.sqrt(dx ** 2 + dy ** 2))

    # def __setRandomPermutation(self):
    #     # Get the size of the space
    #     n = self.__size
    #     if n is None:
    #         raise Exception('Uninitialised city size')
    #     # Represent the cities as integers from 0 to n-1
    #     self.__permutation = np.arange(n) # generates a permutation from 0 to n-1
    #     # Shuffle the linear order of the permutation
    #     np.random.shuffle(self.__permutation)


class FastLocalSearch:
    """
    The 'Physics Library'. It contains your O(1) math.
    It is static because it doesn't need to remember anything, 
    it just calculates improvements.
    """
    
    @staticmethod
    def np_tour_length(tsp_instance: TSPInstance, permutation: np.ndarray) -> int: 
        #init the length to 0 as a placeholder
        if tsp_instance.distances is None:
            raise ValueError("Distances are not initialized.")
        if tsp_instance.size is None:
            raise ValueError("Size is not initialized.")
        distances : np.ndarray = np.array([])
        # create a closed loop by appending the first city to the end 
        closed_loop_tour = np.append(permutation, permutation[0])
        # advanced indexing to get all distances in a single, vectorized step 
        distances = tsp_instance.distances[closed_loop_tour[:-1], closed_loop_tour[1:]]
        distance = int(np.sum(distances))
        return distance 
    
    @staticmethod
    def jump(instance: TSPInstance, permutation: np.ndarray) -> tuple[np.ndarray, int]:
        # Copy your O(1) jump logic here.
        # CRITICAL CHANGE: Instead of using 'self.__distances', 
        # use 'instance.distances'.
        if permutation is None:
            raise ValueError("Permutation is not initialized.")
        if instance.distances is None:
            raise ValueError("Distances are not initialized.")
        if instance.size is None:
            raise ValueError("Instance size is not initialized.")
        current_route: np.ndarray = np.copy(permutation)
        n: int = instance.size
        current_tour_length: int = FastLocalSearch.np_tour_length(instance, current_route)
        improved: bool = True
        bound: int = 0
        max_iterations = 1300

        while improved and bound < max_iterations:
            improved = False 
            for i in range(n):
                for j in range(n):
                    if i == j or abs(i - j) == n - 1: # Cannot move a city after itself
                        continue
                    # ============================ O(1) operations (exchange 3 edges at most)============================================
                    # --- Corrected Delta Calculation for "Insert-After" ---
                    c_i = current_route[i]
                    c_j = current_route[j]
                    
                    # 1. Neighbors of the city to be removed
                    c_i_prev = current_route[(i - 1 + n) % n]
                    c_i_next = current_route[(i + 1) % n]
                    
                    # 2. Neighbors at the insertion point. We break the edge AFTER c_j.
                    c_j_next = current_route[(j + 1) % n]
                    # This move is invalid if c_i is already c_j's neighbor.
                    if c_i == c_j_next or c_i_prev == c_j:
                        continue
                    
                    # 3. Calculate the change in length
                    len_removed = (instance.distances[c_i_prev, c_i] + 
                                instance.distances[c_i, c_i_next] + 
                                instance.distances[c_j, c_j_next])
                    
                    len_added = (instance.distances[c_i_prev, c_i_next] + # Bridge gap at i
                                instance.distances[c_j, c_i] +           # Connect c_j to c_i
                                instance.distances[c_i, c_j_next])      # Connect c_i to c_j_next
                    delta = int(len_added - len_removed)
                    if delta < 0:
                        # Found an improvement, apply the move
                        city_to_move = current_route[i]
                        temp_route = np.delete(current_route, i)
                        
                        # Find the new index of c_j after the deletion
                        # The logic is tricky, so a simple search is robust
                        new_j_idx = np.where(temp_route == c_j)[0][0]
                        
                        # insert after new_j_idx by index new_j_idx + 1
                        insert_pos = new_j_idx + 1
                        current_route = np.insert(temp_route, insert_pos, city_to_move)
                        # update tour length and restart search
                        current_tour_length += delta
                        improved = True
                        break
                    # ========================================================================
                if improved:
                    break
            bound += 1

        return current_route, current_tour_length

    @staticmethod
    def twoOpt(instance: TSPInstance, permutation: np.ndarray) -> tuple[np.ndarray, int]: 
        try:
            if instance is None:
                raise ValueError("TSP instance is not initialized.")
            if permutation is None:
                raise ValueError("Permutation is not initialized.")
            current_route = np.copy(permutation)
            
            n = instance.size
            if n is None or instance.distances is None:
                raise ValueError("Size or distances are not initialized.")
            # 2. CACHE INITIAL LENGTH: Calculate the full tour length only once at the start.
            current_tour_length:int = FastLocalSearch.np_tour_length(instance, current_route)
            
            improved = True
            bound = 0
            max_iteration = 1000
            while improved and bound < max_iteration:
                improved = False
                # Iterate over all distinct pairs of edges
                for i in range(n - 1):
                    for j in range(i + 2, n):
                        # Define the nodes involved in the potential swap
                        # Edge 1: (c_i -> c_i_plus_1)
                        # Edge 2: (c_j -> c_j_plus_1)
                        c_i = current_route[i]
                        c_i_plus_1 = current_route[i+1]
                        c_j = current_route[j]
                        # Handle the wrap-around case for the last edge of the tour
                        c_j_plus_1 = current_route[(j + 1) % n]
                        # 3. DELTA CALCULATION (O(1) operation)
                        # Cost of edges to be removed
                        len_removed = instance.distances[c_i, c_i_plus_1] + instance.distances[c_j, c_j_plus_1]
                        # Cost of edges to be added
                        len_added = instance.distances[c_i, c_j] + instance.distances[c_i_plus_1, c_j_plus_1]
                        # Calculate the change in tour length
                        delta = int(len_added - len_removed)
                        
                        if delta < 0:
                            # 4. APPLY THE CHANGE: Reverse the segment from i+1 to j
                            current_route[i+1 : j+1] = np.flip(current_route[i+1 : j+1])
                            
                            # 5. UPDATE CACHED LENGTH: Update the length using the delta
                            current_tour_length += delta
                            
                            improved = True
                            break
                    if improved:
                        break
                    
                bound += 1
            return current_route, current_tour_length
        except Exception as e:
            logging.exception(e)
            # Always return a valid np.ndarray, even on exception
            if permutation is not None:
                return np.copy(permutation), current_tour_length
            else:
                return np.array([]), 0



    @staticmethod
    def exchange(instance: TSPInstance, permutation: np.ndarray) -> tuple[np.ndarray, int]:
        if permutation is None:
            raise ValueError("Permutation is not initialized.")
        current_route = np.copy(permutation)
        n = instance.size
        if n is None or instance.distances is None:
            raise ValueError("Size or distances are not initialized.")
        # Cache the initial tour length once before starting
        current_tour_length = FastLocalSearch.np_tour_length(instance, current_route)
        
        improved = True
        bound = 0 
        max_iterations = 1000
        while improved and bound < max_iterations:
            improved = False
            # Use more efficient loops to check each pair (i, j) once
            for i in range(n):
                for j in range(i + 1, n):
                    
                    c_i = current_route[i]
                    c_j = current_route[j]
                    
                    # Get neighboring cities, using modulo to handle tour ends
                    c_i_prev = current_route[(i - 1 + n) % n]
                    c_i_next = current_route[(i + 1) % n]
                    
                    # Check if the swap is for adjacent cities
                    if j == i + 1:
                        # Adjacent case: ... c_i_prev -> c_i -> c_j -> c_i_next (which is c_j_next)...
                        len_removed = instance.distances[c_i_prev, c_i] + instance.distances[c_j, c_i_next]
                        len_added = instance.distances[c_i_prev, c_j] + instance.distances[c_i, c_i_next]
                        delta = len_added - len_removed
                    else:
                        # Non-adjacent case
                        c_j_prev = current_route[(j - 1 + n) % n]
                        c_j_next = current_route[(j + 1) % n]
                        
                        len_removed = (instance.distances[c_i_prev, c_i] + instance.distances[c_i, c_i_next] +
                                    instance.distances[c_j_prev, c_j] + instance.distances[c_j, c_j_next])
                        
                        len_added = (instance.distances[c_i_prev, c_j] + instance.distances[c_j, c_i_next] +
                                    instance.distances[c_j_prev, c_i] + instance.distances[c_i, c_j_next])
                        
                        delta = len_added - len_removed
                    if delta < 0:
                        # Improvement found, apply the swap
                        current_route[i], current_route[j] = current_route[j], current_route[i]
                        print(f"Found improvement!")
                        # Update the cached tour length with the delta
                        current_tour_length += delta
                        improved = True
                        
                        # Restart search from the new, improved route
                        break
                if improved:
                    break
            bound += 1
        if current_route is None or current_tour_length is None:
            raise ValueError("Current route is not initialized.")
        return current_route, int(current_tour_length)



