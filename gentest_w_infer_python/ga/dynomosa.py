import numpy as np
from typing import List
import random
# from instrumentation.main import execute_file_with_given_arugment
import string
import ast


MAX_STRING_LENGTH = 32
MIN_STRING_LENGTH = 1


# class FunctionTarget:
#     '''
#     Branch target of the function under test
#     Each branch has an id, and branches on which is dependent.
#     Covered flag is helpful in later implementations
#     '''
#     def __init__(self, sut):
#         # pass
#         self.sut = sut
#         self.covered = False
#         #later add more to here.... ......


class Args:
    def __init__(self, args, file_name, function_name):
        '''
        Argument object, for the given sut calculates 
        the fitness vector for all branches..
        '''
        # self.sut = sut
        self.args = args
        self.file_name = file_name
        self.function_name = function_name
        self.fitness = self.get_fitness()
    @staticmethod
    def build_arg(file_name, function_name):
        '''
        Type hint part comes here
        '''
        arg_types = Args.get_args_of_sut(function_name)
        args = []
        for arg_type in arg_types:
            args.append(Args.assign_random(arg_type))
        return Args(args, function_name, file_name)

    @staticmethod
    def get_args_of_sut(function_name):
        '''
        
        '''
        return ['int', 'str', 'int']
    @staticmethod
    def assign_random(argument_type):
        '''
        Look this later ...
        '''
        match argument_type:
            case 'str':
                return ''.join(random.choices(string.ascii_letters,k = random.randrange(MIN_STRING_LENGTH,MAX_STRING_LENGTH)))
            case 'int':
                return random.randrange(-250, 250)

    def get_fitness(self):
        '''
        returns the fitness vector of the function call 
        with arguments produced for all targets.
        '''
        # return execute_file_with_given_arugment(self.args, self.file_name, self.function_name)
        return [1]
        # return [self.args[0], self.args[2]]

    def __str__(self):
        return "{}: Args({})".format(self.function_name, self.args)
    #might define helper functions later....

class TestCase:
    '''
    TestCase can have 5 statements according to DynoMOSA, 
    but we will only use function call for our testcase...
    '''
    def __init__(self, sut, num_of_call_per_function, container):
        self.sut = sut
        self.num_of_call_per_function = num_of_call_per_function 
        self.container =container
        self.targets = []
        # self.function_names = self.get_function_names()
        self.function_name = TestCase.get_function_names(sut)
        self.fitness = self.get_fitness()
        #look here later
    def size(self):
        return len(self.container)
    def clone(self):
        return TestCase(self.sut, self.num_of_call_per_function, self.container)

    @staticmethod
    def get_function_names(sut):
        # pass
        with open(sut, 'r') as file:
            tree = ast.parse(file.read())

        function_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        return function_names
    @staticmethod
    def build_testcase(max_number_of_calls, sut):
        '''
        Builds test case consisting of calls to 
        functions and 
        '''
        container = []
        num_of_call_per_function = []
        for function in TestCase.get_function_names(sut):
            number_of_calls = random.randint(1, max_number_of_calls)
            num_of_call_per_function.append(number_of_calls)
            for _ in range(number_of_calls):
                container.append(Args.build_arg(function, sut))

        return TestCase(sut, num_of_call_per_function, container)
        # pass
    def get_fitness(self):
        prev_index = 0
        fitness_for_class = []
        for index in self.num_of_call_per_function:
            fitness_matrix_for_function = np.array([x.fitness for x in self.container[prev_index:index]])
            fitness_for_class.append(fitness_matrix_for_function.min(0).tolist())
            prev_index = index
        fitness_for_class = [score for vec in fitness_for_class for score in vec]
        return fitness_for_class
    
    def get_fitness_for_target(self, target):
        '''
        Returns the objective score for the target
        '''
        # pass
        return self.fitness[target]

    def dominance_comparator(self, t2: 'TestCase', coverage_targets) -> int:
        # pass
        dominates1 = False
        dominates2 = False
        for target in coverage_targets.keys():
            if not coverage_targets[target]:
                score1 = self.get_fitness_for_target(target)
                score2 = t2.get_fitness_for_target(target)
                if score1 < score2:
                    dominates1 = True
                else:
                    dominates2 = True
                if dominates1 and dominates2:
                    break
        if dominates1 == dominates2:
            #neither dominates each other
            return 0
        else:
            if dominates1:
                #t1 dominates t2
                return 1
            else:
                #t2 dominates t1
                return 2
    def crossover(self, other: 'TestCase') -> ('TestCase', 'TestCase'):
        # pass
        return (self.clone(), other)
        
    def mutation(self) -> 'TestCase':
        # pass
        return self.clone()

    def __str__(self):
        return "\n".join(str(arg) for arg in self.container) + "{}".format(self.fitness)
    


class TestSuite:
    '''
    TestSuite class, which is actually holder for 
    non-dominated test-cases none other than that
    '''
    def __init__(self, test_suite):
        self.test_suite: List[TestCase] = test_suite
        # pass
    def replace(self, test_case_1, test_case_2):
        '''
        Replaces the test-case 1 with test-case 2
        '''
        index = self.test_suite.index(test_case_1)
        self.test_suite[index] = test_case_2
        return

    def find_best_test_case(self, target) -> TestCase:
        '''
        Finds the best test case satifying the target
        How do we find this though???????
        '''
        array = [x.fitness[target] for x in self.test_suite]
        index = np.argmax(array)
        return self.test_suite[index]
    def __str__(self):
        return self.test_suite[0]

