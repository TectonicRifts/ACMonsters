import math


def calc_skill(player_skill, skill_modifier, monster_skill):
    player_skill = int(player_skill)
    skill_modifier = float(skill_modifier)
    player_skill = round(player_skill * skill_modifier, 1)
    monster_skill = int(monster_skill)

    result = 1 - 1 / (1 + math.exp(0.03 * (player_skill - monster_skill)))
    return round(result * 100, 2)
