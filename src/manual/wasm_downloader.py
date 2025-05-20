import requests
import gzip
import io
import numpy as np
import os
from urllib.parse import urljoin

class lok_files_downloader:

    def __init__(self, debug=False):
        self.session = requests.Session()
        r = self.session.get('https://play.leagueofkingdoms.com/')
        self.debug=debug
        self.get_version()

    def get_version(self):
        url_version = 'https://play.leagueofkingdoms.com/Build/webgl.json'
        r = self.session.get(url_version)
        js = r.json()
        self.dataurl = urljoin(url_version, js['dataUrl'] )
        self.wasmurl = urljoin(url_version, js['wasmCodeUrl'] )
        self.wasmframeurl = urljoin(url_version, js['wasmFrameworkUrl']) 

    def decompress_gzip_from_bytes(self, data):
        try:
            with gzip.GzipFile(fileobj=io.BytesIO(data)) as f:
                decompressed_data = f.read()
            return decompressed_data
        except Exception as e:
            print(f"An error occurred during decompression: {e}")
            return None

    def download(self, fileurl, filename):
        r = self.session.get(fileurl, headers={"credentials": "same-origin"})
        print(r.status_code)

        # Decompress the gzipped content directly from the response content
        if r.content.startswith(b'\x1f\x8b'):
            decompressed_data = self.decompress_gzip_from_bytes(r.content)
        else:
            return
        
        # Handle the decompressed data as needed
        if decompressed_data:
            with open(filename, 'wb') as ofile:
                ofile.write(decompressed_data)
                if self.debug:
                    test = np.frombuffer(bytearray(decompressed_data), dtype=np.uint8)
                    print(test[:20])
        else:
            print("Failed to decompress data")

if 1:
    lok = lok_files_downloader(True)
    # wasm file
    # lok.download(lok.wasmurl, os.path.join(*['testing',  'js_testing','test.wasm'])) 
    lok.download(lok.wasmurl, "/home/ytee/test/wasmtest/test.wasm")
    # # this is data file
    # lok.download(f'https://play.leagueofkingdoms.com/Build/{VERSION}.webgl.data.unityweb', os.path.join(*['testing',  'js_testing','test']))  
    # # this is the js file
    # lok.download(f'https://play.leagueofkingdoms.com/Build/{VERSION}.webgl.wasm.framework.unityweb', 'test') 

# 
def process_data(content):
    """
    This will parse data file into required format
    """
    # Create a DataView-like structure in Python
    n = memoryview(content)  # DataView equivalent in Python using memoryview
    o = 0
    i = "UnityWebData1.0\0"

    # Check if the data format is correct
    if ''.join(map(chr, content[o:o + len(i)])) != i:
        raise Exception("unknown data format")
    
    o += len(i)

    # Get the total size
    a = int.from_bytes(n[o:o + 4], 'little')  # getUint32 equivalent in Python
    o += 4

    while o < a:
        # Read s, d, and l values
        s = int.from_bytes(n[o:o + 4], 'little')
        o += 4
        d = int.from_bytes(n[o:o + 4], 'little')
        o += 4
        l = int.from_bytes(n[o:o + 4], 'little')
        o += 4

        # Get the string u
        fpath = ''.join(map(chr, content[o:o + l]))
        o += l
        
        print(fpath, s, d, l)
        fpath = os.path.join(*['testing',  'js_testing', 'JS_MOUNT2', fpath])
        folder = os.path.dirname(fpath)
        os.makedirs(folder, exist_ok=True)
        with open(fpath,'wb') as ofile:
            ofile.write(content[s:s + d])

# process_data(open(os.path.join(*['testing',  'js_testing','test']), 'rb').read())