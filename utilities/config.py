from pathlib import Path 
from algorithms.GA import DesignedGA



BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = DATA_DIR / "results"

ALGORITHMS = []
TSP_INSTANCES = [
    # "eil51.tsp",
    # "eil101.tsp",
    "kroC100.tsp",
    # "kroB100.tsp",
]  # List of TSP instance file paths



# POPULATION_SIZES = [100]
MUTATION_TYPES = ["inversion", "swap", "insert"]
MUTATION_RATES = [0.01]

CROSSOVER_TYPE = ["uniform", "pmx", "cycle"]
PARENT_SELECTION = ["tournament", "roulette"]
POPULATION_SELECTION = ["fitness", "tournament"]



ALGORITHMS = [
    # Experiment A: Baseline GA (No local search)
    # DesignedGA(population_size=50, mutation_rate=0.01, local_search_opt=None, name="GA_Pure"),
    
    # Experiment B: GA + Jump Local Search (Memetic)
    DesignedGA(population_size=20, generations=500, mutation_rate=0.1, local_search_opt="jump", name="GA_Memetic_Jump"),

    # Experiment C: High Mutation
    # DesignedGA(population_size=50, mutation_rate=0.10, local_search_opt=None, name="GA_HighMut"),
]