from dataclasses import dataclass
from enum import Enum
import argparse
import ast
import os
import copy

# Types of operations on strings:
#   - concatenation ('+')
#   - comparison (==, !=, <, <=, >, >=)
#   - membership (in)
#   - slicing ([:])
#   - indexing ([])
#   - repetition (*)
#   - length (len())
#   - iteration (for ... in ...)

# Types of operations on integers:
#   - arithmetic (+, -, *, /, //, %, **)
#   - comparison (==, !=, <, <=, >, >=)

# Types of operations on booleans:
#   - logical (and, or, not)
#   - comparison (==, !=, <, <=, >, >=)

# Types of operations on lists:
#   - concatenation ('+')
#   - repetition (*)
#   - membership (in)
#   - length (len())
#   - iteration (for ... in ...)
#   - indexing ([])
#   - slicing ([:])

# Types of functions used on lists:
#   - append()
#   - extend()
#   - insert()
#   - remove()
#   - pop()
#   - clear()
#   - index()
#   - count()
#   - sort()
#   - reverse()
#   - copy()

list_function_names = ["append", "extend", "insert", "remove", "pop", "clear", "index", "count", "sort", "reverse", "copy"]


@dataclass
class StringLiteral:
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)

@dataclass
class IntLiteral:
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)


class operations(Enum):
    #Both string and int
    LT = "<" 
    LE = "<="
    GT = ">"
    GE = ">="
    EQ = "=="
    NE = "!="
    IN = "in"
    ADD = "+"
    MUL = "*" #* can be used by string too but the right side should always be integer

    #String only
    SLICE = "[:]"
    INDEX = "[]"

    #Int only
    SUB = "-"
    DIV = "/"



class Type(Enum):
    INT = "int"
    STR = "str"
    BOOL = "bool"
    FLOAT = "float"
    NONE = "None"
    LIST = "list"


class expression:
    def __init__(self, left, right, operator):
        self.left = left
        self.right = right
        self.relation = operator

    def __str__(self):
        return str(self.left) + " " + str(self.relation) + " " + str(self.right)





def op2str(op):
    match type(op):
        case ast.Lt:
            return "<"
        case ast.LtE:
            return "<="
        case ast.Gt:
            return ">"
        case ast.GtE:
            return ">="
        case ast.Eq:
            return "=="
        case ast.NotEq:
            return "!="
        case ast.In:
            return "in"
        case ast.Add:
            return "+"
        case ast.Mult:
            return "*"
        case ast.Sub:
            return "-"
        case ast.Div:
            return "/"
        case _:
            return "unknown"


def isallint(listtree):
    for node in listtree:
        if(isinstance(node, ast.Constant)):
            if(not isinstance(node.value, int)):
                return False
    return True

def isallstring(listtree):
    for node in listtree:
        if(isinstance(node, ast.Constant)):
            if(not isinstance(node.value, str)):
                return False
    return True


def containsIntliteral(node):
    for n in ast.walk(node):
        if(isinstance(n, ast.Num)):
            return True
    else:
        if(isinstance(node, ast.BinOp)):
            left = containsIntliteral(node.left)
            right = containsIntliteral(node.right)
            containsIntliteral(node.left)
            containsIntliteral(node.right)
        if(isinstance(node, ast.Compare)):
            left = containsIntliteral(node.left)
            for comp in node.comparators:
                right = containsIntliteral(comp)
                containsIntliteral(comp)
            containsIntliteral(node.left)
            if(left or right):
                return True
            if(node.ops[0] == ast.In):
                iterable = node.comparators[0]
                return isallint(iterable.elts)

    return False

def containsStringliteral(node):
    for n in ast.walk(node):
        if(isinstance(n, ast.Str)):
            return True
        
        else:
            if(isinstance(node, ast.BinOp)):
                left = containsStringliteral(node.left)
                right = containsStringliteral(node.right)
                containsStringliteral(node.left)
                containsStringliteral(node.right)
            if(isinstance(node, ast.Compare)):
                left = containsStringliteral(node.left)
                for comp in node.comparators:
                    right = containsStringliteral(comp)
                    containsStringliteral(comp)
                containsStringliteral(node.left)
                if(left or right):
                    return True
                if(node.ops[0] == ast.In):
                    iterable = node.comparators[0]
                    return isallstring(iterable.elts)
    return False

