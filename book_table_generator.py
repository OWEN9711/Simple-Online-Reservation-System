import datetime
import os

ROOMS = [i+j for i in 'ABCDE' for j in '123456']
TYPES_TABLE = {
    'A': 'Single',
    'B': 'Single',
    'C': 'Twin',
    'D': 'Semi-Double',
    'E': 'Triple',
}
PRICES_TABLE = {
    'A': 100,
    'B': 100,
    'C': 150,
    'D': 120,
    'E': 170
}


def remove_data_file(folder):
    dates = [i.split('.')[0] for i in os.listdir(folder)]
    for date in dates:
        year, month, day = date.split('-')
        y, m, d = int(year), int(month), int(day)
        if datetime.datetime(y, m, d).date() < datetime.datetime.now().date():
            os.remove(folder+str(date) + '.txt')



def create_data_file(folder):
    for i in range(11):
        forward_date = datetime.datetime.now().date() + datetime.timedelta(days=i)
        if not os.path.exists(folder+str(forward_date) + '.txt'):
            f = open(folder+str(forward_date) + '.txt', 'w')
            for r in ROOMS:
                f.write(r+' '+TYPES_TABLE[r[0]]+' '+str(PRICES_TABLE[r[0]])+'$ '+'UB\n')
            f.close()

