import re
import logging
import os

try:
    os.remove('logs/bobo.log')
    os.remove('logs/error.log')
except:
    pass

logging.basicConfig(filename=f'logs/bobo.log', level=logging.INFO, format='%(levelname)s %(asctime)s %(message)s')

FILE=  'src/manual/test.wat'
OFILE = 'src/manual/test7.wat'
base = 525
newdx = 2

with open(FILE, 'r') as ifile:
    rows = ifile.readlines()

# for row in rows:
#     # if re.match(r'.*\D533\D.*', row, re.DOTALL):
#     # if re.match(r'.*\(func \(;\d+;\).*'  , row, re.DOTALL ):
#     if ' call ' in row and  re.match(r'.*call \d+.*', row):
#         logging.info(row.strip())
#         continue

# adjust function index by 1
with open(OFILE, 'w') as ofile:
    for row in rows:
        if ' call ' in row and  re.match(r'.*call \d+.*', row):
            funcname = re.findall(r'.*call (\d+).*', row)[0]
            if int(funcname) >= base:
                funcname2 = str(int(funcname)+newdx)
                row = row.replace(funcname, funcname2)

        if re.match(r'.*\(export.*\(func \d+', row):
            funcname =re.findall(r'.*\(export.*\(func (\d+)', row)[0]
            funcname2 = str(int(funcname)+newdx)
            row = row.replace(funcname, funcname2)

        if '(elem (;0;)' in row:
            funcname = re.split('func', row)[1]
            funcname2 = re.findall(r'\d+', funcname)
            funcname3 = ' '.join([str(int(x)+newdx) if int(x)>=base else x for x in funcname2])
            funcname3_pre = ' '.join(funcname2)
            row = row.replace(funcname3_pre, funcname3)


        ofile.write(row)