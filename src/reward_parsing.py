import django
import json
from antlr4 import CommonTokenStream, InputStream

django.setup()

from bestiary.parse.PrizeFormulaParser import PrizeFormulaParser
from bestiary.parse.PrizeFormulaLexer import PrizeFormulaLexer
from bestiary.parse.PrizeFormulaVisitor import PrizeFormulaVisitor


rewards = InputStream('victory[sc:1750,xp:2150,p:100[34(evolutionItemPattern:pattern_reward_evolution_item_0001:1),33(evolutionItemPattern:pattern_reward_evolution_item_0002:1),33(evolutionItemPattern:pattern_reward_evolution_item_0004:1)]];w:5[sc:1458];w:4[sc:1215];w:3[sc:1013];w:2[sc:844];w:5[xp:1792];w:4[xp:1493];w:3[xp:1244];w:2[xp:1037]')
lexer = PrizeFormulaLexer(rewards)
stream = CommonTokenStream(lexer)
parser = PrizeFormulaParser(stream)
tree = parser.rewards()

visitor = PrizeFormulaVisitor()
result = visitor.visit(tree)
print(json.dumps(result))