def containsListliteral(node):
    for n in ast.walk(node):
        if(isinstance(n, ast.List)):
            return True
        else:
            if(isinstance(node, ast.BinOp)):
                left = containsListliteral(node.left)
                right = containsListliteral(node.right)
                containsListliteral(node.left)
                containsListliteral(node.right)
            if(isinstance(node, ast.Compare)):
                left = containsListliteral(node.left)
                for comp in node.comparators:
                    right = containsListliteral(comp)
                    containsListliteral(comp)
                containsListliteral(node.left)
                if(left or right):
                    return True
                if(node.ops[0] == ast.In):
                    iterable = node.comparators[0]
                    condisallstring = isallstring(iterable.elts)
                    condisallint = isallint(iterable.elts)
                    if(not (condisallint or condisallstring)):
                        left = node.left
                        return containsListliteral(left)

    return False

   
def containsListFunction(node):
    global list_function_names
    for n in ast.walk(node):
        if(isinstance(n, ast.Call)):
            if(isinstance(n.func, ast.Attribute)):
                if(n.func.attr in list_function_names):
                    return True
    return False
    





def get_parent(tree, node):
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            if child == node:
                return parent
    return None

def getElements(tree, node_) -> set:
    elements = set()
    for node in ast.walk(node_):
        if(isinstance(node, ast.Name) and not (node.id in {"int", "str", "bool", "float", "None", "set"})):
            if(not (isinstance(get_parent(tree, node), ast.Call) or isinstance(get_parent(tree, node), ast.For))):
                elements.add(node.id)
    return elements



def get_args(tree) -> list:
    args = []
    for node in ast.walk(tree):
        if isinstance(node, ast.arg):
            args.append(node.arg)
    return args


def containts_var(tree, varname) -> bool:
    for node in ast.walk(tree):
        if(isinstance(node, ast.Name)):
            if(node.id == varname):
                return True
    return False

def replace_varname(tree, varname, newname):
    for node in ast.walk(tree):
        if(isinstance(node, ast.Name)):
            if(node.id == varname):
                node.id = newname
    return tree



# for each variable get expression it is involved in
def getExpressionNodes(varname, tree) -> list:
    expressions = []
    for node in ast.walk(tree):
        if(isinstance(node, ast.Assign)):
            if(containts_var(node.value, varname)):
                expressions.append(node)
            for target in node.targets:
                if(containts_var(target, varname)):
                    expressions.append(node)
        if(isinstance(node, ast.Compare)):
            if(containts_var(node.left, varname)):
                expressions.append(node)
            for comp in node.comparators:
                if(containts_var(comp, varname)):
                    expressions.append(node)
        if(isinstance(node, ast.BinOp)):
            if(containts_var(node.left, varname)):
                expressions.append(node)
            if(containts_var(node.right, varname)):
                expressions.append(node)
        if(isinstance(node, ast.For)):
            targetname = node.target.id
            body = (node.body)
            iterable = node.iter
            if(isinstance(iterable, ast.Name)):
                if(iterable.id == varname):
                    expressions.append(node)
            if(isinstance(iterable, ast.List)):
                if(containts_var(iterable, varname)):
                    bodycopy = copy.deepcopy(body)
                    for bodynode in bodycopy:
                        bodynode = replace_varname(bodynode, targetname, varname)
                    expressions.append(bodycopy)
        if(isinstance(node, ast.Call)):
            if(isinstance(node.func, ast.Name)):
                if(node.func.id == varname):
                    expressions.append(node)
            if(isinstance(node.func, ast.Attribute)):
                if(node.func.attr == varname):
                    expressions.append(node)
                    
                    
            
    return expressions


