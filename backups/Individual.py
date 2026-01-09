from TSPlib import np, TSP, Optional, logging

# Solution representation class.
class Individual(TSP):
    """
    Represents an individual solution for TSP as a permutation of cities.
    """
    
    def __init__(self, size: Optional[int], permutation: Optional[np.ndarray] = None, shuffle: Optional[bool] = None, filename: Optional[str] = None):
        """
        Initialize an Individual.
        Args:
            size: Number of cities in the TSP
            permutation: Optional predefined permutation as numpy array. If None, generates random solution
        """
        if(filename is None):
            self.__size = size
            if permutation is not None:
                self.__permutation = np.copy(permutation)
                if(shuffle is not None and shuffle is True): self.__randomise()
            else:
                self.__permutation = self.__generate_random_solution()
        else:
            # self.__operations = np.array(["jump", "2-opt", "exchange"])
            # op = np.random.choice(self.__operations)
            self.__data = TSP(None, filename, True)
            self.__permutation = self.__data._getPerm()

    def getCopyPerm(self) -> np.ndarray:
        return np.copy(self.__permutation)

    def getIndividualSize(self) -> int:
        return self.__permutation.size
    
    def show(self):
        print(self.__permutation)
    
    def evaluate_fitness(self, permutation: np.ndarray):
        """
        Evaluate the quality of this solution with respect to the given problem.
        Args:
            problem_instance: TSP instance with tour_length method
        Returns:
            Tour length (fitness value - lower is better)
        """
        # Convert numpy array to list for compatibility with existing TSP.tour_length method
        return self.__data._np_tour_length(permutation)

    def __randomise(self):
        np.random.shuffle(self.__permutation)
    
    def __generate_random_solution(self) -> np.ndarray:
        """
        Generate a random permutation (tour) solution in linear time and in constant space!
        """
        if self.__size is None:
            raise ValueError("Size must be defined to generate a random solution.")
        # Create array of cities (0 to size-1) and shuffle
        solution = np.arange(self.__size)
        np.random.shuffle(solution) 
        return solution
    
    ### Mutation Method 
    def mutation(self, permutation: np.ndarray, mutation_type: str):
        match mutation_type:
            case "inversion":
                return self.__inversion(permutation)
            case "swap":
                return self.__swap(permutation)
            case "insert":
                return self.__insert(permutation)
            case _:
                print("Unknown mutation type")
            
    def __inversion(self, permutation: np.ndarray) -> np.ndarray:
        """
        Perform inversion mutation operation on single individual
        """
        # choose 2 difference indices 
        i, j = np.sort(np.random.choice(len(permutation), 2, replace=False))

        # if adjacent edges
        if abs(i - j) < 2:
            return permutation
        
        # inversion 
        permutation[i:j+1] = permutation[i:j+1][::-1]

        return permutation
    
    def __insert(self, permutation: np.ndarray) -> np.ndarray:
        """
        Insert mutation perform similarly to jump
        """
        i, j = np.random.choice(len(permutation), 2, replace = False)
        perm = list(permutation)
        city = perm.pop(i)
        perm.insert(j, city)
        permutation = np.array(perm)

        return permutation

    def __swap(self, permutation: np.ndarray) -> np.ndarray: 
        """
        Apply swap mutation operator on a given individual. 
        """
        index1, index2 = np.random.choice(len(permutation), 2, replace=False) # Generates two unique random integers from a given range
        
        permutation[index1] , permutation[index2] = permutation[index2] , permutation[index1] 

        return permutation
