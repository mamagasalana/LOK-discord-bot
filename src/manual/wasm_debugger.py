import re 
import subprocess

WASMBASE_HEADER = """
import math
from wasmtime import Func, FuncType, ValType, Store
from functools import wraps, partial
import logging

HEAP8_DEBUG= []
HEAP32_DEBUG=  []
HEAP64_DEBUG = []

def log_wasm(k,v):
    logging.info(f"from funcname {k}, {v}")

    
def logwrap(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        args_flatten_txt = '()'
        if args:
            args_flatten = [f'(index == {args[0]})'] + [f'(a{idx} == {arg})' for idx, arg in enumerate(args[1:], start=1)]
            args_flatten_txt = ' && '.join(args_flatten)
        log_msg = f"'{func.__name__}' {args_flatten_txt}"
            
        if self.func_stack:
            for k, v in self.func_stack.items():
                log_wasm(k ,v)
            
            self.func_stack = {}

        if HEAP32_DEBUG:
            out = {x: int(self.HEAP32[x//4]) for x in HEAP32_DEBUG}
            log_msg += f" ||| {out}"
            for k, v in self.debugref.items():
                if v == out.get(k):
                    self.debugref[k]= -999
                    logging.info(f'{k} changed here')
                    if k == 240116730:
                        logging.info(log_msg)
                        return
        if self.START_DEBUG:
            logging.info(log_msg)

        try:
            ret =  func(self, *args, **kwargs)
        except Exception as e:
            logging.error(f"'{func.__name__}' failed", exc_info=True)
            raise e
        
        log_msg += f" ||| return {ret}"
        debug=False
        if not 'invoke' in func.__name__ and not func.__name__ in ['_atomic_fetch_add_8', 'getTotalMemory']:
            debug=False

        if HEAP64_DEBUG and debug:
            out = {x: int(self.HEAP64[x//8]) for x in HEAP64_DEBUG}
            log_msg += f" ||| {out}"

        if HEAP32_DEBUG  and debug:
            out = {x: int(self.HEAP32[x//4]) for x in HEAP32_DEBUG}
            log_msg += f" ||| {out}"

        # if not 'invoke' in func.__name__ and not func.__name__ in ['_atomic_fetch_add_8', 'getTotalMemory']:
        if debug:
            logging.info(log_msg)
        return ret
    
    return wrapper

class wasm_base:
    def __init__(self):
        self.PAGE_SIZE = 16384
        self.WASM_PAGE_SIZE = 65536
        self.ASMJS_PAGE_SIZE = 16777216
        self.MIN_TOTAL_MEMORY = 16777216
        self.TOTAL_MEMORY = 33554432
        
        self.TOTAL_STACK= 5242880
        self.STATIC_BASE = 1024
        self.STATICTOP = 5948976
        self.DYNAMICTOP_PTR = self.staticAlloc(4)
        self.staticSealed = True
        self.STACKTOP = self.STACK_BASE = self.alignMemory(self.STATICTOP)
        self.STACK_MAX = self.STACK_BASE + self.TOTAL_STACK
        self.DYNAMIC_BASE = self.alignMemory(self.STACK_MAX)

    def staticAlloc(self, size):
        ret = self.STATICTOP
        self.STATICTOP = self.STATICTOP + size + 15 & -16
        return ret
    
    def alignMemory(self, size, factor=16):
        ret = size = math.ceil(size / factor) * factor;
        return ret
        

    def log(self, *args):
        return
    
    def log2(self, *args):
        return

    @property
    def import_object(self):
        return {
"""

WASMBASE_IMPORTS = """
            "log": Func(self.store, FuncType([ValType.i32()], []), self.log),
            "log2": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self.log2),
            }

"""

