def is_duplicate(digit, digits):
    return digits.count(digit) == 2

def isvalid(code, puzzle2 = False):
    digits = [ord(c) for c in str(code)]
    if len(digits) != 6:
        return False
    if not puzzle2:
        if not any(digits[n] == digits[n+1] for n in range(len(digits)-1)):
            return False
    else:
        if not any(is_duplicate(digit, digits) for digit in digits):
            return False
    if not all(digits[n] <= digits[n+1] for n in range(len(digits)-1)):
        return False

    return True

'''There seem to be a lot of smart things we can do here and I'm sure we're going to need it for puzzle2
but I'm just going to brute force this one'''
def puzzle1(start,end):
    valids = [n for n in range(start, end+1) if isvalid(n)]
    print(len(valids))

def puzzle2(start,end):
    valids = [n for n in range(start, end+1) if isvalid(n, True)]
    print(len(valids))

print(isvalid(111111)) # meets these criteria (double 11, never decreases).
print(isvalid(223450))# does not meet these criteria (decreasing pair of digits 50).
print(isvalid(123789)) # does not meet these criteria (no double).

puzzle1(172851,675869)
puzzle2(172851,675869)