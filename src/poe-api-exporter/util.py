def remove_empty_string(dic):
    if isinstance(dic, str):
        if dic == "":
            return None
        else:
            return dic

    if isinstance(dic, list):
        conv = lambda i: i or None  # noqa: E731
        return [conv(i) for i in dic]

    for e in dic:
        if isinstance(dic[e], dict):
            dic[e] = remove_empty_string(dic[e])
        if isinstance(dic[e], str) and dic[e] == "":
            dic[e] = None
        if isinstance(dic[e], list):
            for entry in dic[e]:
                remove_empty_string(entry)

    return dic
