# File with all configurations
from classes import martial, blaster

# Heroes config
heroes = []
heroes.append(martial("barbarian", 12, 14, 2, "2d6+4", 1, 0, {"dex": 2, "wis": -1}, False))
heroes.append(martial("fighter", 10, 16, 2, "1d12+4", 1, 0, {"dex": 4, "wis": 0}, False))
heroes.append(blaster("cleric", 8, 12, 13, "3d6", 0, {"dex": 0, "wis": 3}, True))

# Monsters config
monsters = []
monsters.append(martial("goblin", 12, 14, 2, "2d6+4", 1, 0, {"dex": 2, "wis": 0}, False))
monsters.append(martial("goblin", 12, 14, 2, "2d6+4", 1, 0, {"dex": 2, "wis": 0}, False))
monsters.append(blaster("goblin shaman", 8, 12, 13, "3d6", 0, {"dex": 1, "wis": 2}, True))

monte_carlo_iterations = 1000
