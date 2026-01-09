#This is from stackoverflow: https://stackoverflow.com/questions/4592162/python-exception-handling
import logging
logging.basicConfig(level=logging.DEBUG)
logging.debug('This message should go to the log file')

import math
import numpy as np
from typing import Optional, Union
import time


class TSP:
    def __init__(self, ops: Optional[str], filename: Optional[str], single: Optional[bool] = None):
        if(single is None or single is False):
            self.__size = None
            self.__ops = ops
            self.__coords = None            #This will be type of class np.ndarray
            self.__distances = None         #This will be type of class np.ndarray
            self.__setup(filename)
            self.__permutation = None
            self.__setRandomPermutation()
            self.__res = self.__localSearch()
        elif(single is not None and single is True):
            self.__size = None
            self.__ops = ops
            self.__coords = None            #This will be type of class np.ndarray
            self.__distances = None         #This will be type of class np.ndarray
            self.__setup(filename)
            self.__permutation = None
            self.__setRandomPermutation()

    def _getResult(self) -> np.ndarray:
        if isinstance(self.__res, np.ndarray):
            return self.__res
        else:
            return np.array(self.__res)
    
    def _getPerm(self) -> np.ndarray:
        if self.__permutation is None:
            return np.array([])
        return self.__permutation
    
    def getRoute(self) -> Union[np.ndarray, list[int]]:
        """
        returns a route that is a local optimum found by our local search algorithm based on the specified operation, `ops`.
        """
        return self.__res[0]
    
    def getTourLength(self) -> int:
        if isinstance(self.__res, np.ndarray):
            return self._np_tour_length(self.__res)
        return self.__res[1]
    
    def __localSearch(self) -> tuple[np.ndarray, int]:
        try:
            if(self.__ops is None): raise Exception('Empty operation value')
            if self.__ops == "jump":
                print("Execute Jump.")
                return self.__jump()
            # elif self.__ops == "2-opt":
            #     print("Execute 2-opt.")
            #     return self.__twoOpt(None)
            # elif self.__ops == "exchange":
            #     print("Execute exchange")
            #     return self.__exchange()
            raise Exception('Invalid operation')
        except Exception as e:
            logging.exception(e)
            # Return a default value of the correct type
            if self.__permutation is not None:
                return np.copy(self.__permutation), -1
            else:
                return np.array([]), -1 

    def __setup(self, filename: Optional[str]):
        self.__setfile(filename)
        self.__setdist()

    def __setfile(self, filename: Optional[str]):
        try:
            if(filename is None): raise Exception('Empty filename')
            # Reading the files from the data folder.
            path = "data/" + filename
            with open(path,'r') as file:
                lines = file.readlines()
            
            # Extract the size of the TSP space.
            numbers = []
            for char in filename:
                if char.isdigit():
                    numbers.append(char)
            # Combine list of char number into a single number 
            self.__size = int(''.join(map(str, numbers)))
            
            if(self.__size is None): raise Exception('Uninitialised city size')
            self.__coords = np.zeros((self.__size, 2), dtype = float)
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
                        self.__coords[index] = np.array([x,y])
                        index += 1 
        except Exception as e:
            logging.exception(e)

    def __setdist(self):
        # Init distances
        if self.__size is None:
            raise Exception('Uninitialised city size')
        if self.__coords is None:
            raise Exception('Uninitialised coordinates')
        self.__distances = np.zeros((self.__size, self.__size), dtype = int) # n x n matrix of distance with row-major style
        # Loop until n - 1 for n as number of coordinations, because we are calculating distance in pair.
        for i in range(self.__size):
            for j in range(self.__size):
                # Getting difference between x1 and x2 of vector 1 and 2, so forth until coordination of n
                dx = self.__coords[j][0] - self.__coords[i][0] 
                # Getting difference between y1 and y2 of vector 1 and 2, so forth until coordination of n
                dy = self.__coords[j][1] - self.__coords[i][1]
                # Euclidean length, rounded to int (Liam said)
                self.__distances[i][j] = int(math.sqrt(dx ** 2 + dy ** 2))

    def __setRandomPermutation(self):
        # Get the size of the space
        n = self.__size
        if n is None:
            raise Exception('Uninitialised city size')
        # Represent the cities as integers from 0 to n-1
        self.__permutation = np.arange(n) # generates a permutation from 0 to n-1
        # Shuffle the linear order of the permutation
        np.random.shuffle(self.__permutation)

    def _np_tour_length(self, permutation: np.ndarray) -> int: 
        #init the length to 0 as a placeholder
        if self.__distances is None:
            raise ValueError("Distances are not initialized.")
        if self.__size is None:
            raise ValueError("Size is not initialized.")
        distances : np.ndarray = np.array([])
        # if i is None and j is None:
        # create a closed loop by appending the first city to the end 
        closed_loop_tour = np.append(permutation, permutation[0])
        # advanced indexing to get all distances in a single, vectorized step 
        distances = self.__distances[closed_loop_tour[:-1], closed_loop_tour[1:]]
        distance = int(np.sum(distances))
        return distance 
    
    
    # change the following method to take in a numpy list for better efficiency.
    def _list_tour_length(self, permutation: list[int]) -> int:
        if self.__distances is None:
            raise ValueError("Distances are not initialized.")
        if self.__size is None:
            raise ValueError("Size is not initialized.")
        #init the length to 0 as a placeholder
        length = 0
        row = permutation[0]     # First city
        col = permutation[-1]    # Last city
        # Calculate the distance between the first and last city, this will close the cycle.
        length = self.__distances[row][col]
        # Calculate the length from city to city.
        for i in range(self.__size - 1):
            length += self.__distances[permutation[i]][permutation[i+1]]
        return length



    def __jump(self) -> tuple[np.ndarray, int]:
        """
        Performs a local search based on the jump/relocation operation, 
        using a first-improvement strategy and "insert-after" logic.
        """
        if self.__permutation is None:
            raise ValueError("Permutation is not initialized.")
        
        current_route = np.copy(self.__permutation)
        n = self.__size
        if n is None or self.__distances is None:
            raise ValueError("Size or distances are not initialized.")
        current_tour_length = self._np_tour_length(current_route)
        
        improved = True
        bound = 0 
        max_iteration = 1300 
        while improved and bound < max_iteration:
            improved = False
            for i in range(n):  # Index of the city to move
                for j in range(n):  # Index of the city to insert AFTER
                    
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
                    len_removed = (self.__distances[c_i_prev, c_i] + 
                                self.__distances[c_i, c_i_next] + 
                                self.__distances[c_j, c_j_next])
                    
                    len_added = (self.__distances[c_i_prev, c_i_next] + # Bridge gap at i
                                self.__distances[c_j, c_i] +           # Connect c_j to c_i
                                self.__distances[c_i, c_j_next])      # Connect c_i to c_j_next
                    delta = len_added - len_removed
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
            
        return current_route, int(current_tour_length)



    # ===============================================================================================================================

    def __twoOpt(self, permutation: Optional[np.ndarray]) -> np.ndarray: 
        try:
            # 1. SETUP: Use class's permutation or a provided one
            if permutation is None:
                if self.__permutation is None:
                    raise ValueError("Permutation is not initialized.")
                current_route = np.copy(self.__permutation)
            else:
                current_route = np.copy(permutation)
            
            n = self.__size
            if n is None or self.__distances is None:
                raise ValueError("Size or distances are not initialized.")
            # 2. CACHE INITIAL LENGTH: Calculate the full tour length only once at the start.
            current_tour_length = self._np_tour_length(current_route)
            
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
                        len_removed = self.__distances[c_i, c_i_plus_1] + self.__distances[c_j, c_j_plus_1]
                        # Cost of edges to be added
                        len_added = self.__distances[c_i, c_j] + self.__distances[c_i_plus_1, c_j_plus_1]
                        # Calculate the change in tour length
                        delta = len_added - len_removed
                        
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
            return current_route
        except Exception as e:
            logging.exception(e)
            # Always return a valid np.ndarray, even on exception
            if self.__permutation is not None:
                return np.copy(self.__permutation)
            else:
                return np.array([])




    def __exchange(self) -> np.ndarray:
        if self.__permutation is None:
            raise ValueError("Permutation is not initialized.")
        current_route = np.copy(self.__permutation)
        n = self.__size
        if n is None or self.__distances is None:
            raise ValueError("Size or distances are not initialized.")
        # Cache the initial tour length once before starting
        current_tour_length = self._np_tour_length(current_route)
        
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
                        len_removed = self.__distances[c_i_prev, c_i] + self.__distances[c_j, c_i_next]
                        len_added = self.__distances[c_i_prev, c_j] + self.__distances[c_i, c_i_next]
                        delta = len_added - len_removed
                    else:
                        # Non-adjacent case
                        c_j_prev = current_route[(j - 1 + n) % n]
                        c_j_next = current_route[(j + 1) % n]
                        
                        len_removed = (self.__distances[c_i_prev, c_i] + self.__distances[c_i, c_i_next] +
                                    self.__distances[c_j_prev, c_j] + self.__distances[c_j, c_j_next])
                        
                        len_added = (self.__distances[c_i_prev, c_j] + self.__distances[c_j, c_i_next] +
                                    self.__distances[c_j_prev, c_i] + self.__distances[c_i, c_j_next])
                        
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
        
        return current_route





if __name__ == '__main__':
    ops: str = "jump"
    # ops: str = "2-opt"
    # ops: str = "exchange"
    # filename: str = "dummy6.tsp"
    filename: str = "eil51.tsp" # 378032
    single = None 
    start_time = time.perf_counter()
    tsp = TSP(ops=ops, filename=filename, single=single)
    initial_perm = tsp._getPerm()
    initial_tour_length = tsp._np_tour_length(initial_perm)
    print(f"Initial permutation length = {initial_tour_length}")
    # set timer and find elapsed time 

    local_opt_route, local_opt_tour_length = tsp._TSP__localSearch() # pyright: ignore[reportAttributeAccessIssue]
    
    end_time = time.perf_counter()

    # local_opt_route = tsp.getRoute()
    # local_opt_tour_length = tsp.getTourLength()
    print(f"Local optimum route length = {local_opt_tour_length}")
    

    improvement_percentage = abs(local_opt_tour_length - initial_tour_length) / initial_tour_length * 100
    print(f"Improvement percentage: {improvement_percentage:.2f}%")
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.4f} seconds")


