def color_str_to_list(color):
    res = []
    for i in range(3):
        res.append(int(color[2 * i:2 * i + 2], 16))
    return res