def expNode2exp(node):
    exp = None
    if(isinstance(node, ast.Assign)):
        left = node.targets[0].id
        right = expNode2exp(node.value)
        exp = expression(left, right, "=")
    if(isinstance(node, ast.Compare)):
        left = expNode2exp(node.left)
        right = expNode2exp(node.comparators[0])
        op = op2str(node.ops[0])
        exp = expression(left, right, op)
    if(isinstance(node, ast.BinOp)):
        left = expNode2exp(node.left)
        right = expNode2exp(node.right)
        op = op2str(node.op)
        exp = expression(left, right, op)
    if(isinstance(node, ast.Num)):
        exp = IntLiteral(node.n)
    if(isinstance(node, ast.Str)):
        exp = StringLiteral(node.s)
    if(isinstance(node, ast.Name)):
        exp = node.id

    return exp

# We will determine if it has an int only operation or it has componenets that are int onlys or it has in literals
# List of int only operations:
'''
arichmetic (/ // % **)

'''
def hasIntonly(node):
    for n in ast.walk(node):
        if(isinstance(n, ast.BinOp)):
            if(isinstance(n.op, ast.Div)):
                return True
            if(isinstance(n.op, ast.FloorDiv)):
                return True
            if(isinstance(n.op, ast.Mod)):
                return True
            if(isinstance(n.op, ast.Pow)):
                return True
        if(isinstance(n, ast.Num)):
            return True
        if(isinstance(n, ast.Constant)):
            if(isinstance(n.value, int)):
                return True

    return False

# We will determine if it has a string only operation or it has componenets that are string onlys or it has string literals
def hasStringonly(node):
    for n in ast.walk(node):
        if(isinstance(n, ast.Str)):
            return True
        if(isinstance(n, ast.Constant)):
            if(isinstance(n.value, str)):
                return True
            
    return False

def hasListonly(node):
    for n in ast.walk(node):
        if(isinstance(n, ast.List)):
            return True
    return False

def getOp(node):
    if(isinstance(node, ast.BinOp)):
        if(isinstance(node.op, ast.Div)):
            return "/"
        if(isinstance(node.op, ast.FloorDiv)):
            return "//"
        if(isinstance(node.op, ast.Mod)):
            return "%"
        if(isinstance(node.op, ast.Pow)):
            return "**"
        if(isinstance(node.op, ast.Add)):
            return "+"
        if(isinstance(node.op, ast.Mult)):
            return "*"
        if(isinstance(node.op, ast.Sub)):
            return "-"
    if(isinstance(node, ast.Compare)):
        if(isinstance(node.ops[0], ast.Eq)):
            return "=="
        if(isinstance(node.ops[0], ast.NotEq)):
            return "!="
        if(isinstance(node.ops[0], ast.Lt)):
            return "<"
        if(isinstance(node.ops[0], ast.LtE)):
            return "<="
        if(isinstance(node.ops[0], ast.Gt)):
            return ">"
        if(isinstance(node.ops[0], ast.GtE)):
            return ">="
        if(isinstance(node.ops[0], ast.In)):
            return "in"
    if isinstance(node, ast.Call):
        if(isinstance(node.func, ast.Name)):
            return node.func.id
    if(isinstance(node, ast.Subscript)):
        return "[]"
    if(isinstance(node, ast.For)):
        return "for"
    
    return "unknown"


def getinthintnum(tree, varname, exprmap):
# Hints for int:
#   - arithmetic (+, -, *, /, //, %, **)
#   - comparison (==, !=, <, <=, >, >=)
#   - membership (in)
    
    oplist = ["+", "-", "*", "/", "//", "%", "**", "==", "!=", "<", "<=", ">", ">=", "in"]
    inthintnum = 0
    for expr in exprmap[varname]:
        if(isinstance(expr, ast.BinOp)):
            op = getOp(expr)
            if(op in oplist):
                inthintnum += 1
        if(isinstance(expr, ast.Compare)):
            op = getOp(expr)
            if(op in oplist):
                inthintnum += 1
    return inthintnum

