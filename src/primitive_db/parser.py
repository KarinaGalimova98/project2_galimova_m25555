def parse_where(args):
    if len(args) != 3 or args[1] != "=":
        print("Некорректное условие WHERE.")
        return None

    col = args[0]
    val = args[2].strip('"')
    return {col: val}


def parse_set(args):
    if len(args) != 3 or args[1] != "=":
        print("Некорректное выражение SET.")
        return None

    col = args[0]
    val = args[2].strip('"')
    return {col: val}
