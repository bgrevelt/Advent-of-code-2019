import abc
import operator
import unittest

class Instruction(abc.ABC):
    @abc.abstractmethod
    def opcode(self):
        pass

    @abc.abstractmethod
    def process(self, memory, startat):
        pass

class BinaryInstruction(Instruction):
    def __init__(self, operator, opcode):
        self._operator = operator
        self._opcode = opcode
        self._number_of_parameters = 3

    def opcode(self):
        return self._opcode

    def process(self, memory, startat):
        parameters = memory[startat : startat + self._number_of_parameters]

        memory[parameters[2]] = self._operator(memory[parameters[0]],memory[parameters[1]])
        return self._number_of_parameters


class InstructionAdd(BinaryInstruction):
    def __init__(self):
        super(InstructionAdd, self).__init__(operator.add, 1)

class InstructionMultiply(BinaryInstruction):
    def __init__(self):
        super(InstructionMultiply, self).__init__(operator.mul, 2)


class IntcodeProcessor:
    def __init__(self):
        self.operations = {operation.opcode() : operation for operation in [InstructionAdd(), InstructionMultiply()]}

    def Process(self, memory):
        instruction_pointer = 0
        while True:
            opcode = memory[instruction_pointer]
            if opcode == 99:
                break

            instruction_pointer += 1
            assert opcode in self.operations, F"Unknown opcode {opcode}"
            tokens_consumed = self.operations[opcode].process(memory, instruction_pointer)
            instruction_pointer += tokens_consumed

def run(intcodes):
    proc = IntcodeProcessor()
    proc.Process(intcodes)
    return intcodes

class UnitTests(unittest.TestCase):
    def test_puzzle1_1(self):
        '''
        For example, suppose you have the following program:
        1,9,10,3,2,3,11,0,99,30,40,50
        ...
        3500,9,10,70,2,3,11,0,99,30,40,50
        '''
        self.assertEqual(run([1,9,10,3,2,3,11,0,99,30,40,50]), [3500,9,10,70,2,3,11,0,99,30,40,50])

    '''Here are the initial and final states of a few more small programs:'''
    def test_puzzle1_2(self):
        '''1,0,0,0,99 becomes 2,0,0,0,99 (1 + 1 = 2).'''
        self.assertEqual(run([1,0,0,0,99]), [2,0,0,0,99])

    def test_puzzle1_3(self):
        '''2,3,0,3,99 becomes 2,3,0,6,99 (3 * 2 = 6).'''
        self.assertEqual(run([2,3,0,3,99]), [2,3,0,6,99])

    def test_puzzle1_4(self):
        '''2,4,4,5,99,0 becomes 2,4,4,5,99,9801 (99 * 99 = 9801).'''
        self.assertEqual(run([2,4,4,5,99,0]), [2,4,4,5,99,9801])

    def test_puzzle1_5(self):
        '''1,1,1,4,99,5,6,0,99 becomes 30,1,1,4,2,5,6,0,99.'''
        self.assertEqual(run([1,1,1,4,99,5,6,0,99]), [30,1,1,4,2,5,6,0,99])

def puzzle1():
    with open('input.txt') as f:
        memory = [int(n) for n in f.read().split(',')]
        memory[1] = 12
        memory[2] = 2
        run(memory)
        print(F"The result of puzzle 1 is {memory[0]}")

def puzzle2():
    '''Naive implementation, but it runs in a couple of seconds, so I can live with it...'''
    with open('input.txt') as f:
        memory_at_reset = [int(n) for n in f.read().split(',')]

        possible_inputs = [(noun,verb) for noun in range(100) for verb in range(100)]
        for noun,verb in possible_inputs:
            memory = [n for n in memory_at_reset]
            memory[1] = noun
            memory[2] = verb
            run(memory)
            if memory[0] == 19690720:
                print(F"The result of puzzle 1 is {100 * noun + verb}")
                break


puzzle1()
puzzle2()
