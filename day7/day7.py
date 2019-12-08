import abc
import unittest

class Instruction(abc.ABC):
    def __init__(self, opcode, parameter_count):
        self._opcode = opcode
        self._parameter_count = parameter_count

    def opcode(self):
        return self._opcode

    @abc.abstractmethod
    def process(self, memory, startat, parameter_modes):
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

    def process(self, memory, startat, parameter_modes):
        super(InstructionAdd, self).get_parameters(memory, startat, parameter_modes)
        super(InstructionAdd, self).store(self.parameter1 + self.parameter2, memory)
        return startat + self.parameter_count()


class InstructionMultiply(TernaryInstruction):
    def __init__(self):
        super(InstructionMultiply, self).__init__(2)

    def process(self, memory, startat, parameter_modes):
        super(InstructionMultiply, self).get_parameters(memory, startat, parameter_modes)
        super(InstructionMultiply, self).store(self.parameter1 * self.parameter2, memory)
        return startat + self.parameter_count()

class InstructionStore(UnaryInstruction):
    def __init__(self):
        super(InstructionStore, self).__init__(3)

    def process(self, memory, startat, parameter_modes):
        param = super(InstructionStore, self).get_parameter(memory[startat], parameter_modes[0], memory)
        value = int(input("Input: "))
        super(InstructionStore, self).set_parameter(memory[startat], parameter_modes[0], memory, value)

        return startat + self.parameter_count()

class InstructionLoad(UnaryInstruction):
    def __init__(self):
        super(InstructionLoad, self).__init__(4)

    def process(self, memory, startat, parameter_modes):
        param = super(InstructionLoad, self).get_parameter(memory[startat], parameter_modes[0], memory)
        print(param)
        return startat + self.parameter_count()

class InstructionJumpIfTrue(BinaryInstruction):
    def __init__(self):
        super(InstructionJumpIfTrue, self).__init__(5)

    def process(self, memory, startat, parameter_modes):
        self.get_parameters(memory, startat, parameter_modes)
        if(self.parameter1 != 0):
            return self.parameter2
        else:
            return startat + self.parameter_count()

class InstructionJumpIfFalse(BinaryInstruction):
    def __init__(self):
        super(InstructionJumpIfFalse, self).__init__(6)

    def process(self, memory, startat, parameter_modes):
        self.get_parameters(memory, startat, parameter_modes)
        if(self.parameter1 == 0):
            return self.parameter2
        else:
            return startat + self.parameter_count()

class InstructionLessThen(TernaryInstruction):
    def __init__(self):
        super(InstructionLessThen, self).__init__(7)

    def process(self, memory, startat, parameter_modes):
        self.get_parameters(memory, startat, parameter_modes)
        super(InstructionLessThen, self).store(1 if self.parameter1 < self.parameter2 else 0, memory)

        return startat + self.parameter_count()

class InstructionEquals(TernaryInstruction):
    def __init__(self):
        super(InstructionEquals, self).__init__(8)

    def process(self, memory, startat, parameter_modes):
        self.get_parameters(memory, startat, parameter_modes)
        super(InstructionEquals, self).store(1 if self.parameter1 == self.parameter2 else 0, memory)

        return startat + self.parameter_count()

class InstructionHalt(NullaryInstruction):
    def __init__(self):
        super(InstructionHalt, self).__init__(99)

    def process(self, memory, startat, parameter_modes):
        return startat + self.parameter_count()


class IntcodeProcessor:
    def __init__(self):
        self.operations = {operation.opcode() : operation for operation in [InstructionAdd(), InstructionMultiply(), InstructionHalt(), InstructionStore(), InstructionLoad(), InstructionJumpIfFalse(), InstructionJumpIfTrue(), InstructionLessThen(), InstructionEquals() ]}

    def Process(self, memory):
        instruction_pointer = 0
        while True:
            opcode, parameter_modes = self.split_instruction(memory[instruction_pointer])
            if opcode == 99:
                break


            instruction_pointer += 1
            assert opcode in self.operations, F"Unknown opcode {opcode}"
            next = self.operations[opcode].process(memory, instruction_pointer, parameter_modes)
            instruction_pointer = next

    def split_instruction(self, instruction):
        opcode = instruction % 100
        assert opcode in self.operations, F"Uknown opcode {opcode}"
        parameter_count = self.operations[opcode].parameter_count()
        parameter_modes = [int(n) for n in str(instruction // 100)]
        parameter_modes.reverse()
        parameter_modes += ([0] *(parameter_count - len(parameter_modes)))
        return (opcode, parameter_modes)

def run(intcodes):
    proc = IntcodeProcessor()
    proc.Process(intcodes)
    return intcodes