import pickle
import typing

from game import db
from gen.groundobjectsgen import TheaterGroundObject
from dcs.mission import Mission
from dcs.mapping import Point

m = Mission()
m.load_file("./cau_groundobjects.miz")

result = {}
result_by_groups = {}  # type: typing.Dict[int, TheaterGroundObject]
ids_counters = {}


def append_group(cp_id, category, group_id, object_id, position, heading):
    global result
    global result_by_groups

    ground_object = TheaterGroundObject(category, cp_id, group_id, object_id, position, heading)

    if cp_id not in result:
        result[cp_id] = []
    result[cp_id].append(ground_object)

    result_by_groups_key = "{}_{}_{}".format(cp_id, category, group_id)
    if result_by_groups_key not in result_by_groups:
        result_by_groups[result_by_groups_key] = []
    result_by_groups[result_by_groups_key].append(ground_object)


def parse_name(name: str) -> typing.Tuple:
    args = str(name.split()[0]).split("|")

    return args[0], int(args[1]), int(args[2])


for group in m.country("Russia").static_group + m.country("Russia").vehicle_group:
    try:
        category, cp_id, group_id = parse_name(str(group.name))
    except:
        print("Failed to parse {}".format(group.name))
        continue

    ids_counters_key = "{}_{}".format(cp_id, group_id)
    ids_counters[ids_counters_key] = ids_counters.get(ids_counters_key, 0) + 1
    object_id = ids_counters[ids_counters_key]
    append_group(cp_id, category, group_id, object_id, group.position, group.units[0].heading)

GROUP_TRESHOLD = 300
did_check_pairs = []
for group_id, objects_in_group in result_by_groups.items():
    for a in objects_in_group:
        for b in objects_in_group:
            if (a, b) in did_check_pairs:
                continue

            did_check_pairs.append((a, b))
            distance = a.position.distance_to_point(b.position)
            if distance > GROUP_TRESHOLD:
                print("Objects {} and {} in group {} are too far apart ({})!".format(a.string_identifier, b.string_identifier, group_id, distance))

print("Total {} objects".format(sum([len(x) for x in result.values()])))


with open("../cau_groundobjects.p", "wb") as f:
    pickle.dump(result, f)
