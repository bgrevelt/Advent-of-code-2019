import abc
import unittest

class Instruction(abc.ABC):
    def __init__(self, opcode, parameter_count):
        self._opcode = opcode
        self._parameter_count = parameter_count

    def opcode(self):
        return self._opcode

    @abc.abstractmethod
    def process(self, machine_state, parameter_modes):
        pass

    def parameter_count(self):
        return self._parameter_count

    def get_parameter(self, parameter, mode, memory, relative_base):
        if mode == 0:
            assert len(memory) > parameter, F"Can't access location {parameter} in memory with size {len(memory)}"
            return memory[parameter]
        if mode == 1:
            return parameter
        if mode == 2:
            assert len(memory) > (parameter + relative_base), F"Can't access location {parameter} in memory with size {len(memory)}"
            return memory[parameter + relative_base]

        assert False, F"Unsupported parameter mode {mode}"

    def set_parameter(self, parameter, mode, memory, value, relative_base):
        assert mode == 0 or mode == 2, F"Unsupported parameter mode for storing: {mode}"
        offset = parameter + relative_base
        assert len(memory) > offset, F"Can't access location {offset} in memory with size {len(memory)}"
        memory[offset] = value

class NullaryInstruction(Instruction):
    def __init__(self, opcode):
        super(NullaryInstruction, self).__init__(opcode, 0)

class UnaryInstruction(Instruction):
    def __init__(self, opcode):
        super(UnaryInstruction, self).__init__(opcode, 1)

class BinaryInstruction(Instruction):
    def __init__(self, opcode):
        super(BinaryInstruction, self).__init__(opcode, 2)

    def get_parameters(self, memory, startat, parameter_modes, relative_base):
        self.parameter1 = super(BinaryInstruction, self).get_parameter(memory[startat], parameter_modes[0], memory, relative_base)
        self.parameter2 = super(BinaryInstruction, self).get_parameter(memory[startat + 1], parameter_modes[1], memory, relative_base)

class TernaryInstruction(Instruction):
    def __init__(self, opcode):
        super(TernaryInstruction, self).__init__(opcode, 3)

    def store(self, value, memory):
        assert len(memory) > self.parameter3, F"Can't access location {self.parameter3} in memory with size {len(memory)}"
        memory[self.parameter3] = value

    def get_parameters(self, memory, startat, parameter_modes, relative_base):
        self.parameter1 = super(TernaryInstruction, self).get_parameter(memory[startat], parameter_modes[0], memory, relative_base)
        self.parameter2 = super(TernaryInstruction, self).get_parameter(memory[startat + 1], parameter_modes[1], memory, relative_base)
        if parameter_modes[2] == 0:
            self.parameter3 = memory[startat + 2]
        elif parameter_modes[2] == 2:
            self.parameter3 = memory[startat + 2] + relative_base



class InstructionAdd(TernaryInstruction):
    def __init__(self):
        super(InstructionAdd, self).__init__(1)

    def process(self, machine_state, parameter_modes):
        super(InstructionAdd, self).get_parameters(machine_state.memory, machine_state.instruction_pointer, parameter_modes, machine_state.relative_base)
        super(InstructionAdd, self).store(self.parameter1 + self.parameter2, machine_state.memory)
        machine_state.instruction_pointer += self.parameter_count()


class InstructionMultiply(TernaryInstruction):
    def __init__(self):
        super(InstructionMultiply, self).__init__(2)

    def process(self, machine_state, parameter_modes):
        super(InstructionMultiply, self).get_parameters(machine_state.memory, machine_state.instruction_pointer, parameter_modes, machine_state.relative_base)
        super(InstructionMultiply, self).store(self.parameter1 * self.parameter2, machine_state.memory)
        machine_state.instruction_pointer += self.parameter_count()

class InstructionStore(UnaryInstruction):
    def __init__(self):
        super(InstructionStore, self).__init__(3)

    def process(self, machine_state, parameter_modes):
        param = super(InstructionStore, self).get_parameter(machine_state.memory[machine_state.instruction_pointer], parameter_modes[0], machine_state.memory, machine_state.relative_base)
        assert len(machine_state.input) > 0, "Input function called but there is no input"
        value = machine_state.input[0]
        input_function = machine_state.input[1:]
        super(InstructionStore, self).set_parameter(machine_state.memory[machine_state.instruction_pointer], parameter_modes[0], machine_state.memory, value, machine_state.relative_base)

        machine_state.instruction_pointer += self.parameter_count()

class InstructionLoad(UnaryInstruction):
    def __init__(self):
        super(InstructionLoad, self).__init__(4)

    def process(self, machine_state, parameter_modes):
        param = super(InstructionLoad, self).get_parameter(machine_state.memory[machine_state.instruction_pointer], parameter_modes[0], machine_state.memory, machine_state.relative_base)
        machine_state.output.append(param)
        machine_state.instruction_pointer += self.parameter_count()

class InstructionJumpIfTrue(BinaryInstruction):
    def __init__(self):
        super(InstructionJumpIfTrue, self).__init__(5)

    def process(self, machine_state, parameter_modes):
        self.get_parameters(machine_state.memory, machine_state.instruction_pointer, parameter_modes, machine_state.relative_base)
        if(self.parameter1 != 0):
            machine_state.instruction_pointer = self.parameter2
        else:
            machine_state.instruction_pointer += self.parameter_count()

