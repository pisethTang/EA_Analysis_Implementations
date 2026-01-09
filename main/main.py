# import standard libraries
import time
import sys 
import os 

# Get the path to the project root (one level up from this file)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add it to the system path so Python can find 'utilities' and 'algorithms'
sys.path.append(project_root)





# import modules 
from utilities import config
# from utilities.utilities import ensure_dir




def main():
    """
    Runs one or more algorithms on specified TSP instances and outputs results.
    """
    print("Starting TSP experiments...")

    # Ensure results directory exists
    # ensure_dir(config.RESULTS_DIR)

    # based on the number of algorithms, create an array of elapsed times for each algorithm
    Elapsed_Times = []


    for algorithm in config.ALGORITHMS:
        print(f"Running algorithm: {algorithm.name} with population size {algorithm.population_size}, generations {algorithm.generations}, mutation rate {algorithm.mutation_rate}, local search option {algorithm.local_search_opt}")
        times = []
        for instance_file in config.TSP_INSTANCES:
            print(f"  on instance: {instance_file}")
            tsp_instance = algorithm.load_instance(instance_file)
            start_time = time.perf_counter()
            best_solution = algorithm.run(tsp_instance)
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
            times.append(elapsed_time)
            print(f"    Best solution length: {best_solution.length}, Time taken: {elapsed_time:.4f} seconds")
            print(f"    Best solution permutation: {best_solution.permutation}")
            print(f"========== Completed experiment for algorithm {algorithm.name} ==========")
        Elapsed_Times.append(times) 
    print("All experiments completed.")
    print(f"Results are saved in {config.RESULTS_DIR} directory.")
    print("Elapsed Times for each algorithm on each instance:")
    for i, algorithm_times in enumerate(Elapsed_Times):
        print(f"Algorithm {config.ALGORITHMS[i].name}: {algorithm_times}")



if __name__ == "__main__":
    main()