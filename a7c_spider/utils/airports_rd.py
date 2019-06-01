#coding=utf-8
import csv


def get_airports():
    with open(u'./utils/济州航空.csv', 'r') as f:
        reader = csv.reader(f)
        airports_dict = []
        for r in reader:
            airports_dict.append({
                'DepartureAirportCode': r[0],
                'ArrivalAirportCode': r[1].strip()
            })
    return airports_dict


if __name__ == '__main__':
    print(get_airports().__len__())
