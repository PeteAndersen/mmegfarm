from antlr4 import InputStream, CommonTokenStream

from .PrizeFormulaParser import PrizeFormulaParser
from .PrizeFormulaLexer import PrizeFormulaLexer
from .PrizeFormulaVisitor import PrizeFormulaVisitor


def get_rewards(reward_string):
    lexer = PrizeFormulaLexer(InputStream(reward_string))
    stream = CommonTokenStream(lexer)
    parser = PrizeFormulaParser(stream)
    tree = parser.rewards()
    visitor = PrizeFormulaVisitor()
    return visitor.visit(tree)
