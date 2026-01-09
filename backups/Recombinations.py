import numpy as np
import random 
import copy 
from typing import Tuple, Optional

#This is from stackoverflow: https://stackoverflow.com/questions/4592162/python-exception-handling
import logging
logging.basicConfig(level=logging.DEBUG)
logging.debug('This message should go to the log file')


class Recombinations:
    # crossover methods
    def crossover(self, crossover_type: str, parent1: np.ndarray, parent2: np.ndarray, size: int) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        try:
            match crossover_type:
                case "order":
                    return self.order(parent1, parent2, size)
                case "pmx":
                    return self.pmx(parent1, parent2, size)
                case "cycle":
                    return self.cycle(parent1, parent2)
                case "edge":
                    offspring = self.edge(parent1, parent2, size)
                    return offspring, self.edge(parent2, parent1, size)
                case _:
                    raise ValueError("Invalid recombination")
        except Exception as e:
            logging.exception(e)


    @staticmethod
    def cycle(first_parent: np.ndarray, second_parent: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Performs Cycle Crossover (CX) on two parent permutations.
        Args:
            first_parent: First parent permutation as numpy array
            second_parent: Second parent permutation as numpy array
            
        Returns:
            tuple: (first_child, second_child) - two offspring permutations
            
        Raises:
            ValueError: If parents have different sizes or contain invalid permutations
        """

        # Validate inputs
        if len(first_parent) != len(second_parent):
            raise ValueError("Parents must have the same length")
        
        if len(first_parent) == 0:
            raise ValueError("Parents cannot be empty")
            
        # Check if parents are valid permutations (contain same elements)
        if not (set(first_parent) == set(second_parent)):
            raise ValueError("Parents must contain the same set of elements")
        
        n = len(first_parent)
        
        # Initialize children with -1
        first_child = np.full(n, -1, dtype=first_parent.dtype)
        second_child = np.full(n, -1, dtype=second_parent.dtype)
        
        # Track which positions have been assigned
        visited = np.zeros(n, dtype=bool)  # Initialize with False values
        
        # Keep track of which cycle we're on (for alternating between parents)
        cycle_number = 0
        
        # Continue until all positions are filled
        while not np.all(visited):
            # Find the first unvisited position to start a new cycle
            start_pos = np.where(~visited)[0][0]
            current_pos = start_pos
            cycle_positions = []
            
            # Trace the cycle
            while True:
                # add current position to the cycle
                cycle_positions.append(current_pos)
                visited[current_pos] = True
                
                # get the value at current position in second_parent
                value_in_p2 = second_parent[current_pos]
                
                # Find where this value appears in first_parent
                next_pos = np.where(first_parent == value_in_p2)[0][0]
                
                # If we've returned to the start, cycle is complete
                if next_pos == start_pos:
                    break
                    
                current_pos = next_pos
                
            # Now we have a complete cycle in cycle_positions
            # Assign values to children based on cycle number
            # Even cycles (0, 2, 4, ...): first_child takes from first_parent, second_child takes from second_parent
            # Odd cycles (1, 3, 5, ...): first_child takes from second_parent, second_child takes from first_parent
            if cycle_number % 2 == 0:
                # even cycle
                for pos in cycle_positions:
                    first_child[pos] = first_parent[pos]
                    second_child[pos] = second_parent[pos]
            else:
                # odd cycle
                for pos in cycle_positions:
                    first_child[pos] = second_parent[pos]
                    second_child[pos] = first_parent[pos]
            
            cycle_number += 1
        
        return first_child, second_child

    @staticmethod
    def order(first_parent: np.ndarray, second_parent: np.ndarray, size: int) -> Tuple[np.ndarray, np.ndarray]:
        """
            The Basic Order Crossover

            Args:
                first_parent (np.ndarray): The first parent to be XOed.
                second_parent (np.ndarray): The second parent to be XOed.
                size (int): Size of the parent, pass this inorder to have quicker calculation.

            Returns:
                Tuple: (first_child, second_child), permutations of two chilren after XO.
        """

        # Initilise the two children with all -1 as a null value
        # Since -1 won't be a value of city represent nor distance representation so this is safe
        first_child = np.full(size, -1, dtype = int)
        second_child = np.full(size, -1, dtype = int)

        #=======================For the first child======================================#
        # Start and end of the arbitary (copied) segment
        start = 0
        end = 0

        # Make sure end-index will be after start-index
        while start >= end:
            start = random.randint(0,size - 1)          # Getting an integer from the range 0 to permutation size - 1
            end = random.randint(start, size - 1)       # Getting an integer from the range of start to permutation size - 1
        
        # Storing the copied segment to be used for validation later
        cut = np.empty(end + 1 - start, dtype = int)

        # Deepcopy the arbitary segment into the offspring
        first_child[start: end + 1] = copy.deepcopy(first_parent[start : end + 1])
        # Store the segment
        cut = np.copy(copy.deepcopy(first_parent[start : end + 1]))

        # Use an independent child index, to have a more control behaviour
        child_index = end + 1
        if child_index == size: child_index = 0         # Make sure the index won't reach over the end of the permutation


        # The arrangement of starting from the outer-right of the segment to the outer-left of which is to follow the
        # order of the second (opposite) parent.

        # Start by looking from the outer-right of the segment
        for i in range(end + 1, size):
            # Make sure the value of the opposite parent won't be same as in the segment
            if(second_parent[i] not in cut):
                first_child[child_index] = second_parent[i]
                # Move the child-index to the next position inside the offspring
                child_index += 1
                if child_index == size: child_index = 0     # Reset it if it reach the end of the permutation

        # Second, start by looking at the outer-left of the segment
        # By the same procedure as before
        for i in range(0, end + 1):
            if(second_parent[i] not in cut):
                first_child[child_index] = second_parent[i]
                child_index += 1
                if child_index == size: child_index = 0

        #=======================For the second child======================================#
        # The second child is analogously created with the common logic.
        start = 0
        end = 0

        while start >= end:
            start = random.randint(0,size - 1)
            end = random.randint(start, size - 1)
        
        cut = np.empty(end + 1 - start, dtype = int)
        temp = []

        second_child[start: end + 1] = copy.deepcopy(second_parent[start : end + 1])
        cut = np.copy(copy.deepcopy(second_parent[start : end + 1]))

        child_index = end + 1
        if child_index == size: child_index = 0

        for i in range(end + 1, size):
            if(first_parent[i] not in cut):
                second_child[child_index] = first_parent[i]
                child_index += 1
                if child_index == size: child_index = 0

        for i in range(0, end + 1):
            if(first_parent[i] not in cut):
                second_child[child_index] = first_parent[i]
                child_index += 1
                if child_index == size: child_index = 0

        return first_child, second_child

    @staticmethod
    def pmx(parent1: np.ndarray, parent2: np.ndarray, size: int) -> Tuple[np.ndarray, np.ndarray]:
        """
            The PM (Partial Mapping) Crossover -- PMX

            Args:
                first_parent (np.ndarray): The first parent to be XOed.
                second_parent (np.ndarray): The second parent to be XOed.
                size (int): Size of the parent, pass this inorder to have quicker calculation.

            Returns:
                Tuple: (first_child, second_child), permutations of two chilren after XO.
        """
        child_1 = np.full(size, -1, dtype=parent1.dtype) # Use a placeholder
        child_2 = np.full(size, -1, dtype=parent1.dtype) # Use a placeholder

        # 1. Choose two unique random points and sort them
        points = np.random.choice(size, 2, replace=False)
        a, b = np.sort(points)

        # 2. Copy the segment from parent 1 to the child
        child_1[a : b + 1] = parent1[a : b + 1]

        # 3. For each value in the segment from parent 2...
        for i in range(a, b + 1):
            # If the value is not already in the child's copied segment...
            val_from_p2 = parent2[i]
            if val_from_p2 not in child_1[a : b + 1]:
                # Start the mapping chain
                current_val = parent1[i]
                
                # Follow the chain until an empty position is found
                while True:
                    # Find where the current value is in parent 2
                    pos = np.where(parent2 == current_val)[0][0]
                    # If that position in the child is outside the copied segment...
                    if not (a <= pos <= b):
                        # Place the original value from parent 2 there
                        child_1[pos] = val_from_p2
                        break
                    else:
                        # Otherwise, continue the chain
                        current_val = parent1[pos]
        
        # 4. Fill any remaining empty spots from parent 2
        for i in range(size):
            if child_1[i] == -1:
                child_1[i] = parent2[i]
        
        #==========================Child 2======================#
        # 1. Choose two unique random points and sort them
        points = np.random.choice(size, 2, replace=False)
        a, b = np.sort(points)

        # 2. Copy the segment from parent 1 to the child
        child_2[a : b + 1] = parent2[a : b + 1]

        for i in range(a, b + 1):
            val_from_p1 = parent1[i]
            if val_from_p1 not in child_2[a : b + 1]:
                current_val = parent2[i]
                
                while True:
                    pos = np.where(parent2 == current_val)[0][0]
                    if not (a <= pos <= b):
                        child_2[pos] = val_from_p1
                        break
                    else:
                        current_val = parent1[pos]
        
        for i in range(size):
            if child_2[i] == -1:
                child_2[i] = parent2[i]

                
        return child_1, child_2


    @staticmethod
    def edge(parent1: np.ndarray, parent2: np.ndarray, size: int) -> np.ndarray:
        """
        Apply edge recombination crossover operator to a given individual.  
        
        Args:
            parent1, parent2: Two permutations as the basis for the offspring
            
        Returns:
            offspring: An individual formed through the edge recombination of the 2 given permutations 
        """

        # Construct edge table as a dictionary 
        edge_table = {}
        par1 = parent1.copy()
        par2 = parent2.copy()
        
        for index, value in enumerate(par1):    # populate table with first parent's edges
            
            if (index == 0):
                edge_table.setdefault(value, list()).append(par1[size - 1]) # preceding city 
                edge_table[value].append(par1[index + 1]) # succeding city 
                continue 

            if (index == size - 1): 
                edge_table.setdefault(value, list()).append(par1[index - 1]) # preceding city 
                edge_table[value].append(par1[0]) # succeding city
                continue 

            # otherwise, if (0 < i < self.__size - 1): 
            edge_table.setdefault(value, list()).append(par1[index - 1]) # preceding city 
            edge_table[value].append(par1[index + 1]) # succeding city

        for index, value in enumerate(par2):    # populate table with second parent's edges
            
            if (index == 0):
                edge_table.setdefault(value, list()).append(par2[size - 1]) # preceding city 
                edge_table[value].append(par2[index + 1]) # succeding city 
                continue 

            if (index == size - 1): 
                edge_table.setdefault(value, list()).append(par2[index - 1]) # preceding city 
                edge_table[value].append(par2[0]) # succeding city
                continue 

            # Otherwise, if (0 < i < self.__size - 1): 
            edge_table.setdefault(value, list()).append(par2[index - 1]) # preceding city 
            edge_table[value].append(par2[index + 1]) # succeding city


        # Randomly select element to initialise offspring 
        offspring = np.zeros(size, dtype=int)
        curr = random.choice(par1)
        visited = [] # To assure all references to chosen elements are disregarded 

        # Examine list for current element to choose next element in offspring permutation.  
        for index, value in enumerate(par1):  

            offspring[index] = curr # add current element to offspring and visited elements/cities
            visited.append(curr)

            # Remove all references of current element from edge_table 
            for i, val in enumerate(par1):   
                if curr in edge_table[val]: edge_table[val].remove(curr)

            # Pick next element based on a common edge 
            for idx, val in enumerate(par1):  
                if val not in visited and edge_table[curr].count(val) > 1: 
                    curr = val 
                    break
            
            # If no new element is to be found by the above...
            if curr in visited : 
                
                # Pick element based on which has the shortest list of DISTINCT edges  
                next_elements = [n for n in edge_table[curr] if n not in visited]
                if len(next_elements) > 0 : 
                    curr = min(next_elements, key = lambda v: len(set(edge_table[v])))

                # In case list of current element is empty
                elif idx < size - 1: 
                    curr = random.choice([n for n in par1 if n not in visited]) 

        return offspring 
