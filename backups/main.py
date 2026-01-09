# Import statements and main function
from files import Output
import sys
from Algorithm import EvolutionaryAlgorithm as ea, np

def main():
    # Get arguments from CLI
    args = sys.argv[1:]
    if len(args) < 2:
        print("Usage: python script.py <population_size> <generations> <filename>")
        sys.exit(1)

    population_size = int(args[0])  # Convert to int for pop_size
    generations = int(args[1])
    filename = args[2]
    text = Output()
    lengths = np.zeros(1, dtype=int) #!!!!

    for i in range(1): #!!!!
        EA = ea(population_size=population_size, filename=filename, mutation="insert", mutation_rate=0.5, 
                crossover="pmx", parent_selection="tournament", population_selection="fitness")
        population = EA.algorithm2(generations)  # Assuming algorithm2 returns the population or fitness
        best_fitness = EA.getbest()  # Get the best fitness from the run
        lengths[i] = best_fitness  # Store the fitness value
        text.output(int(best_fitness), i, "EvolutionaryAlgorithm", filename)  # Use EA name as operation

    text.stats(lengths)

if __name__ == "__main__":
    main()