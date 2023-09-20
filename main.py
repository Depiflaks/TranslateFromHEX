import csv
import pprint
from textwrap import wrap

import pandas as pd

commands = pd.read_csv('commands.csv', encoding="utf-8")
hexdata = list(
wrap(''.join(list(map(lambda n: n[9:41], open("input.txt", mode="r").readlines()))).replace('\n', ''), 4))
data = list(map(lambda n: (bin(int(n[2:] + n[:2], 16))[2:]).rjust(16, "0"), hexdata))
ind = 0

class Cmd():
    def __init__(self):
        global ind
        self.ind = ind
        self.code = data[ind]
        self.hex_code = hexdata[ind]
        self.id = find_command(data[ind])

        self.description = commands['operation'][self.id]
        self.mask = commands['code'][self.id]

        if len(self.mask) != len(self.code):
            ind += 1
            self.hex_code += hexdata[ind]
            self.code += data[ind]

        name = commands['command'][self.id]
        self.name = name.split(' ')[0]
        self.parameters = list() if len(name.split()) == 1 else list(name.split(' ')[1].split(','))


    def get_parameters(self):
        res = dict()
        for par in self.parameters:
            res[par] = ""
            for ch_ind in range(len(self.mask)):
                if self.mask[ch_ind] == par:
                    res[par] += self.code[ch_ind]
            res[par] = int(res[par], 2)
        self.values = res

    #def edit_parameters(self):


    def __str__(self):
        out = ' '.join(wrap(self.hex_code, 2)) + " " * (16 - (len(self.hex_code) + len(self.hex_code) // 2 - 1))
        out += ' ' + self.name  + '\t'
        for i in self.parameters:
            out += " " + i + "=" + hex(self.values[i])[2:]
        return out


def find_command(code):
    l = list(commands['code'])
    for i in range(len(l)):
        flag = True
        for j in range(16):
            if not l[i][j].isalpha() and l[i][j] != code[j]:
                flag = False
                break
        if flag:
            return i


cmd_list = list()
while ind < len(data):
    print(hex((ind) * 2)[2:], end=":\t ")
    cmd_list = list()
    cmd = Cmd()
    cmd.get_parameters()
    print(cmd)
    ind += 1