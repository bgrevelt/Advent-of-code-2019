import abc
import unittest

class Instruction(abc.ABC):
    def __init__(self, opcode, parameter_count):
        self._opcode = opcode
        self._parameter_count = parameter_count

    def opcode(self):
        return self._opcode

    @abc.abstractmethod
    def process(self, memory, startat, parameter_modes, input_function, output_function):
        pass

    def parameter_count(self):
        return self._parameter_count

    def get_parameter(self, parameter, mode, memory):
        if mode == 0:
            assert len(memory) > parameter, F"Can't access location {parameter} in memory with size {len(memory)}"
            return memory[parameter]
        if mode == 1:
            return parameter

        assert False, F"Unsupported parameter mode {mode}"

    def set_parameter(self, parameter, mode, memory, value):
        assert mode == 0, F"Unsupported parameter mode for storing: {mode}"
        assert len(memory) > parameter, F"Can't access location {parameter} in memory with size {len(memory)}"
        memory[parameter] = value

class NullaryInstruction(Instruction):
    def __init__(self, opcode):
        super(NullaryInstruction, self).__init__(opcode, 0)

class UnaryInstruction(Instruction):
    def __init__(self, opcode):
        super(UnaryInstruction, self).__init__(opcode, 1)

class BinaryInstruction(Instruction):
    def __init__(self, opcode):
        super(BinaryInstruction, self).__init__(opcode, 2)

    def get_parameters(self, memory, startat, parameter_modes):
        self.parameter1 = super(BinaryInstruction, self).get_parameter(memory[startat], parameter_modes[0], memory)
        self.parameter2 = super(BinaryInstruction, self).get_parameter(memory[startat + 1], parameter_modes[1], memory)

class TernaryInstruction(Instruction):
    def __init__(self, opcode):
        super(TernaryInstruction, self).__init__(opcode, 3)

    def store(self, value, memory):
        assert len(memory) > self.parameter3, F"Can't access location {self.parameter3} in memory with size {len(memory)}"
        memory[self.parameter3] = value

    def get_parameters(self, memory, startat, parameter_modes):
        self.parameter1 = super(TernaryInstruction, self).get_parameter(memory[startat], parameter_modes[0], memory)
        self.parameter2 = super(TernaryInstruction, self).get_parameter(memory[startat + 1], parameter_modes[1], memory)
        self.parameter3 = memory[startat + 2]



class InstructionAdd(TernaryInstruction):
    def __init__(self):
        super(InstructionAdd, self).__init__(1)

    def process(self, memory, startat, parameter_modes, input_function, output_function):
        super(InstructionAdd, self).get_parameters(memory, startat, parameter_modes)
        super(InstructionAdd, self).store(self.parameter1 + self.parameter2, memory)
        return startat + self.parameter_count()


class InstructionMultiply(TernaryInstruction):
    def __init__(self):
        super(InstructionMultiply, self).__init__(2)

    def process(self, memory, startat, parameter_modes, input_function, output_function):
        super(InstructionMultiply, self).get_parameters(memory, startat, parameter_modes)
        super(InstructionMultiply, self).store(self.parameter1 * self.parameter2, memory)
        return startat + self.parameter_count()

class InstructionStore(UnaryInstruction):
    def __init__(self):
        super(InstructionStore, self).__init__(3)

    def process(self, memory, startat, parameter_modes, input_function, output_function):
        param = super(InstructionStore, self).get_parameter(memory[startat], parameter_modes[0], memory)
        value = input_function()
        super(InstructionStore, self).set_parameter(memory[startat], parameter_modes[0], memory, value)

        return startat + self.parameter_count()

class InstructionLoad(UnaryInstruction):
    def __init__(self):
        super(InstructionLoad, self).__init__(4)

    def process(self, memory, startat, parameter_modes, input_function, output_function):
        param = super(InstructionLoad, self).get_parameter(memory[startat], parameter_modes[0], memory)
        output_function(param)
        return startat + self.parameter_count()

