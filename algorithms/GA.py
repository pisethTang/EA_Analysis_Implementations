from ast import List
import numpy as np
import random 
from typing import Optional, Tuple 



from utilities.TSPLib import TSPInstance, FastLocalSearch, AlgorithmResult



class DesignedGA():
    def __init__(self, 
                population_size: int = 20, 
                generations: int = 1000,
                mutation_rate: float = 0.01,
                local_search_opt: Optional[str] = "jump",
                name: str = "DesignedGA"
                ) -> None:
        if population_size <= 0:
            raise ValueError("Population size must be a positive integer.")
        if generations <= 0:
            raise ValueError("Generations must be a positive integer.")
        if not (0 <= mutation_rate <= 1):
            raise ValueError("Mutation rate must be between 0 and 1.")
        if local_search_opt not in (None, "jump", "two_opt"):
            raise ValueError("local_search_opt must be None, 'jump', or 'two_opt'.")
        if not name:
            raise ValueError("Name must be a non-empty string.")
        self.population_size = max(population_size, 10)  # Ensure at least 10 individuals
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.local_search_opt = local_search_opt
        self.name = name


    def load_instance(self, file_path: str) -> TSPInstance:
        """
        Loads a TSP instance from a file.
        
        Args:
            file_path (str): Path to the TSP instance file.
        """
        return TSPInstance(file_path)

    

    def _get_fitness(self, instance: TSPInstance, population: list[np.ndarray]) -> list[int]:
        """
        Computes the fitness of a given population for the TSP instance.
        
        Args:
            instance (TSPInstance): The TSP instance.
            population (list[np.ndarray]): The population of permutations representing tours.
        """
        return [FastLocalSearch.np_tour_length(instance, individual) for individual in population]
    

    def _selection_tournament(self, population: list[np.ndarray], fitness: list[int]) -> list[np.ndarray]:
        """
        Selects parents using Tournament Selection.
        """
        selected = []
        pop_size = len(population)
        for _ in range(pop_size):
            # Pick two random indices
            i, j = random.sample(range(pop_size), 2)
            # Compare fitness (lower is better for TSP)
            if fitness[i] < fitness[j]:
                selected.append(population[i])
            else:
                selected.append(population[j])
        return selected

    def _crossover_order(self, parent1: np.ndarray, parent2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Performs Order Crossover (OX1) on two parents.
        """
        n = len(parent1)
        cut1, cut2 = sorted(random.sample(range(n), 2))
        
        child1 = -np.ones(n, dtype=int)
        child2 = -np.ones(n, dtype=int)
        
        # Copy the sub-segment
        child1[cut1:cut2] = parent1[cut1:cut2]
        child2[cut1:cut2] = parent2[cut1:cut2]
        
        # Fill the rest
        def fill_child(child, parent, end_pos):
            current_pos = end_pos
            for gene in parent:
                if gene not in child:
                    child[current_pos] = gene
                    current_pos = (current_pos + 1) % n
            return child
        child1 = fill_child(child1, parent2, cut2 % n)
        child2 = fill_child(child2, parent1, cut2 % n)
        
        return child1, child2

    def _mutation_swap(self, individual: np.ndarray) -> None:
        """
        Applies Swap Mutation in-place.
        """
        if random.random() < self.mutation_rate:
            n = len(individual)
            a, b = random.sample(range(n), 2)
            individual[a], individual[b] = individual[b], individual[a]

    def _run_local_search(self, instance: TSPInstance, population: list[np.ndarray]):
        """
        Applies the O(1) local search if configured.
        """
        if self.local_search_opt == "jump":
            for i in range(len(population)):
                population[i], _ = FastLocalSearch.jump(instance, population[i])
        elif self.local_search_opt == "two_opt":
            for i in range(len(population)):
                population[i], _ = FastLocalSearch.twoOpt(instance, population[i])
        elif self.local_search_opt == "exchange":
            for i in range(len(population)):
                population[i], _ = FastLocalSearch.exchange(instance, population[i])
        else:
            raise ValueError("The provided local search operator has to strictly be one of the following: `jump`, `two_opt`, or `exchange`.")


    def run(self, instance: TSPInstance) -> AlgorithmResult:
        """
        The maine execution loop. 
        Args:
            instance (TSPInstance): The TSP instance to solve.
        """ 
        n: int = instance.size
        
        # 1. Initialize the populationq
        population = [np.random.permutation(n) for _ in range(self.population_size)]

        global_best_perm = None 
        global_best_length = float('inf')

        for gen in range(self.generations):
            # 2. Evaluate fitness
            fitness_scores = self._get_fitness(instance, population)

            # check for best solution in current generation (simple elitism tracking)
            min_fitness = min(fitness_scores)
            if min_fitness < global_best_length:
                global_best_length = min_fitness
                global_best_idx = fitness_scores.index(min_fitness)
                global_best_perm = np.copy(population[global_best_idx])

            # 3. Selection (Tournament Selection)
            # selected = []
            # for _ in range(self.population_size):
            #     i, j = random.sample(range(self.population_size), 2)
            #     if fitness[i] < fitness[j]:
            #         selected.append(population[i])
            #     else:
            #         selected.append(population[j])
            parents = self._selection_tournament(population, fitness_scores)
            
            # 4. Crossover (Order Crossover)
            next_population = []
            for i in range(0, self.population_size, 2):
                p1, p2 = parents[i], parents[i+1]
                c1, c2 = self._crossover_order(p1, p2)
                next_population.extend([c1, c2])
            # 5. Mutation (Swap Mutation)
            for i in range(self.population_size):
                self._mutation_swap(next_population[i])

            # 6. Local Search
            if self.local_search_opt is not None:
                self._run_local_search(instance, next_population)

            # 7. Update population
            population = next_population

            # print progress every 10% generations
            if gen % (self.generations // 10) == 0:
                print(f"Generation {gen+1}/{self.generations} completed.")

        # Return the best solution found
        if global_best_perm is None:
            # raise Exception("No solution found.")
            return AlgorithmResult(permutation=np.array([]), length=float('inf'))
        return AlgorithmResult(permutation=global_best_perm, length=global_best_length)
