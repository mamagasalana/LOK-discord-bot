import requests
import gzip
import io
import numpy as np

class lok_files_downloader:

    def __init__(self):
        self.session = requests.Session()
        r = self.session.get('https://play.leagueofkingdoms.com/')

    def decompress_gzip_from_bytes(self, data):
        try:
            with gzip.GzipFile(fileobj=io.BytesIO(data)) as f:
                decompressed_data = f.read()
            return decompressed_data
        except Exception as e:
            print(f"An error occurred during decompression: {e}")
            return None

    def download(self, fileurl, filename, debug=False):
        r = self.session.get(fileurl, headers={"credentials": "same-origin"})
        print(r.status_code)

        # Decompress the gzipped content directly from the response content
        if r.content.startswith(b'\x1f\x8b'):
            decompressed_data = self.decompress_gzip_from_bytes(r.content)
        else:
            test = np.frombuffer(bytearray(r.content), dtype=np.uint8)
            print(test[:20])

        # Handle the decompressed data as needed
        if decompressed_data:
            with open(filename, 'wb') as ofile:
                ofile.write(decompressed_data)
                if debug:
                    test = np.frombuffer(bytearray(decompressed_data), dtype=np.uint8)
                    print(test[:20])
        else:
            print("Failed to decompress data")


lok = lok_files_downloader()
lok.download('https://play.leagueofkingdoms.com/Build/625145317.webgl.wasm.code.unityweb', 'test.wasm')
lok.download('https://play.leagueofkingdoms.com/Build/625145317.webgl.data.unityweb', 'test')
lok.download('https://play.leagueofkingdoms.com/Build/625145317.webgl.wasm.framework.unityweb', 'test')
lok.download('https://play.leagueofkingdoms.com/Build/webgl.json', 'test')