class InstructionJumpIfTrue(BinaryInstruction):
    def __init__(self):
        super(InstructionJumpIfTrue, self).__init__(5)

    def process(self, memory, startat, parameter_modes, input_function, output_function):
        self.get_parameters(memory, startat, parameter_modes)
        if(self.parameter1 != 0):
            return self.parameter2
        else:
            return startat + self.parameter_count()

class InstructionJumpIfFalse(BinaryInstruction):
    def __init__(self):
        super(InstructionJumpIfFalse, self).__init__(6)

    def process(self, memory, startat, parameter_modes, input_function, output_function):
        self.get_parameters(memory, startat, parameter_modes)
        if(self.parameter1 == 0):
            return self.parameter2
        else:
            return startat + self.parameter_count()

class InstructionLessThen(TernaryInstruction):
    def __init__(self):
        super(InstructionLessThen, self).__init__(7)

    def process(self, memory, startat, parameter_modes, input_function, output_function):
        self.get_parameters(memory, startat, parameter_modes)
        super(InstructionLessThen, self).store(1 if self.parameter1 < self.parameter2 else 0, memory)

        return startat + self.parameter_count()

class InstructionEquals(TernaryInstruction):
    def __init__(self):
        super(InstructionEquals, self).__init__(8)

    def process(self, memory, startat, parameter_modes, input_function, output_function):
        self.get_parameters(memory, startat, parameter_modes)
        super(InstructionEquals, self).store(1 if self.parameter1 == self.parameter2 else 0, memory)

        return startat + self.parameter_count()

class InstructionHalt(NullaryInstruction):
    def __init__(self):
        super(InstructionHalt, self).__init__(99)

    def process(self, memory, startat, parameter_modes, input_function, output_function):
        return startat + self.parameter_count()


