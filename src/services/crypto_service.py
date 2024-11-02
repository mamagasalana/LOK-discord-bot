import base64
import json
from services.wasm_service import wasm
import logging

class crypto:
    def __init__(self):
        self.wasm = wasm()
        self.salt = None
        self.accessToken = None

    def update_salt(self, regionhash):
        self.salt = self.wasm.get_salt(regionhash)
        logging.info("updated salt %s from %s" % (self.salt, regionhash))

    def update_token(self, token):
        self.accessToken = token
        logging.info("updated token %s " % token)
        
    def decryption(self, encrypted_text):
        ret = base64.b64decode(encrypted_text)

        salt_key = self.salt
        salt_key_length =len(salt_key)
        idx = 0
        out= []

        for value1 in ret:
            tmp = idx % salt_key_length
            result = value1 ^ salt_key[tmp]
            idx += 1
            out.append(result)

        return json.loads(bytes(out))

    def encryption(self, plain_text):
        if isinstance(plain_text, dict):
            plain_bytes = json.dumps(plain_text).encode('utf-8')
        else:
            plain_bytes = plain_text.encode('utf-8')
        
        salt_key = self.salt
        salt_key_length = len(salt_key)
        
        idx = 0
        encrypted_bytes = []

        for value1 in plain_bytes:
            tmp = idx % salt_key_length
            result = value1 ^ salt_key[tmp]
            idx += 1
            encrypted_bytes.append(result)
        
        encrypted_text = base64.b64encode(bytes(encrypted_bytes))
        return encrypted_text.decode('utf-8')