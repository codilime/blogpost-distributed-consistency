def camel_to_lower_with_spaces(s):
    result = []
    for i, char in enumerate(s):
        if char.isupper() and i != 0:
            result.append(" ")
        result.append(char.lower())
    return "".join(result)
