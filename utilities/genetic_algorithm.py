from typing import List
from utilities.solution_chromosome import SolutionChromosome
from .solution_generator import SolutionGenerator
from random import random
from copy import deepcopy
import numpy as np


class GeneticAlgorithm:
    def __init__(self, population_size,
                 mutation_rate,
                 crossover_rate,
                 maximum_iteration) -> None:
        self.population_size = population_size
        self.population = None

        self.current_iteration = 0
        self.maximum_iteration = maximum_iteration

        self.global_best_route = None
        self.current_best_route = None

        self.solution_generator = SolutionGenerator()

        self.max_mutation_rate = mutation_rate
        self.max_crossover_rate = crossover_rate

        self.mutation_rate_lookup = np.linspace(
            self.max_mutation_rate, 0, self.maximum_iteration)

        self.crossover_rate_lookup = np.linspace(
            0, self.max_crossover_rate, self.maximum_iteration)

    @property
    def current_level_mutation_rate(self) -> float:
        return self.mutation_rate_lookup[self.current_iteration]

    @property
    def current_level_crossover_rate(self) -> float:
        return self.crossover_rate_lookup[self.current_iteration]

    def _generate_initial_population(self) -> None:
        initial_half_population = self.solution_generator.generate_valid_solutions(
            self.population_size // 2)
        half_population_cloned = deepcopy(initial_half_population)
        self._reproduce(half_population_cloned)  # in-place operation
        total_population = [
            *initial_half_population, *half_population_cloned
        ]
        # -> [0, 1, 2, 3], remember to choose last one to get the best fitness, chromosome is sorted by 'FITNESS'
        total_population.sort()

        self.population = total_population
        self.global_best_route = total_population[-1]
        self.current_best_route = total_population[-1]

    def _calculate_total_fitness_of_population(self) -> None:
        total_fitness = 0
        for chromosome in self.population:
            total_fitness += chromosome.fitness

        return total_fitness

    def _select_a_parent(self) -> None:
        '''
        輪盤選擇
        '''

        total_fitness = self._calculate_total_fitness_of_population()
        random_value = random() * total_fitness
        check_sum = 0
        selected_idx = 0
        while (check_sum < random_value and selected_idx < self.population_size):
            check_sum += self.population[selected_idx].fitness
            selected_idx += 1

        return self.population[selected_idx - 1]

    def _crossover_two_parents(self) -> None:
        '''
        產生下一代
        '''
        pass

    def _mutate_two_children(self) -> None:
        pass

    def _reproduce(self, cloned_chromosomes: List[SolutionChromosome]) -> None:
        for chromosome in cloned_chromosomes:
            chromosome._reproduction_mutate()
        return cloned_chromosomes

    @property
    def is_termination_criteria_met(self) -> bool:
        if self.current_iteration > self.maximum_iteration:
            return True

        return False

    def solve(self) -> None:
        self._generate_initial_population()
        # while not (self.is_termination_criteria_met):
        #     self._calculate_total_fitness_of_population()
        #     partent = self._select_a_parent()
        #     self._crossover_two_parents()
        #     self._mutate_two_children()
        #     self.current_iteration += 1
        # print(count)
