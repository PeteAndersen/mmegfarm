grammar PrizeFormula;

rewards
	: reward (';' reward)*
	;

reward
	: singleReward
	| probabilityReward
	| dailyReward
	| waveReward
	| victoryReward
	;

singleReward
	: simpleReward
	| patternReward
	| addMaxEnergyReward
	| creature
	| rune
	| guildPotionReward
	;

probabilityReward
	: 'p:' AMOUNT '[' partialProbReward (',' partialProbReward)* ']'
	;

dailyReward
	: 'daily:' AMOUNT '[' simpleReward ']'
	;
	
waveReward
	: 'w:' AMOUNT '[' battleReward (',' battleReward)* ']'
	;
	
victoryReward
	: 'victory[' battleReward (',' battleReward)* ']'
	;

battleReward
	: probabilityReward
	| singleReward
	| xpReward
	;

partialProbReward
	: AMOUNT '(' singleReward (',' singleReward)* ')'
	;

simpleReward
	: CURRENCY ':' AMOUNT
	;
	
xpReward
	: 'xp:' AMOUNT
	;
	
guildPotionReward
	: 'guildPotion:' SKU ':' AMOUNT
	;

addMaxEnergyReward
	: ENERGY ':addMax'
	;
	
patternReward
	: runePattern
	| evolutionItemPattern
	| creaturePattern
	;
	
runePattern
	: 'runePattern:' SKU ':' AMOUNT
	;

rune
	: 'rune:' SKU
	;

evolutionItemPattern
	: 'evolutionItemPattern:' SKU ':' AMOUNT
	;

creaturePattern
	: 'creaturePattern:' SKU ':' AMOUNT
	;

creature
	: 'creature:' SKU
	;

AMOUNT
	: [0-9]+
	;

CURRENCY
	: 'sc' | 'hc' | 'instantTicket' | 'book'
	| 'smallKey' | 'mediumKey' | 'bigKey' | 'darkKey'
	| 'smallPotion' | 'mediumPotion' | 'bigPotion' 
	| 'smallGatchaChest' | 'mediumGatchaChest' | 'bigGatchaChest' | 'darkGatchaChest'
	| 'smallGatchaStone' | 'mediumGatchaStone' | 'bigGatchaStone'
	| 'smallGatchaStonePart' | 'mediumGatchaStonePart' | 'bigGatchaStonePart'
	| 'airGatchaStone' | 'fireGatchaStone' | 'waterGatchaStone' | 'earthGatchaStone'
	| 'airGatchaStonePart' | 'fireGatchaStonePart' | 'waterGatchaStonePart' | 'earthGatchaStonePart'
    | 'firstJokerGatcha' | 'firstJokerGatchaPart'
    | 'secondJokerGatcha' | 'secondJokerGatchaPart'
    | 'thirdJokerGatcha' | 'thirdJokerGatchaPart'
    | 'fourthJokerGatcha' | 'fourthJokerGatchaPart'
    | 'fifthJokerGatcha' | 'fifthJokerGatchaPart'
    | 'sixthJokerGatcha' | 'sixthJokerGatchaPart'
    | 'seventhJokerGatcha' | 'seventhJokerGatchaPart'
    | 'eighthJokerGatcha' | 'eighthJokerGatchaPart'
    | 'ninthJokerGatcha' | 'ninthJokerGatchaPart'
    | 'tenthJokerGatcha' | 'tenthJokerGatchaPart'
	| 'creaturePart1' | 'creaturePart2' | 'creaturePart3' | 'creaturePart4' | 'creaturePartX'
	| 'energy' | 'pvpEnergy' | 'passPoint' | 'reputationPoint' | 'spellPoint' | 'rankingPoint' | 'xpAvatar'
	| 'guildCoin'
    | 'smallFireEvolutionItem' | 'smallWaterEvolutionItem' | 'smallAirEvolutionItem' | 'smallEarthEvolutionItem'
    | 'smallMateriaEvolutionItem' | 'smallChimeraEvolutionItem' | 'smallAnimaEvolutionItem' | 'bigFireEvolutionItem'
    | 'bigWaterEvolutionItem' | 'bigAirEvolutionItem' | 'bigEarthEvolutionItem' | 'bigMateriaEvolutionItem'
    | 'bigChimeraEvolutionItem' | 'bigAnimaEvolutionItem'
    | 'smallGuildXpPotion' | 'mediumGuildXpPotion' |  'bigGuildXpPotion' | 'epicGuildXpPotion' | 'legendaryGuildXpPotion'
	| 'xpGuild' | 'battleCommand'
	;

ENERGY
	: 'energy'
	| 'pvpEnergy'
	;

SKU: [a-zA-Z_0-9]+ ;

WS
	: [\t\r\n] -> skip
	;