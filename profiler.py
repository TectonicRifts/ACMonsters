import math

class PlayerProfile:
    def __init__(self, name, magic_a, melee_a, missile_a, melee_d, magic_d, melee_d_mod):
        self.name = name
        # attack
        self.magic_a = magic_a
        self.melee_a = melee_a
        self.missile_a = missile_a

        # defense
        self.melee_d = melee_d
        self.magic_d = magic_d
        self.melee_d_mod = melee_d_mod


def calc_skill(player_skill, skill_modifier, monster_skill):
    player_skill = int(player_skill)
    skill_modifier = float(skill_modifier)
    player_skill = round(player_skill * skill_modifier, 1)
    monster_skill = int(monster_skill)

    result = 1 - 1 / (1 + math.exp(0.03 * (player_skill - monster_skill)))
    return round(result * 100, 2)

profile_max = PlayerProfile("Max", 561, 607, 556, 580, 417, 1.55)
profile_150 = PlayerProfile("150", 435, 482, 430, 460, 322, 1.45)
