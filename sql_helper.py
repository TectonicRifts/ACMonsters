from pathlib import Path


def write_sql_file(file_name, commands):
    Path("output/renumbered").mkdir(parents=True, exist_ok=True)

    with open("output/renumbered/" + file_name, 'w') as file_object:
        for command in commands:
            file_object.write(command)


def delete_sql_command(commands, tag):
    my_list = []

    for command in commands:
        if tag in command:
            pass
        else:
            if command.strip() != "":
                my_list.append(command)

    return my_list


def replace_sql_command(commands, tag, new_command):
    my_list = []

    for command in commands:
        if tag in command:
            my_list.append("\n\n" + new_command)
        else:
            if command.strip() != "":
                my_list.append(command)

    return my_list


def append_sql_command(commands, new_command):
    """Append to end of file. Useful for adding the same emote to many files."""
    my_list = []
    for command in commands:
        if command.strip() != "":
            my_list.append(command)
    my_list.append("\n\n" + new_command)

    return my_list

