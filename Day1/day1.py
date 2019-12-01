import unittest

def fuelrequired(mass):
    return (mass // 3) -2

def puzzle1():
    with open('input1.txt') as input:
        masses = (int(line) for line in input.readlines())
        fuel = sum(fuelrequired(mass) for mass in masses)
        print(F'Total fuel required: {fuel}')

def realrequiredfuel(mass):
    fuel = fuelrequired(mass)
    return 0 if fuel <= 0 else fuel + realrequiredfuel(fuel)

def puzzle2():
    with open('input1.txt') as input:
        masses = (int(line) for line in input.readlines())
        fuel = sum(realrequiredfuel(mass) for mass in masses)
        print(F'Real total fuel required: {fuel}')

class TestPuzzle(unittest.TestCase):
    def test_puzzle1(self):
        '''For a mass of 12, divide by 3 and round down to get 4, then subtract 2 to get 2.
        For a mass of 14, dividing by 3 and rounding down still yields 4, so the fuel required is also 2.
        For a mass of 1969, the fuel required is 654.
        For a mass of 100756, the fuel required is 33583.'''
        self.assertEqual(fuelrequired(12), 2)
        self.assertEqual(fuelrequired(14), 2)
        self.assertEqual(fuelrequired(1969), 654)
        self.assertEqual(fuelrequired(100756), 33583)

    def test_puzzle2(self):
        '''A module of mass 14 requires 2 fuel. This fuel requires no further fuel (2 divided by 3 and rounded down is 0, which would call for a negative fuel), so the total fuel required is still just 2.
        At first, a module of mass 1969 requires 654 fuel. Then, this fuel requires 216 more fuel (654 / 3 - 2). 216 then requires 70 more fuel, which requires 21 fuel, which requires 5 fuel, which requires no further fuel. So, the total fuel required for a module of mass 1969 is 654 + 216 + 70 + 21 + 5 = 966.
        The fuel required by a module of mass 100756 and its fuel is: 33583 + 11192 + 3728 + 1240 + 411 + 135 + 43 + 12 + 2 = 50346.
        '''
        self.assertEqual(realrequiredfuel(14), 2)
        self.assertEqual(realrequiredfuel(1969), 966)
        self.assertEqual(realrequiredfuel(100756), 50346)

if __name__ == '__main__':
    puzzle1()
    puzzle2()