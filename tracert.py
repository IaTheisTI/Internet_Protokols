import subprocess
import re
import json
from urllib import request
from prettytable import PrettyTable

def args(count, info):
    try:
        as_number = info['org'].split()[0][2::]
        provider = " ".join(info['org'].split()[1::])
    except KeyError:
        as_number, provider = '*', '*'
    return [f"{count}.", info['ip'], info['country'], as_number, provider]

def bogon_args(count, info):
    return [f"{count}.", info['ip'], '*', '*', '*']


def ip_info(ip):
    return json.loads(request.urlopen('https://ipinfo.io/' + ip + '/json').read())



def start(text_data):
    return 'Трассировка маршрута' in text_data

def root(text_data):
    return 'Нет разрешения' in text_data

def complete(text_data):
    return 'Трассировка завершена' in text_data

def time(text_data):
    return 'Превышено время ожидания' in text_data


def generate_table():
    table = PrettyTable()
    table.field_names = ["number", "ip", "country", "AS number", "provider"]
    return table

def tracect(address, table):
    tracert_proc = subprocess.Popen(["tracert", address], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    number = 0

    for raw_line in iter(tracert_proc.stdout.readline, ''):
        line = raw_line.decode('cp866')
        ip = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line)

        if complete(line):
            print(table)
            return
        if root(line):
            print('Неверный ввод')
            return
        if start(line):
            print(line)
            continue
        if time(line):
            print('Превышено время ожидания')
            continue
        if ip:
            number += 1
            print(f'{"".join(ip)}')
            info = ip_info(ip[0])
            if 'bogon' in info:
                table.add_row(bogon_args(number, info))
            else:
                table.add_row(args(number, info))

    return table

def main():
    address = input('Введите ip-адрес: ')
    table = generate_table()
    tracect(address, table)

if __name__ == '__main__':
    main()
