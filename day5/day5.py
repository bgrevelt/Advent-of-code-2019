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