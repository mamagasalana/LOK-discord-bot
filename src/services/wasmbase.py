

import math

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
        
    def abort(self, *args):
        return 

    def enlargeMemory(self, *args):
        return 0

    def getTotalMemory(self, *args):
        return 0

    def abortOnCannotGrowMemory(self, *args):
        return 0

    def invokedddi(self, *args):
        return 0

    def invokedii(self, *args):
        return 0

    def invokediii(self, *args):
        return 0

    def invokediiid(self, *args):
        return 0

    def invokediiii(self, *args):
        return 0

    def invokeffffi(self, *args):
        return 0

    def invokefffi(self, *args):
        return 0

    def invokefi(self, *args):
        return 0

    def invokefii(self, *args):
        return 0

    def invokefiifi(self, *args):
        return 0

    def invokefiifii(self, *args):
        return 0

    def invokefiii(self, *args):
        return 0

    def invokefiiif(self, *args):
        return 0

    def invokefiiii(self, *args):
        return 0

    def invokei(self, *args):
        return 0

    def invokeifi(self, *args):
        return 0

    def invokeii(self, *args):
        return 0

    def invokeiifii(self, *args):
        return 0

    def invokeiii(self, *args):
        return 0

    def invokeiiifi(self, *args):
        return 0

    def invokeiiii(self, *args):
        return 0

    def invokeiiiifii(self, *args):
        return 0

    def invokeiiiii(self, *args):
        return 0

    def invokeiiiiii(self, *args):
        return 0

    def invokeiiiiiii(self, *args):
        return 0

    def invokeiiiiiiii(self, *args):
        return 0

    def invokeiiiiiiiii(self, *args):
        return 0

    def invokeiiiiiiiiii(self, *args):
        return 0

    def invokeiiiiiiiiiii(self, *args):
        return 0

    def invokev(self, *args):
        return 

    def invokevi(self, *args):
        return 

    def invokevidiii(self, *args):
        return 

    def invokevifffi(self, *args):
        return 

    def invokevifi(self, *args):
        return 

    def invokevifii(self, *args):
        return 

    def invokevii(self, *args):
        return 

    def invokeviidi(self, *args):
        return 

    def invokeviidii(self, *args):
        return 

    def invokeviiff(self, *args):
        return 

    def invokeviiffi(self, *args):
        return 

    def invokeviifi(self, *args):
        return 

    def invokeviifii(self, *args):
        return 

    def invokeviii(self, *args):
        return 

    def invokeviiif(self, *args):
        return 

    def invokeviiii(self, *args):
        return 

    def invokeviiiii(self, *args):
        return 

    def invokeviiiiii(self, *args):
        return 

    def invokeviiiiiii(self, *args):
        return 

    def invokeviiiiiiifddfii(self, *args):
        return 

    def invokeviiiiiiiffffii(self, *args):
        return 

    def invokeviiiiiiifiifii(self, *args):
        return 

    def invokeviiiiiiii(self, *args):
        return 

    def invokeviiiiiiiii(self, *args):
        return 

    def invokeviiiiiiiiii(self, *args):
        return 

    def ESAddEventHandler(self, *args):
        return 

    def ESClose(self, *args):
        return 

    def ESCreate(self, *args):
        return 0

    def ESIsSupported(self, *args):
        return 0

    def ESRelease(self, *args):
        return 

    def GetInputFieldSelectionEnd(self, *args):
        return 0

    def GetInputFieldSelectionStart(self, *args):
        return 0

    def GetInputFieldValue(self, *args):
        return 0

    def HideInputField(self, *args):
        return 

    def IsInputFieldActive(self, *args):
        return 0

    def JSCursorSetImage(self, *args):
        return 

    def JSCursorSetShow(self, *args):
        return 

    def JSEvalClearInterval(self, *args):
        return 

    def JSEvalOpenURL(self, *args):
        return 

    def JSEvalSetInterval(self, *args):
        return 0

    def JSFileSystemInitialize(self, *args):
        return 

    def JSFileSystemSync(self, *args):
        return 

    def JSLogDump(self, *args):
        return 

    def JSLogStackTrace(self, *args):
        return 

    def JSSoundCreateChannel(self, *args):
        return 0

    def JSSoundGetLength(self, *args):
        return 0

    def JSSoundGetLoadState(self, *args):
        return 0

    def JSSoundInit(self, *args):
        return 

    def JSSoundLoad(self, *args):
        return 0

    def JSSoundLoadPCM(self, *args):
        return 0

    def JSSoundPlay(self, *args):
        return 

    def JSSoundReleaseInstance(self, *args):
        return 0

    def JSSoundResumeIfNeeded(self, *args):
        return 

    def JSSoundSet3D(self, *args):
        return 

    def JSSoundSetListenerOrientation(self, *args):
        return 

    def JSSoundSetListenerPosition(self, *args):
        return 

    def JSSoundSetLoop(self, *args):
        return 

    def JSSoundSetLoopPoints(self, *args):
        return 

    def JSSoundSetPaused(self, *args):
        return 

    def JSSoundSetPitch(self, *args):
        return 

    def JSSoundSetPosition(self, *args):
        return 

    def JSSoundSetVolume(self, *args):
        return 

    def JSSoundStop(self, *args):
        return 

    def JSSystemInfoGetBrowserName(self, *args):
        return 0

    def JSSystemInfoGetBrowserVersionString(self, *args):
        return 0

    def JSSystemInfoGetCanvasClientSize(self, *args):
        return 

    def JSSystemInfoGetDocumentURL(self, *args):
        return 0

    def JSSystemInfoGetGPUInfo(self, *args):
        return 0

    def JSSystemInfoGetLanguage(self, *args):
        return 0

    def JSSystemInfoGetMemory(self, *args):
        return 0

    def JSSystemInfoGetOS(self, *args):
        return 0

    def JSSystemInfoGetPreferredDevicePixelRatio(self, *args):
        return 0

    def JSSystemInfoGetScreenSize(self, *args):
        return 

    def JSSystemInfoGetStreamingAssetsURL(self, *args):
        return 0

    def JSSystemInfoHasCursorLock(self, *args):
        return 0

    def JSSystemInfoHasFullscreen(self, *args):
        return 0

    def JSSystemInfoHasWebGL(self, *args):
        return 0

    def JSSystemInfoIsMobile(self, *args):
        return 0

    def JSVideoCanPlayFormat(self, *args):
        return 0

    def JSVideoCreate(self, *args):
        return 0

    def JSVideoDestroy(self, *args):
        return 

    def JSVideoDuration(self, *args):
        return 0

    def JSVideoEnableAudioTrack(self, *args):
        return 

    def JSVideoGetAudioLanguageCode(self, *args):
        return 0

    def JSVideoGetNumAudioTracks(self, *args):
        return 0

    def JSVideoHeight(self, *args):
        return 0

    def JSVideoIsPlaying(self, *args):
        return 0

    def JSVideoIsReady(self, *args):
        return 0

    def JSVideoPause(self, *args):
        return 

    def JSVideoPlay(self, *args):
        return 

    def JSVideoSeek(self, *args):
        return 

    def JSVideoSetEndedHandler(self, *args):
        return 

    def JSVideoSetErrorHandler(self, *args):
        return 

    def JSVideoSetLoop(self, *args):
        return 

    def JSVideoSetMute(self, *args):
        return 

    def JSVideoSetPlaybackRate(self, *args):
        return 

    def JSVideoSetReadyHandler(self, *args):
        return 

    def JSVideoSetSeekedOnceHandler(self, *args):
        return 

    def JSVideoSetVolume(self, *args):
        return 

    def JSVideoTime(self, *args):
        return 0

    def JSVideoUpdateToTexture(self, *args):
        return 0

    def JSVideoWidth(self, *args):
        return 0

    def JSWebCamVideoCanPlay(self, *args):
        return 0

    def JSWebCamVideoGetDeviceName(self, *args):
        return 0

    def JSWebCamVideoGetNativeHeight(self, *args):
        return 0

    def JSWebCamVideoGetNativeWidth(self, *args):
        return 0

    def JSWebCamVideoGetNumDevices(self, *args):
        return 0

    def JSWebCamVideoGrabFrame(self, *args):
        return 

    def JSWebCamVideoStart(self, *args):
        return 

    def JSWebCamVideoStop(self, *args):
        return 

    def JSWebCamIsSupported(self, *args):
        return 0

    def JSWebRequestAbort(self, *args):
        return 

    def JSWebRequestCreate(self, *args):
        return 0

    def JSWebRequestGetResponseHeaders(self, *args):
        return 0

    def JSWebRequestRelease(self, *args):
        return 

    def JSWebRequestSend(self, *args):
        return 

    def JSWebRequestSetProgressHandler(self, *args):
        return 

    def JSWebRequestSetRequestHeader(self, *args):
        return 

    def JSWebRequestSetResponseHandler(self, *args):
        return 

    def JSWebRequestSetTimeout(self, *args):
        return 

    def NativeCall(self, *args):
        return 

    def SetInputFieldSelection(self, *args):
        return 

    def ShowInputField(self, *args):
        return 

    def WSClose(self, *args):
        return 

    def WSCreate(self, *args):
        return 0

    def WSGetBufferedAmount(self, *args):
        return 0

    def WSGetState(self, *args):
        return 0

    def WSRelease(self, *args):
        return 

    def WSSendBinary(self, *args):
        return 0

    def WSSendString(self, *args):
        return 0

    def XHRAbort(self, *args):
        return 

    def XHRCreate(self, *args):
        return 0

    def XHRGetResponseHeaders(self, *args):
        return 

    def XHRGetStatusLine(self, *args):
        return 

    def XHRRelease(self, *args):
        return 

    def XHRSend(self, *args):
        return 

    def XHRSetLoglevel(self, *args):
        return 

    def XHRSetProgressHandler(self, *args):
        return 

    def XHRSetRequestHeader(self, *args):
        return 

    def XHRSetResponseHandler(self, *args):
        return 

    def XHRSetTimeout(self, *args):
        return 

    def buildEnvironment(self, *args):
        return 

    def cxaallocateexception(self, *args):
        return 0

    def cxabegincatch(self, *args):
        return 0

    def cxaendcatch(self, *args):
        return 

    def cxafindmatchingcatch2(self, *args):
        return 0

    def cxafindmatchingcatch3(self, *args):
        return 0

    def cxafindmatchingcatch4(self, *args):
        return 0

    def cxafreeexception(self, *args):
        return 

    def cxapurevirtual(self, *args):
        return 

    def cxarethrow(self, *args):
        return 

    def cxathrow(self, *args):
        return 

    def lock(self, *args):
        return 

    def mapfile(self, *args):
        return 0

    def resumeException(self, *args):
        return 

    def setErrNo(self, *args):
        return 

    def syscall10(self, *args):
        return 0

    def syscall102(self, *args):
        return 0

    def syscall122(self, *args):
        return 0

    def syscall140(self, *args):
        return 0

    def syscall142(self, *args):
        return 0

    def syscall145(self, *args):
        return 0

    def syscall146(self, *args):
        return 0

    def syscall15(self, *args):
        return 0

    def syscall168(self, *args):
        return 0

    def syscall183(self, *args):
        return 0

    def syscall192(self, *args):
        return 0

    def syscall193(self, *args):
        return 0

    def syscall194(self, *args):
        return 0

    def syscall195(self, *args):
        return 0

    def syscall196(self, *args):
        return 0

    def syscall197(self, *args):
        return 0

    def syscall199(self, *args):
        return 0

    def syscall220(self, *args):
        return 0

    def syscall221(self, *args):
        return 0

    def syscall268(self, *args):
        return 0

    def syscall3(self, *args):
        return 0

    def syscall33(self, *args):
        return 0

    def syscall38(self, *args):
        return 0

    def syscall39(self, *args):
        return 0

    def syscall4(self, *args):
        return 0

    def syscall40(self, *args):
        return 0

    def syscall42(self, *args):
        return 0

    def syscall5(self, *args):
        return 0

    def syscall54(self, *args):
        return 0

    def syscall6(self, *args):
        return 0

    def syscall63(self, *args):
        return 0

    def syscall77(self, *args):
        return 0

    def syscall85(self, *args):
        return 0

    def syscall91(self, *args):
        return 0

    def unlock(self, *args):
        return 

    def abort(self, *args):
        return 

    def atexit(self, *args):
        return 0

    def clock(self, *args):
        return 0

    def clockgetres(self, *args):
        return 0

    def clockgettime(self, *args):
        return 0

    def difftime(self, *args):
        return 0

    def dlclose(self, *args):
        return 0

    def dlopen(self, *args):
        return 0

    def dlsym(self, *args):
        return 0

    def emscriptenasmconsti(self, *args):
        return 0

    def emscriptenasmconstsynconmainthreadi(self, *args):
        return 0

    def emscriptencancelmainloop(self, *args):
        return 

    def emscriptenexitfullscreen(self, *args):
        return 0

    def emscriptenexitpointerlock(self, *args):
        return 0

    def emscriptengetcanvaselementsize(self, *args):
        return 0

    def emscriptengetfullscreenstatus(self, *args):
        return 0

    def emscriptengetgamepadstatus(self, *args):
        return 0

    def emscriptengetmainlooptiming(self, *args):
        return 

    def emscriptengetnow(self, *args):
        return 0

    def emscriptengetnumgamepads(self, *args):
        return 0

    def emscriptenhasthreadingsupport(self, *args):
        return 0

    def emscriptenhtml5removealleventlisteners(self, *args):
        return 

    def emscripteniswebglcontextlost(self, *args):
        return 0

    def emscriptenlog(self, *args):
        return 

    def emscriptenlongjmp(self, *args):
        return 

    def emscriptenmemcpybig(self, *args):
        return 0

    def emscriptennumlogicalcores(self, *args):
        return 0

    def emscriptenrequestfullscreen(self, *args):
        return 0

    def emscriptenrequestpointerlock(self, *args):
        return 0

    def emscriptensetblurcallbackonthread(self, *args):
        return 0

    def emscriptensetcanvaselementsize(self, *args):
        return 0

    def emscriptensetdblclickcallbackonthread(self, *args):
        return 0

    def emscriptensetdevicemotioncallbackonthread(self, *args):
        return 0

    def emscriptensetdeviceorientationcallbackonthread(self, *args):
        return 0

    def emscriptensetfocuscallbackonthread(self, *args):
        return 0

    def emscriptensetfullscreenchangecallbackonthread(self, *args):
        return 0

    def emscriptensetgamepadconnectedcallbackonthread(self, *args):
        return 0

    def emscriptensetgamepaddisconnectedcallbackonthread(self, *args):
        return 0

    def emscriptensetkeydowncallbackonthread(self, *args):
        return 0

    def emscriptensetkeypresscallbackonthread(self, *args):
        return 0

    def emscriptensetkeyupcallbackonthread(self, *args):
        return 0

    def emscriptensetmainloop(self, *args):
        return 

    def emscriptensetmainlooptiming(self, *args):
        return 0

    def emscriptensetmousedowncallbackonthread(self, *args):
        return 0

    def emscriptensetmousemovecallbackonthread(self, *args):
        return 0

    def emscriptensetmouseupcallbackonthread(self, *args):
        return 0

    def emscriptensettouchcancelcallbackonthread(self, *args):
        return 0

    def emscriptensettouchendcallbackonthread(self, *args):
        return 0

    def emscriptensettouchmovecallbackonthread(self, *args):
        return 0

    def emscriptensettouchstartcallbackonthread(self, *args):
        return 0

    def emscriptensetwheelcallbackonthread(self, *args):
        return 0

    def emscriptenwebglcreatecontext(self, *args):
        return 0

    def emscriptenwebgldestroycontext(self, *args):
        return 0

    def emscriptenwebglenableextension(self, *args):
        return 0

    def emscriptenwebglgetcurrentcontext(self, *args):
        return 0

    def emscriptenwebglinitcontextattributes(self, *args):
        return 

    def emscriptenwebglmakecontextcurrent(self, *args):
        return 0

    def exit(self, *args):
        return 

    def flock(self, *args):
        return 0

    def getaddrinfo(self, *args):
        return 0

    def getenv(self, *args):
        return 0

    def gethostbyaddr(self, *args):
        return 0

    def gethostbyname(self, *args):
        return 0

    def getnameinfo(self, *args):
        return 0

    def getpagesize(self, *args):
        return 0

    def getpwuid(self, *args):
        return 0

    def gettimeofday(self, *args):
        return 0

    def glActiveTexture(self, *args):
        return 

    def glAttachShader(self, *args):
        return 

    def glBeginQuery(self, *args):
        return 

    def glBeginTransformFeedback(self, *args):
        return 

    def glBindAttribLocation(self, *args):
        return 

    def glBindBuffer(self, *args):
        return 

    def glBindBufferBase(self, *args):
        return 

    def glBindBufferRange(self, *args):
        return 

    def glBindFramebuffer(self, *args):
        return 

    def glBindRenderbuffer(self, *args):
        return 

    def glBindSampler(self, *args):
        return 

    def glBindTexture(self, *args):
        return 

    def glBindTransformFeedback(self, *args):
        return 

    def glBindVertexArray(self, *args):
        return 

    def glBlendEquation(self, *args):
        return 

    def glBlendEquationSeparate(self, *args):
        return 

    def glBlendFuncSeparate(self, *args):
        return 

    def glBlitFramebuffer(self, *args):
        return 

    def glBufferData(self, *args):
        return 

    def glBufferSubData(self, *args):
        return 

    def glCheckFramebufferStatus(self, *args):
        return 0

    def glClear(self, *args):
        return 

    def glClearBufferfi(self, *args):
        return 

    def glClearBufferfv(self, *args):
        return 

    def glClearBufferuiv(self, *args):
        return 

    def glClearColor(self, *args):
        return 

    def glClearDepthf(self, *args):
        return 

    def glClearStencil(self, *args):
        return 

    def glColorMask(self, *args):
        return 

    def glCompileShader(self, *args):
        return 

    def glCompressedTexImage2D(self, *args):
        return 

    def glCompressedTexSubImage2D(self, *args):
        return 

    def glCompressedTexSubImage3D(self, *args):
        return 

    def glCopyBufferSubData(self, *args):
        return 

    def glCopyTexImage2D(self, *args):
        return 

    def glCopyTexSubImage2D(self, *args):
        return 

    def glCreateProgram(self, *args):
        return 0

    def glCreateShader(self, *args):
        return 0

    def glCullFace(self, *args):
        return 

    def glDeleteBuffers(self, *args):
        return 

    def glDeleteFramebuffers(self, *args):
        return 

    def glDeleteProgram(self, *args):
        return 

    def glDeleteQueries(self, *args):
        return 

    def glDeleteRenderbuffers(self, *args):
        return 

    def glDeleteSamplers(self, *args):
        return 

    def glDeleteShader(self, *args):
        return 

    def glDeleteSync(self, *args):
        return 

    def glDeleteTextures(self, *args):
        return 

    def glDeleteTransformFeedbacks(self, *args):
        return 

    def glDeleteVertexArrays(self, *args):
        return 

    def glDepthFunc(self, *args):
        return 

    def glDepthMask(self, *args):
        return 

    def glDetachShader(self, *args):
        return 

    def glDisable(self, *args):
        return 

    def glDisableVertexAttribArray(self, *args):
        return 

    def glDrawArrays(self, *args):
        return 

    def glDrawArraysInstanced(self, *args):
        return 

    def glDrawBuffers(self, *args):
        return 

    def glDrawElements(self, *args):
        return 

    def glDrawElementsInstanced(self, *args):
        return 

    def glEnable(self, *args):
        return 

    def glEnableVertexAttribArray(self, *args):
        return 

    def glEndQuery(self, *args):
        return 

    def glEndTransformFeedback(self, *args):
        return 

    def glFenceSync(self, *args):
        return 0

    def glFinish(self, *args):
        return 

    def glFlush(self, *args):
        return 

    def glFlushMappedBufferRange(self, *args):
        return 

    def glFramebufferRenderbuffer(self, *args):
        return 

    def glFramebufferTexture2D(self, *args):
        return 

    def glFramebufferTextureLayer(self, *args):
        return 

    def glFrontFace(self, *args):
        return 

    def glGenBuffers(self, *args):
        return 

    def glGenFramebuffers(self, *args):
        return 

    def glGenQueries(self, *args):
        return 

    def glGenRenderbuffers(self, *args):
        return 

    def glGenSamplers(self, *args):
        return 

    def glGenTextures(self, *args):
        return 

    def glGenTransformFeedbacks(self, *args):
        return 

    def glGenVertexArrays(self, *args):
        return 

    def glGenerateMipmap(self, *args):
        return 

    def glGetActiveAttrib(self, *args):
        return 

    def glGetActiveUniform(self, *args):
        return 

    def glGetActiveUniformBlockName(self, *args):
        return 

    def glGetActiveUniformBlockiv(self, *args):
        return 

    def glGetActiveUniformsiv(self, *args):
        return 

    def glGetAttribLocation(self, *args):
        return 0

    def glGetError(self, *args):
        return 0

    def glGetFramebufferAttachmentParameteriv(self, *args):
        return 

    def glGetIntegeriv(self, *args):
        return 

    def glGetIntegerv(self, *args):
        return 

    def glGetInternalformativ(self, *args):
        return 

    def glGetProgramBinary(self, *args):
        return 

    def glGetProgramInfoLog(self, *args):
        return 

    def glGetProgramiv(self, *args):
        return 

    def glGetRenderbufferParameteriv(self, *args):
        return 

    def glGetShaderInfoLog(self, *args):
        return 

    def glGetShaderPrecisionFormat(self, *args):
        return 

    def glGetShaderSource(self, *args):
        return 

    def glGetShaderiv(self, *args):
        return 

    def glGetString(self, *args):
        return 0

    def glGetStringi(self, *args):
        return 0

    def glGetTexParameteriv(self, *args):
        return 

    def glGetUniformBlockIndex(self, *args):
        return 0

    def glGetUniformIndices(self, *args):
        return 

    def glGetUniformLocation(self, *args):
        return 0

    def glGetUniformiv(self, *args):
        return 

    def glGetVertexAttribiv(self, *args):
        return 

    def glInvalidateFramebuffer(self, *args):
        return 

    def glIsEnabled(self, *args):
        return 0

    def glIsVertexArray(self, *args):
        return 0

    def glLinkProgram(self, *args):
        return 

    def glMapBufferRange(self, *args):
        return 0

    def glPixelStorei(self, *args):
        return 

    def glPolygonOffset(self, *args):
        return 

    def glProgramBinary(self, *args):
        return 

    def glProgramParameteri(self, *args):
        return 

    def glReadBuffer(self, *args):
        return 

    def glReadPixels(self, *args):
        return 

    def glRenderbufferStorage(self, *args):
        return 

    def glRenderbufferStorageMultisample(self, *args):
        return 

    def glSamplerParameteri(self, *args):
        return 

    def glScissor(self, *args):
        return 

    def glShaderSource(self, *args):
        return 

    def glStencilFuncSeparate(self, *args):
        return 

    def glStencilMask(self, *args):
        return 

    def glStencilOpSeparate(self, *args):
        return 

    def glTexImage2D(self, *args):
        return 

    def glTexImage3D(self, *args):
        return 

    def glTexParameterf(self, *args):
        return 

    def glTexParameteri(self, *args):
        return 

    def glTexParameteriv(self, *args):
        return 

    def glTexStorage2D(self, *args):
        return 

    def glTexStorage3D(self, *args):
        return 

    def glTexSubImage2D(self, *args):
        return 

    def glTexSubImage3D(self, *args):
        return 

    def glTransformFeedbackVaryings(self, *args):
        return 

    def glUniform1fv(self, *args):
        return 

    def glUniform1i(self, *args):
        return 

    def glUniform1iv(self, *args):
        return 

    def glUniform1uiv(self, *args):
        return 

    def glUniform2fv(self, *args):
        return 

    def glUniform2iv(self, *args):
        return 

    def glUniform2uiv(self, *args):
        return 

    def glUniform3fv(self, *args):
        return 

    def glUniform3iv(self, *args):
        return 

    def glUniform3uiv(self, *args):
        return 

    def glUniform4fv(self, *args):
        return 

    def glUniform4iv(self, *args):
        return 

    def glUniform4uiv(self, *args):
        return 

    def glUniformBlockBinding(self, *args):
        return 

    def glUniformMatrix3fv(self, *args):
        return 

    def glUniformMatrix4fv(self, *args):
        return 

    def glUnmapBuffer(self, *args):
        return 0

    def glUseProgram(self, *args):
        return 

    def glValidateProgram(self, *args):
        return 

    def glVertexAttrib4f(self, *args):
        return 

    def glVertexAttrib4fv(self, *args):
        return 

    def glVertexAttribIPointer(self, *args):
        return 

    def glVertexAttribPointer(self, *args):
        return 

    def glViewport(self, *args):
        return 

    def gmtime(self, *args):
        return 0

    def inetaddr(self, *args):
        return 0

    def llvmehtypeidfor(self, *args):
        return 0

    def llvmexp2f32(self, *args):
        return 0

    def llvmlog10f32(self, *args):
        return 0

    def llvmlog10f64(self, *args):
        return 0

    def llvmlog2f32(self, *args):
        return 0

    def llvmtrap(self, *args):
        return 

    def llvmtruncf32(self, *args):
        return 0

    def localtime(self, *args):
        return 0

    def longjmp(self, *args):
        return 

    def mktime(self, *args):
        return 0

    def pthreadconddestroy(self, *args):
        return 0

    def pthreadcondinit(self, *args):
        return 0

    def pthreadcondtimedwait(self, *args):
        return 0

    def pthreadcondwait(self, *args):
        return 0

    def pthreadgetspecific(self, *args):
        return 0

    def pthreadkeycreate(self, *args):
        return 0

    def pthreadkeydelete(self, *args):
        return 0

    def pthreadmutexdestroy(self, *args):
        return 0

    def pthreadmutexinit(self, *args):
        return 0

    def pthreadmutexattrdestroy(self, *args):
        return 0

    def pthreadmutexattrinit(self, *args):
        return 0

    def pthreadmutexattrsetprotocol(self, *args):
        return 0

    def pthreadmutexattrsettype(self, *args):
        return 0

    def pthreadonce(self, *args):
        return 0

    def pthreadsetspecific(self, *args):
        return 0

    def schedyield(self, *args):
        return 0

    def setenv(self, *args):
        return 0

    def sigaction(self, *args):
        return 0

    def sigemptyset(self, *args):
        return 0

    def strftime(self, *args):
        return 0

    def sysconf(self, *args):
        return 0

    def time(self, *args):
        return 0

    def unsetenv(self, *args):
        return 0

    def utime(self, *args):
        return 0

    def f64rem(self, *args):
        return 0

    def invokeiiiiij(self, *args):
        return 0

    def invokeiiiijii(self, *args):
        return 0

    def invokeiiiijjii(self, *args):
        return 0

    def invokeiiiji(self, *args):
        return 0

    def invokeiiijiii(self, *args):
        return 0

    def invokeiij(self, *args):
        return 0

    def invokeiiji(self, *args):
        return 0

    def invokeiijii(self, *args):
        return 0

    def invokeijii(self, *args):
        return 0

    def invokej(self, *args):
        return 0

    def invokejdi(self, *args):
        return 0

    def invokeji(self, *args):
        return 0

    def invokejii(self, *args):
        return 0

    def invokejiii(self, *args):
        return 0

    def invokejiiii(self, *args):
        return 0

    def invokejiiiii(self, *args):
        return 0

    def invokejiiiiiiiiii(self, *args):
        return 0

    def invokejiiij(self, *args):
        return 0

    def invokejiiji(self, *args):
        return 0

    def invokejiji(self, *args):
        return 0

    def invokejijii(self, *args):
        return 0

    def invokejijiii(self, *args):
        return 0

    def invokejijj(self, *args):
        return 0

    def invokejji(self, *args):
        return 0

    def invokeviiiiiiifjjfii(self, *args):
        return 

    def invokeviiiijiiii(self, *args):
        return 

    def invokeviiij(self, *args):
        return 

    def invokeviiiji(self, *args):
        return 

    def invokeviij(self, *args):
        return 

    def invokeviiji(self, *args):
        return 

    def invokeviijji(self, *args):
        return 

    def invokeviji(self, *args):
        return 

    def invokevijii(self, *args):
        return 

    def atomicfetchadd8(self, *args):
        return 0

    def glClientWaitSync(self, *args):
        return 0
