import re
from enum import IntEnum

PROPERTY_HEADERS = {
    "int": "`weenie_properties_int`",
    "bool": "`weenie_properties_bool`",
    "float": "`weenie_properties_float`",
    "string": "`weenie_properties_string`",
    "str": "`weenie_properties_string`",
    "did": "`weenie_properties_d_i_d`"
}

ARMOR_MOD_IDS = {
    "slash": 13,
    "pierce": 14,
    "bludge": 15,
    "cold": 16,
    "fire": 17,
    "acid": 18,
    "electric": 19
}

RESIST_MOD_IDS = {
    "slash": 64,
    "pierce": 65,
    "bludge": 66,
    "cold": 68,
    "fire": 67,
    "acid": 69,
    "electric": 70,
    "nether": 166
}

class GenWhere(IntEnum):
    TOP = 1
    SCATTER = 2
    SPECIFIC = 4

def get_property_header(property_type: str) -> str | None:
    """Property types are int, bool, float, str, and did."""
    return PROPERTY_HEADERS.get(property_type)


def get_armor_mods(sql_data: list) -> dict:
    return extract_float_properties(sql_data, ARMOR_MOD_IDS)


def get_resist_mods(sql_data: list) -> dict:
    return extract_float_properties(sql_data, RESIST_MOD_IDS)


def extract_float_properties(sql_data: list, property_ids: dict) -> dict:
    result = {}

    for k, v in property_ids.items():
        mod = get_property(sql_data, "float", v)
        match = re.search(r"'([\d.]+)'", str(mod))

        if match:
            result[k] = float(match.group(1))
        else:
            result[k] = None

    return result


def get_property(weenie_sql: list, property_type: str, key: int) -> tuple[str, str] | None:
    """
    Returns a tuple (val, comment) or None if the property type is invalid, the property table does
    not exist, or the given key is not found in the property table.
    """
    property_header = get_property_header(property_type)
    if property_header is None:
        return None

    wcid = get_wcid(weenie_sql)

    for table in weenie_sql:
        if property_header in table:
            sql_statement = {}
            split_table = table.split("(")

            for line in split_table:
                if str(wcid) in line:
                    # split on the first two commas only
                    split_comma = line.split(",", 2)
                    my_key = int(split_comma[1].strip())

                    split_other = split_comma[2].split(")")
                    my_val = split_other[0].strip()
                    comment = "".join(split_other[1].rsplit(",", 1)).strip()

                    sql_statement[my_key] = (my_val, comment)

            return sql_statement.get(key)

    return None


def set_property(weenie_sql: list, property_type: str, key, val, desc) -> list:
    """Set a property (int, bool, float, string or did) of a weenie (in sql format). If the
    property already exists, the value is updated. This function does not work for position. """

    is_padded = True
    key = int(key)

    # format value depending on property type
    if property_type in ("str", "string"):
        val = val.replace("'", "''")
        val = f"""'{val}'"""
        is_padded = False

    elif property_type == "bool":
        if int(val) == 0:
            val = False
        else:
            val = True

    elif property_type == "did":
        val = hex(val).upper().replace('X', 'x')
        # these did properties are stored without the 0x prefix
        if key in (32, 35):
            val = val.replace('0x', '')

    property_header = get_property_header(property_type)

    # find number string in first line
    wcid = re.findall('[0-9]+', (weenie_sql[0]))[0]

    # check if this property table already exists
    has_property_table = False

    for table in weenie_sql:
        if str(property_header) in table:
            has_property_table = True

    # if not, add a new insert command
    if not has_property_table:
        new_table = f"""\n\nINSERT INTO {property_header} (`object_Id`, `type`, `value`)\nVALUES """
        new_table += f"""({wcid}, {key}, {val}) {desc}"""
        weenie_sql.append(new_table)
        return weenie_sql

    new_weenie_sql = []

    for table in weenie_sql:
        if str(property_header) in table:

            properties = {}
            split_command = table.split("(")

            for line in split_command:
                if str(wcid) in line:
                    split_comma = line.split(",", 2)

                    existing_key = int(split_comma[1].strip())

                    split_other = split_comma[2].split(")")
                    existing_val = split_other[0].strip()
                    comment = "".join(split_other[1].rsplit(",", 1)).strip()

                    properties[existing_key] = (existing_val, comment)

            # add or replace the target property
            properties[key] = (val, desc)

            # rebuild the insert statement
            new_table = f"""\n\nINSERT INTO {property_header} (`object_Id`, `type`, `value`)\nVALUES """

            # figure out padding
            i = 0
            total_lines = len(properties)

            longest_key, longest_val = get_longest(properties)

            if longest_val < 8:
                longest_val = 8

            for k, v in sorted(properties.items()):
                if is_padded:
                    justified_value = str(v[0]).rjust(longest_val, " ")
                    justified_key = str(k).rjust(longest_key, " ")
                else:
                    justified_value = " " + str(v[0])
                    justified_key = str(k).rjust(longest_key, " ")

                if i == 0:
                    new_table = new_table + f"""({wcid},{justified_key},{justified_value}) {v[1]}"""
                    if i < (total_lines - 1):
                        new_table = new_table + "\n    "
                else:
                    new_table = new_table + f""" , ({wcid},{justified_key},{justified_value}) {v[1]}"""
                    if i < (total_lines - 1):
                        new_table = new_table + "\n    "
                i += 1

            new_weenie_sql.append(new_table)

        elif table.strip():
            new_weenie_sql.append(table)

    return new_weenie_sql


def get_longest(my_dict: dict):
    longest_key = 0
    longest_val = 0

    for k, v in sorted(my_dict.items()):

        value_len = len(str(v[0]))
        if value_len > longest_val:
            longest_val = value_len

        key_len = len(str(k))
        if key_len > longest_key:
            longest_key = key_len

    longest_key += 1
    longest_val += 1

    return longest_key, longest_val


def get_wcid(weenie_sql: list):
    wcid = re.findall('[0-9]+', (weenie_sql[0]))[0]
    return wcid


def get_name(weenie_sql):
    name = str(get_property(weenie_sql, "str", 1))
    split = name.split(",")[0]
    name = split.replace("(", "")
    name = name.replace("''", "'")
    name = name[2:-2]

    return name


def get_xp_value(level):
    with open("resources/xp_by_level.txt", 'r') as my_file:
        for line in my_file:
            split = line.split("\t")
            if int(level) == int(split[0].strip()):
                return split[1].strip()

    return 0


def set_sql_table(weenie_sql: list[str], table_name: str, new_table: list[str]) -> list[str]:
    # example table names: `weenie_properties_generator` or `weenie_properties_body_part`
    new_weenie_sql = []

    # new table has to be a str, not list, because a table is represented by a single string in weenie_sql
    tot_rows = len(new_table)
    table_str = ""

    for i in range(tot_rows):
        if i == 0: # first row is the insert statement
            table_str = "\n\n" + new_table[i]
        elif i == tot_rows - 1:
            prefix = "     "
            table_str = table_str + prefix + new_table[i].strip()
        else:
            table_str = table_str + new_table[i]
        i += 1

    found = False

    for table in weenie_sql:
        if table_name in table:
            # replace the old table with the new one
            found = True
            new_weenie_sql.append(table_str)
        elif table.strip():
            # carry over the existing table
            new_weenie_sql.append(table)

    if not found:
        new_weenie_sql.append(table_str)

    return new_weenie_sql


