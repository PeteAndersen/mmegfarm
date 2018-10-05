from antlr4 import InputStream, CommonTokenStream

from .PrizeFormulaParser import PrizeFormulaParser
from .PrizeFormulaLexer import PrizeFormulaLexer
from .PrizeFormulaVisitor import PrizeFormulaVisitor


def get_rewards(reward_string):
    # Parse using grammar
    lexer = PrizeFormulaLexer(InputStream(reward_string))
    stream = CommonTokenStream(lexer)
    parser = PrizeFormulaParser(stream)
    tree = parser.rewards()
    visitor = PrizeFormulaVisitor()
    rewards = visitor.visit(tree)

    # Convert single reward groups into plain rewards
    rewards = [
        reward['value'][0] if reward['type'] == 'dropGroup' and len(reward.get('value', [])) == 1 else reward for reward in rewards
    ]

    return rewards
