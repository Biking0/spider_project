#coding=utf-8
import csv, os

base_dir = os.path.abspath(os.path.dirname(__file__))
airports_dir = os.path.join(base_dir, 'airports_file')


def get_airports(file_name):
    with open(os.path.join(airports_dir, file_name), 'r') as f:
        fieldnames = ['DepartureAirportCode', 'ArrivalAirportCode']
        reader = csv.DictReader(f, fieldnames=fieldnames)
        return [i for i in reader]


if __name__ == '__main__':
    file_name = u'西捷直航.csv'
    print(get_airports(file_name).__len__())
