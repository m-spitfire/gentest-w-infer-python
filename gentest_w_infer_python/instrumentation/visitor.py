import ast




class ChangeAndsToNested(ast.NodeTransformer):
    '''
    Changing ANDed predicates to Nested If statements.
    '''
    def visit_If(self, node):
        self.generic_visit(node)
        if isinstance(node.test, ast.BoolOp) and isinstance(node.test.op, ast.And):
            new_node = None
            for value in node.test.values:
                new_node = ast.If(test=value, body=[new_node] if new_node else node.body, orelse = node.orelse)
            new_node.orelse = node.orelse
            return new_node 
        return node


def return_predicate_from_match(node,left):
        '''
        Helper function for ChangeMatchToIf ast node visitor
        to get predicate from match statement. 
        '''
        match node:
            case ast.MatchValue():
                return ast.Compare(
                    left = left,
                    ops = [ast.Eq()],
                    comparators = [node.value]
                )
            case ast.MatchOr():
                return ast.BoolOp(
                    op = ast.Or(),
                    values = [return_predicate_from_match(x, left) for x in node.patterns]
                )
            case ast.MatchAs():
                return True

class ChangeMatchToIf(ast.NodeTransformer):
    '''
    Chaning Match Statements to If statements
    '''
    def visit_Match(self, node):
        self.generic_visit(node)
        new_node = None
        for (i, case) in enumerate(reversed(node.cases)):
            predicate_of_match = return_predicate_from_match(case.pattern, node.subject)
            if isinstance(predicate_of_match, bool):
                new_node = case.body
            else: 
                new_node = ast.If(
                    test = predicate_of_match,
                    body = case.body,
                    orelse = [new_node] if new_node else []
                )
        return new_node


class ChangeOrToElseIfs(ast.NodeTransformer):
    '''
    Chaning Or statements to else if statements
    with same body as original if node
    '''
    def visit_If(self, node):
        self.generic_visit(node)
        if isinstance(node.test, ast.BoolOp) and isinstance(node.test.op, ast.Or):
            new_node = None
            for value in node.test.values:
                new_node = ast.If(
                    test = value,
                    body = node.body,
                    orelse = [new_node] if new_node else node.orelse
                )
            return new_node
        else:
            return node
        



class ChangeComplexPredicates(ast.NodeTransformer):
    '''
    Changing Complex nodes for aggressive case of Or And 
    Not statements, and IfExpression
    '''
    def visit_If(self, node):
        self.generic_visit(node)
        if isinstance(node.test, ast.BoolOp):
            pass