class InstructionJumpIfFalse(BinaryInstruction):
    def __init__(self):
        super(InstructionJumpIfFalse, self).__init__(6)

    def process(self, machine_state, parameter_modes):
        self.get_parameters(machine_state.memory, machine_state.instruction_pointer, parameter_modes, machine_state.relative_base)
        if(self.parameter1 == 0):
            machine_state.instruction_pointer = self.parameter2
        else:
            machine_state.instruction_pointer += self.parameter_count()

class InstructionLessThen(TernaryInstruction):
    def __init__(self):
        super(InstructionLessThen, self).__init__(7)

    def process(self, machine_state, parameter_modes):
        self.get_parameters(machine_state.memory, machine_state.instruction_pointer, parameter_modes, machine_state.relative_base)
        super(InstructionLessThen, self).store(1 if self.parameter1 < self.parameter2 else 0, machine_state.memory)

        machine_state.instruction_pointer += self.parameter_count()

class InstructionEquals(TernaryInstruction):
    def __init__(self):
        super(InstructionEquals, self).__init__(8)

    def process(self, machine_state, parameter_modes):
        self.get_parameters(machine_state.memory, machine_state.instruction_pointer, parameter_modes, machine_state.relative_base)
        super(InstructionEquals, self).store(1 if self.parameter1 == self.parameter2 else 0, machine_state.memory)

        machine_state.instruction_pointer += self.parameter_count()

class InstructionAdjustRelativeBase(UnaryInstruction):
    def __init__(self):
        super(InstructionAdjustRelativeBase, self).__init__(9)

    def process(self, machine_state, parameter_modes):
        param = super(InstructionAdjustRelativeBase, self).get_parameter(machine_state.memory[machine_state.instruction_pointer], parameter_modes[0], machine_state.memory, machine_state.relative_base)

        machine_state.instruction_pointer += self.parameter_count()
        machine_state.relative_base += param

class InstructionHalt(NullaryInstruction):
    def __init__(self):
        super(InstructionHalt, self).__init__(99)

    def process(self, machine_state, parameter_modes):
        machine_state.instruction_pointer += self.parameter_count()


class IntcodeProcessor:
    class State:
        def __init__(self):
            self.input = []
            self.output = []
            self.memory = []
            self.instruction_pointer = 0
            self.relative_base = 0

    def __init__(self, program, input = []):
        self.operations = {operation.opcode() : operation for operation in [InstructionAdd(), InstructionMultiply(), InstructionHalt(), InstructionStore(), InstructionLoad(), InstructionJumpIfFalse(), InstructionJumpIfTrue(), InstructionLessThen(), InstructionEquals(), InstructionAdjustRelativeBase() ]}
        self.state = self.State()
        self.state.input = input
        self.state.memory = program

    def Process(self):
        while True:
            opcode, parameter_modes = self.split_instruction(self.state.memory[self.state.instruction_pointer])
            if opcode == 99:
                return 'HALT'

            self.state.instruction_pointer += 1
            assert opcode in self.operations, F"Unknown opcode {opcode}"
            self.operations[opcode].process(self.state, parameter_modes)


    def get_input(self):
        assert len(self.state.input) > 0, "Instruction needs input, but input is empty!"
        v = self.state.input[0]
        self.state.input = self.state.input[1:]
        return v

    def write_output(self, value):
        self.state.output.append(value)

    def split_instruction(self, instruction):
        opcode = instruction % 100
        assert opcode in self.operations, F"Uknown opcode {opcode}"
        parameter_count = self.operations[opcode].parameter_count()
        parameter_modes = [int(n) for n in str(instruction // 100)]
        parameter_modes.reverse()
        parameter_modes += ([0] *(parameter_count - len(parameter_modes)))
        return (opcode, parameter_modes)

def run(intcodes):
    proc = IntcodeProcessor(intcodes + ([0] * 10**3))
    while proc.Process() != 'HALT':
        pass
    return proc.state.memory[:len(intcodes)]

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
            self.assertTrue(all(v == 0 for v in proc.state.output[:-1]))
            self.assertEqual(proc.state.output[-1], 9219874)

    def test_day5_puzzle2(self):
        with open('../day5/input.txt') as f:
            memory = [int(n) for n in f.read().split(',')]
            proc = IntcodeProcessor(memory, [5])
            while proc.Process() != 'HALT':
                pass
            self.assertEqual(proc.state.output, [5893654])

    def test_day9_puzzle1(self):
        with open('input.txt') as f:
            memory = [int(n) for n in f.read().split(',')]
            memory += [0] * 10**3
            proc = IntcodeProcessor(memory, [1])
            proc.Process()
            self.assertEqual(proc.state.output[-1], 2890527621)

    def test_day9_puzzle2(self):
        with open('input.txt') as f:
            memory = [int(n) for n in f.read().split(',')]
            memory += [0] * 10 ** 3
            proc = IntcodeProcessor(memory, [2])
            proc.Process()
            self.assertEqual(proc.state.output[-1], 66772)



def puzzle1(input):
    p = IntcodeProcessor(input + ([0] * 10**3), [1])
    p.Process()
    return p.state.output[-1]

def puzzle2(input):
    p = IntcodeProcessor(input + ([0] * 10**3), [2])
    p.Process()
    return p.state.output[-1]

if __name__ == "__main__":
    with open('input.txt') as f:
        c1 = [int(n) for n in f.read().split(',')]
        c2 = [n for n in c1]
        print(F"The answer to puzzle 1 is {puzzle1(c1)}")
        print(F"The answer to puzzle 2 is {puzzle2(c2)}")

