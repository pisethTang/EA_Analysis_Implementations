from TSPlib import np
import statistics as stats
import os

class Output:
    def __init__(self):
        # Ensure the results directory exists
        self.__path = "./results/algorithm.txt"
        self.__dir = os.path.dirname(self.__path)
        if self.__dir and not os.path.exists(self.__dir):
            os.makedirs(self.__dir)
        self.__info = None
    
    def __output(self, length: int, index: int, op: str, filename: str):
        self.__info = f"Run {index + 1} with {op} from {filename} tour length: {length}\n"
        with open(self.__path, "a") as f:
            f.write(self.__info)

    def output(self, length: int, index: int, op: str, filename: str):
        try:
            self.__output(length, index, op, filename)
        except Exception as e:
            print(f"Error writing to file: {e}")

    def stats(self, array: np.ndarray):
        self.__info = f"Minimum: {np.min(array)}\n"
        self.__info += f"Mean: {np.mean(array)}\n"
        self.__info += f"SD: {np.std(array)}\n\n"
        with open(self.__path, "a") as f:
            f.write(self.__info)