import json
import re
data = json.loads(input())
keys_with_format = ["stop_name", "stop_type", "a_time"]
bus_ids = [128, 256, 512, 1024]
template_name = r'(\b[A-Z].*?\b) (Road|Avenue|Street|Boulevard)$'
template_time = r'([01]\d|2[0-3]):([0-5]\d)$'
template_type = ["S", "O", "F", ""]


def tarf(dane):
    tarf_validation = {key: 0 for key in dane[0].keys()}
    lista = list(tarf_validation.keys())
    list_of_types = [int, int, str, int, str, str]
    list_of_required = [True, True, True, True, False, True]
    for i in range(len(dane)):
        for j in range(len(lista)):
            if lista[j] == "stop_type":
                if dane[i].get(lista[j]) not in template_type:
                    tarf_validation[lista[j]] += 1
            else:
                if type(dane[i].get(lista[j])) is not list_of_types[j]:
                    tarf_validation[lista[j]] += 1
                    continue
                if dane[i].get(lista[j]) == '' and list_of_required[j] is True:
                    tarf_validation[lista[j]] += 1

    print(f"Type and required field validation: {sum(tarf_validation.values())} errors")
    for key, value in tarf_validation.items():
        print(key, value)


def fval(dane):
    f_validation = {key: 0 for key in keys_with_format}
    for i in range(len(dane)):
        if not re.match(template_name, dane[i].get("stop_name")):
            f_validation["stop_name"] += 1
        if dane[i].get("stop_type") not in template_type:
            f_validation["stop_type"] += 1
        if not re.match(template_time, dane[i].get("a_time")):
            f_validation["a_time"] += 1
    print(f"Format validation: {sum(f_validation.values())} errors")
    for key, value in f_validation.items():
        print(key, value)


def number_of_stops(dane):
    ids = {key: 0 for key in bus_ids}
    for i in range(len(dane)):
        idi = dane[i].get("bus_id")
        if idi in ids:
            ids[idi] += 1
    print("Line names and number of stops:")
    for key, value in ids.items():
        print(key, value)


def special_stops(dane):
    start_stops = []
    transfer_stops = []
    finish_stops = []
    check = []
    for i in range(len(dane)):
        tmp, tmp_name, tmp_id = dane[i].get("stop_type"), dane[i].get("stop_name"), dane[i].get("bus_id")
        if tmp == 'S':
            start_stops.append(tmp_name)
            check.append(tmp_id)
        if tmp == 'F':
            finish_stops.append(tmp_name)
            check.append(tmp_id)
        if tmp in template_type:
            transfer_stops.append(tmp_name)
    for idi in bus_ids:
        if check.count(idi) == 1:
            return print(f"There is no start or end stop for the line: {idi}.")
    transfer_stops = [stop for stop in transfer_stops if transfer_stops.count(stop) > 1]
    start_stops = list(set(start_stops))
    transfer_stops = list(set(transfer_stops))
    finish_stops = list(set(finish_stops))

    #print("Start stops:", len(start_stops), sorted(start_stops))
    #print("Transfer stops:", len(transfer_stops), sorted(transfer_stops))
    #print("Finish stops:", len(finish_stops), sorted(finish_stops))
    return [start_stops, transfer_stops, finish_stops]


def unlost_in_time(dane):
    print('Arrival time test:')
    errors = False
    for bus_id in set(stop['bus_id'] for stop in dane):
        last = next(filter(lambda stop: stop['bus_id'] == bus_id and stop['stop_type'] == 'S', dane))
        while last['next_stop'] != 0:
            current = next(
                filter(lambda stop: stop['bus_id'] == bus_id and stop['stop_id'] == last['next_stop'], dane))
            if current['a_time'] <= last['a_time']:
                print(f"bus_id line {bus_id}: wrong time on station {current['stop_name']}")
                errors = True
                break
            last = current
    if not errors:
        print("OK")


def on_demand(dane):
    print("On demand stops test:")
    specials = special_stops(dane)
    specials = set(specials[0]) | set(specials[1]) | set(specials[2])
    wrongs = []

    for i in range(len(dane)):
        tmp = dane[i].get("stop_name")
        if tmp in specials and dane[i].get("stop_type") == "O":
            wrongs.append(tmp)
    wrongs.sort()
    if len(wrongs) > 0:
        return print(f"Wrong stop type: {wrongs}")
    else:
        return print(f"Wrong stop type: OK")

