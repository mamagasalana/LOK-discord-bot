from wasmtime import Config, Store, Engine, Module, FuncType, Func, ValType, Instance, Limits, MemoryType, Global, GlobalType, Val, Memory, Table, TableType
from functools import partial
import numpy as np
import codecs
import math
import logging

# local modules
from wasm_base import wasm_base
from websocketmanager import WebSocketClientManager, UTF8ArrayToString

class LOK_JS2PY(wasm_base):
    def __init__(self, wasmfile= "testing/js_testing/test2.wasm"):
        super().__init__()
        if 1:
            self.config = Config()
            self.config.wasm_multi_value = True
            self.engine = Engine()

            # Load the Wasm module
            self.wasm_module = Module.from_file(self.engine, wasmfile)
            self.store = Store(self.engine)
            # Create memory
            limits = Limits(512, None)  # Replace None with maximum size if needed
            memory_type = MemoryType(limits)
            self.memory = Memory(self.store, memory_type)

            # Create table
            limits = Limits(181773, 181773)
            table_type = TableType(ValType.funcref(), limits)
            table = Table(self.store, table_type, None)

            mutable = False  # Mutable
            global_type32 = GlobalType(ValType.i32(), mutable)
            global_type64 = GlobalType(ValType.f64(), mutable)
            # Create globals
            self.global_tableBase = Global(self.store, global_type32, Val.i32(0))
            self.global_DYNAMICTOP_PTR = Global(self.store, global_type32, Val.i32(self.DYNAMICTOP_PTR))
            self.global_STACKTOP = Global(self.store, global_type32, Val.i32(self.STACKTOP))
            self.global_STACK_MAX = Global(self.store, global_type32, Val.i32(self.STACK_MAX))
            
            self.init_base_func()
            
            wasm_args = [self.memory, 
                    table, 
                    self.global_tableBase,
                    self.global_DYNAMICTOP_PTR,
                    self.global_STACKTOP,
                    self.global_STACK_MAX,
                    Global(self.store, global_type64, Val.f64(float('nan'))),
                    Global(self.store, global_type64, Val.f64(float('inf'))),
                    Func(self.store, FuncType([ValType.f64(), ValType.f64()], [ValType.f64()]), pow),
                    ] + list(self.import_object['env'].values())

            self.instance = Instance(self.store, self.wasm_module, wasm_args)
            self.export_wasm_func()
            self.ws = WebSocketClientManager(self)


    def init_base_func(self):
        self.import_object = {
            "env": {
                "abort": Func(self.store, FuncType([ValType.i32()], []), self.abort),
                "enlargeMemory": Func(self.store, FuncType([], [ValType.i32()]), self.enlargeMemory),
                "getTotalMemory": Func(self.store, FuncType([], [ValType.i32()]), self.getTotalMemory),
                "abortOnCannotGrowMemory": Func(self.store, FuncType([], [ValType.i32()]), self.abortOnCannotGrowMemory),
                "invoke_dddi": Func(self.store, FuncType([ValType.i32(),ValType.f64(),ValType.f64(),ValType.i32()], [ValType.f64()]), self.invoke_dddi),
                "invoke_dii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.f64()]), self.invoke_dii),
                "invoke_diii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.f64()]), self.invoke_diii),
                "invoke_diiid": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64()], [ValType.f64()]), self.invoke_diiid),
                "invoke_diiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.f64()]), self.invoke_diiii),
                "invoke_ffffi": Func(self.store, FuncType([ValType.i32(),ValType.f64(),ValType.f64(),ValType.f64(),ValType.i32()], [ValType.f64()]), self.invoke_ffffi),
                "invoke_fffi": Func(self.store, FuncType([ValType.i32(),ValType.f64(),ValType.f64(),ValType.i32()], [ValType.f64()]), self.invoke_fffi),
                "invoke_fi": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.f64()]), self.invoke_fi),
                "invoke_fii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.f64()]), self.invoke_fii),
                "invoke_fiifi": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32()], [ValType.f64()]), self.invoke_fiifi),
                "invoke_fiifii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32()], [ValType.f64()]), self.invoke_fiifii),
                "invoke_fiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.f64()]), self.invoke_fiii),
                "invoke_fiiif": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64()], [ValType.f64()]), self.invoke_fiiif),
                "invoke_fiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.f64()]), self.invoke_fiiii),
                "invoke_i": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self.invoke_i),
                "invoke_ifi": Func(self.store, FuncType([ValType.i32(),ValType.f64(),ValType.i32()], [ValType.i32()]), self.invoke_ifi),
                "invoke_ii": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_ii),
                "invoke_iifii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iifii),
                "invoke_iii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iii),
                "invoke_iiifi": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32()], [ValType.i32()]), self.invoke_iiifi),
                "invoke_iiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiii),
                "invoke_iiiifii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiiifii),
                "invoke_iiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiiii),
                "invoke_iiiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiiiii),
                "invoke_iiiiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiiiiii),
                "invoke_iiiiiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiiiiiii),
                "invoke_iiiiiiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiiiiiiii),
                "invoke_iiiiiiiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiiiiiiiii),
                "invoke_iiiiiiiiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiiiiiiiiii),
                "invoke_v": Func(self.store, FuncType([ValType.i32()], []), self.invoke_v),
                "invoke_vi": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self.invoke_vi),
                "invoke_vidiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_vidiii),
                "invoke_vifffi": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.f64(),ValType.f64(),ValType.f64(),ValType.i32()], []), self.invoke_vifffi),
                "invoke_vifi": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32()], []), self.invoke_vifi),
                "invoke_vifii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32()], []), self.invoke_vifii),
                "invoke_vii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_vii),
                "invoke_viidi": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32()], []), self.invoke_viidi),
                "invoke_viidii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32()], []), self.invoke_viidii),
                "invoke_viiff": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.f64()], []), self.invoke_viiff),
                "invoke_viiffi": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.f64(),ValType.i32()], []), self.invoke_viiffi),
                "invoke_viifi": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32()], []), self.invoke_viifi),
                "invoke_viifii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32()], []), self.invoke_viifii),
                "invoke_viii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viii),
                "invoke_viiif": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64()], []), self.invoke_viiif),
                "invoke_viiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viiii),
                "invoke_viiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viiiii),
                "invoke_viiiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viiiiii),
                "invoke_viiiiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viiiiiii),
                "invoke_viiiiiiifddfii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.f64(),ValType.f64(),ValType.f64(),ValType.i32(),ValType.i32()], []), self.invoke_viiiiiiifddfii),
                "invoke_viiiiiiiffffii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.f64(),ValType.f64(),ValType.f64(),ValType.i32(),ValType.i32()], []), self.invoke_viiiiiiiffffii),
                "invoke_viiiiiiifiifii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32()], []), self.invoke_viiiiiiifiifii),
                "invoke_viiiiiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viiiiiiii),
                "invoke_viiiiiiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viiiiiiiii),
                "invoke_viiiiiiiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viiiiiiiiii),
                "_ES_AddEventHandler": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._ES_AddEventHandler),
                "_ES_Close": Func(self.store, FuncType([ValType.i32()], []), self._ES_Close),
                "_ES_Create": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._ES_Create),
                "_ES_IsSupported": Func(self.store, FuncType([], [ValType.i32()]), self._ES_IsSupported),
                "_ES_Release": Func(self.store, FuncType([ValType.i32()], []), self._ES_Release),
                "_GetInputFieldSelectionEnd": Func(self.store, FuncType([], [ValType.i32()]), self._GetInputFieldSelectionEnd),
                "_GetInputFieldSelectionStart": Func(self.store, FuncType([], [ValType.i32()]), self._GetInputFieldSelectionStart),
                "_GetInputFieldValue": Func(self.store, FuncType([], [ValType.i32()]), self._GetInputFieldValue),
                "_HideInputField": Func(self.store, FuncType([], []), self._HideInputField),
                "_IsInputFieldActive": Func(self.store, FuncType([], [ValType.i32()]), self._IsInputFieldActive),
                "_JS_Cursor_SetImage": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._JS_Cursor_SetImage),
                "_JS_Cursor_SetShow": Func(self.store, FuncType([ValType.i32()], []), self._JS_Cursor_SetShow),
                "_JS_Eval_ClearInterval": Func(self.store, FuncType([ValType.i32()], []), self._JS_Eval_ClearInterval),
                "_JS_Eval_OpenURL": Func(self.store, FuncType([ValType.i32()], []), self._JS_Eval_OpenURL),
                "_JS_Eval_SetInterval": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_Eval_SetInterval),
                "_JS_FileSystem_Initialize": Func(self.store, FuncType([], []), self._JS_FileSystem_Initialize),
                "_JS_FileSystem_Sync": Func(self.store, FuncType([], []), self._JS_FileSystem_Sync),
                "_JS_Log_Dump": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._JS_Log_Dump),
                "_JS_Log_StackTrace": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._JS_Log_StackTrace),
                "_JS_Sound_Create_Channel": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_Sound_Create_Channel),
                "_JS_Sound_GetLength": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._JS_Sound_GetLength),
                "_JS_Sound_GetLoadState": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._JS_Sound_GetLoadState),
                "_JS_Sound_Init": Func(self.store, FuncType([], []), self._JS_Sound_Init),
                "_JS_Sound_Load": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_Sound_Load),
                "_JS_Sound_Load_PCM": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_Sound_Load_PCM),
                "_JS_Sound_Play": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.f64(),ValType.f64()], []), self._JS_Sound_Play),
                "_JS_Sound_ReleaseInstance": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._JS_Sound_ReleaseInstance),
                "_JS_Sound_ResumeIfNeeded": Func(self.store, FuncType([], []), self._JS_Sound_ResumeIfNeeded),
                "_JS_Sound_Set3D": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._JS_Sound_Set3D),
                "_JS_Sound_SetListenerOrientation": Func(self.store, FuncType([ValType.f64(),ValType.f64(),ValType.f64(),ValType.f64(),ValType.f64(),ValType.f64()], []), self._JS_Sound_SetListenerOrientation),
                "_JS_Sound_SetListenerPosition": Func(self.store, FuncType([ValType.f64(),ValType.f64(),ValType.f64()], []), self._JS_Sound_SetListenerPosition),
                "_JS_Sound_SetLoop": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._JS_Sound_SetLoop),
                "_JS_Sound_SetLoopPoints": Func(self.store, FuncType([ValType.i32(),ValType.f64(),ValType.f64()], []), self._JS_Sound_SetLoopPoints),
                "_JS_Sound_SetPaused": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._JS_Sound_SetPaused),
                "_JS_Sound_SetPitch": Func(self.store, FuncType([ValType.i32(),ValType.f64()], []), self._JS_Sound_SetPitch),
                "_JS_Sound_SetPosition": Func(self.store, FuncType([ValType.i32(),ValType.f64(),ValType.f64(),ValType.f64()], []), self._JS_Sound_SetPosition),
                "_JS_Sound_SetVolume": Func(self.store, FuncType([ValType.i32(),ValType.f64()], []), self._JS_Sound_SetVolume),
                "_JS_Sound_Stop": Func(self.store, FuncType([ValType.i32(),ValType.f64()], []), self._JS_Sound_Stop),
                "_JS_SystemInfo_GetBrowserName": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_SystemInfo_GetBrowserName),
                "_JS_SystemInfo_GetBrowserVersionString": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_SystemInfo_GetBrowserVersionString),
                "_JS_SystemInfo_GetCanvasClientSize": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._JS_SystemInfo_GetCanvasClientSize),
                "_JS_SystemInfo_GetDocumentURL": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_SystemInfo_GetDocumentURL),
                "_JS_SystemInfo_GetGPUInfo": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_SystemInfo_GetGPUInfo),
                "_JS_SystemInfo_GetLanguage": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_SystemInfo_GetLanguage),
                "_JS_SystemInfo_GetMemory": Func(self.store, FuncType([], [ValType.i32()]), self._JS_SystemInfo_GetMemory),
                "_JS_SystemInfo_GetOS": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_SystemInfo_GetOS),
                "_JS_SystemInfo_GetPreferredDevicePixelRatio": Func(self.store, FuncType([], [ValType.f64()]), self._JS_SystemInfo_GetPreferredDevicePixelRatio),
                "_JS_SystemInfo_GetScreenSize": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._JS_SystemInfo_GetScreenSize),
                "_JS_SystemInfo_GetStreamingAssetsURL": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_SystemInfo_GetStreamingAssetsURL),
                "_JS_SystemInfo_HasCursorLock": Func(self.store, FuncType([], [ValType.i32()]), self._JS_SystemInfo_HasCursorLock),
                "_JS_SystemInfo_HasFullscreen": Func(self.store, FuncType([], [ValType.i32()]), self._JS_SystemInfo_HasFullscreen),
                "_JS_SystemInfo_HasWebGL": Func(self.store, FuncType([], [ValType.i32()]), self._JS_SystemInfo_HasWebGL),
                "_JS_SystemInfo_IsMobile": Func(self.store, FuncType([], [ValType.i32()]), self._JS_SystemInfo_IsMobile),
                "_JS_Video_CanPlayFormat": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._JS_Video_CanPlayFormat),
                "_JS_Video_Create": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._JS_Video_Create),
                "_JS_Video_Destroy": Func(self.store, FuncType([ValType.i32()], []), self._JS_Video_Destroy),
                "_JS_Video_Duration": Func(self.store, FuncType([ValType.i32()], [ValType.f64()]), self._JS_Video_Duration),
                "_JS_Video_EnableAudioTrack": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._JS_Video_EnableAudioTrack),
                "_JS_Video_GetAudioLanguageCode": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_Video_GetAudioLanguageCode),
                "_JS_Video_GetNumAudioTracks": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._JS_Video_GetNumAudioTracks),
                "_JS_Video_Height": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._JS_Video_Height),
                "_JS_Video_IsPlaying": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._JS_Video_IsPlaying),
                "_JS_Video_IsReady": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._JS_Video_IsReady),
                "_JS_Video_Pause": Func(self.store, FuncType([ValType.i32()], []), self._JS_Video_Pause),
                "_JS_Video_Play": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._JS_Video_Play),
                "_JS_Video_Seek": Func(self.store, FuncType([ValType.i32(),ValType.f64()], []), self._JS_Video_Seek),
                "_JS_Video_SetEndedHandler": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._JS_Video_SetEndedHandler),
                "_JS_Video_SetErrorHandler": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._JS_Video_SetErrorHandler),
                "_JS_Video_SetLoop": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._JS_Video_SetLoop),
                "_JS_Video_SetMute": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._JS_Video_SetMute),
                "_JS_Video_SetPlaybackRate": Func(self.store, FuncType([ValType.i32(),ValType.f64()], []), self._JS_Video_SetPlaybackRate),
                "_JS_Video_SetReadyHandler": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._JS_Video_SetReadyHandler),
                "_JS_Video_SetSeekedOnceHandler": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._JS_Video_SetSeekedOnceHandler),
                "_JS_Video_SetVolume": Func(self.store, FuncType([ValType.i32(),ValType.f64()], []), self._JS_Video_SetVolume),
                "_JS_Video_Time": Func(self.store, FuncType([ValType.i32()], [ValType.f64()]), self._JS_Video_Time),
                "_JS_Video_UpdateToTexture": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_Video_UpdateToTexture),
                "_JS_Video_Width": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._JS_Video_Width),
                "_JS_WebCamVideo_CanPlay": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._JS_WebCamVideo_CanPlay),
                "_JS_WebCamVideo_GetDeviceName": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_WebCamVideo_GetDeviceName),
                "_JS_WebCamVideo_GetNativeHeight": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._JS_WebCamVideo_GetNativeHeight),
                "_JS_WebCamVideo_GetNativeWidth": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._JS_WebCamVideo_GetNativeWidth),
                "_JS_WebCamVideo_GetNumDevices": Func(self.store, FuncType([], [ValType.i32()]), self._JS_WebCamVideo_GetNumDevices),
                "_JS_WebCamVideo_GrabFrame": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._JS_WebCamVideo_GrabFrame),
                "_JS_WebCamVideo_Start": Func(self.store, FuncType([ValType.i32()], []), self._JS_WebCamVideo_Start),
                "_JS_WebCamVideo_Stop": Func(self.store, FuncType([ValType.i32()], []), self._JS_WebCamVideo_Stop),
                "_JS_WebCam_IsSupported": Func(self.store, FuncType([], [ValType.i32()]), self._JS_WebCam_IsSupported),
                "_JS_WebRequest_Abort": Func(self.store, FuncType([ValType.i32()], []), self._JS_WebRequest_Abort),
                "_JS_WebRequest_Create": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_WebRequest_Create),
                "_JS_WebRequest_GetResponseHeaders": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._JS_WebRequest_GetResponseHeaders),
                "_JS_WebRequest_Release": Func(self.store, FuncType([ValType.i32()], []), self._JS_WebRequest_Release),
                "_JS_WebRequest_Send": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._JS_WebRequest_Send),
                "_JS_WebRequest_SetProgressHandler": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._JS_WebRequest_SetProgressHandler),
                "_JS_WebRequest_SetRequestHeader": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._JS_WebRequest_SetRequestHeader),
                "_JS_WebRequest_SetResponseHandler": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._JS_WebRequest_SetResponseHandler),
                "_JS_WebRequest_SetTimeout": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._JS_WebRequest_SetTimeout),
                "_NativeCall": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._NativeCall),
                "_SetInputFieldSelection": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._SetInputFieldSelection),
                "_ShowInputField": Func(self.store, FuncType([ValType.i32()], []), self._ShowInputField),
                "_WS_Close": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._WS_Close),
                "_WS_Create": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._WS_Create),
                "_WS_GetBufferedAmount": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._WS_GetBufferedAmount),
                "_WS_GetState": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._WS_GetState),
                "_WS_Release": Func(self.store, FuncType([ValType.i32()], []), self._WS_Release),
                "_WS_Send_Binary": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._WS_Send_Binary),
                "_WS_Send_String": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._WS_Send_String),
                "_XHR_Abort": Func(self.store, FuncType([ValType.i32()], []), self._XHR_Abort),
                "_XHR_Create": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._XHR_Create),
                "_XHR_GetResponseHeaders": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._XHR_GetResponseHeaders),
                "_XHR_GetStatusLine": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._XHR_GetStatusLine),
                "_XHR_Release": Func(self.store, FuncType([ValType.i32()], []), self._XHR_Release),
                "_XHR_Send": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._XHR_Send),
                "_XHR_SetLoglevel": Func(self.store, FuncType([ValType.i32()], []), self._XHR_SetLoglevel),
                "_XHR_SetProgressHandler": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._XHR_SetProgressHandler),
                "_XHR_SetRequestHeader": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._XHR_SetRequestHeader),
                "_XHR_SetResponseHandler": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._XHR_SetResponseHandler),
                "_XHR_SetTimeout": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._XHR_SetTimeout),
                "_buildEnvironment": Func(self.store, FuncType([ValType.i32()], []), self._buildEnvironment),
                "_cxa_allocate_exception": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._cxa_allocate_exception),
                "_cxa_begin_catch": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._cxa_begin_catch),
                "_cxa_end_catch": Func(self.store, FuncType([], []), self._cxa_end_catch),
                "_cxa_find_matching_catch_2": Func(self.store, FuncType([], [ValType.i32()]), self._cxa_find_matching_catch_2),
                "_cxa_find_matching_catch_3": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._cxa_find_matching_catch_3),
                "_cxa_find_matching_catch_4": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._cxa_find_matching_catch_4),
                "_cxa_free_exception": Func(self.store, FuncType([ValType.i32()], []), self._cxa_free_exception),
                "_cxa_pure_virtual": Func(self.store, FuncType([], []), self._cxa_pure_virtual),
                "_cxa_rethrow": Func(self.store, FuncType([], []), self._cxa_rethrow),
                "_cxa_throw": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._cxa_throw),
                "_lock": Func(self.store, FuncType([ValType.i32()], []), self._lock),
                "_map_file": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._map_file),
                "_resumeException": Func(self.store, FuncType([ValType.i32()], []), self._resumeException),
                "_setErrNo": Func(self.store, FuncType([ValType.i32()], []), self._setErrNo),
                "_syscall10": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall10),
                "_syscall102": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall102),
                "_syscall122": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall122),
                "_syscall140": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall140),
                "_syscall142": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall142),
                "_syscall145": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall145),
                "_syscall146": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall146),
                "_syscall15": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall15),
                "_syscall168": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall168),
                "_syscall183": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall183),
                "_syscall192": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall192),
                "_syscall193": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall193),
                "_syscall194": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall194),
                "_syscall195": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall195),
                "_syscall196": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall196),
                "_syscall197": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall197),
                "_syscall199": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall199),
                "_syscall220": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall220),
                "_syscall221": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall221),
                "_syscall268": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall268),
                "_syscall3": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall3),
                "_syscall33": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall33),
                "_syscall38": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall38),
                "_syscall39": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall39),
                "_syscall4": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall4),
                "_syscall40": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall40),
                "_syscall42": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall42),
                "_syscall5": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall5),
                "_syscall54": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall54),
                "_syscall6": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall6),
                "_syscall63": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall63),
                "_syscall77": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall77),
                "_syscall85": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall85),
                "_syscall91": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._syscall91),
                "_unlock": Func(self.store, FuncType([ValType.i32()], []), self._unlock),
                "_abort": Func(self.store, FuncType([], []), self._abort),
                "_atexit": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._atexit),
                "_clock": Func(self.store, FuncType([], [ValType.i32()]), self._clock),
                "_clock_getres": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._clock_getres),
                "_clock_gettime": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._clock_gettime),
                "_difftime": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.f64()]), self._difftime),
                "_dlclose": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._dlclose),
                "_dlopen": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._dlopen),
                "_dlsym": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._dlsym),
                "_emscripten_asm_const_i": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._emscripten_asm_const_i),
                "_emscripten_asm_const_sync_on_main_thread_i": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._emscripten_asm_const_sync_on_main_thread_i),
                "_emscripten_cancel_main_loop": Func(self.store, FuncType([], []), self._emscripten_cancel_main_loop),
                "_emscripten_exit_fullscreen": Func(self.store, FuncType([], [ValType.i32()]), self._emscripten_exit_fullscreen),
                "_emscripten_exit_pointerlock": Func(self.store, FuncType([], [ValType.i32()]), self._emscripten_exit_pointerlock),
                "_emscripten_get_canvas_element_size": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_get_canvas_element_size),
                "_emscripten_get_fullscreen_status": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._emscripten_get_fullscreen_status),
                "_emscripten_get_gamepad_status": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_get_gamepad_status),
                "_emscripten_get_main_loop_timing": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._emscripten_get_main_loop_timing),
                "_emscripten_get_now": Func(self.store, FuncType([], [ValType.f64()]), self._emscripten_get_now),
                "_emscripten_get_num_gamepads": Func(self.store, FuncType([], [ValType.i32()]), self._emscripten_get_num_gamepads),
                "_emscripten_has_threading_support": Func(self.store, FuncType([], [ValType.i32()]), self._emscripten_has_threading_support),
                "_emscripten_html5_remove_all_event_listeners": Func(self.store, FuncType([], []), self._emscripten_html5_remove_all_event_listeners),
                "_emscripten_is_webgl_context_lost": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._emscripten_is_webgl_context_lost),
                "_emscripten_log": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._emscripten_log),
                "_emscripten_longjmp": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._emscripten_longjmp),
                "_emscripten_memcpy_big": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_memcpy_big),
                "_emscripten_num_logical_cores": Func(self.store, FuncType([], [ValType.i32()]), self._emscripten_num_logical_cores),
                "_emscripten_request_fullscreen": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_request_fullscreen),
                "_emscripten_request_pointerlock": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_request_pointerlock),
                "_emscripten_set_blur_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_blur_callback_on_thread),
                "_emscripten_set_canvas_element_size": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_canvas_element_size),
                "_emscripten_set_dblclick_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_dblclick_callback_on_thread),
                "_emscripten_set_devicemotion_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_devicemotion_callback_on_thread),
                "_emscripten_set_deviceorientation_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_deviceorientation_callback_on_thread),
                "_emscripten_set_focus_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_focus_callback_on_thread),
                "_emscripten_set_fullscreenchange_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_fullscreenchange_callback_on_thread),
                "_emscripten_set_gamepadconnected_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_gamepadconnected_callback_on_thread),
                "_emscripten_set_gamepaddisconnected_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_gamepaddisconnected_callback_on_thread),
                "_emscripten_set_keydown_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_keydown_callback_on_thread),
                "_emscripten_set_keypress_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_keypress_callback_on_thread),
                "_emscripten_set_keyup_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_keyup_callback_on_thread),
                "_emscripten_set_main_loop": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._emscripten_set_main_loop),
                "_emscripten_set_main_loop_timing": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_main_loop_timing),
                "_emscripten_set_mousedown_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_mousedown_callback_on_thread),
                "_emscripten_set_mousemove_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_mousemove_callback_on_thread),
                "_emscripten_set_mouseup_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_mouseup_callback_on_thread),
                "_emscripten_set_touchcancel_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_touchcancel_callback_on_thread),
                "_emscripten_set_touchend_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_touchend_callback_on_thread),
                "_emscripten_set_touchmove_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_touchmove_callback_on_thread),
                "_emscripten_set_touchstart_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_touchstart_callback_on_thread),
                "_emscripten_set_wheel_callback_on_thread": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_set_wheel_callback_on_thread),
                "_emscripten_webgl_create_context": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_webgl_create_context),
                "_emscripten_webgl_destroy_context": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._emscripten_webgl_destroy_context),
                "_emscripten_webgl_enable_extension": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._emscripten_webgl_enable_extension),
                "_emscripten_webgl_get_current_context": Func(self.store, FuncType([], [ValType.i32()]), self._emscripten_webgl_get_current_context),
                "_emscripten_webgl_init_context_attributes": Func(self.store, FuncType([ValType.i32()], []), self._emscripten_webgl_init_context_attributes),
                "_emscripten_webgl_make_context_current": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._emscripten_webgl_make_context_current),
                "_exit": Func(self.store, FuncType([ValType.i32()], []), self._exit),
                "_flock": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._flock),
                "_getaddrinfo": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._getaddrinfo),
                "_getenv": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._getenv),
                "_gethostbyaddr": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._gethostbyaddr),
                "_gethostbyname": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._gethostbyname),
                "_getnameinfo": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._getnameinfo),
                "_getpagesize": Func(self.store, FuncType([], [ValType.i32()]), self._getpagesize),
                "_getpwuid": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._getpwuid),
                "_gettimeofday": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._gettimeofday),
                "_glActiveTexture": Func(self.store, FuncType([ValType.i32()], []), self._glActiveTexture),
                "_glAttachShader": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glAttachShader),
                "_glBeginQuery": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glBeginQuery),
                "_glBeginTransformFeedback": Func(self.store, FuncType([ValType.i32()], []), self._glBeginTransformFeedback),
                "_glBindAttribLocation": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glBindAttribLocation),
                "_glBindBuffer": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glBindBuffer),
                "_glBindBufferBase": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glBindBufferBase),
                "_glBindBufferRange": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glBindBufferRange),
                "_glBindFramebuffer": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glBindFramebuffer),
                "_glBindRenderbuffer": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glBindRenderbuffer),
                "_glBindSampler": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glBindSampler),
                "_glBindTexture": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glBindTexture),
                "_glBindTransformFeedback": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glBindTransformFeedback),
                "_glBindVertexArray": Func(self.store, FuncType([ValType.i32()], []), self._glBindVertexArray),
                "_glBlendEquation": Func(self.store, FuncType([ValType.i32()], []), self._glBlendEquation),
                "_glBlendEquationSeparate": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glBlendEquationSeparate),
                "_glBlendFuncSeparate": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glBlendFuncSeparate),
                "_glBlitFramebuffer": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glBlitFramebuffer),
                "_glBufferData": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glBufferData),
                "_glBufferSubData": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glBufferSubData),
                "_glCheckFramebufferStatus": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._glCheckFramebufferStatus),
                "_glClear": Func(self.store, FuncType([ValType.i32()], []), self._glClear),
                "_glClearBufferfi": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32()], []), self._glClearBufferfi),
                "_glClearBufferfv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glClearBufferfv),
                "_glClearBufferuiv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glClearBufferuiv),
                "_glClearColor": Func(self.store, FuncType([ValType.f64(),ValType.f64(),ValType.f64(),ValType.f64()], []), self._glClearColor),
                "_glClearDepthf": Func(self.store, FuncType([ValType.f64()], []), self._glClearDepthf),
                "_glClearStencil": Func(self.store, FuncType([ValType.i32()], []), self._glClearStencil),
                "_glColorMask": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glColorMask),
                "_glCompileShader": Func(self.store, FuncType([ValType.i32()], []), self._glCompileShader),
                "_glCompressedTexImage2D": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glCompressedTexImage2D),
                "_glCompressedTexSubImage2D": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glCompressedTexSubImage2D),
                "_glCompressedTexSubImage3D": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glCompressedTexSubImage3D),
                "_glCopyBufferSubData": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glCopyBufferSubData),
                "_glCopyTexImage2D": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glCopyTexImage2D),
                "_glCopyTexSubImage2D": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glCopyTexSubImage2D),
                "_glCreateProgram": Func(self.store, FuncType([], [ValType.i32()]), self._glCreateProgram),
                "_glCreateShader": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._glCreateShader),
                "_glCullFace": Func(self.store, FuncType([ValType.i32()], []), self._glCullFace),
                "_glDeleteBuffers": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glDeleteBuffers),
                "_glDeleteFramebuffers": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glDeleteFramebuffers),
                "_glDeleteProgram": Func(self.store, FuncType([ValType.i32()], []), self._glDeleteProgram),
                "_glDeleteQueries": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glDeleteQueries),
                "_glDeleteRenderbuffers": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glDeleteRenderbuffers),
                "_glDeleteSamplers": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glDeleteSamplers),
                "_glDeleteShader": Func(self.store, FuncType([ValType.i32()], []), self._glDeleteShader),
                "_glDeleteSync": Func(self.store, FuncType([ValType.i32()], []), self._glDeleteSync),
                "_glDeleteTextures": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glDeleteTextures),
                "_glDeleteTransformFeedbacks": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glDeleteTransformFeedbacks),
                "_glDeleteVertexArrays": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glDeleteVertexArrays),
                "_glDepthFunc": Func(self.store, FuncType([ValType.i32()], []), self._glDepthFunc),
                "_glDepthMask": Func(self.store, FuncType([ValType.i32()], []), self._glDepthMask),
                "_glDetachShader": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glDetachShader),
                "_glDisable": Func(self.store, FuncType([ValType.i32()], []), self._glDisable),
                "_glDisableVertexAttribArray": Func(self.store, FuncType([ValType.i32()], []), self._glDisableVertexAttribArray),
                "_glDrawArrays": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glDrawArrays),
                "_glDrawArraysInstanced": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glDrawArraysInstanced),
                "_glDrawBuffers": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glDrawBuffers),
                "_glDrawElements": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glDrawElements),
                "_glDrawElementsInstanced": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glDrawElementsInstanced),
                "_glEnable": Func(self.store, FuncType([ValType.i32()], []), self._glEnable),
                "_glEnableVertexAttribArray": Func(self.store, FuncType([ValType.i32()], []), self._glEnableVertexAttribArray),
                "_glEndQuery": Func(self.store, FuncType([ValType.i32()], []), self._glEndQuery),
                "_glEndTransformFeedback": Func(self.store, FuncType([], []), self._glEndTransformFeedback),
                "_glFenceSync": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._glFenceSync),
                "_glFinish": Func(self.store, FuncType([], []), self._glFinish),
                "_glFlush": Func(self.store, FuncType([], []), self._glFlush),
                "_glFlushMappedBufferRange": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glFlushMappedBufferRange),
                "_glFramebufferRenderbuffer": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glFramebufferRenderbuffer),
                "_glFramebufferTexture2D": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glFramebufferTexture2D),
                "_glFramebufferTextureLayer": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glFramebufferTextureLayer),
                "_glFrontFace": Func(self.store, FuncType([ValType.i32()], []), self._glFrontFace),
                "_glGenBuffers": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glGenBuffers),
                "_glGenFramebuffers": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glGenFramebuffers),
                "_glGenQueries": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glGenQueries),
                "_glGenRenderbuffers": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glGenRenderbuffers),
                "_glGenSamplers": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glGenSamplers),
                "_glGenTextures": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glGenTextures),
                "_glGenTransformFeedbacks": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glGenTransformFeedbacks),
                "_glGenVertexArrays": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glGenVertexArrays),
                "_glGenerateMipmap": Func(self.store, FuncType([ValType.i32()], []), self._glGenerateMipmap),
                "_glGetActiveAttrib": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetActiveAttrib),
                "_glGetActiveUniform": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetActiveUniform),
                "_glGetActiveUniformBlockName": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetActiveUniformBlockName),
                "_glGetActiveUniformBlockiv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetActiveUniformBlockiv),
                "_glGetActiveUniformsiv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetActiveUniformsiv),
                "_glGetAttribLocation": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._glGetAttribLocation),
                "_glGetError": Func(self.store, FuncType([], [ValType.i32()]), self._glGetError),
                "_glGetFramebufferAttachmentParameteriv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetFramebufferAttachmentParameteriv),
                "_glGetIntegeri_v": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetIntegeri_v),
                "_glGetIntegerv": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glGetIntegerv),
                "_glGetInternalformativ": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetInternalformativ),
                "_glGetProgramBinary": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetProgramBinary),
                "_glGetProgramInfoLog": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetProgramInfoLog),
                "_glGetProgramiv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetProgramiv),
                "_glGetRenderbufferParameteriv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetRenderbufferParameteriv),
                "_glGetShaderInfoLog": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetShaderInfoLog),
                "_glGetShaderPrecisionFormat": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetShaderPrecisionFormat),
                "_glGetShaderSource": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetShaderSource),
                "_glGetShaderiv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetShaderiv),
                "_glGetString": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._glGetString),
                "_glGetStringi": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._glGetStringi),
                "_glGetTexParameteriv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetTexParameteriv),
                "_glGetUniformBlockIndex": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._glGetUniformBlockIndex),
                "_glGetUniformIndices": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetUniformIndices),
                "_glGetUniformLocation": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._glGetUniformLocation),
                "_glGetUniformiv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetUniformiv),
                "_glGetVertexAttribiv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glGetVertexAttribiv),
                "_glInvalidateFramebuffer": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glInvalidateFramebuffer),
                "_glIsEnabled": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._glIsEnabled),
                "_glIsVertexArray": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._glIsVertexArray),
                "_glLinkProgram": Func(self.store, FuncType([ValType.i32()], []), self._glLinkProgram),
                "_glMapBufferRange": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._glMapBufferRange),
                "_glPixelStorei": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glPixelStorei),
                "_glPolygonOffset": Func(self.store, FuncType([ValType.f64(),ValType.f64()], []), self._glPolygonOffset),
                "_glProgramBinary": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glProgramBinary),
                "_glProgramParameteri": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glProgramParameteri),
                "_glReadBuffer": Func(self.store, FuncType([ValType.i32()], []), self._glReadBuffer),
                "_glReadPixels": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glReadPixels),
                "_glRenderbufferStorage": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glRenderbufferStorage),
                "_glRenderbufferStorageMultisample": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glRenderbufferStorageMultisample),
                "_glSamplerParameteri": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glSamplerParameteri),
                "_glScissor": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glScissor),
                "_glShaderSource": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glShaderSource),
                "_glStencilFuncSeparate": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glStencilFuncSeparate),
                "_glStencilMask": Func(self.store, FuncType([ValType.i32()], []), self._glStencilMask),
                "_glStencilOpSeparate": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glStencilOpSeparate),
                "_glTexImage2D": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glTexImage2D),
                "_glTexImage3D": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glTexImage3D),
                "_glTexParameterf": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.f64()], []), self._glTexParameterf),
                "_glTexParameteri": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glTexParameteri),
                "_glTexParameteriv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glTexParameteriv),
                "_glTexStorage2D": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glTexStorage2D),
                "_glTexStorage3D": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glTexStorage3D),
                "_glTexSubImage2D": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glTexSubImage2D),
                "_glTexSubImage3D": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glTexSubImage3D),
                "_glTransformFeedbackVaryings": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glTransformFeedbackVaryings),
                "_glUniform1fv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniform1fv),
                "_glUniform1i": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glUniform1i),
                "_glUniform1iv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniform1iv),
                "_glUniform1uiv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniform1uiv),
                "_glUniform2fv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniform2fv),
                "_glUniform2iv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniform2iv),
                "_glUniform2uiv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniform2uiv),
                "_glUniform3fv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniform3fv),
                "_glUniform3iv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniform3iv),
                "_glUniform3uiv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniform3uiv),
                "_glUniform4fv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniform4fv),
                "_glUniform4iv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniform4iv),
                "_glUniform4uiv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniform4uiv),
                "_glUniformBlockBinding": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniformBlockBinding),
                "_glUniformMatrix3fv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniformMatrix3fv),
                "_glUniformMatrix4fv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glUniformMatrix4fv),
                "_glUnmapBuffer": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._glUnmapBuffer),
                "_glUseProgram": Func(self.store, FuncType([ValType.i32()], []), self._glUseProgram),
                "_glValidateProgram": Func(self.store, FuncType([ValType.i32()], []), self._glValidateProgram),
                "_glVertexAttrib4f": Func(self.store, FuncType([ValType.i32(),ValType.f64(),ValType.f64(),ValType.f64(),ValType.f64()], []), self._glVertexAttrib4f),
                "_glVertexAttrib4fv": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._glVertexAttrib4fv),
                "_glVertexAttribIPointer": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glVertexAttribIPointer),
                "_glVertexAttribPointer": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glVertexAttribPointer),
                "_glViewport": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self._glViewport),
                "_gmtime": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._gmtime),
                "_inet_addr": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._inet_addr),
                "_llvm_eh_typeid_for": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._llvm_eh_typeid_for),
                "_llvm_exp2_f32": Func(self.store, FuncType([ValType.f64()], [ValType.f64()]), self._llvm_exp2_f32),
                "_llvm_log10_f32": Func(self.store, FuncType([ValType.f64()], [ValType.f64()]), self._llvm_log10_f32),
                "_llvm_log10_f64": Func(self.store, FuncType([ValType.f64()], [ValType.f64()]), self._llvm_log10_f64),
                "_llvm_log2_f32": Func(self.store, FuncType([ValType.f64()], [ValType.f64()]), self._llvm_log2_f32),
                "_llvm_trap": Func(self.store, FuncType([], []), self._llvm_trap),
                "_llvm_trunc_f32": Func(self.store, FuncType([ValType.f64()], [ValType.f64()]), self._llvm_trunc_f32),
                "_localtime": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._localtime),
                "_longjmp": Func(self.store, FuncType([ValType.i32(),ValType.i32()], []), self._longjmp),
                "_mktime": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._mktime),
                "_pthread_cond_destroy": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._pthread_cond_destroy),
                "_pthread_cond_init": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._pthread_cond_init),
                "_pthread_cond_timedwait": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._pthread_cond_timedwait),
                "_pthread_cond_wait": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._pthread_cond_wait),
                "_pthread_getspecific": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._pthread_getspecific),
                "_pthread_key_create": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._pthread_key_create),
                "_pthread_key_delete": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._pthread_key_delete),
                "_pthread_mutex_destroy": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._pthread_mutex_destroy),
                "_pthread_mutex_init": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._pthread_mutex_init),
                "_pthread_mutexattr_destroy": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._pthread_mutexattr_destroy),
                "_pthread_mutexattr_init": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._pthread_mutexattr_init),
                "_pthread_mutexattr_setprotocol": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._pthread_mutexattr_setprotocol),
                "_pthread_mutexattr_settype": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._pthread_mutexattr_settype),
                "_pthread_once": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._pthread_once),
                "_pthread_setspecific": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._pthread_setspecific),
                "_sched_yield": Func(self.store, FuncType([], [ValType.i32()]), self._sched_yield),
                "_setenv": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._setenv),
                "_sigaction": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._sigaction),
                "_sigemptyset": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._sigemptyset),
                "_strftime": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._strftime),
                "_sysconf": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._sysconf),
                "_time": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._time),
                "_unsetenv": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self._unsetenv),
                "_utime": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self._utime),
                "f64_rem": Func(self.store, FuncType([ValType.f64(),ValType.f64()], [ValType.f64()]), self.f64_rem),
                "invoke_iiiiij": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiiiij),
                "invoke_iiiijii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiiijii),
                "invoke_iiiijjii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiiijjii),
                "invoke_iiiji": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiiji),
                "invoke_iiijiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiijiii),
                "invoke_iij": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iij),
                "invoke_iiji": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iiji),
                "invoke_iijii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_iijii),
                "invoke_ijii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_ijii),
                "invoke_j": Func(self.store, FuncType([ValType.i32()], [ValType.i32()]), self.invoke_j),
                "invoke_jdi": Func(self.store, FuncType([ValType.i32(),ValType.f64(),ValType.i32()], [ValType.i32()]), self.invoke_jdi),
                "invoke_ji": Func(self.store, FuncType([ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_ji),
                "invoke_jii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_jii),
                "invoke_jiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_jiii),
                "invoke_jiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_jiiii),
                "invoke_jiiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_jiiiii),
                "invoke_jiiiiiiiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_jiiiiiiiiii),
                "invoke_jiiij": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_jiiij),
                "invoke_jiiji": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_jiiji),
                "invoke_jiji": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_jiji),
                "invoke_jijii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_jijii),
                "invoke_jijiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_jijiii),
                "invoke_jijj": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_jijj),
                "invoke_jji": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self.invoke_jji),
                "invoke_viiiiiiifjjfii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.f64(),ValType.i32(),ValType.i32()], []), self.invoke_viiiiiiifjjfii),
                "invoke_viiiijiiii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viiiijiiii),
                "invoke_viiij": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viiij),
                "invoke_viiiji": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viiiji),
                "invoke_viij": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viij),
                "invoke_viiji": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viiji),
                "invoke_viijji": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viijji),
                "invoke_viji": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_viji),
                "invoke_vijii": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], []), self.invoke_vijii),
                "_atomic_fetch_add_8": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._atomic_fetch_add_8),
                "_glClientWaitSync": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32(),ValType.i32()], [ValType.i32()]), self._glClientWaitSync),
                # "log": Func(self.store, FuncType([ValType.i32()], []), self.log),
                # "log2": Func(self.store, FuncType([ValType.i32(),ValType.i32(),ValType.i32()], []), self.log2),
        }}

    def export_wasm_func(self):
        self.__growWasmMemory = partial(self.instance.exports(self.store)["__growWasmMemory"], self.store)
        self.stackAlloc = partial(self.instance.exports(self.store)["stackAlloc"], self.store)
        self.stackSave = partial(self.instance.exports(self.store)["stackSave"], self.store)
        self.stackRestore = partial(self.instance.exports(self.store)["stackRestore"], self.store)
        self.establishStackSpace = partial(self.instance.exports(self.store)["establishStackSpace"], self.store)
        self.setThrew = partial(self.instance.exports(self.store)["setThrew"], self.store)
        self.setTempRet0 = partial(self.instance.exports(self.store)["setTempRet0"], self.store)
        self.getTempRet0 = partial(self.instance.exports(self.store)["getTempRet0"], self.store)
        self.__GLOBAL__sub_I_AIScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_AIScriptingClasses_cpp"], self.store)
        self.___cxx_global_var_init = partial(self.instance.exports(self.store)["___cxx_global_var_init"], self.store)
        self._pthread_mutex_unlock = partial(self.instance.exports(self.store)["_pthread_mutex_unlock"], self.store)
        self.runPostSets = partial(self.instance.exports(self.store)["runPostSets"], self.store)
        self.__GLOBAL__sub_I_AccessibilityScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_AccessibilityScriptingClasses_cpp"], self.store)
        self.__GLOBAL__sub_I_AndroidJNIScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_AndroidJNIScriptingClasses_cpp"], self.store)
        self.__GLOBAL__sub_I_AnimationScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_AnimationScriptingClasses_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_Animation_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Animation_1_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_Animation_3_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Animation_3_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_Animation_6_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Animation_6_cpp"], self.store)
        self.__GLOBAL__sub_I_Avatar_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Avatar_cpp"], self.store)
        self.__GLOBAL__sub_I_ConstraintManager_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_ConstraintManager_cpp"], self.store)
        self.__GLOBAL__sub_I_AnimationClip_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_AnimationClip_cpp"], self.store)
        self.__GLOBAL__sub_I_AssetBundleScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_AssetBundleScriptingClasses_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_AssetBundle_Public_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_AssetBundle_Public_0_cpp"], self.store)
        self.__GLOBAL__sub_I_AudioScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_AudioScriptingClasses_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Video_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Video_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_Audio_Public_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Audio_Public_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_Audio_Public_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Audio_Public_1_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_Audio_Public_3_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Audio_Public_3_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_Audio_Public_ScriptBindings_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Audio_Public_ScriptBindings_1_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_Audio_Public_sound_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Audio_Public_sound_0_cpp"], self.store)
        self.__GLOBAL__sub_I_ClothScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_ClothScriptingClasses_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_Cloth_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Cloth_0_cpp"], self.store)
        self.___cxx_global_var_init_18 = partial(self.instance.exports(self.store)["___cxx_global_var_init_18"], self.store)
        self.__GLOBAL__sub_I_nvcloth_src_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_nvcloth_src_0_cpp"], self.store)
        self.__GLOBAL__sub_I_nvcloth_src_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_nvcloth_src_1_cpp"], self.store)
        self.__GLOBAL__sub_I_SwInterCollision_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_SwInterCollision_cpp"], self.store)
        self.__GLOBAL__sub_I_SwSolverKernel_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_SwSolverKernel_cpp"], self.store)
        self.__GLOBAL__sub_I_artifacts_WebGL_codegenerator_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_artifacts_WebGL_codegenerator_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_GfxDevice_opengles_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_GfxDevice_opengles_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_VirtualFileSystem_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_VirtualFileSystem_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Input_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Input_0_cpp"], self.store)
        self.__GLOBAL__sub_I_GfxDeviceNull_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_GfxDeviceNull_cpp"], self.store)
        self.__GLOBAL__sub_I_External_ProphecySDK_BlitOperations_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_External_ProphecySDK_BlitOperations_1_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_2D_Renderer_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_2D_Renderer_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_2D_Sorting_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_2D_Sorting_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_2D_SpriteAtlas_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_2D_SpriteAtlas_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Allocator_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Allocator_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Allocator_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Allocator_2_cpp"], self.store)
        self.___cxx_global_var_init_7 = partial(self.instance.exports(self.store)["___cxx_global_var_init_7"], self.store)
        self.__GLOBAL__sub_I_Runtime_Application_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Application_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_BaseClasses_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_BaseClasses_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_BaseClasses_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_BaseClasses_1_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_BaseClasses_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_BaseClasses_2_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_BaseClasses_3_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_BaseClasses_3_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Burst_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Burst_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Camera_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Camera_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Camera_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Camera_1_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Camera_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Camera_2_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Camera_3_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Camera_3_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Camera_4_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Camera_4_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Camera_5_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Camera_5_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Camera_6_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Camera_6_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Camera_7_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Camera_7_cpp"], self.store)
        self.__GLOBAL__sub_I_Shadows_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Shadows_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Camera_Culling_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Camera_Culling_0_cpp"], self.store)
        self.__GLOBAL__sub_I_GUITexture_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_GUITexture_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Camera_RenderLoops_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Camera_RenderLoops_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Camera_RenderLoops_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Camera_RenderLoops_2_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Containers_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Containers_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Core_Callbacks_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Core_Callbacks_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_File_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_File_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Geometry_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Geometry_2_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Graphics_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_0_cpp"], self.store)
        self.___cxx_global_var_init_98 = partial(self.instance.exports(self.store)["___cxx_global_var_init_98"], self.store)
        self.__GLOBAL__sub_I_Runtime_Graphics_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_1_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Graphics_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_2_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Graphics_4_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_4_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Graphics_5_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_5_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Graphics_6_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_6_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Graphics_8_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_8_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Graphics_10_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_10_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Graphics_11_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_11_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Graphics_Billboard_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_Billboard_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Graphics_LOD_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_LOD_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Graphics_Mesh_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_Mesh_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Graphics_Mesh_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_Mesh_1_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Graphics_Mesh_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_Mesh_2_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Graphics_Mesh_4_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_Mesh_4_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Graphics_Mesh_5_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_Mesh_5_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Graphics_ScriptableRenderLoop_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Graphics_ScriptableRenderLoop_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Interfaces_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Interfaces_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Interfaces_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Interfaces_1_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Interfaces_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Interfaces_2_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Jobs_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Jobs_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Jobs_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Jobs_1_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Jobs_Internal_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Jobs_Internal_1_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Jobs_ScriptBindings_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Jobs_ScriptBindings_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Math_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Math_2_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Math_Random_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Math_Random_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Misc_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Misc_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Misc_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Misc_2_cpp"], self.store)
        self.___cxx_global_var_init_131 = partial(self.instance.exports(self.store)["___cxx_global_var_init_131"], self.store)
        self.__GLOBAL__sub_I_Runtime_Misc_4_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Misc_4_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Misc_5_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Misc_5_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_PreloadManager_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_PreloadManager_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Profiler_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Profiler_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Profiler_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Profiler_2_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Profiler_ScriptBindings_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Profiler_ScriptBindings_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_SceneManager_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_SceneManager_0_cpp"], self.store)
        self.___cxx_global_var_init_8100 = partial(self.instance.exports(self.store)["___cxx_global_var_init_8100"], self.store)
        self.__GLOBAL__sub_I_Runtime_Shaders_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Shaders_1_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Shaders_3_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Shaders_3_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Shaders_4_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Shaders_4_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Shaders_ShaderImpl_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Shaders_ShaderImpl_2_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Transform_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Transform_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Transform_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Transform_1_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Utilities_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Utilities_2_cpp"], self.store)
        self.___cxx_global_var_init_2_9504 = partial(self.instance.exports(self.store)["___cxx_global_var_init_2_9504"], self.store)
        self.__GLOBAL__sub_I_Runtime_Utilities_5_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Utilities_5_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Utilities_6_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Utilities_6_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Utilities_7_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Utilities_7_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Utilities_9_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Utilities_9_cpp"], self.store)
        self.__GLOBAL__sub_I_AssetBundleFileSystem_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_AssetBundleFileSystem_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Modules_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Modules_0_cpp"], self.store)
        self.___cxx_global_var_init_13 = partial(self.instance.exports(self.store)["___cxx_global_var_init_13"], self.store)
        self.___cxx_global_var_init_14 = partial(self.instance.exports(self.store)["___cxx_global_var_init_14"], self.store)
        self.___cxx_global_var_init_15 = partial(self.instance.exports(self.store)["___cxx_global_var_init_15"], self.store)
        self.__GLOBAL__sub_I_Modules_Profiler_Public_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Profiler_Public_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_Profiler_Runtime_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Profiler_Runtime_1_cpp"], self.store)
        self.__GLOBAL__sub_I_UnsafeUtility_bindings_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_UnsafeUtility_bindings_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_GfxDevice_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_GfxDevice_1_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_GfxDevice_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_GfxDevice_2_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_GfxDevice_3_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_GfxDevice_3_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_GfxDevice_4_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_GfxDevice_4_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_GfxDevice_5_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_GfxDevice_5_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_PluginInterface_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_PluginInterface_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Director_Core_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Director_Core_1_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_ScriptingBackend_Il2Cpp_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_ScriptingBackend_Il2Cpp_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Scripting_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Scripting_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Scripting_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Scripting_1_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Scripting_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Scripting_2_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Scripting_3_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Scripting_3_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Mono_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Mono_2_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Mono_SerializationBackend_DirectMemoryAccess_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Mono_SerializationBackend_DirectMemoryAccess_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Mono_SerializationBackend_DirectMemoryAccess_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Mono_SerializationBackend_DirectMemoryAccess_1_cpp"], self.store)
        self.__GLOBAL__sub_I_TemplateInstantiations_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_TemplateInstantiations_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Scripting_APIUpdating_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Scripting_APIUpdating_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Serialize_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Serialize_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Serialize_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Serialize_1_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Serialize_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Serialize_2_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Serialize_TransferFunctions_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Serialize_TransferFunctions_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Runtime_Serialize_TransferFunctions_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Runtime_Serialize_TransferFunctions_1_cpp"], self.store)
        self.__GLOBAL__sub_I_PlatformDependent_WebGL_Source_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_PlatformDependent_WebGL_Source_0_cpp"], self.store)
        self.__GLOBAL__sub_I_PlatformDependent_WebGL_Source_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_PlatformDependent_WebGL_Source_2_cpp"], self.store)
        self.__GLOBAL__sub_I_LogAssert_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_LogAssert_cpp"], self.store)
        self.__GLOBAL__sub_I_Shader_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Shader_cpp"], self.store)
        self.__GLOBAL__sub_I_Transform_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Transform_cpp"], self.store)
        self.__GLOBAL__sub_I_PlatformDependent_WebGL_External_baselib_builds_Source_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_PlatformDependent_WebGL_External_baselib_builds_Source_0_cpp"], self.store)
        self._SendMessage = partial(self.instance.exports(self.store)["_SendMessage"], self.store)
        self._SendMessageString = partial(self.instance.exports(self.store)["_SendMessageString"], self.store)
        self._SetFullscreen = partial(self.instance.exports(self.store)["_SetFullscreen"], self.store)
        self._main = partial(self.instance.exports(self.store)["_main"], self.store)
        self.__GLOBAL__sub_I_Modules_DSPGraph_Public_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_DSPGraph_Public_1_cpp"], self.store)
        self.__GLOBAL__sub_I_DirectorScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_DirectorScriptingClasses_cpp"], self.store)
        self.__GLOBAL__sub_I_GridScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_GridScriptingClasses_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_Grid_Public_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Grid_Public_0_cpp"], self.store)
        self.__GLOBAL__sub_I_IMGUIScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_IMGUIScriptingClasses_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_IMGUI_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_IMGUI_0_cpp"], self.store)
        self.___cxx_global_var_init_22 = partial(self.instance.exports(self.store)["___cxx_global_var_init_22"], self.store)
        self.__GLOBAL__sub_I_Modules_IMGUI_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_IMGUI_1_cpp"], self.store)
        self.___cxx_global_var_init_3893 = partial(self.instance.exports(self.store)["___cxx_global_var_init_3893"], self.store)
        self.__GLOBAL__sub_I_InputLegacyScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_InputLegacyScriptingClasses_cpp"], self.store)
        self.__GLOBAL__sub_I_InputScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_InputScriptingClasses_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_Input_Private_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Input_Private_0_cpp"], self.store)
        self.__GLOBAL__sub_I_ParticleSystemScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_ParticleSystemScriptingClasses_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_ParticleSystem_Modules_3_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_ParticleSystem_Modules_3_cpp"], self.store)
        self.__GLOBAL__sub_I_ParticleSystemRenderer_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_ParticleSystemRenderer_cpp"], self.store)
        self.__GLOBAL__sub_I_ShapeModule_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_ShapeModule_cpp"], self.store)
        self.__GLOBAL__sub_I_Physics2DScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Physics2DScriptingClasses_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_Physics2D_Public_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Physics2D_Public_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_Physics2D_Public_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Physics2D_Public_1_cpp"], self.store)
        self.__GLOBAL__sub_I_PhysicsScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_PhysicsScriptingClasses_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_Physics_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Physics_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_Physics_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Physics_1_cpp"], self.store)
        self.__GLOBAL__sub_I_PhysicsQuery_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_PhysicsQuery_cpp"], self.store)
        self.__GLOBAL__sub_I_SubsystemsScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_SubsystemsScriptingClasses_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_Subsystems_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Subsystems_0_cpp"], self.store)
        self.__GLOBAL__sub_I_TerrainScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_TerrainScriptingClasses_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_Terrain_Public_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Terrain_Public_0_cpp"], self.store)
        self.___cxx_global_var_init_69 = partial(self.instance.exports(self.store)["___cxx_global_var_init_69"], self.store)
        self.__GLOBAL__sub_I_Modules_Terrain_Public_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Terrain_Public_1_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_Terrain_Public_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Terrain_Public_2_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_Terrain_Public_3_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Terrain_Public_3_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_Terrain_VR_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Terrain_VR_0_cpp"], self.store)
        self.__GLOBAL__sub_I_TextCoreScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_TextCoreScriptingClasses_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_TextCore_Native_FontEngine_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_TextCore_Native_FontEngine_0_cpp"], self.store)
        self.__GLOBAL__sub_I_TextRenderingScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_TextRenderingScriptingClasses_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_TextRendering_Public_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_TextRendering_Public_0_cpp"], self.store)
        self.__GLOBAL__sub_I_TilemapScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_TilemapScriptingClasses_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_Tilemap_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Tilemap_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_Tilemap_Public_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Tilemap_Public_0_cpp"], self.store)
        self.__GLOBAL__sub_I_UIElementsScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_UIElementsScriptingClasses_cpp"], self.store)
        self.__GLOBAL__sub_I_External_Yoga_Yoga_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_External_Yoga_Yoga_0_cpp"], self.store)
        self.__GLOBAL__sub_I_UIScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_UIScriptingClasses_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_UI_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_UI_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_UI_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_UI_1_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_UI_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_UI_2_cpp"], self.store)
        self.__GLOBAL__sub_I_umbra_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_umbra_cpp"], self.store)
        self.__GLOBAL__sub_I_UnityAnalyticsScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_UnityAnalyticsScriptingClasses_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_UnityAnalytics_Dispatcher_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_UnityAnalytics_Dispatcher_0_cpp"], self.store)
        self.__GLOBAL__sub_I_UnityAdsSettings_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_UnityAdsSettings_cpp"], self.store)
        self.__GLOBAL__sub_I_UnityWebRequestScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_UnityWebRequestScriptingClasses_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_UnityWebRequest_Public_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_UnityWebRequest_Public_0_cpp"], self.store)
        self.__GLOBAL__sub_I_VFXScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_VFXScriptingClasses_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_VFX_Public_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_VFX_Public_1_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_VFX_Public_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_VFX_Public_2_cpp"], self.store)
        self.__GLOBAL__sub_I_VRScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_VRScriptingClasses_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_VR_2_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_VR_2_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_VR_PluginInterface_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_VR_PluginInterface_0_cpp"], self.store)
        self.__GLOBAL__sub_I_VideoScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_VideoScriptingClasses_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_Video_Public_Base_0_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_Video_Public_Base_0_cpp"], self.store)
        self.__GLOBAL__sub_I_Wind_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Wind_cpp"], self.store)
        self.__GLOBAL__sub_I_XRScriptingClasses_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_XRScriptingClasses_cpp"], self.store)
        self.__GLOBAL__sub_I_Modules_XR_Subsystems_Input_Public_1_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Modules_XR_Subsystems_Input_Public_1_cpp"], self.store)
        self.__GLOBAL__sub_I_Lump_libil2cpp_os_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Lump_libil2cpp_os_cpp"], self.store)
        self.__GLOBAL__sub_I_Il2CppCodeRegistration_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Il2CppCodeRegistration_cpp"], self.store)
        self.__GLOBAL__sub_I_Lump_libil2cpp_vm_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Lump_libil2cpp_vm_cpp"], self.store)
        self.__GLOBAL__sub_I_Lump_libil2cpp_metadata_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Lump_libil2cpp_metadata_cpp"], self.store)
        self.__GLOBAL__sub_I_Lump_libil2cpp_utils_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Lump_libil2cpp_utils_cpp"], self.store)
        self.__GLOBAL__sub_I_Lump_libil2cpp_gc_cpp = partial(self.instance.exports(self.store)["__GLOBAL__sub_I_Lump_libil2cpp_gc_cpp"], self.store)
        self._malloc = partial(self.instance.exports(self.store)["_malloc"], self.store)
        self._free = partial(self.instance.exports(self.store)["_free"], self.store)
        self._realloc = partial(self.instance.exports(self.store)["_realloc"], self.store)
        self._memalign = partial(self.instance.exports(self.store)["_memalign"], self.store)
        self.___errno_location = partial(self.instance.exports(self.store)["___errno_location"], self.store)
        self._strlen = partial(self.instance.exports(self.store)["_strlen"], self.store)
        self._ntohs = partial(self.instance.exports(self.store)["_ntohs"], self.store)
        self._htonl = partial(self.instance.exports(self.store)["_htonl"], self.store)
        self.___emscripten_environ_constructor = partial(self.instance.exports(self.store)["___emscripten_environ_constructor"], self.store)
        self.__get_tzname = partial(self.instance.exports(self.store)["__get_tzname"], self.store)
        self.__get_daylight = partial(self.instance.exports(self.store)["__get_daylight"], self.store)
        self.__get_timezone = partial(self.instance.exports(self.store)["__get_timezone"], self.store)
        self._get_environ = partial(self.instance.exports(self.store)["__get_environ"], self.store)
        self._cxa_can_catch = partial(self.instance.exports(self.store)["___cxa_can_catch"], self.store)
        self._cxa_is_pointer_type = partial(self.instance.exports(self.store)["___cxa_is_pointer_type"], self.store)
        self._i64Add = partial(self.instance.exports(self.store)["_i64Add"], self.store)
        self._saveSetjmp = partial(self.instance.exports(self.store)["_saveSetjmp"], self.store)
        self._testSetjmp = partial(self.instance.exports(self.store)["_testSetjmp"], self.store)
        self._llvm_bswap_i32 = partial(self.instance.exports(self.store)["_llvm_bswap_i32"], self.store)
        self._llvm_ctlz_i64 = partial(self.instance.exports(self.store)["_llvm_ctlz_i64"], self.store)
        self._llvm_ctpop_i32 = partial(self.instance.exports(self.store)["_llvm_ctpop_i32"], self.store)
        self._llvm_maxnum_f64 = partial(self.instance.exports(self.store)["_llvm_maxnum_f64"], self.store)
        self._llvm_minnum_f32 = partial(self.instance.exports(self.store)["_llvm_minnum_f32"], self.store)
        self._llvm_round_f32 = partial(self.instance.exports(self.store)["_llvm_round_f32"], self.store)
        self._memcpy = partial(self.instance.exports(self.store)["_memcpy"], self.store)
        self._memmove = partial(self.instance.exports(self.store)["_memmove"], self.store)
        self._memset = partial(self.instance.exports(self.store)["_memset"], self.store)
        self._rintf = partial(self.instance.exports(self.store)["_rintf"], self.store)
        self._sbrk = partial(self.instance.exports(self.store)["_sbrk"], self.store)
        self.dynCall_dddi = partial(self.instance.exports(self.store)["dynCall_dddi"], self.store)
        self.dynCall_ddi = partial(self.instance.exports(self.store)["dynCall_ddi"], self.store)
        self.dynCall_ddidi = partial(self.instance.exports(self.store)["dynCall_ddidi"], self.store)
        self.dynCall_ddii = partial(self.instance.exports(self.store)["dynCall_ddii"], self.store)
        self.dynCall_ddiii = partial(self.instance.exports(self.store)["dynCall_ddiii"], self.store)
        self.dynCall_di = partial(self.instance.exports(self.store)["dynCall_di"], self.store)
        self.dynCall_diddi = partial(self.instance.exports(self.store)["dynCall_diddi"], self.store)
        self.dynCall_didi = partial(self.instance.exports(self.store)["dynCall_didi"], self.store)
        self.dynCall_dii = partial(self.instance.exports(self.store)["dynCall_dii"], self.store)
        self.dynCall_diidi = partial(self.instance.exports(self.store)["dynCall_diidi"], self.store)
        self.dynCall_diii = partial(self.instance.exports(self.store)["dynCall_diii"], self.store)
        self.dynCall_diiid = partial(self.instance.exports(self.store)["dynCall_diiid"], self.store)
        self.dynCall_diiii = partial(self.instance.exports(self.store)["dynCall_diiii"], self.store)
        self.dynCall_diiiii = partial(self.instance.exports(self.store)["dynCall_diiiii"], self.store)
        self.dynCall_i = partial(self.instance.exports(self.store)["dynCall_i"], self.store)
        self.dynCall_idddi = partial(self.instance.exports(self.store)["dynCall_idddi"], self.store)
        self.dynCall_iddi = partial(self.instance.exports(self.store)["dynCall_iddi"], self.store)
        self.dynCall_iddii = partial(self.instance.exports(self.store)["dynCall_iddii"], self.store)
        self.dynCall_idi = partial(self.instance.exports(self.store)["dynCall_idi"], self.store)
        self.dynCall_idii = partial(self.instance.exports(self.store)["dynCall_idii"], self.store)
        self.dynCall_idiii = partial(self.instance.exports(self.store)["dynCall_idiii"], self.store)
        self.dynCall_idiiii = partial(self.instance.exports(self.store)["dynCall_idiiii"], self.store)
        self.dynCall_ii = partial(self.instance.exports(self.store)["dynCall_ii"], self.store)
        self.dynCall_iiddi = partial(self.instance.exports(self.store)["dynCall_iiddi"], self.store)
        self.dynCall_iidi = partial(self.instance.exports(self.store)["dynCall_iidi"], self.store)
        self.dynCall_iidii = partial(self.instance.exports(self.store)["dynCall_iidii"], self.store)
        self.dynCall_iidiii = partial(self.instance.exports(self.store)["dynCall_iidiii"], self.store)
        self.dynCall_iii = partial(self.instance.exports(self.store)["dynCall_iii"], self.store)
        self.dynCall_iiiddi = partial(self.instance.exports(self.store)["dynCall_iiiddi"], self.store)
        self.dynCall_iiidi = partial(self.instance.exports(self.store)["dynCall_iiidi"], self.store)
        self.dynCall_iiidii = partial(self.instance.exports(self.store)["dynCall_iiidii"], self.store)
        self.dynCall_iiidiii = partial(self.instance.exports(self.store)["dynCall_iiidiii"], self.store)
        self.dynCall_iiii = partial(self.instance.exports(self.store)["dynCall_iiii"], self.store)
        self.dynCall_iiiii = partial(self.instance.exports(self.store)["dynCall_iiiii"], self.store)
        self.dynCall_iiiiidii = partial(self.instance.exports(self.store)["dynCall_iiiiidii"], self.store)
        self.dynCall_iiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiii"], self.store)
        self.dynCall_iiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiii"], self.store)
        self.dynCall_iiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiii"], self.store)
        self.dynCall_iiiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiiii"], self.store)
        self.dynCall_iiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiiiii"], self.store)
        self.dynCall_iiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiiiiii"], self.store)
        self.dynCall_iiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiiiiiii"], self.store)
        self.dynCall_iiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiiiiiiii"], self.store)
        self.dynCall_iiiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiiiiiiiii"], self.store)
        self.dynCall_iiiiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiiiiiiiiii"], self.store)
        self.dynCall_iiiiiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiiiiiiiiiii"], self.store)
        self.dynCall_iiiiiiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiiiiiiiiiiii"], self.store)
        self.dynCall_iiiiiiiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiiiiiiiiiiiii"], self.store)
        self.dynCall_iiiiiiiiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiiiiiiiiiiiiii"], self.store)
        self.dynCall_iiiiiiiiiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiiiiiiiiiiiiiii"], self.store)
        self.dynCall_iiiiiiiiiiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiiiiiiiiiiiiiiii"], self.store)
        self.dynCall_v = partial(self.instance.exports(self.store)["dynCall_v"], self.store)
        self.dynCall_vd = partial(self.instance.exports(self.store)["dynCall_vd"], self.store)
        self.dynCall_vdi = partial(self.instance.exports(self.store)["dynCall_vdi"], self.store)
        self.dynCall_vi = partial(self.instance.exports(self.store)["dynCall_vi"], self.store)
        self.dynCall_vid = partial(self.instance.exports(self.store)["dynCall_vid"], self.store)
        self.dynCall_vidd = partial(self.instance.exports(self.store)["dynCall_vidd"], self.store)
        self.dynCall_vidddi = partial(self.instance.exports(self.store)["dynCall_vidddi"], self.store)
        self.dynCall_viddi = partial(self.instance.exports(self.store)["dynCall_viddi"], self.store)
        self.dynCall_viddiiii = partial(self.instance.exports(self.store)["dynCall_viddiiii"], self.store)
        self.dynCall_vidi = partial(self.instance.exports(self.store)["dynCall_vidi"], self.store)
        self.dynCall_vidii = partial(self.instance.exports(self.store)["dynCall_vidii"], self.store)
        self.dynCall_vidiii = partial(self.instance.exports(self.store)["dynCall_vidiii"], self.store)
        self.dynCall_vii = partial(self.instance.exports(self.store)["dynCall_vii"], self.store)
        self.dynCall_viid = partial(self.instance.exports(self.store)["dynCall_viid"], self.store)
        self.dynCall_viidd = partial(self.instance.exports(self.store)["dynCall_viidd"], self.store)
        self.dynCall_viidi = partial(self.instance.exports(self.store)["dynCall_viidi"], self.store)
        self.dynCall_viidii = partial(self.instance.exports(self.store)["dynCall_viidii"], self.store)
        self.dynCall_viii = partial(self.instance.exports(self.store)["dynCall_viii"], self.store)
        self.dynCall_viiidi = partial(self.instance.exports(self.store)["dynCall_viiidi"], self.store)
        self.dynCall_viiii = partial(self.instance.exports(self.store)["dynCall_viiii"], self.store)
        self.dynCall_viiiiddi = partial(self.instance.exports(self.store)["dynCall_viiiiddi"], self.store)
        self.dynCall_viiiii = partial(self.instance.exports(self.store)["dynCall_viiiii"], self.store)
        self.dynCall_viiiiii = partial(self.instance.exports(self.store)["dynCall_viiiiii"], self.store)
        self.dynCall_viiiiiii = partial(self.instance.exports(self.store)["dynCall_viiiiiii"], self.store)
        self.dynCall_viiiiiiii = partial(self.instance.exports(self.store)["dynCall_viiiiiiii"], self.store)
        self.dynCall_viiiiiiiii = partial(self.instance.exports(self.store)["dynCall_viiiiiiiii"], self.store)
        self.dynCall_viiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_viiiiiiiiii"], self.store)
        self.dynCall_viiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_viiiiiiiiiii"], self.store)
        self.dynCall_viiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_viiiiiiiiiiii"], self.store)
        self.dynCall_viiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_viiiiiiiiiiiii"], self.store)
        self.dynCall_viiiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_viiiiiiiiiiiiii"], self.store)
        self.dynCall_viiiiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_viiiiiiiiiiiiiii"], self.store)
        self.dynCall_viiiiiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_viiiiiiiiiiiiiiii"], self.store)
        self.dynCall_viiiiiiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_viiiiiiiiiiiiiiiii"], self.store)
        self.dynCall_viiiiiiiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_viiiiiiiiiiiiiiiiii"], self.store)
        self._SendMessageFloat = partial(self.instance.exports(self.store)["_SendMessageFloat"], self.store)
        self.dynCall_dfi = partial(self.instance.exports(self.store)["dynCall_dfi"], self.store)
        self.dynCall_dij = partial(self.instance.exports(self.store)["dynCall_dij"], self.store)
        self.dynCall_diji = partial(self.instance.exports(self.store)["dynCall_diji"], self.store)
        self.dynCall_dji = partial(self.instance.exports(self.store)["dynCall_dji"], self.store)
        self.dynCall_f = partial(self.instance.exports(self.store)["dynCall_f"], self.store)
        self.dynCall_fdi = partial(self.instance.exports(self.store)["dynCall_fdi"], self.store)
        self.dynCall_ff = partial(self.instance.exports(self.store)["dynCall_ff"], self.store)
        self.dynCall_fff = partial(self.instance.exports(self.store)["dynCall_fff"], self.store)
        self.dynCall_ffff = partial(self.instance.exports(self.store)["dynCall_ffff"], self.store)
        self.dynCall_fffff = partial(self.instance.exports(self.store)["dynCall_fffff"], self.store)
        self.dynCall_ffffffi = partial(self.instance.exports(self.store)["dynCall_ffffffi"], self.store)
        self.dynCall_fffffi = partial(self.instance.exports(self.store)["dynCall_fffffi"], self.store)
        self.dynCall_ffffi = partial(self.instance.exports(self.store)["dynCall_ffffi"], self.store)
        self.dynCall_ffffii = partial(self.instance.exports(self.store)["dynCall_ffffii"], self.store)
        self.dynCall_fffi = partial(self.instance.exports(self.store)["dynCall_fffi"], self.store)
        self.dynCall_fffiffffffi = partial(self.instance.exports(self.store)["dynCall_fffiffffffi"], self.store)
        self.dynCall_fffifffffi = partial(self.instance.exports(self.store)["dynCall_fffifffffi"], self.store)
        self.dynCall_fffifffi = partial(self.instance.exports(self.store)["dynCall_fffifffi"], self.store)
        self.dynCall_fffifi = partial(self.instance.exports(self.store)["dynCall_fffifi"], self.store)
        self.dynCall_fffii = partial(self.instance.exports(self.store)["dynCall_fffii"], self.store)
        self.dynCall_fffiii = partial(self.instance.exports(self.store)["dynCall_fffiii"], self.store)
        self.dynCall_ffi = partial(self.instance.exports(self.store)["dynCall_ffi"], self.store)
        self.dynCall_fi = partial(self.instance.exports(self.store)["dynCall_fi"], self.store)
        self.dynCall_fidi = partial(self.instance.exports(self.store)["dynCall_fidi"], self.store)
        self.dynCall_fif = partial(self.instance.exports(self.store)["dynCall_fif"], self.store)
        self.dynCall_fiff = partial(self.instance.exports(self.store)["dynCall_fiff"], self.store)
        self.dynCall_fiffffi = partial(self.instance.exports(self.store)["dynCall_fiffffi"], self.store)
        self.dynCall_fifffi = partial(self.instance.exports(self.store)["dynCall_fifffi"], self.store)
        self.dynCall_fiffi = partial(self.instance.exports(self.store)["dynCall_fiffi"], self.store)
        self.dynCall_fifi = partial(self.instance.exports(self.store)["dynCall_fifi"], self.store)
        self.dynCall_fifii = partial(self.instance.exports(self.store)["dynCall_fifii"], self.store)
        self.dynCall_fii = partial(self.instance.exports(self.store)["dynCall_fii"], self.store)
        self.dynCall_fiif = partial(self.instance.exports(self.store)["dynCall_fiif"], self.store)
        self.dynCall_fiifdi = partial(self.instance.exports(self.store)["dynCall_fiifdi"], self.store)
        self.dynCall_fiiffffi = partial(self.instance.exports(self.store)["dynCall_fiiffffi"], self.store)
        self.dynCall_fiiffi = partial(self.instance.exports(self.store)["dynCall_fiiffi"], self.store)
        self.dynCall_fiifi = partial(self.instance.exports(self.store)["dynCall_fiifi"], self.store)
        self.dynCall_fiifii = partial(self.instance.exports(self.store)["dynCall_fiifii"], self.store)
        self.dynCall_fiifji = partial(self.instance.exports(self.store)["dynCall_fiifji"], self.store)
        self.dynCall_fiii = partial(self.instance.exports(self.store)["dynCall_fiii"], self.store)
        self.dynCall_fiiif = partial(self.instance.exports(self.store)["dynCall_fiiif"], self.store)
        self.dynCall_fiiii = partial(self.instance.exports(self.store)["dynCall_fiiii"], self.store)
        self.dynCall_fiiiif = partial(self.instance.exports(self.store)["dynCall_fiiiif"], self.store)
        self.dynCall_fiiiii = partial(self.instance.exports(self.store)["dynCall_fiiiii"], self.store)
        self.dynCall_fiiiiii = partial(self.instance.exports(self.store)["dynCall_fiiiiii"], self.store)
        self.dynCall_fiiiiiifiifif = partial(self.instance.exports(self.store)["dynCall_fiiiiiifiifif"], self.store)
        self.dynCall_fiiiiiifiiiif = partial(self.instance.exports(self.store)["dynCall_fiiiiiifiiiif"], self.store)
        self.dynCall_fji = partial(self.instance.exports(self.store)["dynCall_fji"], self.store)
        self.dynCall_iffffffi = partial(self.instance.exports(self.store)["dynCall_iffffffi"], self.store)
        self.dynCall_iffffi = partial(self.instance.exports(self.store)["dynCall_iffffi"], self.store)
        self.dynCall_ifffi = partial(self.instance.exports(self.store)["dynCall_ifffi"], self.store)
        self.dynCall_iffi = partial(self.instance.exports(self.store)["dynCall_iffi"], self.store)
        self.dynCall_ifi = partial(self.instance.exports(self.store)["dynCall_ifi"], self.store)
        self.dynCall_ifii = partial(self.instance.exports(self.store)["dynCall_ifii"], self.store)
        self.dynCall_ifiii = partial(self.instance.exports(self.store)["dynCall_ifiii"], self.store)
        self.dynCall_ifiiii = partial(self.instance.exports(self.store)["dynCall_ifiiii"], self.store)
        self.dynCall_iif = partial(self.instance.exports(self.store)["dynCall_iif"], self.store)
        self.dynCall_iiff = partial(self.instance.exports(self.store)["dynCall_iiff"], self.store)
        self.dynCall_iifff = partial(self.instance.exports(self.store)["dynCall_iifff"], self.store)
        self.dynCall_iiffffffiii = partial(self.instance.exports(self.store)["dynCall_iiffffffiii"], self.store)
        self.dynCall_iiffffi = partial(self.instance.exports(self.store)["dynCall_iiffffi"], self.store)
        self.dynCall_iiffffiii = partial(self.instance.exports(self.store)["dynCall_iiffffiii"], self.store)
        self.dynCall_iifffi = partial(self.instance.exports(self.store)["dynCall_iifffi"], self.store)
        self.dynCall_iifffiii = partial(self.instance.exports(self.store)["dynCall_iifffiii"], self.store)
        self.dynCall_iiffi = partial(self.instance.exports(self.store)["dynCall_iiffi"], self.store)
        self.dynCall_iiffifiii = partial(self.instance.exports(self.store)["dynCall_iiffifiii"], self.store)
        self.dynCall_iiffii = partial(self.instance.exports(self.store)["dynCall_iiffii"], self.store)
        self.dynCall_iiffiii = partial(self.instance.exports(self.store)["dynCall_iiffiii"], self.store)
        self.dynCall_iiffiiiii = partial(self.instance.exports(self.store)["dynCall_iiffiiiii"], self.store)
        self.dynCall_iifi = partial(self.instance.exports(self.store)["dynCall_iifi"], self.store)
        self.dynCall_iifii = partial(self.instance.exports(self.store)["dynCall_iifii"], self.store)
        self.dynCall_iifiifii = partial(self.instance.exports(self.store)["dynCall_iifiifii"], self.store)
        self.dynCall_iifiifiii = partial(self.instance.exports(self.store)["dynCall_iifiifiii"], self.store)
        self.dynCall_iifiii = partial(self.instance.exports(self.store)["dynCall_iifiii"], self.store)
        self.dynCall_iifiiii = partial(self.instance.exports(self.store)["dynCall_iifiiii"], self.store)
        self.dynCall_iifiiiii = partial(self.instance.exports(self.store)["dynCall_iifiiiii"], self.store)
        self.dynCall_iifiiiiii = partial(self.instance.exports(self.store)["dynCall_iifiiiiii"], self.store)
        self.dynCall_iiif = partial(self.instance.exports(self.store)["dynCall_iiif"], self.store)
        self.dynCall_iiiffffi = partial(self.instance.exports(self.store)["dynCall_iiiffffi"], self.store)
        self.dynCall_iiifffi = partial(self.instance.exports(self.store)["dynCall_iiifffi"], self.store)
        self.dynCall_iiifffii = partial(self.instance.exports(self.store)["dynCall_iiifffii"], self.store)
        self.dynCall_iiiffi = partial(self.instance.exports(self.store)["dynCall_iiiffi"], self.store)
        self.dynCall_iiiffifiii = partial(self.instance.exports(self.store)["dynCall_iiiffifiii"], self.store)
        self.dynCall_iiiffii = partial(self.instance.exports(self.store)["dynCall_iiiffii"], self.store)
        self.dynCall_iiiffiii = partial(self.instance.exports(self.store)["dynCall_iiiffiii"], self.store)
        self.dynCall_iiifi = partial(self.instance.exports(self.store)["dynCall_iiifi"], self.store)
        self.dynCall_iiififi = partial(self.instance.exports(self.store)["dynCall_iiififi"], self.store)
        self.dynCall_iiififii = partial(self.instance.exports(self.store)["dynCall_iiififii"], self.store)
        self.dynCall_iiififiii = partial(self.instance.exports(self.store)["dynCall_iiififiii"], self.store)
        self.dynCall_iiififiiii = partial(self.instance.exports(self.store)["dynCall_iiififiiii"], self.store)
        self.dynCall_iiifii = partial(self.instance.exports(self.store)["dynCall_iiifii"], self.store)
        self.dynCall_iiifiifii = partial(self.instance.exports(self.store)["dynCall_iiifiifii"], self.store)
        self.dynCall_iiifiifiii = partial(self.instance.exports(self.store)["dynCall_iiifiifiii"], self.store)
        self.dynCall_iiifiifiiii = partial(self.instance.exports(self.store)["dynCall_iiifiifiiii"], self.store)
        self.dynCall_iiifiii = partial(self.instance.exports(self.store)["dynCall_iiifiii"], self.store)
        self.dynCall_iiifiiii = partial(self.instance.exports(self.store)["dynCall_iiifiiii"], self.store)
        self.dynCall_iiifiiiii = partial(self.instance.exports(self.store)["dynCall_iiifiiiii"], self.store)
        self.dynCall_iiiifffffi = partial(self.instance.exports(self.store)["dynCall_iiiifffffi"], self.store)
        self.dynCall_iiiifffffii = partial(self.instance.exports(self.store)["dynCall_iiiifffffii"], self.store)
        self.dynCall_iiiiffffi = partial(self.instance.exports(self.store)["dynCall_iiiiffffi"], self.store)
        self.dynCall_iiiiffi = partial(self.instance.exports(self.store)["dynCall_iiiiffi"], self.store)
        self.dynCall_iiiiffii = partial(self.instance.exports(self.store)["dynCall_iiiiffii"], self.store)
        self.dynCall_iiiifi = partial(self.instance.exports(self.store)["dynCall_iiiifi"], self.store)
        self.dynCall_iiiififi = partial(self.instance.exports(self.store)["dynCall_iiiififi"], self.store)
        self.dynCall_iiiifii = partial(self.instance.exports(self.store)["dynCall_iiiifii"], self.store)
        self.dynCall_iiiifiii = partial(self.instance.exports(self.store)["dynCall_iiiifiii"], self.store)
        self.dynCall_iiiifiiii = partial(self.instance.exports(self.store)["dynCall_iiiifiiii"], self.store)
        self.dynCall_iiiifiiiii = partial(self.instance.exports(self.store)["dynCall_iiiifiiiii"], self.store)
        self.dynCall_iiiiifi = partial(self.instance.exports(self.store)["dynCall_iiiiifi"], self.store)
        self.dynCall_iiiiifii = partial(self.instance.exports(self.store)["dynCall_iiiiifii"], self.store)
        self.dynCall_iiiiifiii = partial(self.instance.exports(self.store)["dynCall_iiiiifiii"], self.store)
        self.dynCall_iiiiifiiiiif = partial(self.instance.exports(self.store)["dynCall_iiiiifiiiiif"], self.store)
        self.dynCall_iiiiiifff = partial(self.instance.exports(self.store)["dynCall_iiiiiifff"], self.store)
        self.dynCall_iiiiiifffiiifiii = partial(self.instance.exports(self.store)["dynCall_iiiiiifffiiifiii"], self.store)
        self.dynCall_iiiiiiffiiiiiiiiiffffiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiffiiiiiiiiiffffiii"], self.store)
        self.dynCall_iiiiiiffiiiiiiiiiffffiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiffiiiiiiiiiffffiiii"], self.store)
        self.dynCall_iiiiiiffiiiiiiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_iiiiiiffiiiiiiiiiiiiiii"], self.store)
        self.dynCall_iiiiiifi = partial(self.instance.exports(self.store)["dynCall_iiiiiifi"], self.store)
        self.dynCall_iiiiiifiif = partial(self.instance.exports(self.store)["dynCall_iiiiiifiif"], self.store)
        self.dynCall_iiiiiifiii = partial(self.instance.exports(self.store)["dynCall_iiiiiifiii"], self.store)
        self.dynCall_iiiiiiifiif = partial(self.instance.exports(self.store)["dynCall_iiiiiiifiif"], self.store)
        self.dynCall_iiiiij = partial(self.instance.exports(self.store)["dynCall_iiiiij"], self.store)
        self.dynCall_iiiiiji = partial(self.instance.exports(self.store)["dynCall_iiiiiji"], self.store)
        self.dynCall_iiiij = partial(self.instance.exports(self.store)["dynCall_iiiij"], self.store)
        self.dynCall_iiiiji = partial(self.instance.exports(self.store)["dynCall_iiiiji"], self.store)
        self.dynCall_iiiijii = partial(self.instance.exports(self.store)["dynCall_iiiijii"], self.store)
        self.dynCall_iiiijiiii = partial(self.instance.exports(self.store)["dynCall_iiiijiiii"], self.store)
        self.dynCall_iiiijjii = partial(self.instance.exports(self.store)["dynCall_iiiijjii"], self.store)
        self.dynCall_iiiijjiiii = partial(self.instance.exports(self.store)["dynCall_iiiijjiiii"], self.store)
        self.dynCall_iiij = partial(self.instance.exports(self.store)["dynCall_iiij"], self.store)
        self.dynCall_iiiji = partial(self.instance.exports(self.store)["dynCall_iiiji"], self.store)
        self.dynCall_iiijii = partial(self.instance.exports(self.store)["dynCall_iiijii"], self.store)
        self.dynCall_iiijiii = partial(self.instance.exports(self.store)["dynCall_iiijiii"], self.store)
        self.dynCall_iiijji = partial(self.instance.exports(self.store)["dynCall_iiijji"], self.store)
        self.dynCall_iiijjii = partial(self.instance.exports(self.store)["dynCall_iiijjii"], self.store)
        self.dynCall_iiijjiii = partial(self.instance.exports(self.store)["dynCall_iiijjiii"], self.store)
        self.dynCall_iiijjiiii = partial(self.instance.exports(self.store)["dynCall_iiijjiiii"], self.store)
        self.dynCall_iij = partial(self.instance.exports(self.store)["dynCall_iij"], self.store)
        self.dynCall_iiji = partial(self.instance.exports(self.store)["dynCall_iiji"], self.store)
        self.dynCall_iijii = partial(self.instance.exports(self.store)["dynCall_iijii"], self.store)
        self.dynCall_iijiii = partial(self.instance.exports(self.store)["dynCall_iijiii"], self.store)
        self.dynCall_iijiiii = partial(self.instance.exports(self.store)["dynCall_iijiiii"], self.store)
        self.dynCall_iijiiiiii = partial(self.instance.exports(self.store)["dynCall_iijiiiiii"], self.store)
        self.dynCall_iijji = partial(self.instance.exports(self.store)["dynCall_iijji"], self.store)
        self.dynCall_iijjii = partial(self.instance.exports(self.store)["dynCall_iijjii"], self.store)
        self.dynCall_iijjiii = partial(self.instance.exports(self.store)["dynCall_iijjiii"], self.store)
        self.dynCall_iijjji = partial(self.instance.exports(self.store)["dynCall_iijjji"], self.store)
        self.dynCall_ij = partial(self.instance.exports(self.store)["dynCall_ij"], self.store)
        self.dynCall_iji = partial(self.instance.exports(self.store)["dynCall_iji"], self.store)
        self.dynCall_ijii = partial(self.instance.exports(self.store)["dynCall_ijii"], self.store)
        self.dynCall_ijiii = partial(self.instance.exports(self.store)["dynCall_ijiii"], self.store)
        self.dynCall_ijiiii = partial(self.instance.exports(self.store)["dynCall_ijiiii"], self.store)
        self.dynCall_ijj = partial(self.instance.exports(self.store)["dynCall_ijj"], self.store)
        self.dynCall_ijji = partial(self.instance.exports(self.store)["dynCall_ijji"], self.store)
        self.dynCall_j = partial(self.instance.exports(self.store)["dynCall_j"], self.store)
        self.dynCall_jdi = partial(self.instance.exports(self.store)["dynCall_jdi"], self.store)
        self.dynCall_jdii = partial(self.instance.exports(self.store)["dynCall_jdii"], self.store)
        self.dynCall_jfi = partial(self.instance.exports(self.store)["dynCall_jfi"], self.store)
        self.dynCall_ji = partial(self.instance.exports(self.store)["dynCall_ji"], self.store)
        self.dynCall_jid = partial(self.instance.exports(self.store)["dynCall_jid"], self.store)
        self.dynCall_jidi = partial(self.instance.exports(self.store)["dynCall_jidi"], self.store)
        self.dynCall_jidii = partial(self.instance.exports(self.store)["dynCall_jidii"], self.store)
        self.dynCall_jii = partial(self.instance.exports(self.store)["dynCall_jii"], self.store)
        self.dynCall_jiii = partial(self.instance.exports(self.store)["dynCall_jiii"], self.store)
        self.dynCall_jiiii = partial(self.instance.exports(self.store)["dynCall_jiiii"], self.store)
        self.dynCall_jiiiii = partial(self.instance.exports(self.store)["dynCall_jiiiii"], self.store)
        self.dynCall_jiiiiii = partial(self.instance.exports(self.store)["dynCall_jiiiiii"], self.store)
        self.dynCall_jiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_jiiiiiiiii"], self.store)
        self.dynCall_jiiiiiiiiii = partial(self.instance.exports(self.store)["dynCall_jiiiiiiiiii"], self.store)
        self.dynCall_jiiij = partial(self.instance.exports(self.store)["dynCall_jiiij"], self.store)
        self.dynCall_jiiji = partial(self.instance.exports(self.store)["dynCall_jiiji"], self.store)
        self.dynCall_jiji = partial(self.instance.exports(self.store)["dynCall_jiji"], self.store)
        self.dynCall_jijii = partial(self.instance.exports(self.store)["dynCall_jijii"], self.store)
        self.dynCall_jijiii = partial(self.instance.exports(self.store)["dynCall_jijiii"], self.store)
        self.dynCall_jijj = partial(self.instance.exports(self.store)["dynCall_jijj"], self.store)
        self.dynCall_jijji = partial(self.instance.exports(self.store)["dynCall_jijji"], self.store)
        self.dynCall_jji = partial(self.instance.exports(self.store)["dynCall_jji"], self.store)
        self.dynCall_jjii = partial(self.instance.exports(self.store)["dynCall_jjii"], self.store)
        self.dynCall_jjji = partial(self.instance.exports(self.store)["dynCall_jjji"], self.store)
        self.dynCall_jjjji = partial(self.instance.exports(self.store)["dynCall_jjjji"], self.store)
        self.dynCall_vf = partial(self.instance.exports(self.store)["dynCall_vf"], self.store)
        self.dynCall_vff = partial(self.instance.exports(self.store)["dynCall_vff"], self.store)
        self.dynCall_vfff = partial(self.instance.exports(self.store)["dynCall_vfff"], self.store)
        self.dynCall_vffff = partial(self.instance.exports(self.store)["dynCall_vffff"], self.store)
        self.dynCall_vfffffffffiiii = partial(self.instance.exports(self.store)["dynCall_vfffffffffiiii"], self.store)
        self.dynCall_vffffi = partial(self.instance.exports(self.store)["dynCall_vffffi"], self.store)
        self.dynCall_vfffi = partial(self.instance.exports(self.store)["dynCall_vfffi"], self.store)
        self.dynCall_vffi = partial(self.instance.exports(self.store)["dynCall_vffi"], self.store)
        self.dynCall_vfi = partial(self.instance.exports(self.store)["dynCall_vfi"], self.store)
        self.dynCall_vfii = partial(self.instance.exports(self.store)["dynCall_vfii"], self.store)
        self.dynCall_vfiii = partial(self.instance.exports(self.store)["dynCall_vfiii"], self.store)
        self.dynCall_vfiiiii = partial(self.instance.exports(self.store)["dynCall_vfiiiii"], self.store)
        self.dynCall_vif = partial(self.instance.exports(self.store)["dynCall_vif"], self.store)
        self.dynCall_viff = partial(self.instance.exports(self.store)["dynCall_viff"], self.store)
        self.dynCall_vifff = partial(self.instance.exports(self.store)["dynCall_vifff"], self.store)
        self.dynCall_viffff = partial(self.instance.exports(self.store)["dynCall_viffff"], self.store)
        self.dynCall_viffffffffffffiiii = partial(self.instance.exports(self.store)["dynCall_viffffffffffffiiii"], self.store)
        self.dynCall_vifffffffi = partial(self.instance.exports(self.store)["dynCall_vifffffffi"], self.store)
        self.dynCall_viffffffi = partial(self.instance.exports(self.store)["dynCall_viffffffi"], self.store)
        self.dynCall_vifffffi = partial(self.instance.exports(self.store)["dynCall_vifffffi"], self.store)
        self.dynCall_viffffi = partial(self.instance.exports(self.store)["dynCall_viffffi"], self.store)
        self.dynCall_viffffii = partial(self.instance.exports(self.store)["dynCall_viffffii"], self.store)
        self.dynCall_viffffiifffiiiiif = partial(self.instance.exports(self.store)["dynCall_viffffiifffiiiiif"], self.store)
        self.dynCall_viffffiii = partial(self.instance.exports(self.store)["dynCall_viffffiii"], self.store)
        self.dynCall_vifffi = partial(self.instance.exports(self.store)["dynCall_vifffi"], self.store)
        self.dynCall_vifffii = partial(self.instance.exports(self.store)["dynCall_vifffii"], self.store)
        self.dynCall_viffi = partial(self.instance.exports(self.store)["dynCall_viffi"], self.store)
        self.dynCall_viffii = partial(self.instance.exports(self.store)["dynCall_viffii"], self.store)
        self.dynCall_viffiifffffiii = partial(self.instance.exports(self.store)["dynCall_viffiifffffiii"], self.store)
        self.dynCall_viffiii = partial(self.instance.exports(self.store)["dynCall_viffiii"], self.store)
        self.dynCall_viffiiifi = partial(self.instance.exports(self.store)["dynCall_viffiiifi"], self.store)
        self.dynCall_viffiiiif = partial(self.instance.exports(self.store)["dynCall_viffiiiif"], self.store)
        self.dynCall_vifi = partial(self.instance.exports(self.store)["dynCall_vifi"], self.store)
        self.dynCall_vififiii = partial(self.instance.exports(self.store)["dynCall_vififiii"], self.store)
        self.dynCall_vifii = partial(self.instance.exports(self.store)["dynCall_vifii"], self.store)
        self.dynCall_vifiii = partial(self.instance.exports(self.store)["dynCall_vifiii"], self.store)
        self.dynCall_vifiiii = partial(self.instance.exports(self.store)["dynCall_vifiiii"], self.store)
        self.dynCall_vifiiiii = partial(self.instance.exports(self.store)["dynCall_vifiiiii"], self.store)
        self.dynCall_viif = partial(self.instance.exports(self.store)["dynCall_viif"], self.store)
        self.dynCall_viiff = partial(self.instance.exports(self.store)["dynCall_viiff"], self.store)
        self.dynCall_viifff = partial(self.instance.exports(self.store)["dynCall_viifff"], self.store)
        self.dynCall_viiffffffffi = partial(self.instance.exports(self.store)["dynCall_viiffffffffi"], self.store)
        self.dynCall_viiffffffffiii = partial(self.instance.exports(self.store)["dynCall_viiffffffffiii"], self.store)
        self.dynCall_viifffffffi = partial(self.instance.exports(self.store)["dynCall_viifffffffi"], self.store)
        self.dynCall_viiffffffi = partial(self.instance.exports(self.store)["dynCall_viiffffffi"], self.store)
        self.dynCall_viifffffi = partial(self.instance.exports(self.store)["dynCall_viifffffi"], self.store)
        self.dynCall_viiffffi = partial(self.instance.exports(self.store)["dynCall_viiffffi"], self.store)
        self.dynCall_viifffi = partial(self.instance.exports(self.store)["dynCall_viifffi"], self.store)
        self.dynCall_viiffi = partial(self.instance.exports(self.store)["dynCall_viiffi"], self.store)
        self.dynCall_viiffifiii = partial(self.instance.exports(self.store)["dynCall_viiffifiii"], self.store)
        self.dynCall_viiffii = partial(self.instance.exports(self.store)["dynCall_viiffii"], self.store)
        self.dynCall_viiffiifi = partial(self.instance.exports(self.store)["dynCall_viiffiifi"], self.store)
        self.dynCall_viiffiifiii = partial(self.instance.exports(self.store)["dynCall_viiffiifiii"], self.store)
        self.dynCall_viiffiiii = partial(self.instance.exports(self.store)["dynCall_viiffiiii"], self.store)
        self.dynCall_viiffiiiii = partial(self.instance.exports(self.store)["dynCall_viiffiiiii"], self.store)
        self.dynCall_viifi = partial(self.instance.exports(self.store)["dynCall_viifi"], self.store)
        self.dynCall_viififii = partial(self.instance.exports(self.store)["dynCall_viififii"], self.store)
        self.dynCall_viififiii = partial(self.instance.exports(self.store)["dynCall_viififiii"], self.store)
        self.dynCall_viifii = partial(self.instance.exports(self.store)["dynCall_viifii"], self.store)
        self.dynCall_viifiii = partial(self.instance.exports(self.store)["dynCall_viifiii"], self.store)
        self.dynCall_viifiiii = partial(self.instance.exports(self.store)["dynCall_viifiiii"], self.store)
        self.dynCall_viiif = partial(self.instance.exports(self.store)["dynCall_viiif"], self.store)
        self.dynCall_viiifffi = partial(self.instance.exports(self.store)["dynCall_viiifffi"], self.store)
        self.dynCall_viiifffiiij = partial(self.instance.exports(self.store)["dynCall_viiifffiiij"], self.store)
        self.dynCall_viiiffi = partial(self.instance.exports(self.store)["dynCall_viiiffi"], self.store)
        self.dynCall_viiiffii = partial(self.instance.exports(self.store)["dynCall_viiiffii"], self.store)
        self.dynCall_viiifi = partial(self.instance.exports(self.store)["dynCall_viiifi"], self.store)
        self.dynCall_viiififfi = partial(self.instance.exports(self.store)["dynCall_viiififfi"], self.store)
        self.dynCall_viiififi = partial(self.instance.exports(self.store)["dynCall_viiififi"], self.store)
        self.dynCall_viiififii = partial(self.instance.exports(self.store)["dynCall_viiififii"], self.store)
        self.dynCall_viiifii = partial(self.instance.exports(self.store)["dynCall_viiifii"], self.store)
        self.dynCall_viiifiii = partial(self.instance.exports(self.store)["dynCall_viiifiii"], self.store)
        self.dynCall_viiifiiiii = partial(self.instance.exports(self.store)["dynCall_viiifiiiii"], self.store)
        self.dynCall_viiiif = partial(self.instance.exports(self.store)["dynCall_viiiif"], self.store)
        self.dynCall_viiiiffffffi = partial(self.instance.exports(self.store)["dynCall_viiiiffffffi"], self.store)
        self.dynCall_viiiifffffi = partial(self.instance.exports(self.store)["dynCall_viiiifffffi"], self.store)
        self.dynCall_viiiiffffii = partial(self.instance.exports(self.store)["dynCall_viiiiffffii"], self.store)
        self.dynCall_viiiifffi = partial(self.instance.exports(self.store)["dynCall_viiiifffi"], self.store)
        self.dynCall_viiiiffiii = partial(self.instance.exports(self.store)["dynCall_viiiiffiii"], self.store)
        self.dynCall_viiiifi = partial(self.instance.exports(self.store)["dynCall_viiiifi"], self.store)
        self.dynCall_viiiififfi = partial(self.instance.exports(self.store)["dynCall_viiiififfi"], self.store)
        self.dynCall_viiiifii = partial(self.instance.exports(self.store)["dynCall_viiiifii"], self.store)
        self.dynCall_viiiifiifi = partial(self.instance.exports(self.store)["dynCall_viiiifiifi"], self.store)
        self.dynCall_viiiifiii = partial(self.instance.exports(self.store)["dynCall_viiiifiii"], self.store)
        self.dynCall_viiiifiiii = partial(self.instance.exports(self.store)["dynCall_viiiifiiii"], self.store)
        self.dynCall_viiiifiiiii = partial(self.instance.exports(self.store)["dynCall_viiiifiiiii"], self.store)
        self.dynCall_viiiifiiiiif = partial(self.instance.exports(self.store)["dynCall_viiiifiiiiif"], self.store)
        self.dynCall_viiiifiiiiiiii = partial(self.instance.exports(self.store)["dynCall_viiiifiiiiiiii"], self.store)
        self.dynCall_viiiiif = partial(self.instance.exports(self.store)["dynCall_viiiiif"], self.store)
        self.dynCall_viiiiiffi = partial(self.instance.exports(self.store)["dynCall_viiiiiffi"], self.store)
        self.dynCall_viiiiiffii = partial(self.instance.exports(self.store)["dynCall_viiiiiffii"], self.store)
        self.dynCall_viiiiifi = partial(self.instance.exports(self.store)["dynCall_viiiiifi"], self.store)
        self.dynCall_viiiiifiii = partial(self.instance.exports(self.store)["dynCall_viiiiifiii"], self.store)
        self.dynCall_viiiiiif = partial(self.instance.exports(self.store)["dynCall_viiiiiif"], self.store)
        self.dynCall_viiiiiifddfiii = partial(self.instance.exports(self.store)["dynCall_viiiiiifddfiii"], self.store)
        self.dynCall_viiiiiiffffiii = partial(self.instance.exports(self.store)["dynCall_viiiiiiffffiii"], self.store)
        self.dynCall_viiiiiifiifiii = partial(self.instance.exports(self.store)["dynCall_viiiiiifiifiii"], self.store)
        self.dynCall_viiiiiifjjfiii = partial(self.instance.exports(self.store)["dynCall_viiiiiifjjfiii"], self.store)
        self.dynCall_viiiiiiifddfii = partial(self.instance.exports(self.store)["dynCall_viiiiiiifddfii"], self.store)
        self.dynCall_viiiiiiiffffii = partial(self.instance.exports(self.store)["dynCall_viiiiiiiffffii"], self.store)
        self.dynCall_viiiiiiifiifii = partial(self.instance.exports(self.store)["dynCall_viiiiiiifiifii"], self.store)
        self.dynCall_viiiiiiifjjfii = partial(self.instance.exports(self.store)["dynCall_viiiiiiifjjfii"], self.store)
        self.dynCall_viiiiiiiiiiifii = partial(self.instance.exports(self.store)["dynCall_viiiiiiiiiiifii"], self.store)
        self.dynCall_viiiiiji = partial(self.instance.exports(self.store)["dynCall_viiiiiji"], self.store)
        self.dynCall_viiiij = partial(self.instance.exports(self.store)["dynCall_viiiij"], self.store)
        self.dynCall_viiiijii = partial(self.instance.exports(self.store)["dynCall_viiiijii"], self.store)
        self.dynCall_viiiijiiii = partial(self.instance.exports(self.store)["dynCall_viiiijiiii"], self.store)
        self.dynCall_viiij = partial(self.instance.exports(self.store)["dynCall_viiij"], self.store)
        self.dynCall_viiiji = partial(self.instance.exports(self.store)["dynCall_viiiji"], self.store)
        self.dynCall_viiijji = partial(self.instance.exports(self.store)["dynCall_viiijji"], self.store)
        self.dynCall_viij = partial(self.instance.exports(self.store)["dynCall_viij"], self.store)
        self.dynCall_viiji = partial(self.instance.exports(self.store)["dynCall_viiji"], self.store)
        self.dynCall_viijii = partial(self.instance.exports(self.store)["dynCall_viijii"], self.store)
        self.dynCall_viijiii = partial(self.instance.exports(self.store)["dynCall_viijiii"], self.store)
        self.dynCall_viijiijiii = partial(self.instance.exports(self.store)["dynCall_viijiijiii"], self.store)
        self.dynCall_viijijii = partial(self.instance.exports(self.store)["dynCall_viijijii"], self.store)
        self.dynCall_viijijiii = partial(self.instance.exports(self.store)["dynCall_viijijiii"], self.store)
        self.dynCall_viijijj = partial(self.instance.exports(self.store)["dynCall_viijijj"], self.store)
        self.dynCall_viijj = partial(self.instance.exports(self.store)["dynCall_viijj"], self.store)
        self.dynCall_viijji = partial(self.instance.exports(self.store)["dynCall_viijji"], self.store)
        self.dynCall_viijjii = partial(self.instance.exports(self.store)["dynCall_viijjii"], self.store)
        self.dynCall_viijjiii = partial(self.instance.exports(self.store)["dynCall_viijjiii"], self.store)
        self.dynCall_viijjji = partial(self.instance.exports(self.store)["dynCall_viijjji"], self.store)
        self.dynCall_vij = partial(self.instance.exports(self.store)["dynCall_vij"], self.store)
        self.dynCall_viji = partial(self.instance.exports(self.store)["dynCall_viji"], self.store)
        self.dynCall_vijii = partial(self.instance.exports(self.store)["dynCall_vijii"], self.store)
        self.dynCall_vijiii = partial(self.instance.exports(self.store)["dynCall_vijiii"], self.store)
        self.dynCall_vijiiii = partial(self.instance.exports(self.store)["dynCall_vijiiii"], self.store)
        self.dynCall_vijiji = partial(self.instance.exports(self.store)["dynCall_vijiji"], self.store)
        self.dynCall_vijijji = partial(self.instance.exports(self.store)["dynCall_vijijji"], self.store)
        self.dynCall_vijji = partial(self.instance.exports(self.store)["dynCall_vijji"], self.store)
        self.dynCall_vijjii = partial(self.instance.exports(self.store)["dynCall_vijjii"], self.store)
        self.dynCall_vijjji = partial(self.instance.exports(self.store)["dynCall_vijjji"], self.store)
        self.dynCall_vji = partial(self.instance.exports(self.store)["dynCall_vji"], self.store)
        self.dynCall_vjii = partial(self.instance.exports(self.store)["dynCall_vjii"], self.store)
        self.dynCall_vjiiii = partial(self.instance.exports(self.store)["dynCall_vjiiii"], self.store)
        self.dynCall_vjji = partial(self.instance.exports(self.store)["dynCall_vjji"], self.store)

    def buffer(self, dtype):
        return np.frombuffer(self.memory.get_buffer_ptr(self.store), dtype=dtype)
    
    @property
    def HEAP8(self):
        return self.buffer(np.int8)
    
    @property
    def HEAP16(self):
        return self.buffer(np.int16)
    
    @property
    def HEAP32(self):
        return self.buffer(np.int32)

    @property
    def HEAP64(self):
        return self.buffer(np.int64)
    
    @property
    def HEAPU8(self):
        return self.buffer(np.uint8)
    
    @property
    def HEAPU16(self):
        return self.buffer(np.uint16)

    @property
    def HEAPU32(self):
        return self.buffer(np.uint32)

    @property
    def HEAPF32(self):
        return self.buffer(np.float32)
    
    @property
    def HEAPF64(self):
        return self.buffer(np.float64)


    
    def lengthBytesUTF8(self, s):
        return len(s.encode('utf-8')) 

    def stringToUTF8(self, s, outPtr, maxBytesToWrite):
        return self.stringToUTF8Array(s, self.HEAPU8, outPtr, maxBytesToWrite)
    
    def stringToUTF8Array(self, s, outU8Array, outIdx, maxBytesToWrite):
        if not (maxBytesToWrite > 0):
            return 0

        utf8_bytes = s.encode('utf-8')
        bytes_to_copy = min(len(utf8_bytes), maxBytesToWrite - 1)  # Leave space for the null terminator

        # Copy the bytes to the output array
        to_be_input= np.frombuffer(utf8_bytes[:bytes_to_copy], dtype=np.uint8) 
        for idx, inp in enumerate(to_be_input, start=outIdx):
            outU8Array[idx] = int(inp)
        # outU8Array[outIdx:outIdx + bytes_to_copy] = np.frombuffer(utf8_bytes[:bytes_to_copy], dtype=np.uint8)
        outU8Array[outIdx + bytes_to_copy] = 0  # Null terminator

        return bytes_to_copy

    def UTF8ToString(self,ptr):
        return UTF8ArrayToString(self.HEAPU8, ptr)

    def Pointer_stringify(self, ptr, length=None):
        if (length == 0 or  not ptr):
            return ""
        hasUtf = 0
        i = 0
        while True:
            t = self.HEAPU8[ptr + i]
            hasUtf |= t
            if t == 0 and not length:
                break
            i += 1
            if length and i == length:
                break

        if not length:
            length = i

        ret = ""
        if hasUtf < 128:
            MAX_CHUNK = 1024
            while (length > 0):
                curr = "".join(chr(self.HEAPU8[ptr + j]) for j in range(min(length, MAX_CHUNK)))
                ret += curr
                ptr += MAX_CHUNK
                length -= MAX_CHUNK
            return ret
        
        return self.UTF8ToString(ptr)

    def allocateUTF8(self, _in):
        size = self.lengthBytesUTF8(_in) + 1
        ret = self._malloc(size)
        if ret:
            self.stringToUTF8Array(_in, self.HEAP8, ret, size)
        return ret

    def allocateUTF8OnStack(self, _in):
        size = self.lengthBytesUTF8(_in) +1
        ret = self.stackAlloc(size)
        self.stringToUTF8Array(_in, self.HEAP8, ret, size)
        return ret

    def alignUp(self, x, multiple):
        if x % multiple > 0:
            x += multiple - (x % multiple)
        return x
    
    def reallocBuffer(self, size):
        PAGE_MULTIPLE = self.WASM_PAGE_SIZE 
        size = self.alignUp(size, PAGE_MULTIPLE)
        oldSize = self.HEAP8.nbytes

        ret = self.memory.grow(self.store, (size - oldSize) // PAGE_MULTIPLE)
        return True
            
    def alignMemory(self, size, factor=16):
        ret = size = math.ceil(size / factor) * factor;
        return ret

    def staticAlloc(self, size):
        ret = self.STATICTOP
        self.STATICTOP = self.STATICTOP + size + 15 & -16
        return ret
    
    def dynamicAlloc(self, size):
        ret = self.HEAP32[self.DYNAMICTOP_PTR >> 2]
        end = (ret + size + 15) & -16
        self.HEAP32[self.DYNAMICTOP_PTR >> 2] = end

        if end >= self.TOTAL_MEMORY:
            success = self.enlargeMemory()
            if not success:
                self.HEAP32[self.DYNAMICTOP_PTR >> 2] = ret
                return 0

        return ret

    def writeAsciiToMemory(self, string, buffer, dontAddNull=False):
        for i in range(len(string)):
            self.HEAP8[buffer] = ord(string[i])
            buffer += 1

        if not dontAddNull:
            self.HEAP8[buffer] = 0

    def getMemory(self, size):
        if not self.staticSealed:
            return self.staticAlloc(size)
        if not self.runtimeInitialized:
            return self.dynamicAlloc(size)
        return self._malloc(size)
    
    def intArrayFromString(self, stringy, dontAddNull=False, length=None):
        # Determine the length of the array (with room for a null terminator unless dontAddNull is True)
        if length and length > 0:
            len_bytes = length
        else:
            len_bytes = self.lengthBytesUTF8(stringy) + 1  # +1 for null terminator

        # Create an array to hold the UTF-8 bytes
        u8array = [0] * len_bytes

        # Convert string to UTF-8 array
        numBytesWritten = self.stringToUTF8Array(stringy, u8array, 0, len(u8array))

        # Optionally remove the null terminator
        if dontAddNull:
            u8array = u8array[:numBytesWritten]

        return u8array

    def setValue(self, ptr, value, type=None, noSafe=False):
        # Default type is "i8"
        type = type or "i8"
        
        # Handle pointers as i32
        if type[-1] == "*":
            type = "i32"
        
        # Perform value assignment based on type
        if type == "i1" or type == "i8":
            self.HEAP8[ptr] = value 
        elif type == "i16":
            self.HEAP16[ptr >> 1] = value
        elif type == "i32":
            self.HEAP32[ptr >> 2] = value
        elif type == "i64":
            # Handle i64 by splitting the value into two 32-bit parts
            tempI64 = [0, 0]
            tempI64[0] = value & 0xFFFFFFFF  # Lower 32 bits
            tempI64[1] = (math.floor(value / 4294967296)) & 0xFFFFFFFF  # Upper 32 bits
            self.HEAP32[ptr >> 2] = tempI64[0]
            self.HEAP32[(ptr + 4) >> 2] = tempI64[1]
        elif type == "float":
            self.HEAPF32[ptr >> 2] = value
        elif type == "double":
            self.HEAPF64[ptr >> 3] = value
        else:
            # Invalid type
            logging.error("invalid type for setValue: " + type)
        
    def getNativeTypeSize(self, type):
        if type in ["i1", "i8"]:
            return 1
        elif type == "i16":
            return 2
        elif type == "i32":
            return 4
        elif type == "i64":
            return 8
        elif type == "float":
            return 4
        elif type == "double":
            return 8
        else:
            if type.endswith("*"):  # Pointer types
                return 4  # Assume 32-bit pointers
            elif type.startswith("i"):  # Types like i16, i64, etc.
                bits = int(type[1:])
                assert(bits % 8 == 0)
                return bits // 8
            else:
                return 0  # Unknown type
            
    def allocate(self, slab, types, allocator=None, ptr=None):        

        if isinstance(slab, int):
            zeroinit = True
            size = slab
        else:
            zeroinit = False
            size = len(slab)
        
        singleType = types if isinstance(types, str) else None
        ret = None
        
        # Determine the allocation strategy
        if allocator == self.ALLOC_NONE:
            ret = ptr
        else:
            # Use the appropriate allocator
            allocators = [self._malloc, self.staticAlloc, self.stackAlloc, self.dynamicAlloc]
            funcidx = self.ALLOC_STATIC if allocator is None else allocator
            ret = allocators[funcidx](max(size, 1 if singleType else len(types)))
        
        # Zero initialize the memory if needed
        if zeroinit:
            stop = ret + (size & ~3)
            ptr = ret
            assert (ret & 3) == 0
            
            while ptr < stop:
                self.HEAP32[ptr // 4] = 0  # Emulate 32-bit zeroing
                ptr += 4
            
            stop = ret + size
            while ptr < stop:
                self.HEAPU8[ptr] = 0  # Emulate byte zeroing
                ptr += 1
            
            return ret
        
        # Handle the single type case for i8
        if singleType == "i8":
            if isinstance(slab, list) or isinstance(slab, np.array):
                self.HEAPU8[ret:ret + len(slab)] = slab
            else:
                self.HEAPU8[ret:ret + len(slab)] = bytearray(slab)
            
            return ret
        
        # General case for allocating types
        i = 0
        previousType = None
        typeSize = 0
        
        while i < size:
            curr = slab[i]
            type = singleType or types[i]
            
            if type == 0:
                i += 1
                continue
            
            if type == "i64":
                type = "i32"  # Handle i64 as i32
            
            self.setValue(ret + i, curr, type)
            
            if previousType != type:
                typeSize = self.getNativeTypeSize(type)
                previousType = type
            
            i += typeSize
        
        return ret
    
    
    def _AT_INIT(self):
        logging.info("AT_INIT >> __GLOBAL__sub_I_AIScriptingClasses_cpp")        
        self.__GLOBAL__sub_I_AIScriptingClasses_cpp()
        logging.info("AT_INIT >> ___cxx_global_var_init")
        self.___cxx_global_var_init()
        logging.info("AT_INIT >> __GLOBAL__sub_I_AccessibilityScriptingClasses_cpp")
        self.__GLOBAL__sub_I_AccessibilityScriptingClasses_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_AndroidJNIScriptingClasses_cpp")
        self.__GLOBAL__sub_I_AndroidJNIScriptingClasses_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_AnimationScriptingClasses_cpp")
        self.__GLOBAL__sub_I_AnimationScriptingClasses_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_Animation_1_cpp")
        self.__GLOBAL__sub_I_Modules_Animation_1_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_Animation_3_cpp")
        self.__GLOBAL__sub_I_Modules_Animation_3_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_Animation_6_cpp")
        self.__GLOBAL__sub_I_Modules_Animation_6_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Avatar_cpp")
        self.__GLOBAL__sub_I_Avatar_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_ConstraintManager_cpp")
        self.__GLOBAL__sub_I_ConstraintManager_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_AnimationClip_cpp")
        self.__GLOBAL__sub_I_AnimationClip_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_AssetBundleScriptingClasses_cpp")
        self.__GLOBAL__sub_I_AssetBundleScriptingClasses_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_AssetBundle_Public_0_cpp")
        self.__GLOBAL__sub_I_Modules_AssetBundle_Public_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_AudioScriptingClasses_cpp")
        self.__GLOBAL__sub_I_AudioScriptingClasses_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Video_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Video_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_Audio_Public_0_cpp")
        self.__GLOBAL__sub_I_Modules_Audio_Public_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_Audio_Public_1_cpp")
        self.__GLOBAL__sub_I_Modules_Audio_Public_1_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_Audio_Public_3_cpp")
        self.__GLOBAL__sub_I_Modules_Audio_Public_3_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_Audio_Public_ScriptBindings_1_cpp")
        self.__GLOBAL__sub_I_Modules_Audio_Public_ScriptBindings_1_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_Audio_Public_sound_0_cpp")
        self.__GLOBAL__sub_I_Modules_Audio_Public_sound_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_ClothScriptingClasses_cpp")
        self.__GLOBAL__sub_I_ClothScriptingClasses_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_Cloth_0_cpp")
        self.__GLOBAL__sub_I_Modules_Cloth_0_cpp()
        logging.info("AT_INIT >> ___cxx_global_var_init_18")
        self.___cxx_global_var_init_18()
        logging.info("AT_INIT >> __GLOBAL__sub_I_nvcloth_src_0_cpp")
        self.__GLOBAL__sub_I_nvcloth_src_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_nvcloth_src_1_cpp")
        self.__GLOBAL__sub_I_nvcloth_src_1_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_SwInterCollision_cpp")
        self.__GLOBAL__sub_I_SwInterCollision_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_SwSolverKernel_cpp")
        self.__GLOBAL__sub_I_SwSolverKernel_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_artifacts_WebGL_codegenerator_0_cpp")
        self.__GLOBAL__sub_I_artifacts_WebGL_codegenerator_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_GfxDevice_opengles_0_cpp")
        self.__GLOBAL__sub_I_Runtime_GfxDevice_opengles_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_VirtualFileSystem_0_cpp")
        self.__GLOBAL__sub_I_Runtime_VirtualFileSystem_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Input_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Input_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_GfxDeviceNull_cpp")
        self.__GLOBAL__sub_I_GfxDeviceNull_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_External_ProphecySDK_BlitOperations_1_cpp")
        self.__GLOBAL__sub_I_External_ProphecySDK_BlitOperations_1_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_2D_Renderer_0_cpp")
        self.__GLOBAL__sub_I_Runtime_2D_Renderer_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_2D_Sorting_0_cpp")
        self.__GLOBAL__sub_I_Runtime_2D_Sorting_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_2D_SpriteAtlas_0_cpp")
        self.__GLOBAL__sub_I_Runtime_2D_SpriteAtlas_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Allocator_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Allocator_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Allocator_2_cpp")
        self.__GLOBAL__sub_I_Runtime_Allocator_2_cpp()
        logging.info("AT_INIT >> ___cxx_global_var_init_7")
        self.___cxx_global_var_init_7()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Application_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Application_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_BaseClasses_0_cpp")
        self.__GLOBAL__sub_I_Runtime_BaseClasses_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_BaseClasses_1_cpp")
        self.__GLOBAL__sub_I_Runtime_BaseClasses_1_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_BaseClasses_2_cpp")
        self.__GLOBAL__sub_I_Runtime_BaseClasses_2_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_BaseClasses_3_cpp")
        self.__GLOBAL__sub_I_Runtime_BaseClasses_3_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Burst_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Burst_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Camera_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Camera_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Camera_1_cpp")
        self.__GLOBAL__sub_I_Runtime_Camera_1_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Camera_2_cpp")
        self.__GLOBAL__sub_I_Runtime_Camera_2_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Camera_3_cpp")
        self.__GLOBAL__sub_I_Runtime_Camera_3_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Camera_4_cpp")
        self.__GLOBAL__sub_I_Runtime_Camera_4_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Camera_5_cpp")
        self.__GLOBAL__sub_I_Runtime_Camera_5_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Camera_6_cpp")
        self.__GLOBAL__sub_I_Runtime_Camera_6_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Camera_7_cpp")
        self.__GLOBAL__sub_I_Runtime_Camera_7_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Shadows_cpp")
        self.__GLOBAL__sub_I_Shadows_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Camera_Culling_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Camera_Culling_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_GUITexture_cpp")
        self.__GLOBAL__sub_I_GUITexture_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Camera_RenderLoops_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Camera_RenderLoops_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Camera_RenderLoops_2_cpp")
        self.__GLOBAL__sub_I_Runtime_Camera_RenderLoops_2_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Containers_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Containers_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Core_Callbacks_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Core_Callbacks_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_File_0_cpp")
        self.__GLOBAL__sub_I_Runtime_File_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Geometry_2_cpp")
        self.__GLOBAL__sub_I_Runtime_Geometry_2_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Graphics_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Graphics_0_cpp()
        logging.info("AT_INIT >> ___cxx_global_var_init_98")
        self.___cxx_global_var_init_98()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Graphics_1_cpp")
        self.__GLOBAL__sub_I_Runtime_Graphics_1_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Graphics_2_cpp")
        self.__GLOBAL__sub_I_Runtime_Graphics_2_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Graphics_4_cpp")
        self.__GLOBAL__sub_I_Runtime_Graphics_4_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Graphics_5_cpp")
        self.__GLOBAL__sub_I_Runtime_Graphics_5_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Graphics_6_cpp")
        self.__GLOBAL__sub_I_Runtime_Graphics_6_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Graphics_8_cpp")
        self.__GLOBAL__sub_I_Runtime_Graphics_8_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Graphics_10_cpp")
        self.__GLOBAL__sub_I_Runtime_Graphics_10_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Graphics_11_cpp")
        self.__GLOBAL__sub_I_Runtime_Graphics_11_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Graphics_Billboard_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Graphics_Billboard_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Graphics_LOD_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Graphics_LOD_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Graphics_Mesh_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Graphics_Mesh_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Graphics_Mesh_1_cpp")
        self.__GLOBAL__sub_I_Runtime_Graphics_Mesh_1_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Graphics_Mesh_2_cpp")
        self.__GLOBAL__sub_I_Runtime_Graphics_Mesh_2_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Graphics_Mesh_4_cpp")
        self.__GLOBAL__sub_I_Runtime_Graphics_Mesh_4_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Graphics_Mesh_5_cpp")
        self.__GLOBAL__sub_I_Runtime_Graphics_Mesh_5_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Graphics_ScriptableRenderLoop_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Graphics_ScriptableRenderLoop_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Interfaces_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Interfaces_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Interfaces_1_cpp")
        self.__GLOBAL__sub_I_Runtime_Interfaces_1_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Interfaces_2_cpp")
        self.__GLOBAL__sub_I_Runtime_Interfaces_2_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Jobs_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Jobs_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Jobs_1_cpp")
        self.__GLOBAL__sub_I_Runtime_Jobs_1_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Jobs_Internal_1_cpp")#here
        self.__GLOBAL__sub_I_Runtime_Jobs_Internal_1_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Jobs_ScriptBindings_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Jobs_ScriptBindings_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Math_2_cpp")
        self.__GLOBAL__sub_I_Runtime_Math_2_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Math_Random_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Math_Random_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Misc_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Misc_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Misc_2_cpp")
        self.__GLOBAL__sub_I_Runtime_Misc_2_cpp()
        logging.info("AT_INIT >> ___cxx_global_var_init_131")
        self.___cxx_global_var_init_131()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Misc_4_cpp")
        self.__GLOBAL__sub_I_Runtime_Misc_4_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Misc_5_cpp")
        self.__GLOBAL__sub_I_Runtime_Misc_5_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_PreloadManager_0_cpp")
        self.__GLOBAL__sub_I_Runtime_PreloadManager_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Profiler_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Profiler_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Profiler_2_cpp")
        self.__GLOBAL__sub_I_Runtime_Profiler_2_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Profiler_ScriptBindings_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Profiler_ScriptBindings_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_SceneManager_0_cpp")
        self.__GLOBAL__sub_I_Runtime_SceneManager_0_cpp()
        logging.info("AT_INIT >> ___cxx_global_var_init_8100")
        self.___cxx_global_var_init_8100()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Shaders_1_cpp")
        self.__GLOBAL__sub_I_Runtime_Shaders_1_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Shaders_3_cpp")
        self.__GLOBAL__sub_I_Runtime_Shaders_3_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Shaders_4_cpp")
        self.__GLOBAL__sub_I_Runtime_Shaders_4_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Shaders_ShaderImpl_2_cpp")
        self.__GLOBAL__sub_I_Runtime_Shaders_ShaderImpl_2_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Transform_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Transform_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Transform_1_cpp")
        self.__GLOBAL__sub_I_Runtime_Transform_1_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Utilities_2_cpp")
        self.__GLOBAL__sub_I_Runtime_Utilities_2_cpp()
        logging.info("AT_INIT >> ___cxx_global_var_init_2_9504")
        self.___cxx_global_var_init_2_9504()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Utilities_5_cpp")
        self.__GLOBAL__sub_I_Runtime_Utilities_5_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Utilities_6_cpp")
        self.__GLOBAL__sub_I_Runtime_Utilities_6_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Utilities_7_cpp")
        self.__GLOBAL__sub_I_Runtime_Utilities_7_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Utilities_9_cpp")
        self.__GLOBAL__sub_I_Runtime_Utilities_9_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_AssetBundleFileSystem_cpp")
        self.__GLOBAL__sub_I_AssetBundleFileSystem_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Modules_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Modules_0_cpp()
        logging.info("AT_INIT >> ___cxx_global_var_init_13")
        self.___cxx_global_var_init_13()
        logging.info("AT_INIT >> ___cxx_global_var_init_14")
        self.___cxx_global_var_init_14()
        logging.info("AT_INIT >> ___cxx_global_var_init_15")
        self.___cxx_global_var_init_15()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_Profiler_Public_0_cpp")
        self.__GLOBAL__sub_I_Modules_Profiler_Public_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_Profiler_Runtime_1_cpp")
        self.__GLOBAL__sub_I_Modules_Profiler_Runtime_1_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_UnsafeUtility_bindings_cpp")
        self.__GLOBAL__sub_I_UnsafeUtility_bindings_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_GfxDevice_1_cpp")
        self.__GLOBAL__sub_I_Runtime_GfxDevice_1_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_GfxDevice_2_cpp")
        self.__GLOBAL__sub_I_Runtime_GfxDevice_2_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_GfxDevice_3_cpp")
        self.__GLOBAL__sub_I_Runtime_GfxDevice_3_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_GfxDevice_4_cpp")
        self.__GLOBAL__sub_I_Runtime_GfxDevice_4_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_GfxDevice_5_cpp")
        self.__GLOBAL__sub_I_Runtime_GfxDevice_5_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_PluginInterface_0_cpp")
        self.__GLOBAL__sub_I_Runtime_PluginInterface_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Director_Core_1_cpp")
        self.__GLOBAL__sub_I_Runtime_Director_Core_1_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_ScriptingBackend_Il2Cpp_0_cpp")
        self.__GLOBAL__sub_I_Runtime_ScriptingBackend_Il2Cpp_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Scripting_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Scripting_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Scripting_1_cpp")
        self.__GLOBAL__sub_I_Runtime_Scripting_1_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Scripting_2_cpp")
        self.__GLOBAL__sub_I_Runtime_Scripting_2_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Scripting_3_cpp")
        self.__GLOBAL__sub_I_Runtime_Scripting_3_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Mono_2_cpp")
        self.__GLOBAL__sub_I_Runtime_Mono_2_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Mono_SerializationBackend_DirectMemoryAccess_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Mono_SerializationBackend_DirectMemoryAccess_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Mono_SerializationBackend_DirectMemoryAccess_1_cpp")
        self.__GLOBAL__sub_I_Runtime_Mono_SerializationBackend_DirectMemoryAccess_1_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_TemplateInstantiations_cpp")
        self.__GLOBAL__sub_I_TemplateInstantiations_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Scripting_APIUpdating_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Scripting_APIUpdating_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Serialize_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Serialize_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Serialize_1_cpp")
        self.__GLOBAL__sub_I_Runtime_Serialize_1_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Serialize_2_cpp")
        self.__GLOBAL__sub_I_Runtime_Serialize_2_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Serialize_TransferFunctions_0_cpp")
        self.__GLOBAL__sub_I_Runtime_Serialize_TransferFunctions_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Runtime_Serialize_TransferFunctions_1_cpp")
        self.__GLOBAL__sub_I_Runtime_Serialize_TransferFunctions_1_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_PlatformDependent_WebGL_Source_0_cpp")
        self.__GLOBAL__sub_I_PlatformDependent_WebGL_Source_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_PlatformDependent_WebGL_Source_2_cpp")  # 5913980 should print 1024
        self.__GLOBAL__sub_I_PlatformDependent_WebGL_Source_2_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_LogAssert_cpp")
        self.__GLOBAL__sub_I_LogAssert_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Shader_cpp")
        self.__GLOBAL__sub_I_Shader_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Transform_cpp")
        self.__GLOBAL__sub_I_Transform_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_PlatformDependent_WebGL_External_baselib_builds_Source_0_cpp")
        self.__GLOBAL__sub_I_PlatformDependent_WebGL_External_baselib_builds_Source_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_DSPGraph_Public_1_cpp")
        self.__GLOBAL__sub_I_Modules_DSPGraph_Public_1_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_DirectorScriptingClasses_cpp")
        self.__GLOBAL__sub_I_DirectorScriptingClasses_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_GridScriptingClasses_cpp")
        self.__GLOBAL__sub_I_GridScriptingClasses_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_Grid_Public_0_cpp")
        self.__GLOBAL__sub_I_Modules_Grid_Public_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_IMGUIScriptingClasses_cpp")
        self.__GLOBAL__sub_I_IMGUIScriptingClasses_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_IMGUI_0_cpp")
        self.__GLOBAL__sub_I_Modules_IMGUI_0_cpp()
        logging.info("AT_INIT >> ___cxx_global_var_init_22")
        self.___cxx_global_var_init_22()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_IMGUI_1_cpp")
        self.__GLOBAL__sub_I_Modules_IMGUI_1_cpp()
        logging.info("AT_INIT >> ___cxx_global_var_init_3893")
        self.___cxx_global_var_init_3893()
        logging.info("AT_INIT >> __GLOBAL__sub_I_InputLegacyScriptingClasses_cpp")
        self.__GLOBAL__sub_I_InputLegacyScriptingClasses_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_InputScriptingClasses_cpp")
        self.__GLOBAL__sub_I_InputScriptingClasses_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_Input_Private_0_cpp")
        self.__GLOBAL__sub_I_Modules_Input_Private_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_ParticleSystemScriptingClasses_cpp")
        self.__GLOBAL__sub_I_ParticleSystemScriptingClasses_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_ParticleSystem_Modules_3_cpp")
        self.__GLOBAL__sub_I_Modules_ParticleSystem_Modules_3_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_ParticleSystemRenderer_cpp")
        self.__GLOBAL__sub_I_ParticleSystemRenderer_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_ShapeModule_cpp")
        self.__GLOBAL__sub_I_ShapeModule_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Physics2DScriptingClasses_cpp")
        self.__GLOBAL__sub_I_Physics2DScriptingClasses_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_Physics2D_Public_0_cpp")
        self.__GLOBAL__sub_I_Modules_Physics2D_Public_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_Physics2D_Public_1_cpp")
        self.__GLOBAL__sub_I_Modules_Physics2D_Public_1_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_PhysicsScriptingClasses_cpp")
        self.__GLOBAL__sub_I_PhysicsScriptingClasses_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_Physics_0_cpp")
        self.__GLOBAL__sub_I_Modules_Physics_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_Physics_1_cpp")
        self.__GLOBAL__sub_I_Modules_Physics_1_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_PhysicsQuery_cpp")
        self.__GLOBAL__sub_I_PhysicsQuery_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_SubsystemsScriptingClasses_cpp")
        self.__GLOBAL__sub_I_SubsystemsScriptingClasses_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_Subsystems_0_cpp")
        self.__GLOBAL__sub_I_Modules_Subsystems_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_TerrainScriptingClasses_cpp")
        self.__GLOBAL__sub_I_TerrainScriptingClasses_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_Terrain_Public_0_cpp")
        self.__GLOBAL__sub_I_Modules_Terrain_Public_0_cpp()
        logging.info("AT_INIT >> ___cxx_global_var_init_69")
        self.___cxx_global_var_init_69()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_Terrain_Public_1_cpp")
        self.__GLOBAL__sub_I_Modules_Terrain_Public_1_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_Terrain_Public_2_cpp")
        self.__GLOBAL__sub_I_Modules_Terrain_Public_2_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_Terrain_Public_3_cpp")
        self.__GLOBAL__sub_I_Modules_Terrain_Public_3_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_Terrain_VR_0_cpp")
        self.__GLOBAL__sub_I_Modules_Terrain_VR_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_TextCoreScriptingClasses_cpp")
        self.__GLOBAL__sub_I_TextCoreScriptingClasses_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_TextCore_Native_FontEngine_0_cpp")
        self.__GLOBAL__sub_I_Modules_TextCore_Native_FontEngine_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_TextRenderingScriptingClasses_cpp")
        self.__GLOBAL__sub_I_TextRenderingScriptingClasses_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_TextRendering_Public_0_cpp")
        self.__GLOBAL__sub_I_Modules_TextRendering_Public_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_TilemapScriptingClasses_cpp")
        self.__GLOBAL__sub_I_TilemapScriptingClasses_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_Tilemap_0_cpp")
        self.__GLOBAL__sub_I_Modules_Tilemap_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_Tilemap_Public_0_cpp")
        self.__GLOBAL__sub_I_Modules_Tilemap_Public_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_UIElementsScriptingClasses_cpp")
        self.__GLOBAL__sub_I_UIElementsScriptingClasses_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_External_Yoga_Yoga_0_cpp")
        self.__GLOBAL__sub_I_External_Yoga_Yoga_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_UIScriptingClasses_cpp")
        self.__GLOBAL__sub_I_UIScriptingClasses_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_UI_0_cpp")
        self.__GLOBAL__sub_I_Modules_UI_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_UI_1_cpp")
        self.__GLOBAL__sub_I_Modules_UI_1_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_UI_2_cpp")
        self.__GLOBAL__sub_I_Modules_UI_2_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_umbra_cpp")
        self.__GLOBAL__sub_I_umbra_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_UnityAnalyticsScriptingClasses_cpp")
        self.__GLOBAL__sub_I_UnityAnalyticsScriptingClasses_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_UnityAnalytics_Dispatcher_0_cpp")
        self.__GLOBAL__sub_I_Modules_UnityAnalytics_Dispatcher_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_UnityAdsSettings_cpp")
        self.__GLOBAL__sub_I_UnityAdsSettings_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_UnityWebRequestScriptingClasses_cpp")
        self.__GLOBAL__sub_I_UnityWebRequestScriptingClasses_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_UnityWebRequest_Public_0_cpp")
        self.__GLOBAL__sub_I_Modules_UnityWebRequest_Public_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_VFXScriptingClasses_cpp")
        self.__GLOBAL__sub_I_VFXScriptingClasses_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_VFX_Public_1_cpp")
        self.__GLOBAL__sub_I_Modules_VFX_Public_1_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_VFX_Public_2_cpp")
        self.__GLOBAL__sub_I_Modules_VFX_Public_2_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_VRScriptingClasses_cpp")
        self.__GLOBAL__sub_I_VRScriptingClasses_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_VR_2_cpp")
        self.__GLOBAL__sub_I_Modules_VR_2_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_VR_PluginInterface_0_cpp")
        self.__GLOBAL__sub_I_Modules_VR_PluginInterface_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_VideoScriptingClasses_cpp")
        self.__GLOBAL__sub_I_VideoScriptingClasses_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_Video_Public_Base_0_cpp")
        self.__GLOBAL__sub_I_Modules_Video_Public_Base_0_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Wind_cpp")
        self.__GLOBAL__sub_I_Wind_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_XRScriptingClasses_cpp")
        self.__GLOBAL__sub_I_XRScriptingClasses_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Modules_XR_Subsystems_Input_Public_1_cpp")
        self.__GLOBAL__sub_I_Modules_XR_Subsystems_Input_Public_1_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Lump_libil2cpp_os_cpp")
        self.__GLOBAL__sub_I_Lump_libil2cpp_os_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Il2CppCodeRegistration_cpp")
        self.__GLOBAL__sub_I_Il2CppCodeRegistration_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Lump_libil2cpp_vm_cpp")
        self.__GLOBAL__sub_I_Lump_libil2cpp_vm_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Lump_libil2cpp_metadata_cpp")
        self.__GLOBAL__sub_I_Lump_libil2cpp_metadata_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Lump_libil2cpp_utils_cpp")
        self.__GLOBAL__sub_I_Lump_libil2cpp_utils_cpp()
        logging.info("AT_INIT >> __GLOBAL__sub_I_Lump_libil2cpp_gc_cpp")
        self.__GLOBAL__sub_I_Lump_libil2cpp_gc_cpp()
        logging.info("AT_INIT >> ___emscripten_environ_constructor")
        self.___emscripten_environ_constructor()
        logging.info("AT_INIT >> DONE!")

    def _AT_MAIN(self):
        try:
            argc = 1
            argv = self.stackAlloc( (argc+1)*4)
            self.HEAP32[argv >> 2] = self.allocateUTF8OnStack('./this.program')
            self.HEAP32[(argv >> 2) + argc] = 0
            logging.info("AT_MAIN >> _main")
            tmp = self._main(argc, argv)
        except Exception as e:
            logging.error( "_AT_MAIN failed" , exc_info=True)
            raise e