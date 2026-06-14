direction_angles = {
    "N":  (1, 0, 0, 0),
    "S":  (0, 0, 0, 1),
    "W":  (0.707107, 0, 0, 0.707107),
    "E":  (-0.707107, 0, 0, 0.707107),

    "NW": (0.923880, 0, 0, 0.382683),
    "NE": (-0.923880, 0, 0, 0.382683),
    "SE": (-0.382683, 0, 0, 0.923880),
    "SW": (0.382683, 0, 0, 0.923880),
}

bitmask_comments = {
    1: "Unrestricted",
    17: "Unrestricted, NoSummon",
    49: "Unrestricted, NoSummon, NoRecall"
}

# keys become values, and vice versa (note all values must be unique to work)
bitmask_flipped = {v: k for k, v in bitmask_comments.items()}

portal_colors = {
    "pink": "0x020001B3",
    "blue": "0x020005D2",
    "green": "0x020005D3",
    "orange": "0x020005D4",
    "red": "0x020005D5",
    "yellow": "0x020005D6",
    "white": "0x020006F4",
    "shadow": "0x020008FD",
    "shadow red": "0x02001029",
    "shadow orange": "0x0200102A"
}

class Location:

    def __init__(self, cell_id, ox, oy, oz, aw, ax, ay, az):
        self.cell_id = cell_id

        self.ox = ox
        self.oy = oy
        self.oz = oz

        self.aw = aw
        self.ax = ax
        self.ay = ay
        self.az = az

    def set_angles(self, direction):
        if direction in direction_angles:
            angles = direction_angles[direction]
            self.aw = angles[0]
            self.ax = angles[1]
            self.ay = angles[2]
            self.az = angles[3]


def parse_loc(loc_string: str) -> Location:
    # 0x01AC0117 [31.013346 -19.342186 0.005000] -0.763732 0.000000 0.000000 -0.645533
    first_bracket = loc_string.index('[')
    second_bracket = loc_string.index(']')

    # cell id
    cell_id = loc_string[:first_bracket].strip()
    # coords inside brackets
    coords = loc_string[first_bracket + 1:second_bracket].split()
    # quaternion values after ]
    angles = loc_string[second_bracket + 1:].split()

    return Location (
        cell_id,
        float(coords[0]), float(coords[1]), float(coords[2]),
        float(angles[0]), float(angles[1]), float(angles[2]), float(angles[3]),
    )


def make_position_table(port_wcid, loc: Location):
    comment = f"/* @teleloc {loc.cell_id} [{loc.ox} {loc.oy} {loc.oz}] {loc.aw} {loc.ax} {loc.ay} {loc.az} */;\n"

    commands = [
        "INSERT INTO `weenie_properties_position` (`object_Id`, `position_Type`, `obj_Cell_Id`, `origin_X`, `origin_Y`, `origin_Z`, `angles_W`, `angles_X`, `angles_Y`, `angles_Z`)\n",
        f"VALUES ({port_wcid}, 2, {loc.cell_id}, {loc.ox}, {loc.oy}, {loc.oz}, {loc.aw}, {loc.ax}, {loc.ay}, {loc.az}) /* Destination */\n" + comment
    ]
    return commands


