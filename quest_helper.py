from pathlib import Path


def make_event_sql(event_name):

    Path("output/B GameEventDefDB").mkdir(parents=True, exist_ok=True)

    with open("output/B GameEventDefDB/" + event_name + ".sql", 'w') as my_file:
        my_file.write("DELETE FROM `event` WHERE `name` = '" + event_name + "';\n")
        my_file.write("INSERT INTO `event` (`name`, `start_Time`, `end_Time`, `state`, `last_Modified`)\n")
        my_file.write("VALUES ('" + event_name + "', -1, -1, 3, '2020-01-24 19:57:17');\n")


def make_quest_sql(quest_name):

    Path("output/8 QuestDefDB").mkdir(parents=True, exist_ok=True)

    with open("output/8 QuestDefDB/" + quest_name + ".sql", 'w') as my_file:
        my_file.write("DELETE FROM `quest` WHERE `name` = '" + quest_name + "';\n")
        my_file.write("INSERT INTO `quest` (`name`, `min_Delta`, `max_Solves`, `message`, `last_Modified`)\n")
        my_file.write("VALUES ('" + quest_name + "', 72000, -1, 'quest timer', '2020-01-24 19:57:17');\n")


def make_kill_count(quest_name, total_kills):

    Path("output/8 QuestDefDB").mkdir(parents=True, exist_ok=True)

    with open("output/8 QuestDefDB/" + quest_name + ".sql", 'w') as my_file:
        my_file.write("DELETE FROM `quest` WHERE `name` = '" + quest_name + "';\n")
        my_file.write("INSERT INTO `quest` (`name`, `min_Delta`, `max_Solves`, `message`, `last_Modified`)\n")
        my_file.write(
            "VALUES ('" + quest_name + "', 0, " + str(total_kills) + ", 'kill counter', '2020-01-24 19:57:17');\n")