def getstrhintnum(tree, varname, exprmap):
# Hints for str:
#   - concatenation ('+')
#   - comparison (==, !=, <, <=, >, >=)
#   - membership (in)
#   - slicing ([:])
#   - indexing ([])
#   - repetition (*)
#   - length (len())
#   - iteration (for ... in ...)
    oplist = ["+", "==", "!=", "<", "<=", ">", ">=", "in", "[:]", "[]", "*"]
    strhintnum = 0
    for expr in exprmap[varname]:
        if(isinstance(expr, ast.BinOp)):
            op = getOp(expr)
            if(op in oplist):
                strhintnum += 1
        if(isinstance(expr, ast.Compare)):
            op = getOp(expr)
            if(op in oplist):
                strhintnum += 1
        if(isinstance(expr, ast.For)):
            strhintnum += 1
        if(isinstance(expr, ast.Call)):
            op = getOp(expr)
            if(op in oplist):
                strhintnum += 1
        if(isinstance(expr, ast.Subscript)):
            strhintnum += 1

    return strhintnum

def getlisthintnum(tree, varname, exprmap):
# Hints for list:
#   - concatenation ('+')
#   - repetition (*)
#   - membership (in)
#   - length (len())
#   - iteration (for ... in ...)
#   - indexing ([])
#   - slicing ([:])
#   - append()
#   - extend()
#   - insert()
#   - remove()
#   - pop()
#   - clear()
#   - index()
#   - count()
#   - sort()
#   - reverse()
    
    oplist = ["+", "*", "in", "len", "for", "[]", "[:]", "append", "extend", "insert", "remove", "pop", "clear", "index", "count", "sort", "reverse"]
    listhintnum = 0
    for expr in exprmap[varname]:
        if(isinstance(expr, ast.Assign)):
            target = expr.targets[0]
            if target.id == varname:
                if(isinstance(expr.value, ast.List)):
                    listhintnum += 1
                
        if(isinstance(expr, ast.BinOp)):
            op = getOp(expr)
            if(op in oplist):
                listhintnum += 1
        if(isinstance(expr, ast.Compare)):
            op = getOp(expr)
            if(op in oplist):
                listhintnum += 1
        if(isinstance(expr, ast.For)):
            listhintnum += 1
        if(isinstance(expr, ast.Call)):
            op = getOp(expr)
            if(op in oplist):
                listhintnum += 1
        if(isinstance(expr, ast.Subscript)):
            listhintnum += 1
    return listhintnum


                    







def derivetype(tree, varname, exprmap):
    typemap = {}
    exprlist = exprmap[varname]

    inthintnum = getinthintnum(tree, varname, exprmap)
    strhintnum = getstrhintnum(tree, varname, exprmap)
    listhintnum = getlisthintnum(tree, varname, exprmap)
    intprob = inthintnum/(inthintnum + strhintnum + listhintnum)
    strprob = strhintnum/(inthintnum + strhintnum + listhintnum)
    listprob = listhintnum/(inthintnum + strhintnum + listhintnum)
    typemap["int"] = intprob
    typemap["str"] = strprob
    typemap["list"] = listprob

    return typemap






def getfuncdefnodes(tree):
    funcdefnodes = []
    for node in ast.walk(tree):
        if(isinstance(node, ast.FunctionDef)):
            funcdefnodes.append(node)
    return funcdefnodes

def runtheprocess(tree):
    varlist = getElements(tree, tree)
    exprmap = {}
    exprlist = []
    for var in varlist:
        exprmap[var] = getExpressionNodes(var, tree)
        for expr in exprmap[var]:
            exprlist.append(expr)
    for var in varlist:
        print(var, ":")
        typeprob = derivetype(tree, var, exprmap)
        print(typeprob)
        for e in (exprmap[var]):
            print(ast.dump(e, indent=2))
            print(" ")
        print("=====================================")


# usage: python sbst.py examples/example$N$.py
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="the target python file to generate unit tests for")
    args = parser.parse_args()




    with open(args.target, "r") as f:
        code = f.read()

    
    tree = ast.parse(code)

    # print(ast.dump(tree, indent=2))

    # varlist = getElements(tree, tree)
    # exprmap = {}
    # exprlist = []
    # for var in varlist:
    #     exprmap[var] = getExpressionNodes(var, tree)
    #     for expr in exprmap[var]:
    #         exprlist.append(expr)

    # for var in varlist:
    #     print(var, ":")
    #     print(exprmap[var])
    
    funclist = getfuncdefnodes(tree)
    for func in funclist:
        print(func.name, ":", get_args(func))
        print("=====================================")
        runtheprocess(func)
        print(" ")
        print("=====================================")