def make_portal_body(port_wcid: int, port_name: str, port_setup: str, port_bitmask: int, min_level: int, on_click: bool, quest_stamp: str | None, quest_restrict: str | None) -> list:
    class_name = port_name.replace(" ", "").lower()
    if not port_setup:
        port_setup = "0x020001B3"

    if not port_bitmask:
        port_bitmask = 49

    bitmask_comment = bitmask_comments[port_bitmask]

    if on_click == 1:
        physics_state = f"     , ({port_wcid},  93,       2052) /* PhysicsState - Ethereal, LightingOn */\n"
    else:
        physics_state = f"     , ({port_wcid},  93,       3084) /* PhysicsState - Ethereal, ReportCollisions, Gravity, LightingOn */\n"

    port_header = [
        f"DELETE FROM `weenie` WHERE `class_Id` = {port_wcid};\n\n",

        "INSERT INTO `weenie` (`class_Id`, `class_Name`, `type`, `last_Modified`)\n",
        f"VALUES ({port_wcid}, 'ace{port_wcid}-{class_name}', 7, '2005-02-09 10:00:00') /* Portal */;\n\n"
    ]

    if min_level > 0:
        int_table = [
            "INSERT INTO `weenie_properties_int` (`object_Id`, `type`, `value`)\n",
            f"VALUES ({port_wcid},   1,      65536) /* ItemType - Portal */\n",
            f"     , ({port_wcid},  16,         32) /* ItemUseable - Remote */\n",
            f"     , ({port_wcid},  86,         {min_level}) /* MinLevel */\n",
            physics_state,
            f"     , ({port_wcid}, 111,         {port_bitmask}) /* PortalBitmask - {bitmask_comment} */\n",
            f"     , ({port_wcid}, 133,          4) /* ShowableOnRadar - ShowAlways */;\n\n",
        ]
    else:
        int_table = [
            "INSERT INTO `weenie_properties_int` (`object_Id`, `type`, `value`)\n",
            f"VALUES ({port_wcid},   1,      65536) /* ItemType - Portal */\n",
            f"     , ({port_wcid},  16,         32) /* ItemUseable - Remote */\n",
            physics_state,
            f"     , ({port_wcid}, 111,         {port_bitmask}) /* PortalBitmask - {bitmask_comment} */\n",
            f"     , ({port_wcid}, 133,          4) /* ShowableOnRadar - ShowAlways */;\n\n",
        ]

    bool_table = [
        "INSERT INTO `weenie_properties_bool` (`object_Id`, `type`, `value`)\n",
        f"VALUES ({port_wcid},   1, True ) /* Stuck */\n",
        f"     , ({port_wcid},  11, False) /* IgnoreCollisions */\n",
        f"     , ({port_wcid},  12, True ) /* ReportCollisions */\n",
        f"     , ({port_wcid},  13, True ) /* Ethereal */\n",
        f"     , ({port_wcid},  15, False) /* LightsStatus */;\n\n",

        "INSERT INTO `weenie_properties_float` (`object_Id`, `type`, `value`)\n",
        f"VALUES ({port_wcid},  54,    -0.1) /* UseRadius */;\n\n",
    ]

    if quest_stamp and not quest_restrict:
        str_table = [
            "INSERT INTO `weenie_properties_string` (`object_Id`, `type`, `value`)\n",
            f"VALUES ({port_wcid},   1, '{port_name}') /* Name */\n",
            f"     , ({port_wcid},  33, '{quest_stamp}') /* Quest */;\n\n",
        ]
    elif quest_stamp and quest_restrict:
        str_table = [
            "INSERT INTO `weenie_properties_string` (`object_Id`, `type`, `value`)\n",
            f"VALUES ({port_wcid},   1, '{port_name}') /* Name */\n",
            f"     , ({port_wcid},  37, '{quest_restrict}') /* QuestRestriction */;\n\n",
        ]
    else:
        str_table = [
            "INSERT INTO `weenie_properties_string` (`object_Id`, `type`, `value`)\n",
            f"VALUES ({port_wcid},   1, '{port_name}') /* Name */;\n\n"
        ]

    did_table = [
        "INSERT INTO `weenie_properties_d_i_d` (`object_Id`, `type`, `value`)\n",
        f"VALUES ({port_wcid},   1, {port_setup}) /* Setup */\n",
        f"     , ({port_wcid},   2, 0x09000003) /* MotionTable */\n",
        f"     , ({port_wcid},   8, 0x0600106B) /* Icon */;\n\n"
    ]

    commands = port_header + int_table + bool_table + str_table + did_table

    return commands
