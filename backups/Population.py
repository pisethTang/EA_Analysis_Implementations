from Individual import Individual, np, Optional, logging

class Population:
    """
    Represents a population which is a set of individuals.
    """
    
    def __init__(self, size: int, individual: Optional[np.ndarray] = None, individual_size: Optional[int] = None, filename: Optional[str] = None):
        """
        Initialize a Population.
        
        Args:
            size: Number of individuals in the population
            individual_size: Size of each individual (number of cities)
        """
        self.__i_size = None
        self.__p_size = None
        self.__population = None
        self.__fitness_flag = None
        if(filename is None): 
            self.__fitness_flag = False
            try:
                if(individual is None):
                    # Set the population size
                    self.__p_size = size

                    # Checking and setting the individual size
                    if(individual_size is None): raise Exception('Empty individual size')
                    self.__i_size = individual_size
                    
                    # Create population with random individuals (we can change this later ...)
                    self.__population = np.zeros(self.__p_size, dtype = Individual)
                    for k in range(self.__p_size):
                        i = Individual(self.__i_size, None, True)
                        # Make sure the permutation is type array
                        if(type(i) is not Individual): raise TypeError("Wrong individual permutation structure type.")
                        self.__population[k] = i
                # Provided a single individual as a seed
                elif(individual is not None):
                    # Checking all the possible execeptions
                    if(individual_size is not None and individual_size == individual.size): self.__i_size = individual_size
                    elif(individual_size is not None and individual_size != individual.size): raise Exception('Input size is not same as individual size.')
                    elif(type(individual) is not np.ndarray): raise Exception('Invalid permutation type')

                    # Set the size according to the 
                    self.__i_size = individual.size
                    self.__p_size = size 
                    i = Individual(self.__i_size, individual)

                    # Create population with random individuals (we can change this later ...)
                    self.__population = np.zeros(self.__p_size, dtype = Individual)
                    self.__population[0] = i
                    for k in range(1, self.__p_size):
                        m = Individual(self.__i_size, i.getCopyPerm(), True)
                        self.__population[k] = m
            except Exception as e:
                logging.exception(e)
        else:
            try:
                self.__fitness_flag = True
                self.__p_size = size
                self.__population = np.zeros(self.__p_size, dtype = np.ndarray)
                self.__ind = Individual(None, None, None, filename)

                for i in range(self.__p_size):
                    x = self.__ind.getCopyPerm()
                    np.random.shuffle(x)
                    self.__population[i] = x

            except Exception as e:
                logging.exception(e) 
    
    def getIndividual(self) -> Individual:
        return self.__ind

    def getPopulationSize(self) -> int:
        if self.__p_size is None:
            return -1
        return self.__p_size
    
    def getPopulation(self) -> np.ndarray:
        if self.__population is None: 
            return np.array([-1])
        return self.__population

    def show(self):
        if self.__population is None:
            raise Exception("Population is undefined.")
        if self.__p_size is None:
            raise Exception("Population size is undefined.")
        if(self.__fitness_flag is False):
            for i in range(self.__p_size):
                print(self.__population[i].getCopyPerm())
        else:
           for i in range(self.__p_size):
               print(self.__population[i])
    
    def evaluate_population(self) -> Optional[np.ndarray]:
        """
        Evaluate the quality of all solutions with respect to the given problem.
        
        Args:
            problem_instance: TSP instance for fitness evaluation
            
        Returns:
            Numpy array of fitness values for all individuals
        """
        if(self.__fitness_flag is False):
            raise Exception("Population was not initialized with fitness evaluation capability.")
        if self.__p_size is None or self.__population is None:
            raise ValueError("Population is not properly initialized.")
        # More numpy-efficient: pre-allocate array
        fitness_values = np.zeros(self.__p_size, dtype=int)
        for i, individual in enumerate(self.__population):
            fitness_values[i] = self.__ind.evaluate_fitness(individual)
        return fitness_values
    
    def get_individual(self, index: int) -> np.ndarray:
        """
        Get individual at specified index.
        
        Args:
            index: Index of individual to retrieve
            
        Returns:
            Individual at the specified index
        """
        if self.__population is None:
            raise ValueError("Population is not initialized.")
        return self.__population[index]
    
    def replace_population(self, new_population: np.ndarray):
        self.__population = new_population
        
    # Selection method
    def selection(self, selection_size: int, operation: str) -> Optional[np.ndarray]:
        try:
            match operation:
                case "fitness":
                    return self.__fps(selection_size)
                case "tournament":
                    return self.__tournament(selection_size, 10)
                case "elitism":
                    return self.__elitism(selection_size)
                case _:
                    raise ValueError("Unkown Selection Method")
        except Exception as e:
            logging.exception(e)

    def __fps(self, selection_size: int) -> np.ndarray:
        """
        Perform fitness proportion selection using linear windowing

        Args:
            num__to_select: number of individuals to select from the population

        """
        if self.__population is None or self.__p_size is None:
            raise ValueError("Population is not properly initialized.")
        # get all fitness values from the population
        fitnesses = self.evaluate_population()

        if fitnesses is None or len(fitnesses) == 0:
            return np.array([])
        
        # find the worst fitness (largest number) in the current population
        worst = np.max(fitnesses)

        # calculate the scaled ftnesses using windowing method
        scaled_fitnesses = worst - fitnesses + 1e-6

        # calculate sum of scaled fitnesses
        total_scaled_fitnesses = np.sum(scaled_fitnesses)

        # edge case when sum is 0
        if total_scaled_fitnesses == 0:
            probabilities = np.full(self.__p_size, 1.0/self.__p_size) # every have same prob
        else:
            # calculate selection probabilities
            probabilities = scaled_fitnesses / total_scaled_fitnesses

        # select individuals based on the probabilities
        selected_indices = np.random.choice(self.__p_size, size=selection_size, p=probabilities, replace=True) # can choose same number

        # get the actual individuals from indices
        selected_individuals = self.__population[selected_indices]

        return selected_individuals
    
    def __elitism(self, size: int) -> np.ndarray: 
        """
        Applies selection of fitest permutations using the method of elitism. 
        
        Args:
            
        Returns:
            elites: 
                    elites[0] is the fittest of the last generation, and 
        """
        if self.__population is None or self.__p_size is None:
            raise ValueError("Population is not properly initialized.")
        # # Find the fittest individual, then use them to initialise next generation
        # elite = self.get_individual(0)

        # for i in range(1, self.__p_size):
        #     if self.__ind.evaluate_fitness(elite) > self.__ind.evaluate_fitness(self.get_individual(i)):
        #         elite = self.get_individual(i) 

        # # Return the selected individuals 
        if size <= 0:
            return np.array([], dtype=object)

        # 1. Evaluate the fitness of the entire population.
        fitness_values = self.evaluate_population()

        # Check if fitness_values is None
        if fitness_values is None:
            return np.array([], dtype=object)

        # 2. Get the indices of the individuals with the lowest fitness values.
        # np.argsort returns the indices that would sort an array.
        sorted_indices = np.argsort(fitness_values)

        # 3. Select the top 'size' fittest individuals using the sorted indices.
        # This ensures a 2D array is always returned, even for size=1.
        elite_indices = sorted_indices[:size]
        elites = self.__population[elite_indices]

        return elites
    
    def __tournament(self, selection_size: int, k_size: int) -> np.ndarray:
        if self.__population is None or self.__p_size is None:
            raise ValueError("Population is not properly initialized.")
        # selected = np.full(selection_size, -1, dtype = int)
        selected =[]
        fitnesses = self.evaluate_population()
        if fitnesses is None:
            raise ValueError("Fitness evaluation returned None.")
        for i in range(selection_size):
            competitors_idx = np.random.choice(self.__p_size, k_size, replace = False)
            best_idx = min(competitors_idx, key = lambda idx: fitnesses[idx])
            # selected[i](self.__population[best_idx])
            selected.append(self.__population[best_idx])
        return np.array(selected)
