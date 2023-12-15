import random

import numpy as np
import string
# from  instrumentation.main import execute_file_with_given_arugment
import ast

MAX_STRING_LENGTH = 32
MIN_STRING_LENGTH = 1


def execute_file_with_given_arugment(a, b, c,):
    return 34


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
        '''change this later.......'''
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
        return [self.args[0], self.args[2]]
    def cross_over(self, other: 'TestCase') -> ('TestCase', 'TestCase'):
        pass
    def mutate(self) -> 'TestCase':
        pass
    def __str__(self):
        return "{}: Args({}) {}".format(self.function_name, self.args, self.fitness)
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
    def generate_offspring(self, other: 'TestCase') -> ('TestCase', 'TestCase'):
        # pass
        pass
    def mutation(self) -> 'TestCase':
        pass

    def __str__(self):
        return "\n".join(str(arg) for arg in self.container) + "{}".format(self.fitness)
    


file_ = "/Users/coll1ns/gentest-w-infer-python/gentest_w_infer_python/instrumentation/examples/example1.py"

# new_arg = Args.build_arg('aklsdjfkasldf', 'asdlfsdf')
arg_1 = Args([3, 'cool', 1], file_, "foo")
arg_2 = Args([6, "caist", 8], file_, "foo")

arg_3 = Args([1, 'cool', -5], file_, "foo")
arg_4 = Args([-4, 'cool', -9], file_, "foo")
test_1 = TestCase(file_, [2], [arg_1, arg_2])
test_2 = TestCase(file_, [2], [arg_3, arg_4])

print(test_1.dominance_comparator(test_2, ))
print(test_1)


# print(new_arg.args, new_arg.fitness)
# print(new_test_case)





