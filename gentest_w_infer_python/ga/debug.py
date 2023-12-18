import numpy as np
from typing import List
import random
# from instrumentation.main import execute_file_with_given_arugment
import string
import ast


MAX_STRING_LENGTH = 32
MIN_STRING_LENGTH = 1


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
        
    def mutation(self, beta = 0.08):
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


class TestCase:
    '''
    TestCase can have 5 statements according to DynoMOSA, 
    but we will only use function call for our testcase...
    '''
    def __init__(self, sut, num_of_call_per_function, container):
        self.sut = sut
        self.num_of_call_per_function = num_of_call_per_function 
        self.container = container
        self.targets = []
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
            crossover_point = random.randint(1, min(len(parent1), len(parent2)) - 1)
            child1 = parent1[:crossover_point] + parent2[crossover_point:]
            child2 = parent2[:crossover_point] + parent1[crossover_point:]
            new_1_container.extend(child1)
            new_1_num_function_calls.append(len(child1))
            new_2_container.extend(child2)
            new_2_num_function_calls.append(len(child2))
            sum_1 += call_1
            sum_2 += call_2
        return (TestCase(self.sut, new_1_num_function_calls, new_1_container), TestCase(self.sut, new_2_num_function_calls, new_2_container))
    def mutation(self, beta = 0.88):
        '''In place mutation of testcases'''
        # 
        prob = random.random()
        if prob < beta:
            if prob > 2 :
                #insertion
                # pass
                self.container.append(Args.build_arg(self.sut, self.function_name))
            elif prob >1:
                #deletion
                # pass
                random_index = random.randint(1, len(self.container) - 1)
                self.container.pop(random_index)
            else:
                #in_place_change_arg.
                # pass     
                random_index = random.randint(1, len(self.container) - 1)
                print(random_index)
                print("HERE", self.container[random_index])
                self.container[random_index].mutation()
        return


    def __str__(self):
        return "\n".join(str(arg) for arg in self.container) + "\nfitness vector: {}".format(self.fitness)
    


file_ = "/Users/coll1ns/gentest-w-infer-python/gentest_w_infer_python/instrumentation/examples/example1.py"

# new_arg = Args.build_arg('aklsdjfkasldf', 'asdlfsdf')
arg_1 = Args([3, 'cool', 1], file_, "foo")
arg_2 = Args([6, "caist", 8], file_, "foo")

arg_3 = Args([1, 'cool', -5], file_, "foo")
arg_4 = Args([-4, 'cool', -9], file_, "foo")

# print(arg_1)
# arg_1.mutation(beta = 0.99)
# print(arg_1)
# arg_5, arg_6 = arg_1.crossover(arg_2)
# print(arg_1, arg_2, arg_5, arg_6)

test_1 = TestCase(file_, [2], [arg_1, arg_2])
test_2 = TestCase(file_, [2], [arg_3, arg_4])

print(test_1)
test_1.mutation()
print(test_1)
# print(test_2)
# new_test_1, new_test_2 = test_1.crossover(test_2)
# print(new_test_1)
# print(new_test_2)
# print(test_1.dominance_comparator(test_2, ))
# print(test_1)


# print(new_arg.args, new_arg.fitness)
# print(new_test_case)





