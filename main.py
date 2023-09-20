import csv
import pprint
from textwrap import wrap

import pandas as pd

# чтение csv файла с помощью библиотеки pandas
commands = pd.read_csv('commands.csv', encoding="utf-8")
# производим редактирование полученных данных: отбрысываем информацию, тип команды, контрольную сумму, группируем по 4 символа
# так как именно столько символов в 1 инструкции
hexdata = list(
wrap(''.join(list(map(lambda n: n[9:41], open("input.txt", mode="r").readlines()))).replace('\n', ''), 4))
# второй уровень редактирования: меняем местами старший и младший байт, переводим в двоичную сс
data = list(map(lambda n: (bin(int(n[2:] + n[:2], 16))[2:]).rjust(16, "0"), hexdata))
# глобальная переменная, в которой находится номер команды
ind = 0

# класс для описания 1 команды
class Cmd():
    def __init__(self):
        global ind # копируем глбальную переменную
        self.ind = ind # сохраняем номер команды
        self.code = data[ind] # сохраняем код команды
        self.hex_code = hexdata[ind] # сохраняем код команды в 16-ичной сс
        self.id = find_command(data[ind]) # ищем команду в бд по маске

        self.description = commands['operation'][self.id] # сохраняем значение описания работы команды из бд
        self.mask = commands['code'][self.id] # сохраняем маску
        # некоторые команды могут занимать 2 байта памяти вместо 1, поэтому выполняем следующую проверку
        if len(self.mask) != len(self.code):
            ind += 1 # прибавляем 1 к указателю
            self.hex_code += hexdata[ind] # дополняем команду символами
            self.code += data[ind] # дополняем команду двоичными символами

        name = commands['command'][self.id] # название команды
        self.name = name.split(' ')[0] # делим его на 2 части согласно структуре бд
        # одна часто - название, вторая - параметры
        self.parameters = list() if len(name.split()) == 1 else list(name.split(' ')[1].split(','))
        # заполняем параметры, если они есть

    def get_parameters(self):
        # здесь заполянем значение параметров относительно маски объекта
        res = dict() # словарь для хранения данных, ключ - название параметра
        for par in self.parameters: # перебираем все параметры
            res[par] = ""
            for ch_ind in range(len(self.mask)): # заполянем из относительно маски
                if self.mask[ch_ind] == par:
                    res[par] += self.code[ch_ind]
        self.values = res # сохраняем полученный словарь внутри класса
        self.edit_parameters() # процедура для корректировки параметров
        self.translate_parameters() # процедура для перевода значений параметров в 16-ичную сс

    def edit_parameters(self):
        # если нет параметров, нечего редактировать
        if self.values == {}:
            return
        # строка для знака операции (rjmp)
        add = ''
        # если это команда по типу rjmp или rcall, то при необходимости делаем ревёрс строки
        if 'k' in self.description and self.description.count('PC') >= 2 and self.values['k'][0] == '1':
            add = '-'
            for i in range(len(self.values['k'])):
                self.values['k'] = '0' if self.values['k'] == '1' else '1'
            self.values['k'] = bin(int(self.values['k'], 2) + 1)[2:]
        # если команда начинается с 16 регистра для записи
        if 'Exc' in self.description:
            self.values['d'] = bin(int(self.values['d'], 2) + 16)[2:]
        # если это команда перевода строки, умножем её на 2
        if 'k' in self.description and self.description.count('PC') >= 1:
            self.values['k'] += '0'
            self.values['k'] = add + self.values['k']

    def translate_parameters(self):
        # переводим всё в 16-ичную сс
        for i in self.values.keys():
            if i == "r" or i == "d":
                self.values[i] = str(int(self.values[i], 2))
                continue
            if self.values[i][0] == '-':
                self.values[i] = '-' + hex(int(self.values[i], 2))[3:]
            else:
                self.values[i] = hex(int(self.values[i], 2))[2:]

    def __str__(self):
        # процедура для красивого вывода информации
        out = ' '.join(wrap(self.hex_code, 2)) + " " * (16 - (len(self.hex_code) + len(self.hex_code) // 2 - 1))
        out += ' ' + self.name  + '\t'
        for i in self.parameters:
            out += i + "=" + self.values[i] + '\t'
        return out


def find_command(code):
    # ищем команду в базе данных
    l = list(commands['code'])
    for i in range(len(l)):
        flag = True
        # выполняем побитовую проверку на соответствие, если не подходит, просто идём дальше
        for j in range(16):
            if not l[i][j].isalpha() and l[i][j] != code[j]:
                flag = False
                break
        if flag:
            return i


if __name__ == "__main__":
    cmd_list = list() # список всех команд
    while ind < len(data):
        # выводим текущее количество байт
        print(hex((ind) * 2)[2:], end=":\t ")
        cmd_list = list()
        # объявляем поиск новой программы
        cmd = Cmd()
        cmd.get_parameters()
        # выводим значение команды
        print(cmd)
        # переходим к следующей команде
        ind += 1