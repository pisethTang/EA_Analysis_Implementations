from Population import Population, Individual, np, logging, Optional
from Recombinations import Recombinations as rcb, Tuple
import copy
import random
from typing import List

class EvolutionaryAlgorithm:
    def __init__(self, population_size: int, filename: str, mutation: str, mutation_rate: float, crossover: str, parent_selection: str, 
                 population_selection: str, elite_size: int = 2):
        """
        Initialise the evolutionary algorithm / genetic algorithm

        Args:
            filename: the file name of the instance
            pop_size: population size (e.g: 50)
            crossover_type: name of the crossover method (e.g:pmx)
            mutation_type: name of the mutation method (e.g: inversion)
            selection_type: name of the selection method (e.g: fitness_proportion)
            mutation_rate: the probability of an individual mutating
            elitism_size: choose to keep how many elite individual (default = 1)
        """
        self.__pop_size = population_size
        self.__max_selection_size = int(self.__pop_size / 2)
        self.__min_selection_size = 2
        self.__crossover = crossover
        self.__mutation = mutation
        self.__parent_selection = parent_selection
        self.__population_selection = population_selection

        self.__elite_size = elite_size
        self.__mutation_rate = mutation_rate

        # Initialise the population by passing the tsp
        self.__filename = filename
        self.__population = Population(size=self.__pop_size, filename=filename)
        self.__recombination = rcb()

        # Since the selected parent population size is undeterministic, it is a waste of space to determine the child population to be as big as possible,
        # but it is worth it for the speed.
        self.__individual = self.__population.getIndividual()

        # Initialize best fitness with the fitness of the elite individual
        elite_perm = self.__population.selection(elite_size, "elitism")
        if elite_perm is not None and len(elite_perm) > 0:
            self.__best_fitness = self.__individual.evaluate_fitness(elite_perm[0])
        else:
            self.__best_fitness = float('inf')

    def __parent_selection_method(self, type: str) -> np.ndarray:
        n = random.randint(self.__min_selection_size, self.__max_selection_size)
        parent =  self.__population.selection(n, type)
        if parent is None:
            return np.array([], dtype=np.ndarray)
        return parent
    
    def __population_selection_method(self, size: int, type: str) -> np.ndarray:
        if size <= 0:
            return np.array([], dtype=np.ndarray)
        result = self.__population.selection(size, type)
        if result is None:
            return np.array([], dtype=np.ndarray)
        return result

    def __current_best_fitness(self):
        fitnesses = self.__population.evaluate_population()
        if fitnesses is None or len(fitnesses) == 0:
            return float('inf')
        return min(fitnesses)

    def getbest(self):
        return self.__best_fitness

    def algorithm(self, generations: int) -> np.ndarray:
        """
        Run the evolutionary algorithm for specified number of generations.
        """

        for gen in range(generations):
            # print(self.__population.getPopulation())

            #==================Start of Parent Selection=================#
            parents_population = self.__parent_selection_method(self.__parent_selection)
            #==================End of Parent Selection==================#

            #===========================Start of Recombination===========================#
            parents_population_size = len(parents_population)
            child_population = []  # Use a list to dynamically collect offspring

            for i in range(0, len(parents_population), 2):
                if i + 1 < len(parents_population):
                    result = self.__recombination.crossover(self.__crossover, parents_population[i], parents_population[i + 1], 
                                                                self.__individual.getIndividualSize())
                    if result is not None:
                        child1, child2 = result
                        child_population.append(child1)
                        child_population.append(child2)

                        #--------Included the mutation inside for every offspring who just got birth----------------#
                        # For the first child
                        if child_population[-2] is not None and random.uniform(0, 1) <= self.__mutation_rate:
                            child_population[-2] = self.__individual.mutation(child_population[-2], self.__mutation)

                        # For the second child
                        if child_population[-1] is not None and random.uniform(0, 1) <= self.__mutation_rate:
                            child_population[-1] = self.__individual.mutation(child_population[-1], self.__mutation)
                        #------------------End of Mutation------------------------#
            #===========================End of Recombination==============================#

        #     #------------------Temporary population to accommodate the------------------#
            # new_population = np.array([None] * self.__pop_size, dtype=np.ndarray)

            # # Replace with offspring up to the population size
            new_population[0 : parents_population_size - 1] = [np.copy(ind) for ind in child_population]

            # new_population = np.concatenate((child_population))
            #---------------------------------------------------------------------------#

            #===========================Start of Population Selection==============================#
            if len(new_population) < self.__pop_size:
                num_to_refill = self.__pop_size - len(new_population)
                random_fill = self.__population_selection_method(num_to_refill, self.__population_selection)
                new_population = np.concatenate((new_population + random_fill))
                
            self.__population.replace_population(new_population)
            # selected_population = self.__population_selection_method(self.__pop_size - parents_population_size, self.__population_selection)
            # new_population[parents_population_size : self.__pop_size] = [np.copy(ind) for ind in selected_population]
            # self.__population.replace_population(new_population)
            #===========================End of Population Selection==============================#

            # Update best fitness
            current_best = self.__current_best_fitness()
            if current_best < self.__best_fitness:
                self.__best_fitness = current_best

        return self.__population.getPopulation()

    def algorithm2(self, generations: int) -> np.ndarray:
        """
        Run the evolutionary algorithm for a specified number of generations.
        """

        for gen in range(generations):
            # ==================Start of Parent Selection=================#
            parents_population = self.__parent_selection_method(self.__parent_selection)
            # ==================End of Parent Selection==================#

            # ===========================Start of Recombination===========================#
            child_population_list = []  # Use a list to dynamically collect offspring

            for i in range(0, len(parents_population), 2):
                if i + 1 < len(parents_population):
                    parent1 = parents_population[i]
                    parent2 = parents_population[i + 1]

                    # Correctly handle all crossover types, including 'edge' which returns a single child.
                    if self.__crossover == "edge":
                        children_tuple = (self.__recombination.crossover(self.__crossover, parent1, parent2, self.__individual.getIndividualSize()),)
                    else:
                        children_tuple = self.__recombination.crossover(self.__crossover, parent1, parent2, self.__individual.getIndividualSize())
                    
                    if children_tuple is not None:
                        for child in children_tuple:
                            # Ensure child is a valid ndarray before processing
                            if child is not None and isinstance(child, np.ndarray):
                                # Apply mutation based on the mutation rate.
                                if random.uniform(0, 1) <= self.__mutation_rate:
                                    mutated_child = self.__individual.mutation(child, self.__mutation)
                                    child_population_list.append(mutated_child)
                                else:
                                    child_population_list.append(child)
            # ===========================End of Recombination==============================#

            # ===========================Start of Population Replacement===========================

            # 1. Get the elite individuals from the current population.
            current_population = self.__population.getPopulation()
            fitnesses = self.__population.evaluate_population()
            if fitnesses is None:
                fitnesses = np.array([])
            elite_indices = np.argsort(fitnesses)[:self.__elite_size]
            
            # Ensure 'elites' is always a 2D array by using a list comprehension.
            elites = np.array([current_population[i] for i in elite_indices], dtype=object)

            # 2. Select the best offspring to fill the rest of the new generation.
            num_offspring_needed = self.__pop_size - len(elites)
            
            if len(child_population_list) > 0:
                offspring_fitnesses = np.array([self.__individual.evaluate_fitness(c) for c in child_population_list])
                best_offspring_indices = np.argsort(offspring_fitnesses)
                best_offspring = np.array(child_population_list, dtype=object)[best_offspring_indices]
            else:
                best_offspring = np.array([], dtype=object)
            
            next_gen_offspring = best_offspring[:num_offspring_needed]

            # 3. Combine elites and offspring to form the complete new population.
            new_population = np.concatenate((elites, next_gen_offspring))

            # 4. Fill any remaining slots with random individuals to prevent size issues.
            if len(new_population) < self.__pop_size:
                num_to_fill = self.__pop_size - len(new_population)
                random_fill = np.array([self.__individual.getCopyPerm() for _ in range(num_to_fill)], dtype=np.ndarray)
                new_population = np.concatenate((new_population, random_fill))

            # 5. Update the population.
            self.__population.replace_population(new_population)

            # ===========================End of Population Replacement===========================
            
            # Update best fitness
            current_best = self.__current_best_fitness()
            if current_best < self.__best_fitness:
                self.__best_fitness = current_best

            #if gen % 20 == 0:
                #print(f"Gen: {gen} got current best is {self.__best_fitness}")
                
        return self.__population.getPopulation()
    
    def getFileName(self):
        return self.__filename
    
    def getCrossoverType(self):
        return self.__crossover
    
    def getMutationType(self):
        return self.__mutation
    
    def getSelectionType_Parent(self):
        return self.__parent_selection
    
    def getSelectionType_Population(self):
        return self.__population_selection
    