import labels_module


class UpdateWeenie:

    def is_creature(self, my_json):
        item_type = self.get_stat(my_json, "intStats", 1)
        return item_type == 16

    def set_wcid(self, my_json, wcid):
        """Set the wcid."""
        my_json['wcid'] = wcid

    def set_weenie_type(self, my_json, weenie_type):
        my_json['weenieType'] = weenie_type

    def get_wcid(self, my_json):
        for k1, v1 in my_json.items():
            if k1 == 'wcid':
                return v1

    def get_name(self, my_json):
        return self.get_stat(my_json, "stringStats", 1)

    def get_item_type(self, my_json):
        return self.get_stat(my_json, "intStats", 1)

    def get_attributes(self, my_json):
        """Get the primary attributes."""

        my_dict = {}

        attributes = ['strength', 'endurance', 'coordination', 'quickness', 'focus', 'self', 'health', 'stamina',
                      'mana']

        for k1, v1 in my_json.items():
            if k1 == 'attributes':
                for k2, v2 in v1.items():
                    for k3, v3 in v2.items():
                        if k3 == 'init_level':
                            for attribute in attributes:
                                if k2 == attribute:
                                    my_dict[attribute] = int(my_json[k1][k2][k3])
        return my_dict

    def check_attributes(self, my_json):
        for k1, v1 in my_json.items():
            if k1 == 'attributes':
                for k2, v2 in v1.items():

                    has_init_level = False

                    for k3, v3 in v2.items():
                        if k3 == 'init_level':
                            has_init_level = True

                    if has_init_level is False:
                        my_json[k1][k2]['init_level'] = 0

    def set_attributes(self, my_json, attributes):
        """Set the primary attributes."""

        self.check_attributes(my_json)

        if 'health' in attributes:
            attributes['health'] = self.compute_health(attributes)

        if 'stamina' in attributes:
            attributes['stamina'] = self.compute_stamina(attributes)

        if 'mana' in attributes:
            attributes['mana'] = self.compute_mana(attributes)

        for k1, v1 in my_json.items():
            if k1 == 'attributes':
                for k2, v2 in v1.items():
                    for k3, v3 in v2.items():
                        if k3 == 'init_level':
                            for attribute in attributes:
                                if k2 == attribute:
                                    my_json[k1][k2][k3] = attributes[k2]  # set to the value in attributes

    def compute_health(self, attributes):
        """Compute what initial health should be based on endurance."""
        health = attributes['health'] - round(attributes['endurance'] / 2)
        if health < 0:
            health = 0
        return health

    def compute_stamina(self, attributes):
        """Compute what initial stamina should be based on endurance."""
        stamina = attributes['stamina'] - attributes['endurance']
        if stamina < 0:
            stamina = 0
        return stamina

    def compute_mana(self, attributes):
        """Compute what initial mana should be based on self."""
        mana = attributes['mana'] - attributes['self']
        if mana < 0:
            mana = 0
        return mana

    def set_base_armor(self, my_json, armor_dict):
        """Set base armor for all body parts to the given values."""
        for k1, v1 in my_json.items():
            if k1 == 'body':
                for k2, v2 in v1.items():
                    for i, v3 in enumerate(v2):
                        for damage_type, armor_value in armor_dict.items():
                            my_json[k1][k2][i]['value']['acache'][damage_type] = armor_value

    def boost_base_armor(self, my_json, boost_value):
        """Has not been tested."""
        my_list = labels_module.get_armor_labels()

        for k1, v1 in my_json.items():
            if k1 == 'body':
                for k2, v2 in v1.items():
                    for i, v3 in enumerate(v2):
                        for damage_type in my_list:
                            my_json[k1][k2][i]['value']['acache'][damage_type] += boost_value

    def set_body_part_damage(self, my_json, damage_dict):
        """Set the damage for all body parts to the given values. Used when
        the monster is unarmed."""
        for k1, v1 in my_json.items():
            if k1 == 'body':
                for k2, v2 in v1.items():
                    for i, v3 in enumerate(v2):
                        for field, my_value in damage_dict.items():
                            my_json[k1][k2][i]['value'][field] = my_value

    def get_destination(self, destination):
        """Get the int value of a destination for the create list."""
        destinations = {'contain': 9, 'wield': 10}

        if destination in destinations:
            return destinations[destination]
        else:
            return destinations['contain']

    def add_create_list(self, my_json):
        """Add a create list if it doesn't exist."""
        has_list = False

        for k1, v1 in my_json.items():
            group_name = 'createList'
            if k1 == group_name:
                has_list = True

        if has_list is False:
            my_json.update({"createList": []})

    def add_empty_slot(self, my_json, shade):
        """Add an empty create slot to an existing create list."""
        wcid = 0
        palette = 0
        destination = 9
        stack_size = 1
        try_to_bond = 0

        my_json['createList'].append(
            {"wcid": wcid, "palette": palette, "shade": shade, "destination": destination, "stack_size": stack_size,
             "try_to_bond": try_to_bond})

    def set_create_list(self, my_json, wcid, destination, palette, shade, quantity):
        """If the item given by the wcid exists, update it. Otherwise, add it."""
        try_to_bond = 0

        for k1, v1 in my_json.items():
            group_name = 'createList'
            if k1 == group_name:
                contains_item = False
                for i, val in enumerate(v1):
                    if my_json[group_name][i]['wcid'] == wcid:  # already contains the item so update it
                        my_json[group_name][i]['palette'] = palette
                        my_json[group_name][i]['shade'] = shade
                        my_json[group_name][i]['destination'] = destination
                        my_json[group_name][i]['stack_size'] = quantity
                        my_json[group_name][i]['try_to_bond'] = try_to_bond
                        contains_item = True
                if contains_item is False:  # append the item
                    my_json[group_name].append(
                        {"wcid": wcid, "palette": palette, "shade": shade, "destination": destination,
                         "stack_size": quantity, "try_to_bond": try_to_bond})

    def append_item(self, my_json, wcid, destination, palette, shade, quantity):
        """Append an item to the create list. Used when multiple copies are needed (i.e., for quest drops)."""
        try_to_bond = 0

        for k1, v1 in my_json.items():
            group_name = 'createList'
            if k1 == group_name:
                my_json[group_name].append(
                    {"wcid": wcid, "palette": palette, "shade": shade, "destination": destination,
                     "stack_size": quantity, "try_to_bond": try_to_bond})

    def get_pos_sql(self, loc_paste):

        loc_paste = loc_paste.strip()
        split_loc = loc_paste.split(" ")

        cell_hex = split_loc[0]
        cell_dec = int(cell_hex, 16)

        ox = split_loc[1].replace("[", "")
        oy = split_loc[2]
        oz = split_loc[3].replace("]", "")

        aw = split_loc[4]
        ax = split_loc[5]
        ay = split_loc[6]
        az = split_loc[7]

        comment = "/* @teleloc " + loc_paste + " */;"
        new_value = "VALUES (99999, 2, " + str(cell_dec) + ", " + str(ox) + ", " + str(oy) + ", " + str(oz) + ", " + str(aw) + ", " + str(ax) + ", " + str(ay) + ", " + str(az) + ") /* Destination */\n" + comment

        return new_value

    def set_pos(self, my_json, loc_paste):

        has_pos = False

        for k1, v1 in my_json.items():
            group_name = 'posStats'
            if k1 == group_name:
                has_pos = True

        if has_pos is False:
            my_json.update({"posStats": []})

        loc_paste = loc_paste.strip()
        split_loc = loc_paste.split(" ")

        cell_hex = split_loc[0]
        cell_dec = int(cell_hex, 16)

        ox = split_loc[1].replace("[", "")
        oy = split_loc[2]
        oz = split_loc[3].replace("]", "")

        aw = split_loc[4]
        ax = split_loc[5]
        ay = split_loc[6]
        az = split_loc[7]

        group_name = "posStats"
        group_key = 2
        new_value = [{'frame': {'origin': {'x': ox, 'y': oy, 'z': oz}, 'angles': {'w': aw, 'x': ax, 'y': ay, 'z': az}},
                      'objcell_id': cell_dec}]

        for k1, v1 in my_json.items():
            if k1 == group_name:
                contains_key = False
                for i, val in enumerate(v1):
                    if my_json[group_name][i]['key'] == group_key:
                        my_json[group_name][i]['value'] = new_value
                        contains_key = True
                if contains_key is False:
                    my_json[group_name].append({"key": group_key, "value": new_value})

    def set_stat(self, my_json, group_name, group_key, new_value):
        """Set a stat including boolStats, intStats, floatStats, didStats and stringStats. If the
        stat doesn't exist, it will be added. For example, intStats would be the group name."""
        for k1, v1 in my_json.items():
            if k1 == group_name:
                contains_key = False
                for i, val in enumerate(v1):
                    if my_json[group_name][i]['key'] == group_key:
                        my_json[group_name][i]['value'] = new_value
                        contains_key = True
                if contains_key is False:
                    my_json[group_name].append({"key": group_key, "value": new_value})

    def del_stat(self, my_json, group_name, group_key):
        """Delete a stat including boolStats, intStats, floatStats, didStats and stringStats."""
        for k1, v1 in my_json.items():
            if k1 == group_name:
                for i, val in enumerate(v1):
                    if my_json[group_name][i]['key'] == group_key:
                        del my_json[group_name][i]

    def get_stat(self, my_json, group_name, group_key):
        """Get a stat including boolStats, intStats, floatStats, did and stringStats."""
        for k1, v1 in my_json.items():
            if k1 == group_name:
                for i, val in enumerate(v1):
                    if my_json[group_name][i]['key'] == group_key:
                        return my_json[group_name][i]['value']
                return None
    # skills

    def add_skill_list(self, my_json):
        """Add a skill list if it doesn't exist."""
        has_list = False

        for k1, v1 in my_json.items():
            group_name = 'skills'
            if k1 == group_name:
                has_list = True

        if has_list is False:
            my_json.update({"skills": []})

    def set_skill(self, my_json, group_name, skill_id, init_level):
        """Set the initial level of a skill. If the monster doesn't already have the skill, it will be added."""
        new_value = {'level_from_pp': 0, 'last_used_time': 0.0, 'init_level': init_level, 'pp': 0,
                     'resistance_of_last_check': 0, 'sac': 2}
        self.set_stat(my_json, group_name, skill_id, new_value)

        # spells

    def add_spell_list(self, my_json):
        """Add a spell list if it doesn't exist."""
        has_list = False

        for k1, v1 in my_json.items():
            group_name = 'spellbook'
            if k1 == group_name:
                has_list = True

        if has_list is False:
            my_json.update({"spellbook": []})

    def set_spell(self, my_json, group_name, spell_id, spell_pr):
        """Add a spell to the spellbook, but only if the monster does not already have it.
        Also set casting likelihood, which must be a decimal greater than 2 (e.g., 2.15 or 2.25)."""
        new_value = {'casting_likelihood': float(spell_pr)}
        self.set_stat(my_json, group_name, spell_id, new_value)

    def set_xp_override(self, my_json, new_value):
        """Set how much XP the monster is worth."""
        self.set_stat(my_json, 'intStats', 146, int(new_value))

    def set_level(self, my_json, new_value):
        """Set the monster's level."""
        self.set_stat(my_json, 'intStats', 25, new_value)

    def set_palette_template(self, my_json, new_value):
        """Set the color of the monster."""
        self.set_stat(my_json, 'intStats', 3, new_value)

    def set_regen(self, my_json, health_rate):
        self.set_stat(my_json, 'floatStats', 1, 5)
        self.set_stat(my_json, 'floatStats', 2, 0)
        self.set_stat(my_json, 'floatStats', 3, health_rate)
        self.set_stat(my_json, 'floatStats', 4, 3)
        self.set_stat(my_json, 'floatStats', 5, 1)

    def set_scale(self, my_json, new_value):
        """Set the scale of the monster's body."""
        self.set_stat(my_json, 'floatStats', 39, new_value)

    def set_shade(self, my_json, new_value):
        self.set_stat(my_json, 'floatStats', 12, new_value)

    def set_armor_mods(self, my_json, mods_dict):
        """Set the armor mods to the given values."""
        self.set_stat(my_json, 'floatStats', 13, mods_dict['slash'])
        self.set_stat(my_json, 'floatStats', 14, mods_dict['pierce'])
        self.set_stat(my_json, 'floatStats', 15, mods_dict['bludge'])
        self.set_stat(my_json, 'floatStats', 16, mods_dict['cold'])
        self.set_stat(my_json, 'floatStats', 17, mods_dict['fire'])
        self.set_stat(my_json, 'floatStats', 18, mods_dict['acid'])
        self.set_stat(my_json, 'floatStats', 19, mods_dict['electric'])

    def set_resistance_mods(self, my_json, mods_dict):
        self.set_stat(my_json, 'floatStats', 64, mods_dict['slash'])
        self.set_stat(my_json, 'floatStats', 65, mods_dict['pierce'])
        self.set_stat(my_json, 'floatStats', 66, mods_dict['bludge'])
        self.set_stat(my_json, 'floatStats', 67, mods_dict['cold'])
        self.set_stat(my_json, 'floatStats', 68, mods_dict['fire'])
        self.set_stat(my_json, 'floatStats', 69, mods_dict['acid'])
        self.set_stat(my_json, 'floatStats', 70, mods_dict['electric'])

    def set_heartbeat(self, my_json):
        """Set heartbeat interval, health, stamina and mana regeneration."""
        self.set_stat(my_json, 'floatStats', 1, 5)  # heartbeat interval, length of time between heartbeat emote actions
        self.set_stat(my_json, 'floatStats', 2, 0)  # heartbeat timestamp, timestamp of last heartbeat emote
        self.set_stat(my_json, 'floatStats', 3, 0.1)  # health rate, 0 to 5000, usually 0-10
        self.set_stat(my_json, 'floatStats', 4, 3)  # stamina rate
        self.set_stat(my_json, 'floatStats', 5, 1)  # mana rate

    def set_setup_model(self, my_json, new_value):
        self.set_stat(my_json, 'didStats', 1, new_value)

    def set_motion_table(self, my_json, new_value):
        self.set_stat(my_json, 'didStats', 2, new_value)

    def set_sound_table(self, my_json, new_value):
        self.set_stat(my_json, 'didStats', 3, new_value)

    def set_combat_table(self, my_json, new_value):
        self.set_stat(my_json, 'didStats', 4, new_value)

    def set_treasure_type(self, my_json, new_value):
        """Set the treasure profile used for random loot."""
        self.set_stat(my_json, 'didStats', 35, new_value)

    def set_palette_base(self, my_json, new_value):
        self.set_stat(my_json, 'didStats', 6, new_value)

    def clothing_base(self, my_json, new_value):
        self.set_stat(my_json, 'didStats', 7, new_value)

    def remove_element(self, my_json, element_name):
        """Remove an element such as createList, emoteTable, userChangeSummary, etc."""
        for element in my_json:
            if element_name in element:
                my_copy = dict(my_json)
                del my_copy[element_name]
                return my_copy

    def get_body_table(self, my_json):
        body_table = None

        for k, v in my_json.items():
            if k == "body":
                body_table = v

        return body_table

    def append_body_table(self, my_json, body_table):
        """Add a body table if there's none."""
        contains_key = False

        for k, v in my_json.items():
            if k == "body":
                contains_key = True

        if contains_key is False:
            my_json["body"] = body_table

        return my_json
