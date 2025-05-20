import re 
import subprocess

WASMBASE_HEADER = """
import math
from wasmtime import Func, FuncType, ValType

class wasm_base:
    def __init__(self):
        pass

    def log(self, *args):
        return
    
    def log2(self, *args):
        return

    @property
    def import_object(self):
        return {
            "log": Func(self.store, FuncType([ValType.i32()], []), self.log),
            "log2": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self.log2),
"""

class wasm_debug:
    def __init__(self, wasmfile='test.wasm', outwasm='testout.wasm'):
        self.rawfile = wasmfile
        self.outwasm = outwasm
        self.IFILE = 'test.wat'
        self.OFILE = 'testout.wat'

        self.SPECIAL_BREAKER = '  (func ('
        # wasm2wat test.wasm -o test.wat

    def add_debug_line(self):

        with open(self.IFILE, 'r') as ifile:
            rows = ifile.readlines()
        
        # find base
        for row in rows:
            if row.startswith(self.SPECIAL_BREAKER): #from wat, end of import
                break
        debug_funcs =[
            '(import "env" "log" (func (param i32)))\n',
            '(import "env" "log2" (func (param i32 i32 i32)))\n'
            ]
        base = int(re.findall(';(\d+);', row)[0])
        newdx = len(debug_funcs) # we add 2 lines, adjust as per needed

        add_debug = False
        with open(self.OFILE, 'w') as ofile:
            for row in rows:
                
                if not add_debug:
                    if row.startswith(self.SPECIAL_BREAKER): #from wat, end of import
                        add_debug=True
                        ofile.writelines(debug_funcs)
                
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

    def create_new_wasmbase(self):

        funcs = []

        with open(self.OFILE, 'r') as ifile:
            rows = ifile.readlines()
            for row in rows:
                if '(import' in row: # from wat
                    funcs.append(row)
                elif row.startswith(self.SPECIAL_BREAKER): #from wat, end of import
                    break

        # (import "env" "enlargeMemory" (func (;2;) (type 41)))
        # (import "asm2wasm" "f64-rem" (func (;489;) (type 57)))

        wasm_func =[]
        py_func = []
        duplicate_funcname =set()
        for fun in funcs:
            funname = re.findall('"(.*?)"', fun)[1]
            funname = re.sub(r'[-_]+', '_', funname)
            assert funname not in duplicate_funcname, "%s already exists"  % funname
            duplicate_funcname.add(funname)
            fun_in = ''
            fun_in_py = 'self'
            if '(param' in fun:
                fun_in_pre = re.findall(r'\(param\s+(.*?)\)', fun)[0].split(' ')
                fun_in = ','.join([f'ValType.{x}()' for x in fun_in_pre])
                fun_in_py += ',' +','.join([f'param{idx}' for idx,_ in enumerate(fun_in_pre)])
            fun_out = ''
            fun_out_py = ''
            if '(result' in fun:
                fun_out_pre = re.findall(r'\(result\s+(.*?)\)', fun)[0].split(' ')
                fun_out = ','.join([f'ValType.{x}()' for x in fun_out_pre])
                fun_out_py = ','.join([f'{idx}' for idx,_ in enumerate(fun_out_pre)])

            # wasm func declaration
            fun2 = f'\t\t\t"{funname}": Func(self.store, FuncType([{fun_in}], [{fun_out}]), self.{funname.replace("_", "")}),\n'
            wasm_func.append(fun2.replace('\t', ' '*4))

            # funpy = f'def {funname}({fun_in_py}):\n\tprint("{funname} not implemented")\n\treturn {fun_out_py}\n\n'
            funpy = f'\tdef {funname.replace("_", "")}(self, *args):\n\t\treturn {fun_out_py}\n\n'
            py_func.append(funpy.replace('\t', ' '*4))


        with open('wasmbase.py' , 'w') as ofile:
            ofile.write(WASMBASE_HEADER)
            ofile.writelines(wasm_func)
            ofile.writelines([
                ' '*8 + '}\n\n',
            ])

            ofile.writelines(py_func)

    def run(self):
        # Convert .wasm to .wat
        subprocess.run(['wasm2wat', self.rawfile, '-o', self.IFILE], check=True)
        self.add_debug_line()
        self.create_new_wasmbase()
        subprocess.run(['wat2wasm', self.OFILE, '-o', self.outwasm], check=True)


if __name__ =='__main__':
    a = wasm_debug()
    a.run()