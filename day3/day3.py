def is_vertical(line):
    return line[0][0] == line[1][0]

def do_lines_cross(horizontal, vertical):
    # x of the vertical crosses the horizontal
    horx = horizontal[0][0]
    verx = (min(vertical[0][0], vertical[1][0]), max(vertical[0][0], vertical[1][0]))
    # y of the horizontal crosses the vertical
    very = vertical[0][1]
    hory = (min(horizontal[0][1], horizontal[1][1]), max(horizontal[0][1], horizontal[1][1]))

    r = (verx[0] <= horx and verx[1] >= horx and hory[0] <= very and hory[1] >= very)
    return r

def line_length(line):
    if is_vertical(line):
        return abs(line[1][1] - line[0][1])
    else:
        return abs(line[1][0] - line[0][0])

def distance_from_start(line, point):
    if is_vertical(line):
        assert line[0][0] == point[0]
        return abs(point[1] - line[0][1])
    else:
        return abs(point[0] - line[0][0])


def cross(line1, line2):
    if is_vertical(line1) and not is_vertical(line2) and do_lines_cross(line1, line2):
        return line1[0][0], line2[0][1]
    elif not is_vertical(line1) and is_vertical(line2) and do_lines_cross(line2, line1):
        return line2[0][0], line1[0][1]

    return None

def texttoline(text, start):
    direction = text[0]
    length = int(text[1:])
    if (direction == 'U'):
        return (start[0], start[1] + length)
    elif (direction == 'D'):
        return (start[0], start[1] - length)
    elif (direction == 'L'):
        return (start[0] - length, start[1])
    elif (direction == 'R'):
        return (start[0] + length, start[1])
    else:
        assert False

    return None

def distance(coord):
    return abs(coord[0]) + abs(coord[1])

def path_to_lines(path):
    coords = [(0, 0)]
    for token in path:
        coords.append(texttoline(token, coords[-1]))

    return [(coords[n], coords[n + 1]) for n in range(len(coords) - 1)]

def get_min_cross_distance(path1, path2):
    path1 = path_to_lines(path1)
    path2 = path_to_lines(path2)

    crosses = []
    for line1 in path1:
        for line2 in path2:
            c = cross(line1, line2)
            if c is not None and c != (0,0):
                crosses.append(c)

    distances = [distance(c) for c in crosses]
    print(min(distances))

def get_min_cross_distance2(path1, path2):
    path1 = path_to_lines(path1)
    path2 = path_to_lines(path2)

    steps = []
    for i1, line1 in enumerate(path1):
        for i2, line2 in enumerate(path2):
            c = cross(line1, line2)
            if c is not None and c != (0,0):
                length1 =[line_length(l) for l in path1[:i1]] + [distance_from_start(line1, c)]
                length2 = [line_length(l) for l in path2[:i2]] + [distance_from_start(line2, c)]
                steps.append(sum(length1+length2))

    print(min(steps))

with open("input.txt") as f:
    paths = [l.split(',') for l in f.readlines()]
    get_min_cross_distance(paths[0], paths[1])
    get_min_cross_distance2(paths[0], paths[1])

# get_min_cross_distance2("R8,U5,L5,D3".split(','),"U7,R6,D4,L4".split(','))
# get_min_cross_distance2("R75,D30,R83,U83,L12,D49,R71,U7,L72".split(','),"U62,R66,U55,R34,D71,R55,D58,R83".split(','))
# get_min_cross_distance2("R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51".split(','),"U98,R91,D20,R16,D67,R40,U7,R15,U6,R7".split(','))