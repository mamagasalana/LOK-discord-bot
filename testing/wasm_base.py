import threading
import logging
from urllib.parse import quote
import sys
import os
import ctypes
import time
import io
from functools import wraps
import re
import numpy as np
import math

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'testing')))

from websocketmanager import customWebSocket, JSSYS,ERRNO_CODES, FS, ASM_CONSTS, UTF8ArrayToString

# HEAP32_DEBUG= [5914000, 5913988, 5913980, 5913984, 5914448, 5914456] 
# HEAP32_DEBUG_FULL = HEAP32_DEBUG + [5914000,  5202024, 5949232, 5084484, 5913996, 5949244, 5271560, 5271564, 5271108, 18729848, 18730008]
HEAP32_DEBUG=  [5914040, 5949364, 5914048,5913976, 5913992, 5913996, 5914000]
HEAP32_DEBUG_FULL = [5914040, 5949364,  5914048,5913976, 5913992, 5913996, 5914000]

def log_wasm(k,v):
    logging.info(f"from funcname {k}, {dict(sorted(v.items()))}")

def logwrap(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        args_flatten_txt = '()'
        if args:
            args_flatten = [f'(index == {args[0]})'] + [f'(a{idx} == {arg})' for idx, arg in enumerate(args[1:], start=1)]
            args_flatten_txt = ' && '.join(args_flatten)
        log_msg = f"'{func.__name__}' {args_flatten_txt}"
        
        if HEAP32_DEBUG:
            out = {x: self.HEAP32[x//4] for x in HEAP32_DEBUG_FULL}
            # out.update({x: self.HEAP32[x//4] for x in range(min(HEAP32_DEBUG), max(HEAP32_DEBUG)+4, 4)})
            log_msg += f" ||| {out}"
            if self.func_stack:
                for k, v in self.func_stack.items():
                    log_wasm(k ,v)
                
                self.func_stack = {}
        logging.info(log_msg)
        try:
            ret =  func(self, *args, **kwargs)
        except Exception as e:
            logging.error(f"'{func.__name__}' failed", exc_info=True)
            raise e
        return ret
    
    return wrapper

class wasm_base:
    def __init__(self):
        self.ENV = {}
        self.GETENV_RET = {}
        self.PAGE_SIZE = 16384;
        self.WASM_PAGE_SIZE = 65536;
        self.ASMJS_PAGE_SIZE = 16777216;
        self.MIN_TOTAL_MEMORY = 16777216;
        self.TOTAL_MEMORY = 33554432;
        
        self.TOTAL_STACK= 5242880;
        self.STATIC_BASE = 1024
        self.STATICTOP = 5948976;
        self.DYNAMICTOP_PTR = self.staticAlloc(4)
        self.staticSealed = True
        self.STACKTOP = self.STACK_BASE = self.alignMemory(self.STATICTOP)
        self.STACK_MAX = self.STACK_BASE + self.TOTAL_STACK
        self.DYNAMIC_BASE = self.alignMemory(self.STACK_MAX)
        
        self.clock_start = None
        self.SYSCALLS = JSSYS(self)
        self.init_time = time.time()*1000 #start time
        self.___buildEnvironment = False
        self.runtimeInitialized = True
        self.streams = {
            sys.stdin.fileno() : FS(sys.stdin.fileno(), 'dev/tty', tty=True),
            sys.stdout.fileno() : FS(sys.stdout.fileno(), 'dev/tty', tty=True),
            sys.stderr.fileno() : FS(sys.stderr.fileno(), 'dev/tty1', tty=True)
        }

        self.JSEVENTS = {}
        self.PTHREAD_SPECIFIC = {}
        self.PTHREAD_SPECIFIC_NEXT_KEY = 1
        with open('testing/funcidx.txt', 'r') as ofile:
            row = ofile.read()
        self.func_tables = re.findall(r'\d+', row[row.find('func'):])
        self.func_stack = {}


        self.GLctx_VERSION= 7938
        self.GLctx_SHADING_LANGUAGE_VERSION = 35724
        self.GLctx_getSupportedExtensions= ['EXT_clip_control', 'EXT_color_buffer_float', 'EXT_color_buffer_half_float', 'EXT_conservative_depth', 'EXT_depth_clamp', 'EXT_disjoint_timer_query_webgl2', 'EXT_float_blend', 'EXT_polygon_offset_clamp', 'EXT_render_snorm', 'EXT_texture_compression_bptc', 'EXT_texture_compression_rgtc', 'EXT_texture_filter_anisotropic', 'EXT_texture_mirror_clamp_to_edge', 'EXT_texture_norm16', 'KHR_parallel_shader_compile', 'NV_shader_noperspective_interpolation', 'OES_draw_buffers_indexed', 'OES_sample_variables', 'OES_shader_multisample_interpolation', 'OES_texture_float_linear', 'OVR_multiview2', 'WEBGL_blend_func_extended', 'WEBGL_clip_cull_distance', 'WEBGL_compressed_texture_s3tc', 'WEBGL_compressed_texture_s3tc_srgb', 'WEBGL_debug_renderer_info', 'WEBGL_debug_shaders', 'WEBGL_lose_context', 'WEBGL_multi_draw', 'WEBGL_polygon_mode', 'WEBGL_provoking_vertex', 'WEBGL_stencil_texturing']
        self.GLctx_getParameter = {
            7936 : 'WebKit',
            7937 : 'WebKit WebGL',
            7938 : 'WebGL 2.0 (OpenGL ES 3.0 Chromium)',
            35724 : 'WebGL GLSL ES 3.00 (OpenGL ES GLSL ES 3.0 Chromium)',
            34467: np.array([33776, 33777, 33778, 33779, 35916, 35917, 35918, 35919], dtype=np.uint32),
            34016 : 33984,
        }

        self.GL_lasterror = None
        self.GL_stringCache = {}
        self.GL_contexts = []
        self.GL_currentContext = None
        self.GL_contexts_ext  = {
            'WEBGL_compressed_texture_s3tc_srgb' : 'WebGLCompressedTextureS3TCsRGB',
            'EXT_color_buffer_float' : 'EXTColorBufferFloat',
            }

        self.ALLOC_NORMAL = 0
        self.ALLOC_STACK = 1
        self.ALLOC_STATIC = 2
        self.ALLOC_NONE = 4

    @logwrap
    def abort(self,param0):
        logging.error("abort not implemented")
        return 
    
    @logwrap
    def enlargeMemory(self):
        PAGE_MULTIPLE = self.WASM_PAGE_SIZE
        LIMIT = 2147483648 - PAGE_MULTIPLE
        if self.HEAP32[self.DYNAMICTOP_PTR >> 2] > LIMIT:
            return False
        OLD_TOTAL_MEMORY = self.TOTAL_MEMORY
        self.TOTAL_MEMORY = max(self.TOTAL_MEMORY, self.MIN_TOTAL_MEMORY)
        while self.TOTAL_MEMORY < self.HEAP32[self.DYNAMICTOP_PTR >> 2]:
            if self.TOTAL_MEMORY <= 536870912:
                self.TOTAL_MEMORY = self.alignUp(2 * self.TOTAL_MEMORY, PAGE_MULTIPLE)
            else:
                self.TOTAL_MEMORY = min(self.alignUp((3 * self.TOTAL_MEMORY + 2147483648) // 4, PAGE_MULTIPLE), LIMIT)

        replacement = self.reallocBuffer(self.TOTAL_MEMORY)
        if (not replacement or replacement.nbytes != self.TOTAL_MEMORY):
            self.TOTAL_MEMORY = OLD_TOTAL_MEMORY
            return False
        
        return True
    
    @logwrap
    def getTotalMemory(self):
        return self.TOTAL_MEMORY
    
    @logwrap
    def abortOnCannotGrowMemory(self):
        logging.error("abortOnCannotGrowMemory not implemented")
        return 0
    
    @logwrap
    def invoke_dddi(self,*args):
        sp = self.stackSave()
        try:
            return self.dynCall_dddi(*args)
        except:
            logging.error('invoke_i fail?', exc_info=True)
            self.stackRestore()
        return 0
    
    @logwrap
    def invoke_dii(self,param0,param1,param2):
        logging.error("invoke_dii not implemented")
        return 0
    
    @logwrap
    def invoke_diii(self,param0,param1,param2,param3):
        logging.error("invoke_diii not implemented")
        return 0
    
    @logwrap
    def invoke_diiid(self,param0,param1,param2,param3,param4):
        logging.error("invoke_diiid not implemented")
        return 0
    
    @logwrap
    def invoke_diiii(self,param0,param1,param2,param3,param4):
        logging.error("invoke_diiii not implemented")
        return 0
    
    @logwrap
    def invoke_ffffi(self,param0,param1,param2,param3,param4):
        logging.error("invoke_ffffi not implemented")
        return 0
    
    @logwrap
    def invoke_fffi(self,param0,param1,param2,param3):
        logging.error("invoke_fffi not implemented")
        return 0
    
    @logwrap
    def invoke_fi(self,param0,param1):
        logging.error("invoke_fi not implemented")
        return 0
    
    @logwrap
    def invoke_fii(self,param0,param1,param2):
        logging.error("invoke_fii not implemented")
        return 0
    
    @logwrap
    def invoke_fiifi(self,param0,param1,param2,param3,param4):
        logging.error("invoke_fiifi not implemented")
        return 0
    
    @logwrap
    def invoke_fiifii(self,param0,param1,param2,param3,param4,param5):
        logging.error("invoke_fiifii not implemented")
        return 0
    
    @logwrap
    def invoke_fiii(self,param0,param1,param2,param3):
        logging.error("invoke_fiii not implemented")
        return 0
    
    @logwrap
    def invoke_fiiif(self,param0,param1,param2,param3,param4):
        logging.error("invoke_fiiif not implemented")
        return 0
    
    @logwrap
    def invoke_fiiii(self,param0,param1,param2,param3,param4):
        logging.error("invoke_fiiii not implemented")
        return 0
    
    @logwrap
    def invoke_i(self,param0):
        sp = self.stackSave()
        try:
            return self.dynCall_i(param0)
        except:
            logging.error('invoke_i fail?', exc_info=True)
            self.stackRestore()
        return 0
    
    @logwrap
    def invoke_ifi(self,param0,param1,param2):
        logging.error("invoke_ifi not implemented")
        return 0
    
    @logwrap
    def invoke_ii(self,param0,param1):
        sp = self.stackSave()
        try:
            return self.dynCall_ii(param0, param1)
        except:
            logging.error('invoke_ii fail?', exc_info=True)
            self.stackRestore()
        return 0
    
    @logwrap
    def invoke_iifii(self,param0,param1,param2,param3,param4):
        logging.error("invoke_iifii not implemented")
        return 0
    
    @logwrap
    def invoke_iii(self,param0,param1,param2):
        sp = self.stackSave()
        try:
            return self.dynCall_iii(param0, param1,param2)
        except:
            logging.error('invoke_iii fail?', exc_info=True)
            self.stackRestore()
        return 0
    
    @logwrap
    def invoke_iiifi(self,param0,param1,param2,param3,param4):
        logging.error("invoke_iiifi not implemented")
        return 0
    
    @logwrap
    def invoke_iiii(self,param0,param1,param2,param3):
        sp = self.stackSave()
        try:
            return self.dynCall_iiii(param0, param1,param2, param3)
        except:
            logging.error('invoke_iiii fail?', exc_info=True)
            self.stackRestore()
        return 0
    
    @logwrap
    def invoke_iiiifii(self,param0,param1,param2,param3,param4,param5,param6):
        logging.error("invoke_iiiifii not implemented")
        return 0
    
    @logwrap
    def invoke_iiiii(self,param0,param1,param2,param3,param4):
        sp = self.stackSave()
        try:
            return self.dynCall_iiiii(param0,param1,param2,param3,param4)
        except:
            logging.error('invoke_iiiii fail?', exc_info=True)
            self.stackRestore()
        return 0
    
    @logwrap
    def invoke_iiiiii(self,param0,param1,param2,param3,param4,param5):
        sp = self.stackSave()
        try:
            return self.dynCall_iiiiii(param0,param1,param2,param3,param4,param5)
        except:
            logging.error('invoke_iiiiii fail?', exc_info=True)
            self.stackRestore()
        return 0
    
    
    @logwrap
    def invoke_iiiiiii(self,param0,param1,param2,param3,param4,param5,param6):
        sp = self.stackSave()
        try:
            return self.dynCall_iiiiiii(param0,param1,param2,param3,param4,param5,param6)
        except:
            logging.error('invoke_iiiiiii fail?', exc_info=True)
            self.stackRestore()
        return 0
    
    @logwrap
    def invoke_iiiiiiii(self,param0,param1,param2,param3,param4,param5,param6,param7):
        sp = self.stackSave()
        try:
            return self.dynCall_iiiiiiii(param0,param1,param2,param3,param4,param5,param6,param7)
        except:
            logging.error('invoke_iiiiiiii fail?', exc_info=True)
            self.stackRestore()
        return 0
    
    @logwrap
    def invoke_iiiiiiiii(self,param0,param1,param2,param3,param4,param5,param6,param7,param8):
        logging.error("invoke_iiiiiiiii not implemented")
        return 0
    
    @logwrap
    def invoke_iiiiiiiiii(self,param0,param1,param2,param3,param4,param5,param6,param7,param8,param9):
        logging.error("invoke_iiiiiiiiii not implemented")
        return 0
    
    @logwrap
    def invoke_iiiiiiiiiii(self,param0,param1,param2,param3,param4,param5,param6,param7,param8,param9,param10):
        logging.error("invoke_iiiiiiiiiii not implemented")
        return 0
    
    @logwrap
    def invoke_v(self,param0):
        sp = self.stackSave()
        try:
            self.dynCall_v(param0)
        except:
            logging.error('invoke_v fail?', exc_info=True)
            self.stackRestore()
        return 
    
    @logwrap
    def invoke_vi(self,param0,param1):
        sp = self.stackSave()
        try:
            self.dynCall_vi(param0, param1)
        except:
            logging.error('invoke_vi fail?', exc_info=True)
            self.stackRestore()
        return 
    
    @logwrap
    def invoke_vidiii(self,param0,param1,param2,param3,param4,param5):
        logging.error("invoke_vidiii not implemented")
        return 
    
    @logwrap
    def invoke_vifffi(self,param0,param1,param2,param3,param4,param5):
        logging.error("invoke_vifffi not implemented")
        return 
    
    @logwrap
    def invoke_vifi(self,param0,param1,param2,param3):
        logging.error("invoke_vifi not implemented")
        return 
    
    @logwrap
    def invoke_vifii(self,param0,param1,param2,param3,param4):
        logging.error("invoke_vifii not implemented")
        return 
    
    @logwrap
    def invoke_vii(self,param0,param1,param2):
        sp = self.stackSave()

        try:
            self.dynCall_vii(param0, param1, param2)
        except:
            logging.error('invoke_vii fail?', exc_info=True)
            self.stackRestore()
        return 
    
    @logwrap
    def invoke_viidi(self,param0,param1,param2,param3,param4):
        logging.error("invoke_viidi not implemented")
        return 
    
    @logwrap
    def invoke_viidii(self,param0,param1,param2,param3,param4,param5):
        logging.error("invoke_viidii not implemented")
        return 
    
    @logwrap
    def invoke_viiff(self,param0,param1,param2,param3,param4):
        logging.error("invoke_viiff not implemented")
        return 
    
    @logwrap
    def invoke_viiffi(self,param0,param1,param2,param3,param4,param5):
        logging.error("invoke_viiffi not implemented")
        return 
    
    @logwrap
    def invoke_viifi(self,param0,param1,param2,param3,param4):
        logging.error("invoke_viifi not implemented")
        return 
    
    @logwrap
    def invoke_viifii(self,param0,param1,param2,param3,param4,param5):
        logging.error("invoke_viifii not implemented")
        return 
    
    @logwrap
    def invoke_viii(self,param0,param1,param2,param3):
        sp = self.stackSave()
        try:
            self.dynCall_viii(param0, param1, param2,param3)
        except:
            logging.error('invoke_viii fail?', exc_info=True)
            self.stackRestore()
        return 
    
    @logwrap
    def invoke_viiif(self,param0,param1,param2,param3,param4):
        logging.error("invoke_viiif not implemented")
        return 
    
    @logwrap
    def invoke_viiii(self,param0,param1,param2,param3,param4):
        sp = self.stackSave()
        try:
            self.dynCall_viiii(param0, param1, param2,param3,param4)
        except:
            logging.error('invoke_viiii fail?', exc_info=True)
            self.stackRestore()
        return 
    
    @logwrap
    def invoke_viiiii(self,param0,param1,param2,param3,param4,param5):
        sp = self.stackSave()
        try:
            self.dynCall_viiiii(param0, param1, param2,param3,param4, param5)
        except:
            logging.error('invoke_viiiii fail?', exc_info=True)
            self.stackRestore()
        return 
    
    @logwrap    
    def invoke_viiiiii(self,param0,param1,param2,param3,param4,param5,param6):
        sp = self.stackSave()
        try:
            self.dynCall_viiiiii(param0,param1,param2,param3,param4,param5,param6)
        except:
            logging.error('invoke_viiiiii fail?', exc_info=True)
            self.stackRestore()
        return 
    
    @logwrap
    def invoke_viiiiiii(self,param0,param1,param2,param3,param4,param5,param6,param7):
        logging.error("invoke_viiiiiii not implemented")
        return 
    
    @logwrap
    def invoke_viiiiiiifddfii(self,param0,param1,param2,param3,param4,param5,param6,param7,param8,param9,param10,param11,param12,param13):
        logging.error("invoke_viiiiiiifddfii not implemented")
        return 
    
    @logwrap
    def invoke_viiiiiiiffffii(self,param0,param1,param2,param3,param4,param5,param6,param7,param8,param9,param10,param11,param12,param13):
        logging.error("invoke_viiiiiiiffffii not implemented")
        return 
    
    @logwrap
    def invoke_viiiiiiifiifii(self,param0,param1,param2,param3,param4,param5,param6,param7,param8,param9,param10,param11,param12,param13):
        logging.error("invoke_viiiiiiifiifii not implemented")
        return 
    
    @logwrap
    def invoke_viiiiiiii(self,param0,param1,param2,param3,param4,param5,param6,param7,param8):
        logging.error("invoke_viiiiiiii not implemented")
        return 
    
    @logwrap
    def invoke_viiiiiiiii(self,param0,param1,param2,param3,param4,param5,param6,param7,param8,param9):
        logging.error("invoke_viiiiiiiii not implemented")
        return 
    
    @logwrap
    def invoke_viiiiiiiiii(self,param0,param1,param2,param3,param4,param5,param6,param7,param8,param9,param10):
        logging.error("invoke_viiiiiiiiii not implemented")
        return 
    
    @logwrap
    def _ES_AddEventHandler(self,param0,param1):
        logging.error("_ES_AddEventHandler not implemented")
        return 
    
    @logwrap
    def _ES_Close(self,param0):
        logging.error("_ES_Close not implemented")
        return 
    
    @logwrap
    def _ES_Create(self,param0,param1,param2,param3,param4):
        logging.error("_ES_Create not implemented")
        return 0
    
    @logwrap
    def _ES_IsSupported(self):
        logging.error("_ES_IsSupported not implemented")
        return 0
    
    @logwrap
    def _ES_Release(self,param0):
        logging.error("_ES_Release not implemented")
        return 
    
    @logwrap
    def _GetInputFieldSelectionEnd(self):
        logging.error("_GetInputFieldSelectionEnd not implemented")
        return 0
    
    @logwrap
    def _GetInputFieldSelectionStart(self):
        logging.error("_GetInputFieldSelectionStart not implemented")
        return 0
    
    @logwrap
    def _GetInputFieldValue(self):
        logging.error("_GetInputFieldValue not implemented")
        return 0
    
    @logwrap
    def _HideInputField(self):
        logging.error("_HideInputField not implemented")
        return 
    
    @logwrap
    def _IsInputFieldActive(self):
        logging.error("_IsInputFieldActive not implemented")
        return 0
    
    @logwrap
    def _JS_Cursor_SetImage(self,param0,param1):
        logging.error("_JS_Cursor_SetImage not implemented")
        return 
    
    @logwrap
    def _JS_Cursor_SetShow(self,param0):
        logging.error("_JS_Cursor_SetShow not implemented")
        return 
    
    @logwrap
    def _JS_Eval_ClearInterval(self,param0):
        logging.error("_JS_Eval_ClearInterval not implemented")
        return 
    
    @logwrap
    def _JS_Eval_OpenURL(self,param0):
        logging.error("_JS_Eval_OpenURL not implemented")
        return 
    
    @logwrap
    def _JS_Eval_SetInterval(self,param0,param1,param2):
        logging.error("_JS_Eval_SetInterval not implemented")
        return 0
    
    @logwrap
    def _JS_FileSystem_Initialize(self):
        logging.error("_JS_FileSystem_Initialize not implemented")
        return 
    
    @logwrap
    def _JS_FileSystem_Sync(self):
        logging.error("_JS_FileSystem_Sync not implemented")
        return 
    
    @logwrap
    def _JS_Log_Dump(self,ptr,param1):
        strr = self.Pointer_stringify(ptr);
        if param1 in [0, 1, 4]:
            logging.error(strr)
        elif param1 == 2:
            logging.warning(strr)
        elif param1 in [3, 5]:
            logging.info(strr)
        else:
            logging.error("Unknown console message param1!")
            logging.error(strr)
        return
    
    @logwrap
    def _JS_Log_StackTrace(self,param0,param1):
        logging.error("_JS_Log_StackTrace not implemented")
        return 
    
    @logwrap
    def _JS_Sound_Create_Channel(self,param0,param1):
        logging.error("_JS_Sound_Create_Channel not implemented")
        return 0
    
    @logwrap
    def _JS_Sound_GetLength(self,param0):
        logging.error("_JS_Sound_GetLength not implemented")
        return 0
    
    @logwrap
    def _JS_Sound_GetLoadState(self,param0):
        logging.error("_JS_Sound_GetLoadState not implemented")
        return 0
    
    @logwrap
    def _JS_Sound_Init(self):
        logging.error("_JS_Sound_Init not implemented")
        return 
    
    @logwrap
    def _JS_Sound_Load(self,param0,param1):
        logging.error("_JS_Sound_Load not implemented")
        return 0
    
    @logwrap
    def _JS_Sound_Load_PCM(self,param0,param1,param2,param3):
        logging.error("_JS_Sound_Load_PCM not implemented")
        return 0
    
    @logwrap
    def _JS_Sound_Play(self,param0,param1,param2,param3):
        logging.error("_JS_Sound_Play not implemented")
        return 
    
    @logwrap
    def _JS_Sound_ReleaseInstance(self,param0):
        logging.error("_JS_Sound_ReleaseInstance not implemented")
        return 0
    
    @logwrap
    def _JS_Sound_ResumeIfNeeded(self):
        logging.error("_JS_Sound_ResumeIfNeeded not implemented")
        return 
    
    @logwrap
    def _JS_Sound_Set3D(self,param0,param1):
        logging.error("_JS_Sound_Set3D not implemented")
        return 
    
    @logwrap
    def _JS_Sound_SetListenerOrientation(self,param0,param1,param2,param3,param4,param5):
        logging.error("_JS_Sound_SetListenerOrientation not implemented")
        return 
    
    @logwrap
    def _JS_Sound_SetListenerPosition(self,param0,param1,param2):
        logging.error("_JS_Sound_SetListenerPosition not implemented")
        return 
    
    @logwrap
    def _JS_Sound_SetLoop(self,param0,param1):
        logging.error("_JS_Sound_SetLoop not implemented")
        return 
    
    @logwrap
    def _JS_Sound_SetLoopPoints(self,param0,param1,param2):
        logging.error("_JS_Sound_SetLoopPoints not implemented")
        return 
    
    @logwrap
    def _JS_Sound_SetPaused(self,param0,param1):
        logging.error("_JS_Sound_SetPaused not implemented")
        return 
    
    @logwrap
    def _JS_Sound_SetPitch(self,param0,param1):
        logging.error("_JS_Sound_SetPitch not implemented")
        return 
    
    @logwrap
    def _JS_Sound_SetPosition(self,param0,param1,param2,param3):
        logging.error("_JS_Sound_SetPosition not implemented")
        return 
    
    @logwrap
    def _JS_Sound_SetVolume(self,param0,param1):
        logging.error("_JS_Sound_SetVolume not implemented")
        return 
    
    @logwrap
    def _JS_Sound_Stop(self,param0,param1):
        logging.error("_JS_Sound_Stop not implemented")
        return 
    
    @logwrap
    def _JS_SystemInfo_GetBrowserName(self,param0,param1):
        logging.error("_JS_SystemInfo_GetBrowserName not implemented")
        return 0
    
    @logwrap
    def _JS_SystemInfo_GetBrowserVersionString(self,param0,param1):
        logging.error("_JS_SystemInfo_GetBrowserVersionString not implemented")
        return 0
    
    @logwrap
    def _JS_SystemInfo_GetCanvasClientSize(self,param0,param1,param2):
        logging.error("_JS_SystemInfo_GetCanvasClientSize not implemented")
        return 
    
    @logwrap
    def _JS_SystemInfo_GetDocumentURL(self,param0,param1):
        url ='https://play.leagueofkingdoms.com/'
        if param0:
            self.stringToUTF8(url, param0, param1)
        return self.lengthBytesUTF8(url)
    
    @logwrap
    def _JS_SystemInfo_GetGPUInfo(self,param0,param1):
        logging.error("_JS_SystemInfo_GetGPUInfo not implemented")
        return 0
    
    @logwrap
    def _JS_SystemInfo_GetLanguage(self,param0,param1):
        logging.error("_JS_SystemInfo_GetLanguage not implemented")
        return 0
    
    @logwrap
    def _JS_SystemInfo_GetMemory(self):
        return self.TOTAL_MEMORY // (1024 * 1024)
    
    @logwrap
    def _JS_SystemInfo_GetOS(self,param0,param1):
        logging.error("_JS_SystemInfo_GetOS not implemented")
        return 0
    
    @logwrap
    def _JS_SystemInfo_GetPreferredDevicePixelRatio(self):
        return 1.0
    
    @logwrap
    def _JS_SystemInfo_GetScreenSize(self,param0,param1):
        logging.error("_JS_SystemInfo_GetScreenSize not implemented")
        return 
    
    @logwrap
    def _JS_SystemInfo_GetStreamingAssetsURL(self,param0,param1):
        logging.error("_JS_SystemInfo_GetStreamingAssetsURL not implemented")
        return 0
    
    @logwrap
    def _JS_SystemInfo_HasCursorLock(self):
        logging.error("_JS_SystemInfo_HasCursorLock not implemented")
        return 0
    
    @logwrap
    def _JS_SystemInfo_HasFullscreen(self):
        logging.error("_JS_SystemInfo_HasFullscreen not implemented")
        return 0
    
    @logwrap
    def _JS_SystemInfo_HasWebGL(self):
        return 2
    
    @logwrap
    def _JS_SystemInfo_IsMobile(self):
        logging.error("_JS_SystemInfo_IsMobile not implemented")
        return 0
    
    @logwrap
    def _JS_Video_CanPlayFormat(self,param0):
        logging.error("_JS_Video_CanPlayFormat not implemented")
        return 0
    
    @logwrap
    def _JS_Video_Create(self,param0):
        logging.error("_JS_Video_Create not implemented")
        return 0
    
    @logwrap
    def _JS_Video_Destroy(self,param0):
        logging.error("_JS_Video_Destroy not implemented")
        return 
    
    @logwrap
    def _JS_Video_Duration(self,param0):
        logging.error("_JS_Video_Duration not implemented")
        return 0
    
    @logwrap
    def _JS_Video_EnableAudioTrack(self,param0,param1,param2):
        logging.error("_JS_Video_EnableAudioTrack not implemented")
        return 
    
    @logwrap
    def _JS_Video_GetAudioLanguageCode(self,param0,param1):
        logging.error("_JS_Video_GetAudioLanguageCode not implemented")
        return 0
    
    @logwrap
    def _JS_Video_GetNumAudioTracks(self,param0):
        logging.error("_JS_Video_GetNumAudioTracks not implemented")
        return 0
    
    @logwrap
    def _JS_Video_Height(self,param0):
        logging.error("_JS_Video_Height not implemented")
        return 0
    
    @logwrap
    def _JS_Video_IsPlaying(self,param0):
        logging.error("_JS_Video_IsPlaying not implemented")
        return 0
    
    @logwrap
    def _JS_Video_IsReady(self,param0):
        logging.error("_JS_Video_IsReady not implemented")
        return 0
    
    @logwrap
    def _JS_Video_Pause(self,param0):
        logging.error("_JS_Video_Pause not implemented")
        return 
    
    @logwrap
    def _JS_Video_Play(self,param0,param1):
        logging.error("_JS_Video_Play not implemented")
        return 
    
    @logwrap
    def _JS_Video_Seek(self,param0,param1):
        logging.error("_JS_Video_Seek not implemented")
        return 
    
    @logwrap
    def _JS_Video_SetEndedHandler(self,param0,param1,param2):
        logging.error("_JS_Video_SetEndedHandler not implemented")
        return 
    
    @logwrap
    def _JS_Video_SetErrorHandler(self,param0,param1,param2):
        logging.error("_JS_Video_SetErrorHandler not implemented")
        return 
    
    @logwrap
    def _JS_Video_SetLoop(self,param0,param1):
        logging.error("_JS_Video_SetLoop not implemented")
        return 
    
    @logwrap
    def _JS_Video_SetMute(self,param0,param1):
        logging.error("_JS_Video_SetMute not implemented")
        return 
    
    @logwrap
    def _JS_Video_SetPlaybackRate(self,param0,param1):
        logging.error("_JS_Video_SetPlaybackRate not implemented")
        return 
    
    @logwrap
    def _JS_Video_SetReadyHandler(self,param0,param1,param2):
        logging.error("_JS_Video_SetReadyHandler not implemented")
        return 
    
    @logwrap
    def _JS_Video_SetSeekedOnceHandler(self,param0,param1,param2):
        logging.error("_JS_Video_SetSeekedOnceHandler not implemented")
        return 
    
    @logwrap
    def _JS_Video_SetVolume(self,param0,param1):
        logging.error("_JS_Video_SetVolume not implemented")
        return 
    
    @logwrap
    def _JS_Video_Time(self,param0):
        logging.error("_JS_Video_Time not implemented")
        return 0
    
    @logwrap
    def _JS_Video_UpdateToTexture(self,param0,param1):
        logging.error("_JS_Video_UpdateToTexture not implemented")
        return 0
    
    @logwrap
    def _JS_Video_Width(self,param0):
        logging.error("_JS_Video_Width not implemented")
        return 0
    
    @logwrap
    def _JS_WebCamVideo_CanPlay(self,param0):
        logging.error("_JS_WebCamVideo_CanPlay not implemented")
        return 0
    
    @logwrap
    def _JS_WebCamVideo_GetDeviceName(self,param0,param1,param2):
        logging.error("_JS_WebCamVideo_GetDeviceName not implemented")
        return 0
    
    @logwrap
    def _JS_WebCamVideo_GetNativeHeight(self,param0):
        logging.error("_JS_WebCamVideo_GetNativeHeight not implemented")
        return 0
    
    @logwrap
    def _JS_WebCamVideo_GetNativeWidth(self,param0):
        logging.error("_JS_WebCamVideo_GetNativeWidth not implemented")
        return 0
    
    @logwrap
    def _JS_WebCamVideo_GetNumDevices(self):
        logging.error("_JS_WebCamVideo_GetNumDevices not implemented")
        return 0
    
    @logwrap
    def _JS_WebCamVideo_GrabFrame(self,param0,param1,param2,param3):
        logging.error("_JS_WebCamVideo_GrabFrame not implemented")
        return 
    
    @logwrap
    def _JS_WebCamVideo_Start(self,param0):
        logging.error("_JS_WebCamVideo_Start not implemented")
        return 
    
    @logwrap
    def _JS_WebCamVideo_Stop(self,param0):
        logging.error("_JS_WebCamVideo_Stop not implemented")
        return 
    
    @logwrap
    def _JS_WebCam_IsSupported(self):
        logging.error("_JS_WebCam_IsSupported not implemented")
        return 0
    
    @logwrap
    def _JS_WebRequest_Abort(self,param0):
        logging.error("_JS_WebRequest_Abort not implemented")
        return 
    
    @logwrap
    def _JS_WebRequest_Create(self,param0,param1):
        logging.error("_JS_WebRequest_Create not implemented")
        return 0
    
    @logwrap
    def _JS_WebRequest_GetResponseHeaders(self,param0,param1,param2):
        logging.error("_JS_WebRequest_GetResponseHeaders not implemented")
        return 0
    
    @logwrap
    def _JS_WebRequest_Release(self,param0):
        logging.error("_JS_WebRequest_Release not implemented")
        return 
    
    @logwrap
    def _JS_WebRequest_Send(self,param0,param1,param2):
        logging.error("_JS_WebRequest_Send not implemented")
        return 
    
    @logwrap
    def _JS_WebRequest_SetProgressHandler(self,param0,param1,param2):
        logging.error("_JS_WebRequest_SetProgressHandler not implemented")
        return 
    
    @logwrap
    def _JS_WebRequest_SetRequestHeader(self,param0,param1,param2):
        logging.error("_JS_WebRequest_SetRequestHeader not implemented")
        return 
    
    @logwrap
    def _JS_WebRequest_SetResponseHandler(self,param0,param1,param2):
        logging.error("_JS_WebRequest_SetResponseHandler not implemented")
        return 
    
    @logwrap
    def _JS_WebRequest_SetTimeout(self,param0,param1):
        logging.error("_JS_WebRequest_SetTimeout not implemented")
        return 
    
    @logwrap
    def _NativeCall(self,param0,param1):
        logging.error("_NativeCall not implemented")
        return 
    
    @logwrap
    def _SetInputFieldSelection(self,param0,param1):
        logging.error("_SetInputFieldSelection not implemented")
        return 
    
    @logwrap
    def _ShowInputField(self,param0):
        logging.error("_ShowInputField not implemented")
        return 
    
    @logwrap
    def _WS_Close(self,id,code,reason):
        socket = self.ws.get(id)
        reasonStr = self.Pointer_stringify(reason)
        socket['socketImpl'].close(code, reasonStr)
    
    @logwrap
    def _WS_Create(self, url, protocol, on_open, on_text, on_binary, on_error, on_close):
        if str(url).isdigit():
            urlStr = self.Pointer_stringify(url).replace('+', '%2B').replace('%252F', '%2F')
        else:
            urlStr = url
        proto = self.Pointer_stringify(protocol)
        socket = {
            'onError': on_error,
            'onClose' : on_close,
        }
        socket_impl = customWebSocket(urlStr, subprotocols=[proto] if proto else None)
        socket_impl.binaryType = "arraybuffer";
        _id = self.ws.nextInstanceId

        def on_open_wrapper(ws1):
            logging.info("_ws_open")
            self.ws._callOnOpen(on_open, _id)

        def on_message_wrapper(ws1, message):
            logging.info("_ws_create: on message wrapper: %s" % message)
            if isinstance(message, (bytes, bytearray)):
                self.ws._callOnBinary(on_binary, _id, message)
            else:
                self.ws._callOnText(on_text, _id, message)

        def on_error_wrapper(ws1, error):
            logging.info(f"{_id} WS_Create - onError")

        def on_close_wrapper(ws1, close_status_code, close_msg):
            logging.info(f"{_id} WS_Create - onClose {close_status_code} {close_msg}")
            self.ws._callOnClose(on_close, _id, close_status_code, close_msg)

        socket_impl.on_open = on_open_wrapper
        socket_impl.on_message = on_message_wrapper
        socket_impl.on_error = on_error_wrapper
        socket_impl.on_close = on_close_wrapper

        socket['socketImpl'] = socket_impl
        socket_thread = threading.Thread(target=socket_impl.run_forever)
        socket_thread.start()

        return self.ws.set(socket)
    
    @logwrap
    def _WS_GetBufferedAmount(self,id):
        socket = self.ws.get(id)
        return socket['socketImpl'].bufferedAmount
    
    @logwrap
    def _WS_GetState(self,param0):
        logging.error("_WS_GetState not implemented")
        return 0
    
    @logwrap
    def _WS_Release(self,param0):
        logging.error("_WS_Release not implemented")
        return 
    
    @logwrap
    def _WS_Send_Binary(self,id, ptr, pos, length):
        socket = self.ws.get(id)
        try:
            buff = self.HEAPU8[ptr + pos:ptr + pos + length]
            socket['socketImpl'].send(buff)
        except Exception as e:
            self.ws._callOnError(socket.onError, id, str(e))
        return socket['socketImpl'].bufferedAmount
    
    @logwrap
    def _WS_Send_String(self,id, str_in):
        socket = self.ws.get(id)
        str_in = self.Pointer_stringify(str_in)
        try:
            socket['socketImpl'].send(str_in)
        except Exception as e:
            self.ws._callOnError(socket.onError, id, str(e))
        
        return socket['socketImpl'].bufferedAmount
    
    @logwrap
    def _XHR_Abort(self,param0):
        logging.error("_XHR_Abort not implemented")
        return 
    
    @logwrap
    def _XHR_Create(self,param0,param1,param2,param3,param4):
        logging.error("_XHR_Create not implemented")
        return 0
    
    @logwrap
    def _XHR_GetResponseHeaders(self,param0,param1):
        logging.error("_XHR_GetResponseHeaders not implemented")
        return 
    
    @logwrap
    def _XHR_GetStatusLine(self,param0,param1):
        logging.error("_XHR_GetStatusLine not implemented")
        return 
    
    @logwrap
    def _XHR_Release(self,param0):
        logging.error("_XHR_Release not implemented")
        return 
    
    @logwrap
    def _XHR_Send(self,param0,param1,param2):
        logging.error("_XHR_Send not implemented")
        return 
    
    @logwrap
    def _XHR_SetLoglevel(self,param0):
        logging.error("_XHR_SetLoglevel not implemented")
        return 
    
    @logwrap
    def _XHR_SetProgressHandler(self,param0,param1,param2):
        logging.error("_XHR_SetProgressHandler not implemented")
        return 
    
    @logwrap
    def _XHR_SetRequestHeader(self,param0,param1,param2):
        logging.error("_XHR_SetRequestHeader not implemented")
        return 
    
    @logwrap
    def _XHR_SetResponseHandler(self,param0,param1,param2,param3,param4):
        logging.error("_XHR_SetResponseHandler not implemented")
        return 
    
    @logwrap
    def _XHR_SetTimeout(self,param0,param1):
        logging.error("_XHR_SetTimeout not implemented")
        return 
    
    @logwrap
    def _buildEnvironment(self,param0):
        MAX_ENV_VALUES = 64
        TOTAL_ENV_SIZE = 1024
        poolPtr = None
        envPtr = None        
        if not self.___buildEnvironment:
            self.___buildEnvironment = True
            self.ENV["LOGNAME"] = "web_user"
            self.ENV["USER"] = "web_user" 
            self.ENV["PATH"] = "/"
            self.ENV["PWD"] = "/"
            self.ENV["HOME"] = "/home/web_user"
            self.ENV["LANG"] = "C.UTF-8"
            self.ENV["_"] = "./this.program"

            poolPtr = self.getMemory(TOTAL_ENV_SIZE)
            envPtr = self.getMemory(MAX_ENV_VALUES * 4)
            self.HEAP32[envPtr >> 2] = poolPtr
            self.HEAP32[param0 >> 2] = envPtr
        else:
            envPtr = self.HEAP32[param0 >> 2]
            poolPtr = self.HEAP32[envPtr >> 2]

        strings = []
        totalSize = 0
        for key, value in self.ENV.items():
            if isinstance(value, str):
                line = f"{key}={value}"
                strings.append(line)
                totalSize += len(line)

        if totalSize > TOTAL_ENV_SIZE:
            raise ValueError("Environment size exceeded TOTAL_ENV_SIZE!")

        ptrSize = 4
        for i, line in enumerate(strings):
            self.writeAsciiToMemory(line, poolPtr)
            self.HEAP32[(envPtr + i * ptrSize) >> 2] = poolPtr
            poolPtr += len(line) + 1

        self.HEAP32[(envPtr + len(strings) * ptrSize) >> 2] = 0
        return 
    
    @logwrap
    def _cxa_allocate_exception(self,param0):
        logging.error("_cxa_allocate_exception not implemented")
        return 0
    
    @logwrap
    def _cxa_begin_catch(self,param0):
        logging.error("_cxa_begin_catch not implemented")
        return 0
    
    @logwrap
    def _cxa_end_catch(self):
        logging.error("_cxa_end_catch not implemented")
        return 
    
    @logwrap
    def _cxa_find_matching_catch_2(self):
        logging.error("_cxa_find_matching_catch_2 not implemented")
        return 0
    
    @logwrap
    def _cxa_find_matching_catch_3(self,param0):
        logging.error("_cxa_find_matching_catch_3 not implemented")
        return 0
    
    @logwrap
    def _cxa_find_matching_catch_4(self,param0,param1):
        logging.error("_cxa_find_matching_catch_4 not implemented")
        return 0
    
    @logwrap
    def _cxa_free_exception(self,param0):
        logging.error("_cxa_free_exception not implemented")
        return 
    
    @logwrap
    def _cxa_pure_virtual(self):
        logging.error("_cxa_pure_virtual not implemented")
        return 
    
    @logwrap
    def _cxa_rethrow(self):
        logging.error("_cxa_rethrow not implemented")
        return 
    
    @logwrap
    def _cxa_throw(self,param0,param1,param2):
        logging.error("_cxa_throw not implemented")
        return 
    
    @logwrap
    def _lock(self,param0):
        return 
    
    @logwrap
    def _map_file(self,param0,param1):
        logging.error("_map_file not implemented")
        return 0
    
    @logwrap
    def _resumeException(self,param0):
        logging.error("_resumeException not implemented")
        return 
    
    @logwrap
    def _setErrNo(self,param0):
        logging.error("_setErrNo not implemented")
        return 
    
    @logwrap
    def _syscall10(self,param0,param1):
        logging.error("_syscall10 not implemented")
        return 0
    
    @logwrap
    def _syscall102(self,param0,param1):
        logging.error("_syscall102 not implemented")
        return 0
    
    @logwrap
    def _syscall122(self,param0,param1):
        logging.error("_syscall122 not implemented")
        return 0
    
    @logwrap
    def _syscall140(self,param0,varargs):
        self.SYSCALLS.varargs = varargs
        try:
            stream = self.SYSCALLS.getStreamFromFD()
            offset_high = self.SYSCALLS.get()
            offset_low = self.SYSCALLS.get()
            result = self.SYSCALLS.get()
            whence = self.SYSCALLS.get()
            offset = offset_low
            os.lseek(stream.fileno(), offset, whence)
            self.HEAP32[result >> 2] =  stream.tell()
            return 0

        except Exception as e:
            logging.error("_syscall140" , exc_info=True)
            return -1
    
    @logwrap        
    def _syscall142(self,param0,param1):
        logging.error("_syscall142 not implemented")
        return 0
    
    @logwrap
    def _syscall145(self,param0,varargs):
        self.SYSCALLS.varargs = varargs
        try:
            stream = self.SYSCALLS.getStreamFromFD()
            iov = self.SYSCALLS.get()
            iovcnt = self.SYSCALLS.get()
            ret = self.SYSCALLS.doReadv(stream, iov, iovcnt)
            return int(ret)

        except Exception as e:
            logging.error("_syscall145" , exc_info=True)
            return -1
        
    
    @logwrap
    def _syscall146(self,param0,varargs):
        self.SYSCALLS.varargs = varargs
        try:
            stream = self.SYSCALLS.getStreamFromFD()
            iov = self.SYSCALLS.get()
            iovcnt = self.SYSCALLS.get()
            ret =  self.SYSCALLS.doWritev(stream, iov, iovcnt)
            return int(ret)
        except Exception as e:
            logging.error("_syscall146" , exc_info=True)
            return -1

    @logwrap
    def _syscall15(self,param0,param1):
        logging.error("_syscall15 not implemented")
        return 0
    
    @logwrap
    def _syscall168(self,param0,param1):
        logging.error("_syscall168 not implemented")
        return 0
    
    @logwrap
    def _syscall183(self,param0,param1):
        logging.error("_syscall183 not implemented")
        return 0
    
    @logwrap
    def _syscall192(self, which, varargs):
        self.SYSCALLS.varargs = varargs
        try:
            addr = self.SYSCALLS.get()
            len_ = self.SYSCALLS.get()
            prot = self.SYSCALLS.get()
            flags = self.SYSCALLS.get()
            fd = self.SYSCALLS.get()
            off = self.SYSCALLS.get()
            off <<= 12
            ptr = None
            allocated = False

            if fd == -1:
                ptr = self._memalign(self.PAGE_SIZE, len_)
                if not ptr:
                    return -ERRNO_CODES.ENOMEM
                self._memset(ptr, 0, len_)
                allocated = True
            else:
                info = self.streams.get(fd)
                if not info:
                    return -ERRNO_CODES.EBADF
                res = 1
                # res = FS.mmap(info, self.HEAPU8, addr, len_, off, prot, flags)
                ptr = res.ptr
                allocated = res.allocated

            self.SYSCALLS.mappings[ptr] = {
                'malloc': ptr,
                'len': len_,
                'allocated': allocated,
                'fd': fd,
                'flags': flags
            }
            return ptr
        except Exception as e:
            logging.error("_syscall192 failed" , exc_info=True)
            return -1

    
    @logwrap
    def _syscall193(self,param0,param1):
        logging.error("_syscall193 not implemented")
        return 0
    
    @logwrap
    def _syscall194(self,param0,param1):
        logging.error("_syscall194 not implemented")
        return 0
    
    @logwrap
    def _syscall195(self,param0,varargs):
        self.SYSCALLS.varargs = varargs
        try:
            stream = self.SYSCALLS.getStr()
            buf = self.SYSCALLS.get()
            stat = os.stat(stream)
            self.HEAP32[buf >> 2] = stat.st_dev
            self.HEAP32[buf + 4 >> 2] = 0
            self.HEAP32[buf + 8 >> 2] = hash(stat.st_ino) & 0xFFFFFFFF
            self.HEAP32[buf + 12 >> 2] = stat.st_mode
            self.HEAP32[buf + 16 >> 2] = stat.st_nlink
            self.HEAP32[buf + 20 >> 2] = stat.st_uid
            self.HEAP32[buf + 24 >> 2] = stat.st_gid
            self.HEAP32[buf + 28 >> 2] = 0  #stat.rdev
            self.HEAP32[buf + 32 >> 2] = 0
            self.HEAP32[buf + 36 >> 2] = stat.st_size   
            self.HEAP32[buf + 40 >> 2] = 4096
            self.HEAP32[buf + 44 >> 2] = stat.st_size //4096 +1
            self.HEAP32[buf + 48 >> 2] = int(stat.st_atime)
            self.HEAP32[buf + 52 >> 2] = 0
            self.HEAP32[buf + 56 >> 2] = int(stat.st_mtime)
            self.HEAP32[buf + 60 >> 2] = 0
            self.HEAP32[buf + 64 >> 2] = int(stat.st_ctime)
            self.HEAP32[buf + 68 >> 2] = 0
            self.HEAP32[buf + 72 >> 2] = hash(stat.st_ino) & 0xFFFFFFFF
            return 0
        except Exception as e:
            logging.error("_syscall195 failed" , exc_info=True)
            return -1
    
    @logwrap
    def _syscall196(self,param0,param1):
        logging.error("_syscall196 not implemented")
        return 0
    
    @logwrap
    def _syscall197(self,param0,varargs):
        self.SYSCALLS.varargs = varargs
        try:
            stream = self.SYSCALLS.getStreamFromFD()
            buf = self.SYSCALLS.get()
            stat = os.stat(stream.fileno())
            self.HEAP32[buf >> 2] = stat.st_dev
            self.HEAP32[buf + 4 >> 2] = 0
            self.HEAP32[buf + 8 >> 2] = hash(stat.st_ino) & 0xFFFFFFFF
            self.HEAP32[buf + 12 >> 2] = stat.st_mode
            self.HEAP32[buf + 16 >> 2] = stat.st_nlink
            self.HEAP32[buf + 20 >> 2] = stat.st_uid
            self.HEAP32[buf + 24 >> 2] = stat.st_gid
            self.HEAP32[buf + 28 >> 2] = 0  #stat.rdev
            self.HEAP32[buf + 32 >> 2] = 0
            self.HEAP32[buf + 36 >> 2] = stat.st_size   
            self.HEAP32[buf + 40 >> 2] = 4096
            self.HEAP32[buf + 44 >> 2] = stat.st_size //4096 +1
            self.HEAP32[buf + 48 >> 2] = int(stat.st_atime)
            self.HEAP32[buf + 52 >> 2] = 0
            self.HEAP32[buf + 56 >> 2] = int(stat.st_mtime)
            self.HEAP32[buf + 60 >> 2] = 0
            self.HEAP32[buf + 64 >> 2] = int(stat.st_ctime)
            self.HEAP32[buf + 68 >> 2] = 0
            self.HEAP32[buf + 72 >> 2] = hash(stat.st_ino) & 0xFFFFFFFF
            return 0
        except Exception as e:
            logging.error("_syscall197 failed" , exc_info=True)
            return -1
    
    @logwrap
    def _syscall199(self,param0,param1):
        logging.error("_syscall199 not implemented")
        return 0
    
    @logwrap
    def _syscall220(self,param0,param1):
        logging.error("_syscall220 not implemented")
        return 0
    
    @logwrap
    def _syscall221(self,param0,param1):
        logging.error("_syscall221 not implemented")
        return 0
    
    @logwrap
    def _syscall268(self,param0,param1):
        logging.error("_syscall268 not implemented")
        return 0
    
    @logwrap
    def _syscall3(self,param0,varargs):
        self.SYSCALLS.varargs = varargs
        try:
            stream = self.SYSCALLS.getStreamFromFD()
            buf = self.SYSCALLS.get()
            count = self.SYSCALLS.get()
            ret = stream.read_to_buffer(self.HEAP8, buf, count)
            return ret
        except Exception as e:
            logging.error("_syscall3 failed" , exc_info=True)
            return -1
    
    @logwrap
    def _syscall33(self,param0,varargs):

        self.SYSCALLS.varargs = varargs
        try:
            path = self.SYSCALLS.getStr()
            logging.info(path)
            amode = self.SYSCALLS.get()
            if os.path.exists(path):
                return 0
            else:
                return -2
        except Exception as e:
            logging.error("_syscall33 failed" , exc_info=True)
            return -1
    
    @logwrap
    def _syscall38(self,param0,param1):
        logging.error("_syscall38 not implemented")
        return 0
    
    @logwrap
    def _syscall39(self,param0,varargs):
        self.SYSCALLS.varargs = varargs
        try:
            path = self.SYSCALLS.getStr()
            amode = self.SYSCALLS.get()
            os.makedirs(path)
            return 0
        except Exception as e:
            logging.error("_syscall33 failed" , exc_info=True)
            return -1
    
    @logwrap
    def _syscall4(self, notinuse, varargs):
        logging.error("_syscall4 not implemented")
        return 0
    
    @logwrap
    def _syscall40(self,param0,param1):
        logging.error("_syscall40 not implemented")
        return 0
    
    @logwrap
    def _syscall42(self,param0,param1):
        logging.error("_syscall42 not implemented")
        return 0
    
    @logwrap
    def _syscall5(self,param0,varargs):
        self.SYSCALLS.varargs = varargs
        try:
            pathname = self.SYSCALLS.getStr()
            flags = self.SYSCALLS.get()
            mode = self.SYSCALLS.get()
            if not os.path.exists(pathname) and mode ==0:
                return -2
            fd= os.open(pathname, flags=flags, mode=mode)
            self.streams[fd] =  FS(fd, pathname)
            return fd
        except Exception as e:
            logging.error("_syscall5" , exc_info=True)
            return -1

    
    @logwrap
    def _syscall54(self,param0,varargs):
        self.SYSCALLS.varargs = varargs

        try:
            stream = self.SYSCALLS.getStreamFromFD()
            op = self.SYSCALLS.get()

            if op in [21509, 21505, 21510, 21511, 21512, 21506, 21507, 21508, 21523, 21524]:
                if not stream.tty:
                    return -ERRNO_CODES.ENOTTY
                return 0

            elif op == 21519:
                if not stream.tty:
                    return -ERRNO_CODES.ENOTTY
                argp = self.SYSCALLS.get()
                self.HEAP32[argp >> 2] = 0
                return 0

            elif op == 21520:
                if not stream.tty:
                    return -ERRNO_CODES.ENOTTY  
                return -ERRNO_CODES.EINVAL

            elif op == 21531:
                argp = self.SYSCALLS.get()
                return FS.ioctl(stream, op, argp)

            else:
                raise ValueError("bad ioctl syscall " + str(op))

        except Exception as e:
            logging.error("_syscall54" , exc_info=True)
            return -1
    
    @logwrap
    def _syscall6(self,param0,varargs):
        self.SYSCALLS.varargs = varargs
        try:
            stream = self.SYSCALLS.getStreamFromFD()
            fd = stream.fileno()
            stream.close()
            self.streams.pop(fd)
            return 0    
        except Exception as e:
            logging.error("_syscall6" , exc_info=True)
            return -1
    
    @logwrap
    def _syscall63(self,param0,param1):
        logging.error("_syscall63 not implemented")
        return 0
    
    @logwrap
    def _syscall77(self,param0,param1):
        logging.error("_syscall77 not implemented")
        return 0
    
    @logwrap
    def _syscall85(self,param0,param1):
        logging.error("_syscall85 not implemented")
        return 0
    
    @logwrap
    def _syscall91(self,param0,varargs):

        self.SYSCALLS.varargs = varargs
        try:
            addr = self.SYSCALLS.get()
            length = self.SYSCALLS.get()
            info = self.SYSCALLS.mappings.get(addr)
            logging.info(f'_syscall91 {(param0, varargs)} ||| {(addr, length, info)}')
            if not info:
                return 0

            if length == info['len']:
                stream = self.FS.getStream(info['fd'])
                self.SYSCALLS.doMsync(addr, stream, length, info['flags'])
                self.FS.munmap(stream)
                self.SYSCALLS.mappings[addr] = None
                if info['allocated']:
                    self._free(info['malloc'])
            
            return 0
        except Exception as e:
            logging.error("_syscall91" , exc_info=True)
            return -1
    
    @logwrap
    def _unlock(self,param0):
        return 
    
    @logwrap
    def _abort(self):
        logging.error("_abort not implemented")
        return 
    
    @logwrap
    def _atexit(self,param0):
        logging.error("_atexit not implemented")
        return 0
    
    @logwrap
    def _clock(self):
        if self.clock_start is None:
            self.clock_start = time.time()
        return int((time.time() - self.clock_start) * 1e6)
        # return 0
    
    @logwrap
    def _clock_getres(self,param0,param1):
        logging.error("_clock_getres not implemented")
        return 0
    
    @logwrap
    def _clock_gettime(self,param0,param1):
        logging.error("_clock_gettime not implemented")
        return 0
    
    @logwrap
    def _difftime(self,param0,param1):
        logging.error("_difftime not implemented")
        return 0
    
    @logwrap
    def _dlclose(self,param0):
        logging.error("_dlclose not implemented")
        return 0
    
    @logwrap
    def _dlopen(self,param0,param1):
        logging.error("_dlopen not implemented")
        return 0
    
    @logwrap
    def _dlsym(self,param0,param1):
        logging.error("_dlsym not implemented")
        return 0
    
    @logwrap
    def _emscripten_asm_const_i(self,param0):
        ret = ASM_CONSTS[param0]()
        return ret
    
    @logwrap
    def _emscripten_asm_const_sync_on_main_thread_i(self,param0):
        ret = ASM_CONSTS[param0]()  
        return ret
    
    @logwrap
    def _emscripten_cancel_main_loop(self):
        logging.error("_emscripten_cancel_main_loop not implemented")
        return 
    
    @logwrap
    def _emscripten_exit_fullscreen(self):
        logging.error("_emscripten_exit_fullscreen not implemented")
        return 0
    
    @logwrap
    def _emscripten_exit_pointerlock(self):
        logging.error("_emscripten_exit_pointerlock not implemented")
        return 0
    
    @logwrap
    def _emscripten_get_canvas_element_size(self,param0,param1,param2):
        logging.error("_emscripten_get_canvas_element_size not implemented")
        return 0
    
    @logwrap
    def _emscripten_get_fullscreen_status(self,param0):
        logging.error("_emscripten_get_fullscreen_status not implemented")
        return 0
    
    @logwrap
    def _emscripten_get_gamepad_status(self,param0,param1):
        logging.error("_emscripten_get_gamepad_status not implemented")
        return 0
    
    @logwrap
    def _emscripten_get_main_loop_timing(self,param0,param1):
        logging.error("_emscripten_get_main_loop_timing not implemented")
        return 
    
    @logwrap
    def _emscripten_get_now(self):
        return time.time()*1000 - self.init_time
    
    @logwrap
    def _emscripten_get_num_gamepads(self):
        logging.error("_emscripten_get_num_gamepads not implemented")
        return 0
    
    @logwrap
    def _emscripten_has_threading_support(self):
        logging.error("_emscripten_has_threading_support not implemented")
        return 0
    
    @logwrap
    def _emscripten_html5_remove_all_event_listeners(self):
        logging.error("_emscripten_html5_remove_all_event_listeners not implemented")
        return 
    
    @logwrap
    def _emscripten_is_webgl_context_lost(self,param0):
        logging.error("_emscripten_is_webgl_context_lost not implemented")
        return 0
    
    @logwrap
    def _emscripten_log(self,param0,param1):
        logging.error("_emscripten_log not implemented")
        return 
    
    @logwrap
    def _emscripten_longjmp(self,param0,param1):
        logging.error("_emscripten_longjmp not implemented")
        return 
    
    @logwrap
    def _emscripten_memcpy_big(self,dest, src, num):
        self.HEAPU8[dest:dest+num] = self.HEAPU8[src:src+num]
        return dest
        
    @logwrap
    def _emscripten_num_logical_cores(self):
        logging.error("_emscripten_num_logical_cores not implemented")
        return 0
    
    @logwrap
    def _emscripten_request_fullscreen(self,param0,param1):
        logging.error("_emscripten_request_fullscreen not implemented")
        return 0
    
    @logwrap
    def _emscripten_request_pointerlock(self,param0,param1):
        logging.error("_emscripten_request_pointerlock not implemented")
        return 0
    
    @logwrap
    def _emscripten_set_blur_callback_on_thread(self,param0,param1,param2,param3,param4):
        logging.warning("_emscripten_set_blur_callback_on_thread not implemented -- ignore")
        return 0
    
    @logwrap
    def _emscripten_set_canvas_element_size(self,param0,param1,param2):
        logging.error("_emscripten_set_canvas_element_size not implemented")
        return 0
    
    @logwrap
    def _emscripten_set_dblclick_callback_on_thread(self,param0,param1,param2,param3,param4):
        logging.error("_emscripten_set_dblclick_callback_on_thread not implemented")
        return 0
    
    @logwrap
    def _emscripten_set_devicemotion_callback_on_thread(self,param0,param1,param2,param3):
        if not 'deviceMotionEvent' in self.JSEVENTS:
            self.JSEVENTS['deviceMotionEvent'] = self._malloc(80)
        return 0
    
    @logwrap
    def _emscripten_set_deviceorientation_callback_on_thread(self,param0,param1,param2,param3):
        if not 'deviceOrientationEvent' in self.JSEVENTS:
            self.JSEVENTS['deviceOrientationEvent'] = self._malloc(40)
        
        return 0
    
    @logwrap
    def _emscripten_set_focus_callback_on_thread(self,param0,param1,param2,param3,param4):
        if not 'focusEvent' in self.JSEVENTS:
            self.JSEVENTS['focusEvent'] = self._malloc(256)
        return 0
    
    @logwrap
    def _emscripten_set_fullscreenchange_callback_on_thread(self,param0,param1,param2,param3,param4):
        if not 'fullscreenChangeEvent' in self.JSEVENTS:
            self.JSEVENTS['fullscreenChangeEvent'] = self._malloc(280)
        return 0
    
    @logwrap
    def _emscripten_set_gamepadconnected_callback_on_thread(self,param0,param1,param2,param3):
        if not 'gamepadEvent' in self.JSEVENTS:
            self.JSEVENTS['gamepadEvent'] = self._malloc(1432) 
        return 0
    
    @logwrap
    def _emscripten_set_gamepaddisconnected_callback_on_thread(self,param0,param1,param2,param3):
        logging.warning("_emscripten_set_gamepaddisconnected_callback_on_thread -- ignored")
        return 0
    
    @logwrap
    def _emscripten_set_keydown_callback_on_thread(self,param0,param1,param2,param3,param4):
        if not 'keyEvent' in self.JSEVENTS:
            self.JSEVENTS['keyEvent'] = self._malloc(164)
        return 0
    
    @logwrap
    def _emscripten_set_keypress_callback_on_thread(self,param0,param1,param2,param3,param4):
        logging.warning("_emscripten_set_keypress_callback_on_thread -- ignored")
        return 0
    
    @logwrap
    def _emscripten_set_keyup_callback_on_thread(self,param0,param1,param2,param3,param4):
        logging.warning("_emscripten_set_keyup_callback_on_thread -- ignored")
        return 0
    
    @logwrap
    def _emscripten_set_main_loop(self,param0,param1,param2):
        logging.error("_emscripten_set_main_loop not implemented")
        return 
    
    @logwrap
    def _emscripten_set_main_loop_timing(self,param0,param1):
        logging.error("_emscripten_set_main_loop_timing not implemented")
        return 0
    
    @logwrap
    def _emscripten_set_mousedown_callback_on_thread(self,param0,param1,param2,param3,param4):
        logging.warning("_emscripten_set_mousedown_callback_on_thread -- ignored")
        return 0
    
    @logwrap
    def _emscripten_set_mousemove_callback_on_thread(self,param0,param1,param2,param3,param4):
        logging.warning("_emscripten_set_mousemove_callback_on_thread -- ignored")
        return 0
    
    @logwrap
    def _emscripten_set_mouseup_callback_on_thread(self,param0,param1,param2,param3,param4):
        if not 'mouseEvent' in self.JSEVENTS:
            self.JSEVENTS['mouseEvent'] = self._malloc(72)
        return 0
    
    @logwrap
    def _emscripten_set_touchcancel_callback_on_thread(self,param0,param1,param2,param3,param4):
        logging.warning("_emscripten_set_touchcancel_callback_on_thread -- ignored")
        return 0
    
    @logwrap
    def _emscripten_set_touchend_callback_on_thread(self,param0,param1,param2,param3,param4):
        logging.warning("_emscripten_set_touchend_callback_on_thread -- ignored")
        return 0
    
    @logwrap
    def _emscripten_set_touchmove_callback_on_thread(self,param0,param1,param2,param3,param4):
        logging.warning("_emscripten_set_touchmove_callback_on_thread -- ignored")
        return 0
    
    @logwrap
    def _emscripten_set_touchstart_callback_on_thread(self,param0,param1,param2,param3,param4):
        if not 'touchEvent' in self.JSEVENTS:
            self.JSEVENTS['touchEvent'] = self._malloc(1684)  
        return 0
    
    @logwrap
    def _emscripten_set_wheel_callback_on_thread(self,param0,param1,param2,param3,param4):
        if not 'wheelEvent' in self.JSEVENTS:
            self.JSEVENTS['wheelEvent'] = self._malloc(104)   
        return 0
    
    @logwrap
    def _emscripten_webgl_create_context(self,target,attributes):
        contextAttributes = {}
        contextAttributes["alpha"] = bool(self.HEAP32[attributes >> 2])
        contextAttributes["depth"] = bool(self.HEAP32[attributes + 4 >> 2])
        contextAttributes["stencil"] = bool(self.HEAP32[attributes + 8 >> 2])
        contextAttributes["antialias"] = bool(self.HEAP32[attributes + 12 >> 2])
        contextAttributes["premultipliedAlpha"] = bool(self.HEAP32[attributes + 16 >> 2])
        contextAttributes["preserveDrawingBuffer"] = bool(self.HEAP32[attributes + 20 >> 2])
        contextAttributes["preferLowPowerToHighPerformance"] = bool(self.HEAP32[attributes + 24 >> 2])
        contextAttributes["failIfMajorPerformanceCaveat"] = bool(self.HEAP32[attributes + 28 >> 2])
        contextAttributes["majorVersion"] = self.HEAP32[attributes + 32 >> 2]
        contextAttributes["minorVersion"] = self.HEAP32[attributes + 36 >> 2]
        contextAttributes["explicitSwapControl"] = self.HEAP32[attributes + 44 >> 2]
        contextAttributes["proxyContextToMainThread"] = self.HEAP32[attributes + 48 >> 2]
        contextAttributes["renderViaOffscreenBackBuffer"] = self.HEAP32[attributes + 52 >> 2]
        target = self.Pointer_stringify(target)

        handle = self._malloc(8)

        context = {
            'handle': handle,
            'attributes': contextAttributes,
            'version': contextAttributes["majorVersion"],
            'ctx' : 'Not implemented'
        }
        self.HEAP32[handle >> 2] = contextAttributes["explicitSwapControl"]
        self.GL_contexts = [None] * handle + [context]
        return handle

    @logwrap
    def _emscripten_webgl_destroy_context(self,param0):
        logging.error("_emscripten_webgl_destroy_context not implemented")
        return 0
    
    @logwrap
    def _emscripten_webgl_enable_extension(self,contextHandle, extension):
        context  = self.GL_contexts[contextHandle]
        extString = self.Pointer_stringify(extension)
        if extString.startswith("GL_"):
            extString = extString[3:]
        ext = self.GL_contexts_ext.get(extString, False)
        ret = 1 if ext else 0
        return ret
    
    @logwrap
    def _emscripten_webgl_get_current_context(self):
        if self.GL_currentContext: 
            return self.GL_currentContext['handle']
        else:
            return 0
    
    @logwrap
    def _emscripten_webgl_init_context_attributes(self,attributes):
        self.HEAP32[attributes >> 2] = 1
        self.HEAP32[attributes + 4 >> 2] = 1
        self.HEAP32[attributes + 8 >> 2] = 0
        self.HEAP32[attributes + 12 >> 2] = 1
        self.HEAP32[attributes + 16 >> 2] = 1
        self.HEAP32[attributes + 20 >> 2] = 0
        self.HEAP32[attributes + 24 >> 2] = 0
        self.HEAP32[attributes + 28 >> 2] = 0
        self.HEAP32[attributes + 32 >> 2] = 1
        self.HEAP32[attributes + 36 >> 2] = 0
        self.HEAP32[attributes + 40 >> 2] = 1
        self.HEAP32[attributes + 44 >> 2] = 0
        self.HEAP32[attributes + 48 >> 2] = 0
        self.HEAP32[attributes + 52 >> 2] = 0
        return 
    
    @logwrap
    def _emscripten_webgl_make_context_current(self,contextHandle):
        try:
            self.GL_currentContext = self.GL_contexts[contextHandle]
            return 0
        except:
            return -5 
    
    @logwrap
    def _exit(self,param0):
        logging.error("_exit not implemented")
        return 
    
    @logwrap
    def _flock(self,param0,param1):
        logging.error("_flock not implemented")
        return 0
    
    @logwrap
    def _getaddrinfo(self,param0,param1,param2,param3):
        logging.error("_getaddrinfo not implemented")
        return 0
    
    @logwrap
    def _getenv(self,name):
        if (name == 0):
            return 0
        name =self.Pointer_stringify(name)
        if name not in self.ENV:
            return 0
        
        if name in self.GETENV_RET:
            ret = self.GETENV_RET.pop(name)
            self._free(ret)
        ret =  self.allocateUTF8(self.ENV[name])
        self.GETENV_RET[name] = ret
        return ret
    
    
    @logwrap
    def _gethostbyaddr(self,param0,param1,param2):
        logging.error("_gethostbyaddr not implemented")
        return 0
    
    @logwrap
    def _gethostbyname(self,param0):
        logging.error("_gethostbyname not implemented")
        return 0
    
    @logwrap
    def _getnameinfo(self,param0,param1,param2,param3,param4,param5,param6):
        logging.error("_getnameinfo not implemented")
        return 0
    
    @logwrap
    def _getpagesize(self):
        return self.PAGE_SIZE
    
    @logwrap
    def _getpwuid(self,param0):
        logging.error("_getpwuid not implemented")
        return 0
    
    @logwrap
    def _gettimeofday(self,ptr,param1):
        now = time.time()*1000 % 1e3 * 1e3 
        self.HEAP32[ptr >> 2] = int(now / 1e3) | 0;
        self.HEAP32[ptr + 4 >> 2] = int(now % 1e3 * 1e3) | 0;
        return 0
    
    @logwrap
    def _glActiveTexture(self,param0):
        logging.error("_glActiveTexture not implemented")
        return 
    
    @logwrap
    def _glAttachShader(self,param0,param1):
        logging.error("_glAttachShader not implemented")
        return 
    
    @logwrap
    def _glBeginQuery(self,param0,param1):
        logging.error("_glBeginQuery not implemented")
        return 
    
    @logwrap
    def _glBeginTransformFeedback(self,param0):
        logging.error("_glBeginTransformFeedback not implemented")
        return 
    
    @logwrap
    def _glBindAttribLocation(self,param0,param1,param2):
        logging.error("_glBindAttribLocation not implemented")
        return 
    
    @logwrap
    def _glBindBuffer(self,param0,param1):
        logging.error("_glBindBuffer not implemented")
        return 
    
    @logwrap
    def _glBindBufferBase(self,param0,param1,param2):
        logging.error("_glBindBufferBase not implemented")
        return 
    
    @logwrap
    def _glBindBufferRange(self,param0,param1,param2,param3,param4):
        logging.error("_glBindBufferRange not implemented")
        return 
    
    @logwrap
    def _glBindFramebuffer(self,param0,param1):
        logging.error("_glBindFramebuffer not implemented")
        return 
    
    @logwrap
    def _glBindRenderbuffer(self,param0,param1):
        logging.error("_glBindRenderbuffer not implemented")
        return 
    
    @logwrap
    def _glBindSampler(self,param0,param1):
        logging.error("_glBindSampler not implemented")
        return 
    
    @logwrap
    def _glBindTexture(self,param0,param1):
        logging.error("_glBindTexture not implemented")
        return 
    
    @logwrap
    def _glBindTransformFeedback(self,param0,param1):
        logging.error("_glBindTransformFeedback not implemented")
        return 
    
    @logwrap
    def _glBindVertexArray(self,param0):
        logging.error("_glBindVertexArray not implemented")
        return 
    
    @logwrap
    def _glBlendEquation(self,param0):
        logging.error("_glBlendEquation not implemented")
        return 
    
    @logwrap
    def _glBlendEquationSeparate(self,param0,param1):
        logging.error("_glBlendEquationSeparate not implemented")
        return 
    
    @logwrap
    def _glBlendFuncSeparate(self,param0,param1,param2,param3):
        logging.error("_glBlendFuncSeparate not implemented")
        return 
    
    @logwrap
    def _glBlitFramebuffer(self,param0,param1,param2,param3,param4,param5,param6,param7,param8,param9):
        logging.error("_glBlitFramebuffer not implemented")
        return 
    
    @logwrap
    def _glBufferData(self,param0,param1,param2,param3):
        logging.error("_glBufferData not implemented")
        return 
    
    @logwrap
    def _glBufferSubData(self,param0,param1,param2,param3):
        logging.error("_glBufferSubData not implemented")
        return 
    
    @logwrap
    def _glCheckFramebufferStatus(self,param0):
        logging.error("_glCheckFramebufferStatus not implemented")
        return 0
    
    @logwrap
    def _glClear(self,param0):
        logging.error("_glClear not implemented")
        return 
    
    @logwrap
    def _glClearBufferfi(self,param0,param1,param2,param3):
        logging.error("_glClearBufferfi not implemented")
        return 
    
    @logwrap
    def _glClearBufferfv(self,param0,param1,param2):
        logging.error("_glClearBufferfv not implemented")
        return 
    
    @logwrap
    def _glClearBufferuiv(self,param0,param1,param2):
        logging.error("_glClearBufferuiv not implemented")
        return 
    
    @logwrap
    def _glClearColor(self,param0,param1,param2,param3):
        logging.error("_glClearColor not implemented")
        return 
    
    @logwrap
    def _glClearDepthf(self,param0):
        logging.error("_glClearDepthf not implemented")
        return 
    
    @logwrap
    def _glClearStencil(self,param0):
        logging.error("_glClearStencil not implemented")
        return 
    
    @logwrap
    def _glColorMask(self,param0,param1,param2,param3):
        logging.error("_glColorMask not implemented")
        return 
    
    @logwrap
    def _glCompileShader(self,param0):
        logging.error("_glCompileShader not implemented")
        return 
    
    @logwrap
    def _glCompressedTexImage2D(self,param0,param1,param2,param3,param4,param5,param6,param7):
        logging.error("_glCompressedTexImage2D not implemented")
        return 
    
    @logwrap
    def _glCompressedTexSubImage2D(self,param0,param1,param2,param3,param4,param5,param6,param7,param8):
        logging.error("_glCompressedTexSubImage2D not implemented")
        return 
    
    @logwrap
    def _glCompressedTexSubImage3D(self,param0,param1,param2,param3,param4,param5,param6,param7,param8,param9,param10):
        logging.error("_glCompressedTexSubImage3D not implemented")
        return 
    
    @logwrap
    def _glCopyBufferSubData(self,param0,param1,param2,param3,param4):
        logging.error("_glCopyBufferSubData not implemented")
        return 
    
    @logwrap
    def _glCopyTexImage2D(self,param0,param1,param2,param3,param4,param5,param6,param7):
        logging.error("_glCopyTexImage2D not implemented")
        return 
    
    @logwrap
    def _glCopyTexSubImage2D(self,param0,param1,param2,param3,param4,param5,param6,param7):
        logging.error("_glCopyTexSubImage2D not implemented")
        return 
    
    @logwrap
    def _glCreateProgram(self):
        logging.error("_glCreateProgram not implemented")
        return 0
    
    @logwrap
    def _glCreateShader(self,param0):
        logging.error("_glCreateShader not implemented")
        return 0
    
    @logwrap
    def _glCullFace(self,param0):
        logging.error("_glCullFace not implemented")
        return 
    
    @logwrap
    def _glDeleteBuffers(self,param0,param1):
        logging.error("_glDeleteBuffers not implemented")
        return 
    
    @logwrap
    def _glDeleteFramebuffers(self,param0,param1):
        logging.error("_glDeleteFramebuffers not implemented")
        return 
    
    @logwrap
    def _glDeleteProgram(self,param0):
        logging.error("_glDeleteProgram not implemented")
        return 
    
    @logwrap
    def _glDeleteQueries(self,param0,param1):
        logging.error("_glDeleteQueries not implemented")
        return 
    
    @logwrap
    def _glDeleteRenderbuffers(self,param0,param1):
        logging.error("_glDeleteRenderbuffers not implemented")
        return 
    
    @logwrap
    def _glDeleteSamplers(self,param0,param1):
        logging.error("_glDeleteSamplers not implemented")
        return 
    
    @logwrap
    def _glDeleteShader(self,param0):
        logging.error("_glDeleteShader not implemented")
        return 
    
    @logwrap
    def _glDeleteSync(self,param0):
        logging.error("_glDeleteSync not implemented")
        return 
    
    @logwrap
    def _glDeleteTextures(self,param0,param1):
        logging.error("_glDeleteTextures not implemented")
        return 
    
    @logwrap
    def _glDeleteTransformFeedbacks(self,param0,param1):
        logging.error("_glDeleteTransformFeedbacks not implemented")
        return 
    
    @logwrap
    def _glDeleteVertexArrays(self,param0,param1):
        logging.error("_glDeleteVertexArrays not implemented")
        return 
    
    @logwrap
    def _glDepthFunc(self,param0):
        logging.error("_glDepthFunc not implemented")
        return 
    
    @logwrap
    def _glDepthMask(self,param0):
        logging.error("_glDepthMask not implemented")
        return 
    
    @logwrap
    def _glDetachShader(self,param0,param1):
        logging.error("_glDetachShader not implemented")
        return 
    
    @logwrap
    def _glDisable(self,param0):
        logging.error("_glDisable not implemented")
        return 
    
    @logwrap
    def _glDisableVertexAttribArray(self,param0):
        logging.error("_glDisableVertexAttribArray not implemented")
        return 
    
    @logwrap
    def _glDrawArrays(self,param0,param1,param2):
        logging.error("_glDrawArrays not implemented")
        return 
    
    @logwrap
    def _glDrawArraysInstanced(self,param0,param1,param2,param3):
        logging.error("_glDrawArraysInstanced not implemented")
        return 
    
    @logwrap
    def _glDrawBuffers(self,param0,param1):
        logging.error("_glDrawBuffers not implemented")
        return 
    
    @logwrap
    def _glDrawElements(self,param0,param1,param2,param3):
        logging.error("_glDrawElements not implemented")
        return 
    
    @logwrap
    def _glDrawElementsInstanced(self,param0,param1,param2,param3,param4):
        logging.error("_glDrawElementsInstanced not implemented")
        return 
    
    @logwrap
    def _glEnable(self,param0):
        logging.error("_glEnable not implemented")
        return 
    
    @logwrap
    def _glEnableVertexAttribArray(self,param0):
        logging.error("_glEnableVertexAttribArray not implemented")
        return 
    
    @logwrap
    def _glEndQuery(self,param0):
        logging.error("_glEndQuery not implemented")
        return 
    
    @logwrap
    def _glEndTransformFeedback(self):
        logging.error("_glEndTransformFeedback not implemented")
        return 
    
    @logwrap
    def _glFenceSync(self,param0,param1):
        logging.error("_glFenceSync not implemented")
        return 0
    
    @logwrap
    def _glFinish(self):
        logging.error("_glFinish not implemented")
        return 
    
    @logwrap
    def _glFlush(self):
        logging.error("_glFlush not implemented")
        return 
    
    @logwrap
    def _glFlushMappedBufferRange(self,param0,param1,param2):
        logging.error("_glFlushMappedBufferRange not implemented")
        return 
    
    @logwrap
    def _glFramebufferRenderbuffer(self,param0,param1,param2,param3):
        logging.error("_glFramebufferRenderbuffer not implemented")
        return 
    
    @logwrap
    def _glFramebufferTexture2D(self,param0,param1,param2,param3,param4):
        logging.error("_glFramebufferTexture2D not implemented")
        return 
    
    @logwrap
    def _glFramebufferTextureLayer(self,param0,param1,param2,param3,param4):
        logging.error("_glFramebufferTextureLayer not implemented")
        return 
    
    @logwrap
    def _glFrontFace(self,param0):
        logging.error("_glFrontFace not implemented")
        return 
    
    @logwrap
    def _glGenBuffers(self,param0,param1):
        logging.error("_glGenBuffers not implemented")
        return 
    
    @logwrap
    def _glGenFramebuffers(self,param0,param1):
        logging.error("_glGenFramebuffers not implemented")
        return 
    
    @logwrap
    def _glGenQueries(self,param0,param1):
        logging.error("_glGenQueries not implemented")
        return 
    
    @logwrap
    def _glGenRenderbuffers(self,param0,param1):
        logging.error("_glGenRenderbuffers not implemented")
        return 
    
    @logwrap
    def _glGenSamplers(self,param0,param1):
        logging.error("_glGenSamplers not implemented")
        return 
    
    @logwrap
    def _glGenTextures(self,param0,param1):
        logging.error("_glGenTextures not implemented")
        return 
    
    @logwrap
    def _glGenTransformFeedbacks(self,param0,param1):
        logging.error("_glGenTransformFeedbacks not implemented")
        return 
    
    @logwrap
    def _glGenVertexArrays(self,param0,param1):
        logging.error("_glGenVertexArrays not implemented")
        return 
    
    @logwrap
    def _glGenerateMipmap(self,param0):
        logging.error("_glGenerateMipmap not implemented")
        return 
    
    @logwrap
    def _glGetActiveAttrib(self,param0,param1,param2,param3,param4,param5,param6):
        logging.error("_glGetActiveAttrib not implemented")
        return 
    
    @logwrap
    def _glGetActiveUniform(self,param0,param1,param2,param3,param4,param5,param6):
        logging.error("_glGetActiveUniform not implemented")
        return 
    
    @logwrap
    def _glGetActiveUniformBlockName(self,param0,param1,param2,param3,param4):
        logging.error("_glGetActiveUniformBlockName not implemented")
        return 
    
    @logwrap
    def _glGetActiveUniformBlockiv(self,param0,param1,param2,param3):
        logging.error("_glGetActiveUniformBlockiv not implemented")
        return 
    
    @logwrap
    def _glGetActiveUniformsiv(self,param0,param1,param2,param3,param4):
        logging.error("_glGetActiveUniformsiv not implemented")
        return 
    
    @logwrap
    def _glGetAttribLocation(self,param0,param1):
        logging.error("_glGetAttribLocation not implemented")
        return 0
    
    @logwrap
    def _glGetError(self):
        logging.error("_glGetError not implemented")
        return 0
    
    @logwrap
    def _glGetFramebufferAttachmentParameteriv(self,param0,param1,param2,param3):
        logging.error("_glGetFramebufferAttachmentParameteriv not implemented")
        return 
    
    @logwrap
    def _glGetIntegeri_v(self,param0,param1,param2):
        logging.error("_glGetIntegeri_v not implemented")
        return 
    
    @logwrap
    def _glGetIntegerv(self,name_, p):
        self.emscriptenWebGLGet(name_, p, "Integer")
    
    @logwrap
    def _glGetInternalformativ(self,param0,param1,param2,param3,param4):
        logging.error("_glGetInternalformativ not implemented")
        return 
    
    @logwrap
    def _glGetProgramBinary(self,param0,param1,param2,param3,param4):
        logging.error("_glGetProgramBinary not implemented")
        return 
    
    @logwrap
    def _glGetProgramInfoLog(self,param0,param1,param2,param3):
        logging.error("_glGetProgramInfoLog not implemented")
        return 
    
    @logwrap
    def _glGetProgramiv(self,param0,param1,param2):
        logging.error("_glGetProgramiv not implemented")
        return 
    
    @logwrap
    def _glGetRenderbufferParameteriv(self,param0,param1,param2):
        logging.error("_glGetRenderbufferParameteriv not implemented")
        return 
    
    @logwrap
    def _glGetShaderInfoLog(self,param0,param1,param2,param3):
        logging.error("_glGetShaderInfoLog not implemented")
        return 
    
    @logwrap
    def _glGetShaderPrecisionFormat(self,param0,param1,param2,param3):
        logging.error("_glGetShaderPrecisionFormat not implemented")
        return 
    
    @logwrap
    def _glGetShaderSource(self,param0,param1,param2,param3):
        logging.error("_glGetShaderSource not implemented")
        return 
    
    @logwrap
    def _glGetShaderiv(self,param0,param1,param2):
        logging.error("_glGetShaderiv not implemented")
        return 
    
    @logwrap
    def _glGetString(self,name_):
        if name_ in self.GL_stringCache:
            return self.GL_stringCache[name_]
        
        if name_ in [7936, 7937, 37445, 37446]:
            arr = self.intArrayFromString(self.GLctx_getParameter.get(name_))
            ret = self.allocate(arr, "i8", self.ALLOC_NORMAL)

        elif name_ == 7938:
            # Get OpenGL version
            glVersion = self.GLctx_getParameter.get(self.GLctx_VERSION)
            glVersion = "OpenGL ES 3.0 (" + glVersion + ")"
            ret = self.allocate(self.intArrayFromString(glVersion), "i8", self.ALLOC_NORMAL)

        elif name_ == 7939:
            # Get supported extensions
            exts = self.GLctx_getSupportedExtensions
            gl_exts = []
            for ext in exts:
                gl_exts.append(ext)
                gl_exts.append("GL_" + ext)
            arr = self.intArrayFromString(" ".join(gl_exts))
            ret = self.allocate(arr, "i8", self.ALLOC_NORMAL)

        elif name_ == 35724:
            # Get GLSL version
            glslVersion = self.GLctx_getParameter.get(self.GLctx_SHADING_LANGUAGE_VERSION)
            ver_re = r"^WebGL GLSL ES ([0-9]\.[0-9][0-9]?)(?:$| .*)"
            ver_num = re.match(ver_re, glslVersion)
            if ver_num:
                ver_num = ver_num.group(1)
                if len(ver_num) == 3:
                    ver_num = ver_num + "0"
                glslVersion = "OpenGL ES GLSL ES " + ver_num + " (" + glslVersion + ")"
            arr = self.intArrayFromString(glslVersion)
            ret = self.allocate(arr, "i8", "ALLOC_NORMAL")

        else:
            self.GL_lasterror = 1280
            return 0
        self.GL_stringCache[name_] = ret
        return ret
    
    @logwrap
    def _glGetStringi(self,param0,param1):
        logging.error("_glGetStringi not implemented")
        return 0
    
    @logwrap
    def _glGetTexParameteriv(self,param0,param1,param2):
        logging.error("_glGetTexParameteriv not implemented")
        return 
    
    @logwrap
    def _glGetUniformBlockIndex(self,param0,param1):
        logging.error("_glGetUniformBlockIndex not implemented")
        return 0
    
    @logwrap
    def _glGetUniformIndices(self,param0,param1,param2,param3):
        logging.error("_glGetUniformIndices not implemented")
        return 
    
    @logwrap
    def _glGetUniformLocation(self,param0,param1):
        logging.error("_glGetUniformLocation not implemented")
        return 0
    
    @logwrap
    def _glGetUniformiv(self,param0,param1,param2):
        logging.error("_glGetUniformiv not implemented")
        return 
    
    @logwrap
    def _glGetVertexAttribiv(self,param0,param1,param2):
        logging.error("_glGetVertexAttribiv not implemented")
        return 
    
    @logwrap
    def _glInvalidateFramebuffer(self,param0,param1,param2):
        logging.error("_glInvalidateFramebuffer not implemented")
        return 
    
    @logwrap
    def _glIsEnabled(self,param0):
        logging.error("_glIsEnabled not implemented")
        return 0
    
    @logwrap
    def _glIsVertexArray(self,param0):
        logging.error("_glIsVertexArray not implemented")
        return 0
    
    @logwrap
    def _glLinkProgram(self,param0):
        logging.error("_glLinkProgram not implemented")
        return 
    
    @logwrap
    def _glMapBufferRange(self,param0,param1,param2,param3):
        logging.error("_glMapBufferRange not implemented")
        return 0
    
    @logwrap
    def _glPixelStorei(self,param0,param1):
        logging.error("_glPixelStorei not implemented")
        return 
    
    @logwrap
    def _glPolygonOffset(self,param0,param1):
        logging.error("_glPolygonOffset not implemented")
        return 
    
    @logwrap
    def _glProgramBinary(self,param0,param1,param2,param3):
        logging.error("_glProgramBinary not implemented")
        return 
    
    @logwrap
    def _glProgramParameteri(self,param0,param1,param2):
        logging.error("_glProgramParameteri not implemented")
        return 
    
    @logwrap
    def _glReadBuffer(self,param0):
        logging.error("_glReadBuffer not implemented")
        return 
    
    @logwrap
    def _glReadPixels(self,param0,param1,param2,param3,param4,param5,param6):
        logging.error("_glReadPixels not implemented")
        return 
    
    @logwrap
    def _glRenderbufferStorage(self,param0,param1,param2,param3):
        logging.error("_glRenderbufferStorage not implemented")
        return 
    
    @logwrap
    def _glRenderbufferStorageMultisample(self,param0,param1,param2,param3,param4):
        logging.error("_glRenderbufferStorageMultisample not implemented")
        return 
    
    @logwrap
    def _glSamplerParameteri(self,param0,param1,param2):
        logging.error("_glSamplerParameteri not implemented")
        return 
    
    @logwrap
    def _glScissor(self,param0,param1,param2,param3):
        logging.error("_glScissor not implemented")
        return 
    
    @logwrap
    def _glShaderSource(self,param0,param1,param2,param3):
        logging.error("_glShaderSource not implemented")
        return 
    
    @logwrap
    def _glStencilFuncSeparate(self,param0,param1,param2,param3):
        logging.error("_glStencilFuncSeparate not implemented")
        return 
    
    @logwrap
    def _glStencilMask(self,param0):
        logging.error("_glStencilMask not implemented")
        return 
    
    @logwrap
    def _glStencilOpSeparate(self,param0,param1,param2,param3):
        logging.error("_glStencilOpSeparate not implemented")
        return 
    
    @logwrap
    def _glTexImage2D(self,param0,param1,param2,param3,param4,param5,param6,param7,param8):
        logging.error("_glTexImage2D not implemented")
        return 
    
    @logwrap
    def _glTexImage3D(self,param0,param1,param2,param3,param4,param5,param6,param7,param8,param9):
        logging.error("_glTexImage3D not implemented")
        return 
    
    @logwrap
    def _glTexParameterf(self,param0,param1,param2):
        logging.error("_glTexParameterf not implemented")
        return 
    
    @logwrap
    def _glTexParameteri(self,param0,param1,param2):
        logging.error("_glTexParameteri not implemented")
        return 
    
    @logwrap
    def _glTexParameteriv(self,param0,param1,param2):
        logging.error("_glTexParameteriv not implemented")
        return 
    
    @logwrap
    def _glTexStorage2D(self,param0,param1,param2,param3,param4):
        logging.error("_glTexStorage2D not implemented")
        return 
    
    @logwrap
    def _glTexStorage3D(self,param0,param1,param2,param3,param4,param5):
        logging.error("_glTexStorage3D not implemented")
        return 
    
    @logwrap
    def _glTexSubImage2D(self,param0,param1,param2,param3,param4,param5,param6,param7,param8):
        logging.error("_glTexSubImage2D not implemented")
        return 
    
    @logwrap
    def _glTexSubImage3D(self,param0,param1,param2,param3,param4,param5,param6,param7,param8,param9,param10):
        logging.error("_glTexSubImage3D not implemented")
        return 
    
    @logwrap
    def _glTransformFeedbackVaryings(self,param0,param1,param2,param3):
        logging.error("_glTransformFeedbackVaryings not implemented")
        return 
    
    @logwrap
    def _glUniform1fv(self,param0,param1,param2):
        logging.error("_glUniform1fv not implemented")
        return 
    
    @logwrap
    def _glUniform1i(self,param0,param1):
        logging.error("_glUniform1i not implemented")
        return 
    
    @logwrap
    def _glUniform1iv(self,param0,param1,param2):
        logging.error("_glUniform1iv not implemented")
        return 
    
    @logwrap
    def _glUniform1uiv(self,param0,param1,param2):
        logging.error("_glUniform1uiv not implemented")
        return 
    
    @logwrap
    def _glUniform2fv(self,param0,param1,param2):
        logging.error("_glUniform2fv not implemented")
        return 
    
    @logwrap
    def _glUniform2iv(self,param0,param1,param2):
        logging.error("_glUniform2iv not implemented")
        return 
    
    @logwrap
    def _glUniform2uiv(self,param0,param1,param2):
        logging.error("_glUniform2uiv not implemented")
        return 
    
    @logwrap
    def _glUniform3fv(self,param0,param1,param2):
        logging.error("_glUniform3fv not implemented")
        return 
    
    @logwrap
    def _glUniform3iv(self,param0,param1,param2):
        logging.error("_glUniform3iv not implemented")
        return 
    
    @logwrap
    def _glUniform3uiv(self,param0,param1,param2):
        logging.error("_glUniform3uiv not implemented")
        return 
    
    @logwrap
    def _glUniform4fv(self,param0,param1,param2):
        logging.error("_glUniform4fv not implemented")
        return 
    
    @logwrap
    def _glUniform4iv(self,param0,param1,param2):
        logging.error("_glUniform4iv not implemented")
        return 
    
    @logwrap
    def _glUniform4uiv(self,param0,param1,param2):
        logging.error("_glUniform4uiv not implemented")
        return 
    
    @logwrap
    def _glUniformBlockBinding(self,param0,param1,param2):
        logging.error("_glUniformBlockBinding not implemented")
        return 
    
    @logwrap
    def _glUniformMatrix3fv(self,param0,param1,param2,param3):
        logging.error("_glUniformMatrix3fv not implemented")
        return 
    
    @logwrap
    def _glUniformMatrix4fv(self,param0,param1,param2,param3):
        logging.error("_glUniformMatrix4fv not implemented")
        return 
    
    @logwrap
    def _glUnmapBuffer(self,param0):
        logging.error("_glUnmapBuffer not implemented")
        return 0
    
    @logwrap
    def _glUseProgram(self,param0):
        logging.error("_glUseProgram not implemented")
        return 
    
    @logwrap
    def _glValidateProgram(self,param0):
        logging.error("_glValidateProgram not implemented")
        return 
    
    @logwrap
    def _glVertexAttrib4f(self,param0,param1,param2,param3,param4):
        logging.error("_glVertexAttrib4f not implemented")
        return 
    
    @logwrap
    def _glVertexAttrib4fv(self,param0,param1):
        logging.error("_glVertexAttrib4fv not implemented")
        return 
    
    @logwrap
    def _glVertexAttribIPointer(self,param0,param1,param2,param3,param4):
        logging.error("_glVertexAttribIPointer not implemented")
        return 
    
    @logwrap
    def _glVertexAttribPointer(self,param0,param1,param2,param3,param4,param5):
        logging.error("_glVertexAttribPointer not implemented")
        return 
    
    @logwrap
    def _glViewport(self,param0,param1,param2,param3):
        logging.error("_glViewport not implemented")
        return 
    
    @logwrap
    def _gmtime(self,param0):
        logging.error("_gmtime not implemented")
        return 0
    
    @logwrap
    def _inet_addr(self,param0):
        logging.error("_inet_addr not implemented")
        return 0
    
    @logwrap
    def _llvm_eh_typeid_for(self,param0):
        logging.error("_llvm_eh_typeid_for not implemented")
        return 0
    
    @logwrap
    def _llvm_exp2_f32(self,param0):
        logging.error("_llvm_exp2_f32 not implemented")
        return 0
    
    @logwrap
    def _llvm_log10_f32(self,param0):
        logging.error("_llvm_log10_f32 not implemented")
        return 0
    
    @logwrap
    def _llvm_log10_f64(self,param0):
        logging.error("_llvm_log10_f64 not implemented")
        return 0
    
    @logwrap
    def _llvm_log2_f32(self,param0):
        logging.error("_llvm_log2_f32 not implemented")
        return 0
    
    @logwrap
    def _llvm_trap(self):
        logging.error("_llvm_trap not implemented")
        return 
    
    @logwrap
    def _llvm_trunc_f32(self,param0):
        logging.error("_llvm_trunc_f32 not implemented")
        return 0
    
    @logwrap
    def _localtime(self,param0):
        logging.error("_localtime not implemented")
        return 0
    
    @logwrap
    def _longjmp(self,param0,param1):
        logging.error("_longjmp not implemented")
        return 
    
    @logwrap
    def _mktime(self,param0):
        logging.error("_mktime not implemented")
        return 0
    
    @logwrap
    def _pthread_cond_destroy(self,param0):
        return 0
    
    @logwrap
    def _pthread_cond_init(self,param0,param1):
        return 0
    
    @logwrap
    def _pthread_cond_timedwait(self,param0,param1,param2):
        return 0
    
    @logwrap
    def _pthread_cond_wait(self,param0,param1):
        return 0
    
    @logwrap
    def _pthread_getspecific(self,param0):
        logging.error("_pthread_getspecific not implemented")
        return 0
    
    @logwrap
    def _pthread_key_create(self,key,destructor):
        self.HEAP32[key >> 2] = self.PTHREAD_SPECIFIC_NEXT_KEY
        self.PTHREAD_SPECIFIC[self.PTHREAD_SPECIFIC_NEXT_KEY] = 0
        self.PTHREAD_SPECIFIC_NEXT_KEY+=1
        return 0
    
    @logwrap
    def _pthread_key_delete(self,param0):
        logging.error("_pthread_key_delete not implemented")
        return 0
    
    @logwrap
    def _pthread_mutex_destroy(self,param0):
        logging.error("_pthread_mutex_destroy not implemented")
        return 0
    
    @logwrap
    def _pthread_mutex_init(self,param0,param1):
        return 0
    
    @logwrap
    def _pthread_mutexattr_destroy(self,param0):
        return 0
    
    @logwrap
    def _pthread_mutexattr_init(self,param0):
        return 0
    
    @logwrap
    def _pthread_mutexattr_setprotocol(self,param0,param1):
        return 0
    
    @logwrap
    def _pthread_mutexattr_settype(self,param0,param1):
        return 0
    
    @logwrap
    def _pthread_once(self,param0,param1):
        logging.error("_pthread_once not implemented")
        return 0
    
    @logwrap
    def _pthread_setspecific(self,param0,param1):
        logging.error("_pthread_setspecific not implemented")
        return 0
    
    @logwrap
    def _sched_yield(self):
        logging.error("_sched_yield not implemented")
        return 0
    
    @logwrap
    def _setenv(self,envname, envval, overwrite):
        if (envname == 0) :
            raise ERRNO_CODES.EINVAL
        
        name = self.Pointer_stringify(envname)
        val = self.Pointer_stringify(envval)

        if not name or '=' in name:
            raise ERRNO_CODES.EINVAL
        
        if name in self.ENV and not overwrite:
            return 0
        
        self.ENV[name] = val
        tmp = self._get_environ()
        self._buildEnvironment(tmp)
        return 0


    @logwrap
    def _sigaction(self,param0,param1,param2):
        logging.error("_sigaction not implemented")
        return 0
    
    @logwrap
    def _sigemptyset(self,param0):
        logging.error("_sigemptyset not implemented")
        return 0
    
    @logwrap
    def _strftime(self,param0,param1,param2,param3):
        logging.error("_strftime not implemented")
        return 0
    
    @logwrap
    def _sysconf(self,param0):
        logging.error("_sysconf not implemented")
        return 0
    
    @logwrap
    def _time(self,ptr):
        ret = int(time.time())
        if ptr:
            self.HEAP32[ptr >> 2] = ret
        return ret
    
    @logwrap
    def _unsetenv(self,param0):
        logging.error("_unsetenv not implemented")
        return 0
    
    @logwrap
    def _utime(self,param0,param1):
        logging.error("_utime not implemented")
        return 0
    
    @logwrap
    def f64_rem(self,param0,param1):
        logging.error("f64_rem not implemented")
        return 0
    
    @logwrap
    def invoke_iiiiij(self,param0,param1,param2,param3,param4,param5,param6):
        logging.error("invoke_iiiiij not implemented")
        return 0
    
    @logwrap
    def invoke_iiiijii(self,param0,param1,param2,param3,param4,param5,param6,param7):
        logging.error("invoke_iiiijii not implemented")
        return 0
    
    @logwrap
    def invoke_iiiijjii(self,param0,param1,param2,param3,param4,param5,param6,param7,param8,param9):
        logging.error("invoke_iiiijjii not implemented")
        return 0
    
    @logwrap
    def invoke_iiiji(self,param0,param1,param2,param3,param4,param5):
        logging.error("invoke_iiiji not implemented")
        return 0
    
    @logwrap
    def invoke_iiijiii(self,param0,param1,param2,param3,param4,param5,param6,param7):
        sp = self.stackSave()
        try:
            return self.dynCall_iiijiii(param0,param1,param2,param3,param4,param5,param6,param7)
        except:
            logging.error('invoke_iiijiii fail?', exc_info=True)
            self.stackRestore()
        return 0
    
    @logwrap
    def invoke_iij(self,param0,param1,param2,param3):
        logging.error("invoke_iij not implemented")
        return 0
    
    @logwrap
    def invoke_iiji(self,param0,param1,param2,param3,param4):
        logging.error("invoke_iiji not implemented")
        return 0
    
    @logwrap
    def invoke_iijii(self,param0,param1,param2,param3,param4,param5):
        logging.error("invoke_iijii not implemented")
        return 0
    
    @logwrap
    def invoke_ijii(self,param0,param1,param2,param3,param4):
        logging.error("invoke_ijii not implemented")
        return 0
    
    @logwrap
    def invoke_j(self,param0):
        logging.error("invoke_j not implemented")
        return 0
    
    @logwrap
    def invoke_jdi(self,param0,param1,param2):
        logging.error("invoke_jdi not implemented")
        return 0
    
    @logwrap
    def invoke_ji(self,param0,param1):
        logging.error("invoke_ji not implemented")
        return 0
    
    @logwrap
    def invoke_jii(self,param0,param1,param2):
        logging.error("invoke_jii not implemented")
        return 0
    
    @logwrap
    def invoke_jiii(self,param0,param1,param2,param3):
        logging.error("invoke_jiii not implemented")
        return 0
    
    @logwrap
    def invoke_jiiii(self,param0,param1,param2,param3,param4):
        logging.error("invoke_jiiii not implemented")
        return 0
    
    @logwrap
    def invoke_jiiiii(self,param0,param1,param2,param3,param4,param5):
        logging.error("invoke_jiiiii not implemented")
        return 0
    
    @logwrap
    def invoke_jiiiiiiiiii(self,param0,param1,param2,param3,param4,param5,param6,param7,param8,param9,param10):
        logging.error("invoke_jiiiiiiiiii not implemented")
        return 0
    
    @logwrap
    def invoke_jiiij(self,param0,param1,param2,param3,param4,param5):
        logging.error("invoke_jiiij not implemented")
        return 0
    
    @logwrap
    def invoke_jiiji(self,param0,param1,param2,param3,param4,param5):
        logging.error("invoke_jiiji not implemented")
        return 0
    
    @logwrap        
    def invoke_jiji(self,param0,param1,param2,param3,param4):
        sp = self.stackSave()
        try:
            return self.dynCall_jiji(param0, param1,param2,param3,param4)
        except:
            logging.error('invoke_jiji fail?', exc_info=True)
            self.stackRestore()
        return 0
    
    @logwrap
    def invoke_jijii(self,param0,param1,param2,param3,param4,param5):
        logging.error("invoke_jijii not implemented")
        return 0
    
    @logwrap
    def invoke_jijiii(self,param0,param1,param2,param3,param4,param5,param6):
        logging.error("invoke_jijiii not implemented")
        return 0
    
    @logwrap
    def invoke_jijj(self,param0,param1,param2,param3,param4,param5):
        logging.error("invoke_jijj not implemented")
        return 0
    
    @logwrap
    def invoke_jji(self,param0,param1,param2,param3):
        logging.error("invoke_jji not implemented")
        return 0
    
    @logwrap
    def invoke_viiiiiiifjjfii(self,param0,param1,param2,param3,param4,param5,param6,param7,param8,param9,param10,param11,param12,param13,param14,param15):
        logging.error("invoke_viiiiiiifjjfii not implemented")
        return 
    
    @logwrap
    def invoke_viiiijiiii(self,param0,param1,param2,param3,param4,param5,param6,param7,param8,param9,param10):
        logging.error("invoke_viiiijiiii not implemented")
        return 
    
    @logwrap
    def invoke_viiij(self,param0,param1,param2,param3,param4,param5):
        logging.error("invoke_viiij not implemented")
        return 
    
    @logwrap
    def invoke_viiiji(self,param0,param1,param2,param3,param4,param5,param6):
        logging.error("invoke_viiiji not implemented")
        return 
    
    @logwrap
    def invoke_viij(self,param0,param1,param2,param3,param4):
        logging.error("invoke_viij not implemented")
        return 
    
    @logwrap
    def invoke_viiji(self,param0,param1,param2,param3,param4,param5):
        logging.error("invoke_viiji not implemented")
        return 
    
    @logwrap
    def invoke_viijji(self,param0,param1,param2,param3,param4,param5,param6,param7):
        logging.error("invoke_viijji not implemented")
        return 
    
    @logwrap
    def invoke_viji(self,param0,param1,param2,param3,param4):
        logging.error("invoke_viji not implemented")
        return 
    
    @logwrap
    def invoke_vijii(self,param0,param1,param2,param3,param4,param5):
        logging.error("invoke_vijii not implemented")
        return 
    
    @logwrap
    def _atomic_fetch_add_8(self,ptr, vall, valh, memmodel):
        lo = int( self.HEAP32[ptr >> 2])
        hi = int(self.HEAP32[ptr + 4 >> 2])
        self.HEAP32[ptr >> 2] = self._i64Add(lo, hi, vall, valh)
        self.HEAP32[ptr + 4 >> 2] = self.getTempRet0()
        self.setTempRet0(hi)
        return lo
    
    @logwrap
    def _glClientWaitSync(self,param0,param1,param2,param3):
        logging.error("_glClientWaitSync not implemented")
        return 0


    def emscriptenWebGLGet(self, name_, p, type):
        if not p:
            self.GL_lasterror = 1281
            return

        ret = None
        if name_ == 36346:
            ret = 1
        elif name_ == 36344:
            if type not in ["Integer", "Integer64"]:
                self.GL_lasterror = 1280
                return
        elif name_ in [34814, 36345]:
            ret = 0
        elif name_ == 34466:
            formats = self.GLctx_getParameter.get(34467)
            ret = len(formats)
        elif name_ == 33309:
            exts = self.GLctx_getSupportedExtensions
            ret = 2 * len(exts)
        elif name_ in [33307, 33308]:
            ret = 3 if name_ == 33307 else 0

        if ret is None:
            result = self.GLctx_getParameter.get(name_)
            if isinstance(result, (int, float, bool)):
                ret = int(result) if isinstance(result, bool) else result
            elif result is None:
                if name_ in [34964, 35725, 34965, 36006, 36007, 32873, 34229, 35097, 36389, 34068]:
                    ret = 0
                else:
                    self.GL_lasterror = 1280
                    return
            elif isinstance(result, (list, np.array)):
                for i in range(len(result)):
                    index = p + i * 4
                    if type == "Integer":
                        self.HEAP32[index >> 2] = int(result[i])
                    elif type == "Float":
                        self.HEAPF32[index >> 2] = float(result[i])
                    elif type == "Boolean":
                        self.HEAP8[index >> 0] = 1 if result[i] else 0
                    else:
                        raise ValueError(f"internal glGet error, bad type: {type}")
                return
            # elif isinstance(result, (WebGLBuffer, WebGLProgram, WebGLFramebuffer, WebGLRenderbuffer, WebGLQuery, WebGLSampler, WebGLSync, WebGLTransformFeedback, WebGLVertexArrayObject, WebGLTexture)):
            #     ret = int(result.name)
            else:
                self.GL_lasterror = 1280
                logging.error('Unhandled error in emscriptenWebGLGet')
                return

        if type == "Integer64":
            tempI64 = [ret & 0xFFFFFFFF, (int(math.floor(ret / 4294967296)) & 0xFFFFFFFF)]
            self.HEAP32[p >> 2] = tempI64[0]
            self.HEAP32[p + 4 >> 2] = tempI64[1]
        elif type == "Integer":
            self.HEAP32[p >> 2] = int(ret)
        elif type == "Float":
            self.HEAPF32[p >> 2] = float(ret)
        elif type == "Boolean":
            self.HEAP8[p >> 0] = 1 if ret else 0
        else:
            raise ValueError(f"internal glGet error, bad type: {type}")
        
    def log(self, param0):
        return
        out = {}
        for idx in HEAP32_DEBUG_FULL:
            out[idx] =  self.HEAP32[idx//4]
        logging.info(f"from custom log: {param0} ||| {dict(sorted(out.items()))}"  )
        return

    def log2(self, funcname, placeholder, logval):
        return
        if self.func_stack and funcname not in self.func_stack:
            for k, v in self.func_stack.items():
                log_wasm(k ,v)
            self.func_stack = {}
            return self.log2(funcname, placeholder, logval)
        
        if funcname in self.func_stack:
            if placeholder in self.func_stack[funcname] and placeholder not in HEAP32_DEBUG_FULL:
                log_wasm(funcname ,self.func_stack[funcname])
                self.func_stack.pop(funcname)
                return self.log2(funcname, placeholder, logval)
            else:
                self.func_stack[funcname][placeholder] = logval    
        else:
            self.func_stack[funcname] = {}
            self.func_stack[funcname][placeholder] = logval
            for idx in HEAP32_DEBUG_FULL:
                self.func_stack[funcname][idx] =  self.HEAP32[idx//4]
            

        return