from dataclasses import dataclass
from enum import Enum
import enum
import argparse
import ast
import os

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


@dataclass
class StringLiteral:
    def __init__(self, value):
        self.value = value

@dataclass
class IntLiteral:
    def __init__(self, value):
        self.value = value


# class AstExpression():
#     def __init__(self, expr: ast.Expression):
        


@enum.unique
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


class expression:
    def __init__(self, left, right, operator):
        self.left = left
        self.right = right
        self.relation = operator

    def __str__(self):
        return str(self.left) + " " + str(self.relation) + " " + str(self.right)

def op2str(op):
    match op:
        case ast.Lt():
            return operations.LT
        case ast.LtE():
            return operations.LE
        case ast.Gt():
            return operations.GT
        case ast.GtE():
            return operations.GE
        case ast.Eq():
            return operations.EQ
        case ast.NotEq():
            return operations.NE
        case ast.In():
            return operations.IN
        case ast.Add():
            return operations.ADD
        case ast.Mult():
            return operations.MUL
        case ast.Sub():
            return operations.SUB
        case ast.Div():
            return operations.DIV
        case _:
            return "unknown"


def containsIntliteral(node):
    for n in ast.walk(node):
        if(isinstance(n, ast.Num)):
            return True
    return False

def containsStringliteral(node):
    for n in ast.walk(node):
        if(isinstance(n, ast.Str)):
            return True
    return False

def containsStringOp(node):
# Types of operations exclusively on strings:
#   - iteration (for ... in ...)
#   - length (len())
    for n in ast.walk(node):
        if(isinstance(n, ast.For)):
            return True
        if(isinstance(n, ast.Call)):
            if(isinstance(n.func, ast.Name)):
                if(n.func.id == "len"):
                    return True
        if(isinstance(n, ast.BinOp)):
            if(isinstance(n.op, ast.Add)):
                return True
            if(isinstance(n.op, ast.Mult)):
                if(containsIntliteral(n.right)):
                    return True
        if(isinstance(n, ast.Compare)):
            if(isinstance(n.ops[0], ast.In)):
                return True
    return False

def containsIntOp(node):
# Types of operations exclusively on integers:
#   -, /, //, %, **
    for n in ast.walk(node):
        if(isinstance(n, ast.BinOp)):
            if(isinstance(n.op, ast.Sub)):
                return True
            if(isinstance(n.op, ast.Div)):
                return True
            if(isinstance(n.op, ast.FloorDiv)):
                return True
            if(isinstance(n.op, ast.Mod)):
                return True
            if(isinstance(n.op, ast.Pow)):
                return True
    return False
   



def getElements(tree) -> set:
    elements = set()
    for node in ast.walk(tree):
        if(isinstance(node, ast.Name)):
            elements.add(node.id)
    return elements


def get_args(tree) -> list:
    args = []
    for node in ast.walk(tree):
        if(isinstance(node, ast.arguments)):
            for arg in node.args:
                args.append(arg.arg)
    return args


# for each variable get expression it is involved in
def getExpressionNodes(varname, tree) -> list:
    expressions = []
    for node in ast.walk(tree):
        if(isinstance(node, ast.Assign)):
            if(isinstance(node.targets[0], ast.Name)):
                if(node.targets[0].id == varname):
                    expressions.append(node.value)
        if(isinstance(node, ast.Compare)):
            if(isinstance(node.left, ast.Name)):
                if(node.left.id == varname):
                    expressions.append(node)
    return expressions


def deriveType(var, exprnodelist):
    probmap = {}
    inthintnum = 0
    strhintnum = 0
    for expnode in exprnodelist:
            if containsIntliteral(expnode):
                print('odsfl;jasldfkjasdf')
                inthintnum += 1
            if containsIntOp(expnode):
                inthintnum += 1
            if containsStringliteral(expnode):
                strhintnum += 1
            if containsStringOp(expnode):
                strhintnum += 1
    intprob = inthintnum/(inthintnum+strhintnum)
    strprob = strhintnum/(inthintnum+strhintnum)
    probmap["int"] = intprob
    probmap["str"] = strprob
    return probmap 









# usage: python sbst.py examples/example$N$.py
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="the target python file to generate unit tests for")
    args = parser.parse_args()




    with open(args.target, "r") as f:
        code = f.read()
    
    tree = ast.parse(code)
    # print("Parsing target file", args.target)

    # for node in ast.walk(tree):
    #     detect_if_branches(node)

    # print(ast.dump(tree, indent=2))
    print("=====================================")


    varlist = getElements(tree)

    arglist = get_args(tree)

    exprmap = {}



    for var in varlist:
        exprmap[var] = getExpressionNodes(var, tree)

    for exp in exprmap.items():
        print(exp)




    print(varlist)
    print(arglist)

    for arg in arglist:
        print(deriveType(arg, exprmap[arg]))

    for exp in exprmap.items():
        for e in exp[1]:
            print("=====================================")
            print(exp[0])
            print(containsIntliteral(e))
            print(containsStringliteral(e))
            print(ast.dump(e, indent=2))
            print("=====================================")