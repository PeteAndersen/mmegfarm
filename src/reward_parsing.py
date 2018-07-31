import django
import json
from antlr4 import CommonTokenStream, InputStream

django.setup()

from bestiary.parse.PrizeFormulaParser import PrizeFormulaParser
from bestiary.parse.PrizeFormulaLexer import PrizeFormulaLexer
from bestiary.parse.PrizeFormulaVisitor import PrizeFormulaVisitor


rewards = InputStream('victory[p:100[40(runePattern:pattern_reward_rune_0229:1),10(runePattern:pattern_reward_rune_0230:1),10(runePattern:pattern_reward_rune_0413:1),3(runePattern:pattern_reward_rune_0414:1)],p:1000[10(creaturePattern:pattern_reward_creature_0000:1)],sc:840,xp:910,p:100[4(hc:5)],p:100[25(energy:3)],p:1000[120(smallGatchaStonePart:5),24(smallGatchaStonePart:10)],p:100[7(instantTicket:1)]];w:2[xp:404];w:2[sc:373];w:3[xp:606];w:3[sc:560]')
lexer = PrizeFormulaLexer(rewards)
stream = CommonTokenStream(lexer)
parser = PrizeFormulaParser(stream)
tree = parser.rewards()

visitor = PrizeFormulaVisitor()
result = visitor.visit(tree)
print(json.dumps(result))