WASMBASE_EXPORTS = """
    def export_wasm_func(self):
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
        func_types = {}
        with open(self.IFILE, 'r') as ifile:
            rows = ifile.readlines()
            for row in rows:
                if '(import' in row: # from wat
                    funcs.append(row)
                if '(export' in row: # from wat
                    funcs.append(row)
                if '(type' in row and re.findall(r'\(type \(;\d+;\)', row):
                    type_idx = re.findall(r'\(type \(;(\d+);\)', row)[0]
                    func_types[type_idx] = row
                # elif row.startswith(self.SPECIAL_BREAKER): #from wat, end of import
                #     break

        # (import "env" "enlargeMemory" (func (;2;) (type 41)))
        # (import "asm2wasm" "f64-rem" (func (;489;) (type 57)))

        wasm_func =[]
        py_func = []
        export_func = []
        
        #self.__GLOBAL__sub_I_Modules_Terrain_Public_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Terrain_Public_2_cpp"], self.store)
        duplicate_funcname =set()
        for fun in funcs:

            if '(export' in fun:
                funname_raw = re.findall('"(.*?)"', fun)[0]
            else:
                funname_raw = re.findall('"(.*?)"', fun)[1]
            funname = re.sub(r'[-_]+', '_', funname_raw)
            assert funname not in duplicate_funcname, "%s already exists"  % funname
            duplicate_funcname.add(funname)

            if '(export' in fun:
                funexport = f'\t\tself.{funname} = partial(self.instance.exports(self.store)["{funname_raw}"], self.store)\n'
                export_func.append(funexport.replace('\t', ' '*4))
                continue
            
            if any(x in fun for x in ['(global' , '(memory', '(table', 'global.Math'] ):
                continue
            
            type_idx = re.findall('\(type (\d+)', fun)[0]
            mapped_type = func_types[type_idx]
            fun_in = ''
            fun_in_py = 'self'
            if '(param' in mapped_type:
                fun_in_pre = re.findall(r'\(param\s+(.*?)\)', mapped_type)[0].split(' ')
                fun_in = ','.join([f'ValType.{x}()' for x in fun_in_pre])
                fun_in_py += ',' +','.join([f'param{idx}' for idx,_ in enumerate(fun_in_pre)])
            fun_out = ''
            fun_out_py = ''
            if '(result' in mapped_type:
                fun_out_pre = re.findall(r'\(result\s+(.*?)\)', mapped_type)[0].split(' ')
                fun_out = ','.join([f'ValType.{x}()' for x in fun_out_pre])
                fun_out_py = ','.join([f'{idx}' for idx,_ in enumerate(fun_out_pre)])

            # wasm func declaration
            fun2 = f'\t\t\t"{funname_raw}": Func(self.store, FuncType([{fun_in}], [{fun_out}]), self.{funname}),\n'
            wasm_func.append(fun2.replace('\t', ' '*4))

            # funpy = f'def {funname}({fun_in_py}):\n\tprint("{funname} not implemented")\n\treturn {fun_out_py}\n\n'
            funpy = f'\t@logwrap\n\tdef {funname}(self, *args):'
            if 'invoke_' in funname:
                funpy += """
        sp = self.stackSave()
        try:
            return self.{}(*args)
        except:
            logging.error('{} fail?', exc_info=True)
            self.stackRestore(sp)
            self.setThrew(1, 0)
""".format(funname.replace('invoke', 'dynCall'), funname)
            else:
                funpy += """\n\t\tlogging.error("{} not implemented")""".format(funname)

            funpy += f'\n\t\treturn {fun_out_py}\n\n'
            py_func.append(funpy.replace('\t', ' '*4))



        with open('wasmbase.py' , 'w') as ofile:
            ofile.write(WASMBASE_HEADER)
            ofile.writelines(wasm_func)
            ofile.write(WASMBASE_IMPORTS)
            ofile.writelines(py_func)

            ofile.write(WASMBASE_EXPORTS)
            ofile.writelines(export_func)

    def run(self):
        # Convert .wasm to .wat
        subprocess.run(['wasm2wat', self.rawfile, '-o', self.IFILE], check=True)
        self.add_debug_line()
        self.create_new_wasmbase()
        subprocess.run(['wat2wasm', self.OFILE, '-o', self.outwasm], check=True)


if __name__ =='__main__':
    a = wasm_debug()
    a.create_new_wasmbase()