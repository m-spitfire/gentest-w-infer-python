import ast
from copy import deepcopy, copy
stmt_list = []
approach_level = 0
from visitor import ChangeAndsToNested, ChangeMatchToIf, ChangeOrToElseIfs


def parser_of_eqs(stmt):
    '''
    Use match statements to simplify the code
    '''
    match stmt:
        case ast.Eq():
            return '=='
        case ast.Lt():
            return '<'
        case ast.LtE():
            return '<='
        case ast.Gt():
            return '>'
        case ast.GtE():
            return '>='
        case ast.NotEq():
            return '!='
        case ast.In():
            return 'in'
        case ast.NotIn():
            return 'not in'
        case _:
            print("Error: Unreachable statement is reached! panic!")



def change_predicate(stmt, PRED):
    #to resolve trenary relations
    global approach_level
    global prev_predicate
    global stmt_list

    stmt_test = deepcopy(stmt.test)

    if PRED == 0:
        #changes: putting False => putting (not prev_bool)
        function_flag = stmt.test.args[3].value
        stmt.test.args[3] = ast.Constant(value = not function_flag)
    elif PRED == 1:
        approach_level +=1
        stmt_list.append(stmt.test)
        function_flag = True
        ##############addition for tretary expression:
        if isinstance(stmt_test, ast.IfExp):
            stmt_test = deepcopy(stmt.test.test)
            if not eval(ast.unparse(stmt.test.body)):
                function_flag = False
        ##############


        #############addition for NOT expression
        if isinstance(stmt_test, ast.UnaryOp) and isinstance(stmt_test.op, ast.Not()):
            function_flag = False
        #############
        first_arg = stmt_test.left
        second_arg = stmt_test.comparators

        third_arg = parser_of_eqs(stmt_test.ops[0])
        stmt.test = ast.Call(
            func=ast.Name("evaluate_fitness"),
            args=[
                first_arg,
                second_arg,
                ast.Constant(third_arg),
                ast.Constant(value=function_flag)
            ],
            keywords=[]
        
    )
    elif PRED == 2:
        stmt.test = stmt_list.pop()
        approach_level -= 1
    return



def change_all_predicates(element_body: ast.stmt):
    ifExists = False
    for stmt in element_body:
        if isinstance(stmt, ast.If):
            ifExists = True
            change_predicate(stmt, 1) 
            yield from change_all_predicates(stmt.body)
            change_predicate(stmt, 0)
            
            for elem in stmt.body:
                if isinstance(elem, ast.If):
                    change_predicate(elem, 2)
            
            yield from change_all_predicates(stmt.orelse)
            
            for elem in stmt.orelse:
                if isinstance(elem, ast.If):
                    change_predicate(elem, 2)

        elif isinstance(stmt, ast.For) or isinstance(stmt, ast.While):

            stmt.body.append(ast.Expr(ast.Assign(targets=[ast.Name(id='return_approach_level')], value=ast.Constant(value=0))))   
            yield from change_all_predicates(stmt.body)

    if not ifExists:
        yield

def add_files_node_to_body(file, tree):
    if isinstance(file, str):
        file = "".join(open(file).readlines())
        tree.body.insert(0, ast.parse(file))
        return tree

def simplfy_branch(tree):
    tree = ChangeMatchToIf().visit(tree)
    tree = ChangeAndsToNested().visit(tree)
    tree = ast.fix_missing_locations(ChangeOrToElseIfs().visit(tree))
    return tree


def execute_file_with_given_arugment(args = [4,5], file = "examples/example1.py", func_name = "foo" ):
    '''
    Inpute: None,
    Output: Instrumented functions for all branches named sequentially with original name + _ + id
    '''
    #opening file and parsing it
    with open(file, "r") as f:
        source = f.read()
    tree = ast.parse(source)

    simplfy_branch(tree)
    #deepcopy of the tree to write the changes
    new_tree = deepcopy(tree)

    #adding following files the main function.
    new_tree = add_files_node_to_body("fitness.py", new_tree)

    approach_level_list =  []
    for element in tree.body:
            if isinstance(element, ast.FunctionDef) and element.name == func_name:
                i = 1
                #adding return_approach_level as a global to each function and assigning zero to it.
                element.body.insert(0, ast.Assign(targets=[ast.Name(id='return_approach_level',
                                                 ctx=ast.Store())], value=ast.Constant(value=0)))
                element.body.insert(0, ast.Global(names=['return_approach_level']))

                function_copy = deepcopy(element)
                for _ in change_all_predicates(function_copy.body):
                    #changing instrumented name to have {name}_i, and appending it to body.
                    new_name =element.name+ '_' + str(i)
                    function_copy.name = new_name

                    #adding approach level to list for later use
                    approach_level_list.append(approach_level)
                    new_tree.body.append(deepcopy(function_copy))

                    #calling instrumented function with given arguments,appending the fitness value to fitness_value_vector.
                    new_tree.body.append(ast.Expr(value = ast.Call(
                        func=ast.Name(id=new_name, ctx=ast.Load()),
                        args= [ast.Constant(value = x) for x in args],
                        keywords=[])))
                    new_tree.body.append(deepcopy(
                                                 ast.parse("fitness_vector.append(return_approach_level + branch)")
                                                ))
                    i += 1
                #new executable_file
    instrumented_code = ast.unparse(ast.fix_missing_locations(new_tree))
    with open('debug.py', "w") as f:
       f.write(instrumented_code)
    exec(instrumented_code, globals())
    return [x + y for (x, y) in zip(fitness_vector, approach_level_list)]

    # print(ast.unparse(ast.fix_missing_locations(new_tree)))

        

print(execute_file_with_given_arugment(args = [11,"somestring", 5], file = "examples/example1.py" ))


