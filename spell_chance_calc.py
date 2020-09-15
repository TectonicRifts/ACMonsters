def convert(chances):
    spellbook = []

    for chance in chances:
        none = get_prob_none(spellbook)
        spellbook.append(chance / none)

    return spellbook


def get_prob_none(chances):
    pr = 1.0

    for chance in chances:
        pr *= 1.0 - chance

    return pr


def get_prob_any(chances):
    return 1.0 - get_prob_none(chances)


def get_spell_pr(total_spells):
    chances = []

    # total_spells = 14

    for i in range(total_spells):
        pr = 1 / total_spells
        chances.append(pr)

    spellbook = convert(chances)

    for spell in spellbook:
        print(round(spell, 3) + 2)