class MOSA:
    def __init__(self, sut, population_size, budget):
        self.sut = sut
        self.population_size = population_size
        # self.population = self.get_random_population()
        self.budget = budget
        # self.fitness_score = self.fitness(sut, )
        #   
        #fix this part
        # self.coverage_targets = [FunctionTarget(self.sut) for _ in range(20)]
        self.coverage_targets = []

    def get_random_population(self, num_of_calls):
        population = []
        for _ in range(self.population_size):
            population.append(TestCase.build_testcase(num_of_calls, self.sut))
        return population
    def generate_offspring(self, population):
        '''This will be pain in the ass thoug ....'''
        # pass
        return population
    def preference_sorting(self, candidates) -> List[List[TestCase]]:
        # pass
        fronts = []
        first_front = []
        for target in self.coverage_targets:
            if not target.covered:
                #
                t_best = 0
                first_front.append(t_best)
        candidates = [item for item in candidates if item not in first_front] #candidates - first_front
        fronts.append(first_front)
        if len(first_front) > self.population_size:
            fronts.append(candidates)
        else:
            candidates_star = candidates
            new_fronts = self.fast_nondominated_sort(candidates_star)
            for front in new_fronts:
                ######test for dominance
                a = 5
                fronts.append(front)
        return fronts

    def fast_nondominated_sort(self, candidates: List[TestCase]) -> List[List[TestCase]]:
        # pass
        fronts: List[List] = []
        F1 = []
        storage: dict(List[TestCase, int]) = dict()
        for p in candidates:
            S_p = []
            n_p = 0
            for q in candidates:
                #####this might be wrong as dominance might include the equality which is the case 0
                match p.dominance_comparator(q, self.targets):
                    case 0:
                        pass
                    case 1:
                        S_p.append(q)
                    case 2:
                        n_p += 1
                    case _:
                        raise(ValueError)
            storage[p][0] = S_p
            storage[p][1] = n_p
            if np == 0:
                p_rank = 1
                F1.append(p)
        fronts.append(F1)
        i = 0
        while len(fronts[i]) == 0:
            F_i = fronts[i]
            Q = []
            for p in F_i:
                for q in storage[p][0]:
                    storage[q][1] -= 1
                    if storage[q][1] == 0:
                        q_rank = i + 1
                        Q.append(q)
            i += 1
            fronts.append(Q)
        return fronts

    def crowd_distance_assignment(self, front: List[TestCase]) -> dict[TestCase, float]:
        # pass
        front_length = len(front)
        distance_map = {testcase:0 for testcase in front}
        for target in self.target:
            #sorting the front
            front = sorted(front, key = lambda x: x.get_fitness_for_target(target))
            front[0], front[-1] = float('inf')
            for i in range(1, front_length - 1):
                max_objective = front[-1].get_fitness_for_target(target)
                min_objective = front[0].get_fitness_for_target(target)
                update = (front[i+1].get_fitness_for_target(target) - front[i-1].get_fitness_for_target(target))/(max_objective - min_objective)
                distance_map[front[i]] = distance_map[front[i]] + update
        return distance_map
                
    def update_archive(self, candidates: List[TestCase], archive: TestSuite):
        # pass
        '''
        Updates the archive according to the candidate test cases.
        '''
        for target in self.coverage_targets:
            t_best = None
            best_length = float('inf')
            if target.covered:
                t_best = archive.find_best_test_case(target)
                best_length = t_best.number_of_calls
            
            for candidate in candidates:
                score = candidate.fitness[target]
                length = candidate.number_of_calls
                if score == 0 and length <= best_length:
                    archive.replace(t_best, candidate)
                    t_best = candidate
                    best_length = length
        return archive

    def sort(self, map: dict[TestCase, float]) -> List[TestCase]:
        pass

    def train(self, num_of_calls):
        # pass
        population = self.get_random_population(num_of_calls)
        current_generation = 0
        archive = self.update_archive(population, [])
        while self.budget > 0:
            #should we sort population?????
            offspring = self.generate_offspring(population)
            archive = self.update_archive(offspring, archive)
            population.extend(offspring)
            fronts = self.preference_sorting(population)
            population.clear()
            d = 0
            map_of_crowd_distance_d: dict[TestCase, float] = None
            while population.len() + fronts[d].len() <= self.population_size:
                map_of_crowd_distance_d = self.crowd_distance_assignment(fronts[d])
                population = population.extend(fronts[d])
                d+=1
            front_d = self.sort(map_of_crowd_distance_d)
            #should it be 1???????
            population = population.extend(front_d[1:(self.population_size - population.len())])
            current_generation += 1
            self.budget -= 1
        return archive


# class DynoMOSA(MOSA):
#     pass
file = "/Users/coll1ns/gentest-w-infer-python/gentest_w_infer_python/instrumentation/examples/example1.py"
size = 100
budget = 300
solver = MOSA(file, size, budget)
a = solver.train(11)
print(a)

