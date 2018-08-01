import collections

from antlr4 import *

from .PrizeFormulaParser import PrizeFormulaParser
from .evolution_items import evolution_item_reward
from .runes import reward_rune
from .xml import get_creatures_from_rewardpattern


def _deepupdate(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = _deepupdate(d.get(k, {}), v)
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
            return _deepupdate(aggregate, nextResult)
        else:
            raise ValueError(f"Don't know how to aggregate a type of {type(aggregate)}")

    def visitRewards(self, ctx: PrizeFormulaParser.RewardsContext):
        return self.visitChildren(ctx, default=[])

    def visitProbabilityReward(self, ctx: PrizeFormulaParser.ProbabilityRewardContext):
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
        raise NotImplementedError()

    def visitVictoryReward(self, ctx: PrizeFormulaParser.VictoryRewardContext):
        return self.visitChildren(ctx, default=[])

    def visitPartialProbReward(self, ctx: PrizeFormulaParser.PartialProbRewardContext):
        probability = int(ctx.AMOUNT().getText())
        item = self.visitChildren(ctx, default={})
        item.update({
            'probability': probability
        })
        return item

    def visitSimpleReward(self, ctx: PrizeFormulaParser.SimpleRewardContext):
        return {
            'type': ctx.CURRENCY().getText(),
            'quantity': int(ctx.AMOUNT().getText())
        }

    def visitXpReward(self, ctx: PrizeFormulaParser.XpRewardContext):
        return {
            'type': 'xp',
            'quantity': int(ctx.AMOUNT().getText())
        }

    def visitXpGuildReward(self, ctx: PrizeFormulaParser.XpGuildRewardContext):
        raise NotImplementedError()

    def visitGuildPotionReward(self, ctx: PrizeFormulaParser.GuildPotionRewardContext):
        raise NotImplementedError()

    def visitAddMaxEnergyReward(self, ctx: PrizeFormulaParser.AddMaxEnergyRewardContext):
        raise NotImplementedError()

    def visitRunePattern(self, ctx: PrizeFormulaParser.RunePatternContext):
        rune_data = reward_rune(ctx.SKU().getText())

        return {
            'type': 'runePattern',
            'quantity': int(ctx.AMOUNT().getText()),
            'value': rune_data,
        }

    def visitRune(self, ctx: PrizeFormulaParser.RuneContext):
        raise NotImplementedError()

    def visitEvolutionItemPattern(self, ctx: PrizeFormulaParser.EvolutionItemPatternContext):
        item_data = evolution_item_reward(ctx.SKU().getText())
        return {
            'type': 'evolutionItemPattern',
            'quantity': int(ctx.AMOUNT().getText()),
            'value': item_data,
        }

    def visitCreaturePattern(self, ctx: PrizeFormulaParser.CreaturePatternContext):
        creatures = get_creatures_from_rewardpattern(ctx.SKU().getText())
        ids = list(creatures.values_list('pk', flat=True))

        return {
            'type': 'creaturePattern',
            'value': ids,
            'quantity': int(ctx.AMOUNT().getText())
        }

    def visitCreature(self, ctx: PrizeFormulaParser.CreatureContext):
        raise NotImplementedError()

    def visitWaveReward(self, ctx: PrizeFormulaParser.WaveRewardContext):
        # We don't care about wave rewards right now.
        # Don't visit children
        return None


del PrizeFormulaParser
