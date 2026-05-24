from port_module import Location

def get_gen_prs(tot_rows: int) -> list[float]:
    if tot_rows == 1:
        return [-1]

    step = 1 / tot_rows
    probs = []

    for i in range(1, tot_rows + 1):
        prob = round(step * i, 4)

        # force exact 1 for last entry
        if i == tot_rows:
            prob = 1

        probs.append(prob)

    return probs


def make_gen_row(gen_wcid: int, child_wcid: int, where: int, delay: int, spawn_pr: float, loc: Location | None = None) -> str:
    # TODO
    # if no loc provided, uses None
    # need to provide a loc for specific gen
    # spawn_pr = -1
    spawn_name = "Placeholder (" + str(child_wcid) + ")"

    # 1 = Top, 2 = Scatter, 4 = Specific
    where_dict = {
        1: "Top",
        2: "Scatter",
        4: "Specific"
    }
    max_create = 1

    if loc is None:
        loc = Location(0, 0, 0, 0, 1, 0, 0, 0)

    return f"({gen_wcid}, {spawn_pr}, {child_wcid}, {delay}, 1, {max_create}, 1, {where}, -1, 0, 0, {loc.cell_id}, {loc.ox}, {loc.oy}, {loc.oz}, {loc.aw}, {loc.ax}, {loc.ay}, {loc.az}) /* Generate {spawn_name} (x1 up to max of {max_create}) - Regenerate upon Destruction - Location to (re)Generate: {where_dict[where]} */"


def get_default_gen_body(gen_wcid: int, gen_name: str, gen_init: int, gen_max: int, regen_interval: int, gen_radius: int) -> list:

    class_name = gen_name.replace(" ", "").lower()

    commands = [
        f"DELETE FROM `weenie` WHERE `class_Id` = {gen_wcid};\n\n",

        "INSERT INTO `weenie` (`class_Id`, `class_Name`, `type`, `last_Modified`)\n",
        f"VALUES ({gen_wcid}, 'ace{gen_wcid}-{class_name}', 1, '2022-06-21 15:22:25') /* Generic */;\n\n",

        "INSERT INTO `weenie_properties_int` (`object_Id`, `type`, `value`)\n",
        f"VALUES ({gen_wcid},  81,    {gen_max}) /* MaxGeneratedObjects */\n",
        f"     , ({gen_wcid},  82,    {gen_init}) /* InitGeneratedObjects */\n",
        f"     , ({gen_wcid},  93, 1044) /* PhysicsState - Ethereal, IgnoreCollisions, Gravity */\n",
        f"     , ({gen_wcid}, 103,    2) /* GeneratorDestructionType - Destroy */;\n\n",

        "INSERT INTO `weenie_properties_bool`(`object_Id`, `type`, `value`)\n",
        f"VALUES ({gen_wcid},   1, True ) /* Stuck */\n",
        f"     , ({gen_wcid},  11, True ) /* IgnoreCollisions */\n",
        f"     , ({gen_wcid},  18, True ) /* Visibility */;\n\n",

        "INSERT INTO `weenie_properties_float` (`object_Id`, `type`, `value`)\n",
        f"VALUES ({gen_wcid},  41,      {regen_interval}) /* RegenerationInterval */\n",
        f"     , ({gen_wcid},  43,      {gen_radius}) /* GeneratorRadius */;\n\n",

        "INSERT INTO `weenie_properties_string` (`object_Id`, `type`, `value`)\n",
        f"VALUES ({gen_wcid},   1, '{gen_name}') /* Name */;\n\n",

        "INSERT INTO `weenie_properties_d_i_d` (`object_Id`, `type`, `value`)\n",
        f"VALUES ({gen_wcid},   1, 0x0200026B) /* Setup */\n",
        f"     , ({gen_wcid},   8, 0x06001066) /* Icon */;\n\n"
    ]

    return commands


def get_event_gen_body(gen_wcid: int, gen_name: str, gen_init: int, gen_max: int, regen_interval: int, gen_radius: int, event_name: str, init_delay: int) -> list:

    class_name = gen_name.replace(" ", "").lower()

    commands = [
        f"DELETE FROM `weenie` WHERE `class_Id` = {gen_wcid};\n\n",

        "INSERT INTO `weenie` (`class_Id`, `class_Name`, `type`, `last_Modified`)\n",
        f"VALUES ({gen_wcid}, 'ace{gen_wcid}-{class_name}', 1, '2022-06-21 15:22:25') /* Generic */;\n\n",

        "INSERT INTO `weenie_properties_int` (`object_Id`, `type`, `value`)\n",
        f"VALUES ({gen_wcid},  81,    {gen_max}) /* MaxGeneratedObjects */\n",
        f"     , ({gen_wcid},  82,    {gen_init}) /* InitGeneratedObjects */\n",
        f"     , ({gen_wcid},  93, 1044) /* PhysicsState - Ethereal, IgnoreCollisions, Gravity */\n",
        f"     , ({gen_wcid}, 142,    3) /* GeneratorTimeType - Event */\n",
        f"     , ({gen_wcid}, 145,    2) /* GeneratorEndDestructionType - Destroy */;\n\n",

        "INSERT INTO `weenie_properties_bool`(`object_Id`, `type`, `value`)\n",
        f"VALUES ({gen_wcid},   1, True ) /* Stuck */\n",
        f"     , ({gen_wcid},  11, True ) /* IgnoreCollisions */\n",
        f"     , ({gen_wcid},  18, True ) /* Visibility */;\n\n",

        "INSERT INTO `weenie_properties_float` (`object_Id`, `type`, `value`)\n",
        f"VALUES ({gen_wcid},  41,      {regen_interval}) /* RegenerationInterval */\n",
        f"     , ({gen_wcid},  43,      {gen_radius}) /* GeneratorRadius */\n",
        f"     , ({gen_wcid}, 121,      {init_delay}) /* GeneratorInitialDelay */;\n\n",

        "INSERT INTO `weenie_properties_string` (`object_Id`, `type`, `value`)\n",
        f"VALUES ({gen_wcid},   1, '{gen_name}') /* Name */\n",
        f"     , ({gen_wcid},  34, '{event_name}') /* GeneratorEvent */;\n\n",

        "INSERT INTO `weenie_properties_d_i_d` (`object_Id`, `type`, `value`)\n",
        f"VALUES ({gen_wcid},   1, 0x0200026B) /* Setup */\n",
        f"     , ({gen_wcid},   8, 0x06001066) /* Icon */;\n\n"
    ]

    return commands


def get_gen_table(gen_rows: list) -> list:
    # TODO
    commands = [
        f"INSERT INTO `weenie_properties_generator` (`object_Id`, `probability`, `weenie_Class_Id`, `delay`, `init_Create`, `max_Create`, `when_Create`, `where_Create`, `stack_Size`, `palette_Id`, `shade`, `obj_Cell_Id`, `origin_X`, `origin_Y`, `origin_Z`, `angles_W`, `angles_X`, `angles_Y`, `angles_Z`)\n"
    ]

    tot_rows = len(gen_rows)

    for i, row in enumerate(gen_rows):
        if i == 0:
            prefix = "VALUES "
        else:
            prefix = "     , "

        if i == tot_rows - 1:
            suffix = ";\n"
        else:
            suffix = "\n"

        commands.append(prefix + row + suffix)

    # return "".join(commands)
    return commands
