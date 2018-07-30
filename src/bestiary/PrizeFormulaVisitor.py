from antlr4 import *
from .PrizeFormulaParser import PrizeFormulaParser


class PrizeFormulaVisitor(ParseTreeVisitor):
    def aggregateResult(self, aggregate, nextResult):
        if isinstance(aggregate, list):
            return aggregate + [nextResult]
        else:
            raise ValueError('Attempting to append result to non-list object')

    def visitRewards(self, ctx: PrizeFormulaParser.RewardsContext):
        print(f'visitRewards: {ctx.getText()}')
        return self.visitChildren(ctx)

    def visitReward(self, ctx: PrizeFormulaParser.RewardContext):
        print(f'visitReward: {ctx.getText()}')
        return self.visitChildren(ctx)

    def visitSingleReward(self, ctx: PrizeFormulaParser.SingleRewardContext):
        print(f'visitSingleReward: {ctx.getText()}')
        return self.visitChildren(ctx)

    def visitProbabilityReward(self, ctx: PrizeFormulaParser.ProbabilityRewardContext):
        print(f'visitProbabilityReward: {ctx.getText()}')
        return self.visitChildren(ctx)

    def visitDailyReward(self, ctx: PrizeFormulaParser.DailyRewardContext):
        print(f'visitDailyReward: {ctx.getText()}')
        return self.visitChildren(ctx)

    def visitWaveReward(self, ctx: PrizeFormulaParser.WaveRewardContext):
        print(f'visitWaveReward: {ctx.getText()}')
        return {
            'wave': int(ctx.AMOUNT().getText()),
            'rewards': self.visitChildren(ctx)
        }

    def visitVictoryReward(self, ctx: PrizeFormulaParser.VictoryRewardContext):
        print(f'visitVictoryReward: {ctx.getText()}')
        return {
            'victory': self.visitChildren(ctx)
        }

    def visitBattleReward(self, ctx: PrizeFormulaParser.BattleRewardContext):
        print(f'visitBattleReward: {ctx.getText()}')
        return self.visitChildren(ctx)

    def visitPartialProbReward(self, ctx: PrizeFormulaParser.PartialProbRewardContext):
        print(f'visitPartialProbReward: {ctx.getText()}')
        return self.visitChildren(ctx)

    def visitSimpleReward(self, ctx: PrizeFormulaParser.SimpleRewardContext):
        print(f'visitSimpleReward: {ctx.getText()}')
        return {ctx.CURRENCY().getText(): int(ctx.AMOUNT().getText())}

    def visitXpReward(self, ctx: PrizeFormulaParser.XpRewardContext):
        print(f'visitXpReward: {ctx.getText()}')
        return {'xp': int(ctx.AMOUNT().getText())}

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

    def visitPatternReward(self, ctx: PrizeFormulaParser.PatternRewardContext):
        print(f'visitPatternReward: {ctx.getText()}')
        return self.visitChildren(ctx)

    def visitRunePattern(self, ctx: PrizeFormulaParser.RunePatternContext):
        print(f'visitRunePattern: {ctx.getText()}')
        return self.visitChildren(ctx)

    def visitRune(self, ctx: PrizeFormulaParser.RuneContext):
        print(f'visitRune: {ctx.getText()}')
        return self.visitChildren(ctx)

    def visitEvolutionItemPattern(self, ctx: PrizeFormulaParser.EvolutionItemPatternContext):
        print(f'visitEvolutionItemPattern: {ctx.getText()}')
        return self.visitChildren(ctx)

    def visitCreaturePattern(self, ctx: PrizeFormulaParser.CreaturePatternContext):
        print(f'visitCreaturePattern: {ctx.getText()}')
        return self.visitChildren(ctx)

    def visitCreature(self, ctx: PrizeFormulaParser.CreatureContext):
        print(f'visitCreature: {ctx.getText()}')
        return self.visitChildren(ctx)


del PrizeFormulaParser