class IntcodeProcessor:
    def __init__(self, program, input = []):
        self.operations = {operation.opcode() : operation for operation in [InstructionAdd(), InstructionMultiply(), InstructionHalt(), InstructionStore(), InstructionLoad(), InstructionJumpIfFalse(), InstructionJumpIfTrue(), InstructionLessThen(), InstructionEquals() ]}
        self.output = []
        self.input = input
        self.memory = program
        self.instruction_pointer = 0

    def Process(self):
        while True:
            opcode, parameter_modes = self.split_instruction(self.memory[self.instruction_pointer])
            if opcode == 99:
                return 'HALT'

            if opcode == 3 and len(self.input) <= 0:
                return 'INPUT'

            self.instruction_pointer += 1
            assert opcode in self.operations, F"Unknown opcode {opcode}"
            next = self.operations[opcode].process(self.memory, self.instruction_pointer, parameter_modes, self.get_input, self.write_output)
            self.instruction_pointer = next

            if opcode == 4:
                return 'OUTPUT'

    def get_input(self):
        assert len(self.input) > 0, "Instruction needs input, but input is empty!"
        v = self.input[0]
        self.input = self.input[1:]
        return v

    def write_output(self, value):
        self.output.append(value)

    def split_instruction(self, instruction):
        opcode = instruction % 100
        assert opcode in self.operations, F"Uknown opcode {opcode}"
        parameter_count = self.operations[opcode].parameter_count()
        parameter_modes = [int(n) for n in str(instruction // 100)]
        parameter_modes.reverse()
        parameter_modes += ([0] *(parameter_count - len(parameter_modes)))
        return (opcode, parameter_modes)

def run(intcodes):
    proc = IntcodeProcessor(intcodes)
    while proc.Process() != 'HALT':
        pass
    return intcodes

class IntcodeProcessorTests(unittest.TestCase):
    def test_position_mode(self):
        # add
        self.assertEqual(run([1,5,6,3,99,25,35]), [1,5,6,60,99,25,35])
        # mul
        self.assertEqual(run([2, 5, 6, 3, 99, 25, 35]), [2, 5, 6, 875, 99, 25, 35])

    def test_immediate_mode(self):
        # add
        self.assertEqual(run([1101, 5, 6, 3, 99, 25, 35]), [1101, 5, 6, 11, 99, 25, 35])
        # mul
        self.assertEqual(run([1102, 5, 6, 3, 99, 25, 35]), [1102, 5, 6, 30, 99, 25, 35])

    def test_split_oppcode(self):
        proc = IntcodeProcessor([])
        self.assertEqual(proc.split_instruction(1), (1,[0,0,0]))
        self.assertEqual(proc.split_instruction(101), (1, [1, 0, 0]))
        self.assertEqual(proc.split_instruction(1101), (1, [1, 1, 0]))
        self.assertEqual(proc.split_instruction(11101), (1, [1, 1, 1]))
        self.assertEqual(proc.split_instruction(10101), (1, [1, 0, 1]))

    def test_day2_unittests(self):
        #regression test to make sure the programs from day 2 still run
        self.assertEqual(run([1, 9, 10, 3, 2, 3, 11, 0, 99, 30, 40, 50]),
                         [3500, 9, 10, 70, 2, 3, 11, 0, 99, 30, 40, 50])
        self.assertEqual(run([1, 0, 0, 0, 99]), [2, 0, 0, 0, 99])
        self.assertEqual(run([2, 3, 0, 3, 99]), [2, 3, 0, 6, 99])
        self.assertEqual(run([2, 4, 4, 5, 99, 0]), [2, 4, 4, 5, 99, 9801])
        self.assertEqual(run([1, 1, 1, 4, 99, 5, 6, 0, 99]), [30, 1, 1, 4, 2, 5, 6, 0, 99])

    def test_day5_puzzle1(self):
        with open('../day5/input.txt') as f:
            memory = [int(n) for n in f.read().split(',')]
            proc = IntcodeProcessor(memory, [1])
            while proc.Process() != 'HALT':
                pass
            self.assertTrue(all(v == 0 for v in proc.output[:-1]))
            self.assertEqual(proc.output[-1], 9219874)

    def test_day5_puzzle2(self):
        with open('../day5/input.txt') as f:
            memory = [int(n) for n in f.read().split(',')]
            proc = IntcodeProcessor(memory, [5])
            while proc.Process() != 'HALT':
                pass
            self.assertEqual(proc.output, [5893654])

    def test_day7_puzzle1(self):
        '''Max thruster signal 43210(from phase setting sequence 4, 3, 2, 1, 0):
        3, 15, 3, 16, 1002, 16, 10, 16, 1, 16, 15, 15, 4, 15, 99, 0, 0'''
        self.assertEqual(43210, run_amplifier_series([3, 15, 3, 16, 1002, 16, 10, 16, 1, 16, 15, 15, 4, 15, 99, 0, 0],[4, 3, 2, 1, 0]))
        '''Max thruster signal 54321( from phase setting sequence 0, 1, 2, 3, 4):
        3, 23, 3, 24, 1002, 24, 10, 24, 1002, 23, -1, 23, 101, 5, 23, 23, 1, 24, 23, 23, 4, 23, 99, 0, 0'''
        self.assertEqual(54321, run_amplifier_series([3, 23, 3, 24, 1002, 24, 10, 24, 1002, 23, -1, 23, 101, 5, 23, 23, 1, 24, 23, 23, 4, 23, 99, 0, 0],
                                                     [0, 1, 2, 3, 4]))
        '''Max thruster signal 65210(from phase setting sequence 1, 0, 4, 3, 2):
        3, 31, 3, 32, 1002, 32, 10, 32, 1001, 31, -2, 31, 1007, 31, 0, 33, 1002, 33, 7, 33, 1, 33, 31, 31, 1, 32, 31, 31, 4, 31, 99, 0, 0, 0'''
        self.assertEqual(65210, run_amplifier_series([3, 31, 3, 32, 1002, 32, 10, 32, 1001, 31, -2, 31, 1007, 31, 0, 33, 1002, 33, 7, 33, 1, 33, 31, 31, 1, 32, 31, 31, 4, 31, 99, 0, 0, 0],
                                                     [1, 0, 4, 3, 2]))

    def test_day7_puzzle2(self):
        '''Max thruster signal 139629729 (from phase setting sequence 9,8,7,6,5):
        3,26,1001,26,-4,26,3,27,1002,27,2,27,1,27,26,
        27,4,27,1001,28,-1,28,1005,28,6,99,0,0,5'''
        self.assertEqual(139629729,
                         run_amplifier_series_loop([3,26,1001,26,-4,26,3,27,1002,27,2,27,1,27,26,27,4,27,1001,28,-1,28,1005,28,6,99,0,0,5],[9,8,7,6,5]))

        '''Max thruster signal 18216 (from phase setting sequence 9,7,8,5,6):
                3,52,1001,52,-5,52,3,53,1,52,56,54,1007,54,5,55,1005,55,26,1001,54,
                -5,54,1105,1,12,1,53,54,53,1008,54,0,55,1001,55,1,55,2,53,55,53,4,
                53,1001,56,-1,56,1005,56,6,99,0,0,0,0,10'''
        self.assertEqual(18216,
                     run_amplifier_series_loop(
                         [3,52,1001,52,-5,52,3,53,1,52,56,54,1007,54,5,55,1005,55,26,1001,54,-5,54,1105,1,12,1,53,54,53,1008,54,0,55,1001,55,1,55,2,53,55,53,4,53,1001,56,-1,56,1005,56,6,99,0,0,0,0,10], [9,7,8,5,6]))


def permutations(numbers):
    if len(numbers) == 0:
        return [[]]
    r = []
    for i, number in enumerate(numbers):
        rest = numbers[:i] + numbers[i+1:]
        r.extend([[number] + p for p in permutations(rest)])
    return r

def run_amplifier_series(program, phase_setting_sequence):
    assert len(phase_setting_sequence) == 5, F"We only have {len(phase_setting_sequence)} phase settings instead of 5!"

    last_output = [0]
    for stage in range(5):
        #poor mans deepcopy
        memory = [n for n in program]
        processor = IntcodeProcessor(memory, [phase_setting_sequence[stage]] + last_output)
        while processor.Process() != 'HALT':
            pass
        assert len(processor.output) == 1, "I think there should be exactly 1 output"
        last_output = processor.output

    return last_output[0]

def run_amplifier_series_loop(program, phase_setting_sequence):
    amplifiers = [IntcodeProcessor([n for n in program], [phase_setting_sequence[amp]]) for amp in range(5)]
    last_output = 0
    current_amp = 0
    while True:
        amp = amplifiers[current_amp]
        amp.input.append(last_output)
        r = amp.Process()
        if r == 'HALT':
            #assert  current_amp == 4, "The story suggests that only the last amp should halt"
            return last_output
        elif r == 'INPUT':
            assert False, "I don't think we should ever come here..."
            continue
        elif r == 'OUTPUT':
            last_output = amp.output[0]
            amp.output = amp.output[1:]
            # switch to the next amp
            current_amp += 1
            current_amp %= 5
            continue

        assert False, "Ehm.. We shouldn't get here..."


def puzzle1():
    with open('input.txt') as f:
        input =  [int(n) for n in f.read().split(',')]
        phase_setting_sequences = permutations(list(range(5)))
        thruster_signals = [run_amplifier_series(input, sequence) for sequence in phase_setting_sequences]
        return max(thruster_signals)

def puzzle2():
    with open('input.txt') as f:
        input =  [int(n) for n in f.read().split(',')]
        phase_setting_sequences = permutations([5,6,7,8,9])
        thruster_signals = [run_amplifier_series_loop(input, sequence) for sequence in phase_setting_sequences]
        return max(thruster_signals)

print(F'The solution to puzzle one is {puzzle1()}')
print(F'The solution to puzzle one is {puzzle2()}')