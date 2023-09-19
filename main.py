import csv
import pprint
from textwrap import wrap

import pandas as pd

commands = pd.read_csv('commands.csv', encoding="utf-8")
hexdata = list(wrap(''.join(list(map(lambda n: n[9:41], open("input.txt", mode="r").readlines()))).replace('\n', ''), 4))
data = list(map(lambda n: (bin(int(n[2:] + n[:2], 16))[2:]).rjust(16, "0"), hexdata))


class Cmd():
    def __init__(self, ind):
        self.code = data[ind]
        self.hex_code = hexdata[ind]
        self.id = find_command(data[ind])
        self.description = commands['operation'][self.id]
        name = commands['command'][self.id]
        self.name, self.parameters = name.split(' ')[0], list(name.split(' ')[1].split(','))
        self.mask = commands['code'][self.id]

    def get_parameters(self):
        res = dict()
        for par in self.parameters:
            res[par] = ""
            for ch_ind in range(len(self.mask)):
                if self.mask[ch_ind] == par:
                    res[par] += self.code[ch_ind]
            res[par] = hex(int(res[par], 2))
        self.values = res

    def __str__(self):
        out = ' '.join(wrap(self.hex_code, 2))
        out += ' ' + self.name
        for i in self.parameters:
            out += " " + i + self.values[i]
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


ind = 0

while ind < len(data):
    print(hex((ind) * 2), end=" ")
    cmd = Cmd(ind)
    if len(commands['code'][cmd.id]) != len(cmd.code):
        ind += 1
        cmd.hex_code += hexdata[ind]
        cmd.code += data[ind]
    cmd.get_parameters()
    print(cmd)
    ind += 1

#print(data)