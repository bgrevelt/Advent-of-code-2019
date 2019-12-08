import unittest
from collections import defaultdict
def get_orbitees(lines):
    orbits = {}
    for l in lines:
        orbitee, orbiter = l.strip().split(')')
        assert orbiter not in orbits, F"Something went wrong. It seems {orbiter} orbits both {orbits[orbiter]} and {orbitee}"
        orbits[orbiter] = orbitee
    return orbits

def get_orbiters(lines):
    orbits = defaultdict(list)
    for l in lines:
        orbitee, orbiter = l.strip().split(')')
        orbits[orbitee].append(orbiter)
        orbits[orbiter].append(orbitee)
    return orbits

def get_number_of_orbits(orbits, orbiter):
    if not orbiter in orbits:
        return 0;
    else:
        return 1 + get_number_of_orbits(orbits, orbits[orbiter])

def puzzle1(input):
    orbits = get_orbitees(input)
    return sum([get_number_of_orbits(orbits, o) for o in orbits.keys()])

def find_santa(orbits, start_from, hops_so_far = 0, prev=None):
    '''I don't think there can be more than one path to santa and one planet can't directly orbit more than one other planet, but since they explicitly ask for the shortest path I set this
    up based on the assumption that there can be more'''

    if start_from not in orbits:
        return []
    if "SAN" in orbits[start_from]:
        return [hops_so_far]
    r = []
    for next in orbits[start_from]:
        if prev == None or next != prev:
            r.extend(find_santa(orbits, next, hops_so_far + 1, start_from))
    return r

def puzzle2(input):
    orbiters = get_orbiters(input)
    paths = find_santa(orbiters, "YOU")
    # subtracty one to ignore the hop from YOU to the nearest planet
    return min(paths) - 1


class Day6UnitTests(unittest.TestCase):
    def test_puzzle1(self):
        self.assertEqual(puzzle1(["COM)B","B)C","C)D","D)E","E)F","B)G","G)H","D)I","E)J","J)K","K)L"]), 42)

    def test_puzzle2(self):
        self.assertEqual(puzzle2(["COM)B","B)C","C)D","D)E","E)F","B)G","G)H","D)I","E)J","J)K","K)L","K)YOU","I)SAN"]), 4)

if __name__ == "__main__":
    print(F"The asnwer for puzzle 1 is {puzzle1(open('input.txt').readlines())}")
    print(F"The answer for puzzle 2 is {puzzle2(open('input.txt').readlines())}")