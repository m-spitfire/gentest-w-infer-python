import numpy as np
from typing import List
import random
# from instrumentation.main import execute_file_with_given_arugment
import string
import ast
from itertools import chain

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
                '''might change string.ascii_letters -> sring.printable'''
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
    def crossover(self, other: 'Args') -> ['Args', 'Args']:
        assert self.function_name == other.function_name
        child_1_args = []
        child_2_args = []
        for args_tuple in zip(self.args, other.args):
            id = random.choice([0, 1])
            child_1_args.append(args_tuple[id])
            child_2_args.append(args_tuple[not id])
        child_1 = Args(child_1_args, self.file_name, self.function_name)
        child_2 = Args(child_2_args, self.file_name, self.function_name)
        return [child_1, child_2]
        
    def mutation(self, beta = 0.88):
        '''In-place mutation of the args class
        best to save some memory'''
        new_args = []
        for arg in self.args:
            prob = random.random()
            if prob < beta:
                match arg:
                    case str():
                        if prob < beta / 3:
                            #update
                            id = random.randint(0, len(arg) - 1)
                            arg = arg[:id -1] + random.choice(string.ascii_letters)+ arg[id:]
                        elif (2* beta / 3 > prob > beta / 3):
                            #insertion
                            arg += random.choice(string.ascii_letters)
                        else:
                            #deletion
                            id = random.randint(0, len(arg) - 1)
                            arg = arg[:id -1] + arg[id:]
                    case int():
                        arg += random.choice([-1, 1])
                    case float():
                        arg += random.choice([-1, 1])*(arg/100 + (not arg)*0.01)
            new_args.append(arg)
        self.args = new_args
    def __str__(self):
        return "{}: Args({})".format(self.function_name, self.args)
    #might define helper functions later....
    def __hash__(self):
        return hash("".join(str(elem) for elem in self.args) + self.function_name + self.file_name)
    def __eq__(self, other):
        return (self.args == other.args and self.function_name == other.function_name and self.file_name == other.file_name)


class TestCase:
    '''
    TestCase can have 5 statements according to DynoMOSA, 
    but we will only use function call for our testcase...
    '''
    def __init__(self, sut, num_of_call_per_function, container):
        self.sut = sut
        self.num_of_call_per_function = num_of_call_per_function 
        self.container = container
        # self.function_names = self.get_function_names()
        self.function_name = TestCase.get_function_names(sut)
        self.fitness = self.get_fitness()
        #look here later
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
        assert self.sut == other.sut
        # return (self.clone(), other)
        # argument object crossover probability = 0.5
        prob = random.random()
        #new testcase objects.....
        new_1_container = []
        new_1_num_function_calls = []
        new_2_container = []
        new_2_num_function_calls = []
        #helpful local variables ???
        sum_1 = 0
        sum_2 = 0
        for (call_1, call_2) in zip(self.num_of_call_per_function, other.num_of_call_per_function):
            parent1 = self.container[sum_1:call_1]
            parent2 = other.container[sum_2:call_2]
            crossover_point = random.randint(0, min(len(parent1), len(parent2)) - 1)
            child1 = parent1[:crossover_point] + parent2[crossover_point:]
            child2 = parent2[:crossover_point] + parent1[crossover_point:]
            new_1_container.extend(child1)
            new_1_num_function_calls.append(len(child1))
            new_2_container.extend(child2)
            new_2_num_function_calls.append(len(child2))
            sum_1 += call_1
            sum_2 += call_2
        return (TestCase(self.sut, new_1_num_function_calls, new_1_container), TestCase(self.sut, new_2_num_function_calls, new_2_container))
    def mutation(self, beta = 0.08):
        '''In place mutation of testcases'''
        # 
        prob = random.random()
        if prob < beta:
            if prob < beta/3 :
                #insertion
                # pass
                self.container.append(Args.build_arg(self.sut, self.function_name))
            elif prob > 2*beta / 3:
                #deletion
                # pass
                try:
                    random_index = random.randint(1, len(self.container) - 1)
                except:
                    print(self)
                    exit()
                self.container.pop(random_index)
            else:
                #in_place_change_arg.
                # pass     
                try:
                    random_index = random.randint(1, len(self.container) - 1)
                except:
                    print(self)
                    exit()
                self.container[random_index].mutation()
        return
        
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

    def __str__(self):
        return "\n".join(str(arg) for arg in self.container) + "\nfitness:{}".format(self.fitness)
    
    def __hash__(self):
        return hash(map(hash, chain(self.container, self.num_of_call_per_function)))
    def __eq__(self, other):
        return (self.container == other.container and self.num_of_call_per_function == other.num_of_call_per_function)

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
        self.coverage_targets = dict()
    def get_random_population(self, num_of_calls):
        population = []
        for _ in range(self.population_size):
            population.append(TestCase.build_testcase(num_of_calls, self.sut))
        return population
    def generate_offspring(self, population):
        '''This will be pain in the ass thoug ....'''
        # pass
        new_generation = []
        for parents in zip(population[:50], population[50:]):
            child_1, child_2 = parents[0].crossover(parents[1])
            child_1.mutation()
            child_2.mutation()
            new_generation.extend([child_1, child_2])
        return new_generation
    def preference_sorting(self, candidates) -> List[List[TestCase]]:
        # pass
        fronts = []
        first_front = []
        for target in self.coverage_targets.keys():
            if not self.coverage_targets[target]:
                #
                t_best = sorted(candidates, key = lambda x: x.get_fitness_for_target(target))[0]
                first_front.append(t_best)
        try:
            candidates = [item for item in candidates if item not in first_front] #candidates - first_front
        except:
            print(first_front)
            exit()
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
        storage: dict(TestCase, int) = {}
        for p in candidates:
            S_p = []
            n_p = 0
            for q in candidates:
                #####this might be wrong as dominance might include the equality which is the case 0
                match p.dominance_comparator(q, self.coverage_targets):
                    case 0:
                        pass
                    case 1:
                        S_p.append(q)
                    case 2:
                        n_p += 1
                    case _:
                        raise(ValueError)
            storage[p] = [S_p, n_p]
            if np == 0:
                p_rank = 1
                F1.append(p)
        fronts.append(F1)
        i = 0
        print(fronts)
        print()
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
        for target in self.coverage_targets:
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
        #construction of coverage targets dictionary
        for i in range(len(candidates[0].fitness)):
            self.coverage_targets[i] = False

        for target in self.coverage_targets.keys():
            t_best = None
            best_length = float('inf')
            if self.coverage_targets[target]:
                t_best = archive.find_best_test_case(target)
                best_length = t_best.number_of_calls
            
            for candidate in candidates:
                score = candidate.fitness[target]
                length = sum(candidate.num_of_call_per_function)
                if score == 0 and length <= best_length:
                    #update coverage_target list...
                    self.coverage_targets[target] = True
                    archive.replace(t_best, candidate)
                    t_best = candidate
                    best_length = length
        return archive

    def sort(self, map: dict[TestCase, float]) -> List[TestCase]:
        pass

    def train(self, num_of_calls):
        # pass
        population = self.get_random_population(num_of_calls)
        print("Checkpoint 1")
        current_generation = 0
        archive = self.update_archive(population, [])
        print("Checkpoint 2")
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

