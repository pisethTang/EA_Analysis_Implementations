from Population import Population, np, logging

# class Inner(Population):
#     def __init__(self, size: int, filename: str, p_value: float):
#         self.__function = Population(size, None, None, filename)
#         self.__population = self.__function.getPopulation()
#         self.__candidate_size = self.__function._getIndividual().getIndividualSize()
#         self.__p = p_value
#         self.__best = None
#         self.__Inner_over()

#     def __Inner_over(self):
#         index = 100000

#         while index > 0:
#             for individual in self.__population:
#                 sample = np.copy(individual)
#                 self.__best = np.copy(sample)
#                 city = np.random.choice(sample)
#                 _city = None

#                 while True:
#                     if(np.random.uniform(0, 1) <= self.__p):
#                         flag = True
#                         while flag:
#                             _city = np.random.choice(sample)
#                             if(_city != city): flag = False
#                             else: flag = True
#                     else:
#                         _sample = np.random.choice(self.__population)
#                         index = int(np.where(_sample == city)[0] + 1)
#                         if(index >= self.__candidate_size): index = 0
#                         # print(f"{index} - {self.__function._getIndividual().getIndividualSize()}")
#                         _city = _sample[index]

#                     next = int(np.where(sample == city)[0] + 1)
#                     previous = int(np.where(sample == city)[0] - 1)
#                     if(next >= self.__candidate_size): next = 0
#                     if(previous >= self.__candidate_size): previous = 0
#                     if(sample[next] == _city or sample[previous] == _city):
#                         break

#                     i = int(sample[np.where(sample == city)[0]])
#                     j = int(sample[np.where(sample == _city)[0]])

#                     sample[i : j] = sample[i : j] [::-1]
#                     city = _city
                
#                 S_ = self.__function._getIndividual().evaluate_fitness(sample)
#                 S_i = self.__function._getIndividual().evaluate_fitness(individual)
#                 if(S_ <= S_i):
#                     individual = np.copy(sample)
#                     self.__best = np.copy(sample)
#                     print(f"Found a better route: {S_}")

#             index -= 1        

    # def getBest(self) -> np.ndarray:
    #     print(self.__function._getIndividual().evaluate_fitness(self.__best))
    #     return self.__best
