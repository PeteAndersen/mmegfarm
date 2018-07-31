import collections
from antlr4 import *
from .PrizeFormulaParser import PrizeFormulaParser


def deepupdate(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = deepupdate(d.get(k, {}), v)
        else:
            d[k] = v
    return d


class PrizeFormulaVisitor(ParseTreeVisitor):
    def visitChildren(self, node, **kwargs):
        result = kwargs.get('default')
        n = node.getChildCount()
        for i in range(n):
            if not self.shouldVisitNextChild(node, result):
                return

            c = node.getChild(i)
            childResult = c.accept(self)
            result = self.aggregateResult(result, childResult)

        return result

    def aggregateResult(self, aggregate, nextResult):
        if nextResult is None:
            return aggregate

        if aggregate is None:
            return nextResult
        elif isinstance(aggregate, list):
            return aggregate + [nextResult]
        elif isinstance(aggregate, dict):
            return deepupdate(aggregate, nextResult)
        else:
            raise ValueError(f"Don't know how to aggregate a type of {type(aggregate)}")

    def visitRewards(self, ctx: PrizeFormulaParser.RewardsContext):
        print(f'visitRewards: {ctx.getText()}')
        results = self.visitChildren(ctx, default={})

        return results

    def visitProbabilityReward(self, ctx: PrizeFormulaParser.ProbabilityRewardContext):
        print(f'visitProbabilityReward: {ctx.getText()}')
        max_roll = int(ctx.AMOUNT().getText())
        items = self.visitChildren(ctx, default=[])

        # Change each item's probability number to a percentage
        for item in items:
            item['probability'] /= max_roll

        return {
            'type': 'dropGroup',
            'value': items
        }

    def visitDailyReward(self, ctx: PrizeFormulaParser.DailyRewardContext):
        print(f'visitDailyReward: {ctx.getText()}')
        return self.visitChildren(ctx)

    def visitVictoryReward(self, ctx: PrizeFormulaParser.VictoryRewardContext):
        print(f'visitVictoryReward: {ctx.getText()}')
        return {
            'victory': self.visitChildren(ctx, default=[])
        }

    def visitPartialProbReward(self, ctx: PrizeFormulaParser.PartialProbRewardContext):
        print(f'visitPartialProbReward: {ctx.getText()}')
        probability = int(ctx.AMOUNT().getText())
        item = self.visitChildren(ctx, default={})
        item.update({
            'probability': probability
        })
        return item

    def visitSimpleReward(self, ctx: PrizeFormulaParser.SimpleRewardContext):
        print(f'visitSimpleReward: {ctx.getText()}')
        return {
            'type': ctx.CURRENCY().getText(),
            'value': int(ctx.AMOUNT().getText())
        }

    def visitXpReward(self, ctx: PrizeFormulaParser.XpRewardContext):
        print(f'visitXpReward: {ctx.getText()}')
        return {
            'type': 'xp',
            'value': int(ctx.AMOUNT().getText())
        }

    def visitXpGuildReward(self, ctx: PrizeFormulaParser.XpGuildRewardContext):
        print(f'visitXpGuildReward: {ctx.getText()}')
        return self.visitChildren(ctx)
        # No children

    def visitGuildPotionReward(self, ctx: PrizeFormulaParser.GuildPotionRewardContext):
        print(f'visitGuildPotionReward: {ctx.getText()}')
        return self.visitChildren(ctx)

    def visitAddMaxEnergyReward(self, ctx: PrizeFormulaParser.AddMaxEnergyRewardContext):
        print(f'visitAddMaxEnergyReward: {ctx.getText()}')
        return self.visitChildren(ctx)

    def visitRunePattern(self, ctx: PrizeFormulaParser.RunePatternContext):
        print(f'visitRunePattern: {ctx.getText()}')

        return {
            'type': 'runePattern',
            'quantity': int(ctx.AMOUNT().getText()),
            'value': ctx.SKU().getText(),
        }

    def visitRune(self, ctx: PrizeFormulaParser.RuneContext):
        print(f'visitRune: {ctx.getText()}')
        return self.visitChildren(ctx)

    def visitEvolutionItemPattern(self, ctx: PrizeFormulaParser.EvolutionItemPatternContext):
        print(f'visitEvolutionItemPattern: {ctx.getText()}')
        return self.visitChildren(ctx)

    def visitCreaturePattern(self, ctx: PrizeFormulaParser.CreaturePatternContext):
        print(f'visitCreaturePattern: {ctx.getText()}')

        return {
            'type': 'creaturePattern',
            'value': ctx.SKU().getText(),
            'quantity': int(ctx.AMOUNT().getText())
        }

    def visitCreature(self, ctx: PrizeFormulaParser.CreatureContext):
        print(f'visitCreature: {ctx.getText()}')
        return self.visitChildren(ctx)


del PrizeFormulaParser
