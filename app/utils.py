
def humanize_intlist(high_number_list):
    min_list = min([abs(l) for l in high_number_list])
    if min_list >= 1e12:
        unit = "(Trillions)"
        new_list = [l/1e12 for l in high_number_list]
    elif min_list >= 1e9:
        unit = "(Billions)"
        new_list = [l/1e9 for l in high_number_list]
    elif min_list >= 6:
        unit = "(Millions)"
        new_list = [l/1e6 for l in high_number_list]
    elif min_list >= 5:
        unit = "(Hundred Thousand)"
        new_list = [l/1e12 for l in high_number_list]
    else:
        unit = ""
        new_list = high_number_list
    return unit, new_list
