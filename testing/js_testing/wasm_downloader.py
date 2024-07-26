import requests
import gzip
import io

def decompress_gzip_from_bytes(data):
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(data)) as f:
            decompressed_data = f.read()
        return decompressed_data
    except Exception as e:
        print(f"An error occurred during decompression: {e}")
        return None

session = requests.Session()

r = session.get('https://play.leagueofkingdoms.com/')
print(r)

r = session.get('https://play.leagueofkingdoms.com/Build/625145317.webgl.wasm.code.unityweb', headers={"credentials": "same-origin"})
print(r.status_code)

# Decompress the gzipped content directly from the response content
decompressed_data = decompress_gzip_from_bytes(r.content)

# Handle the decompressed data as needed
if decompressed_data:
    with open('test.wasm', 'wb') as ofile:
        ofile.write(decompressed_data)
else:
    print("Failed to decompress data")
