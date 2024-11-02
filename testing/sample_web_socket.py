import aiohttp
import asyncio
import logging
import json
import gzip
import io
import sys
import os

class WSClosedException(Exception):
    pass

if not os.path.isdir('logs'):
    os.mkdir('logs')

if os.path.exists("logs/wss.log"):
    os.remove("logs/wss.log")
logging.basicConfig(filename=f'logs/wss.log', level=logging.DEBUG, format='%(levelname)s %(asctime)s %(message)s')

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from services.lok_service import LokService

class lok_wss:
    def __init__(self, service:LokService):
        self.service = service
        self.token = service.accessToken

        self.url = f"wss://socf-lok-live.leagueofkingdoms.com/socket.io/?EIO=4&transport=websocket&token={ self.token}"
        
        self.session = None # Reuse session
        self.loop = asyncio.get_event_loop()
        self.loc = {}
        self.loc2 = {}
        self.last_zone = []
        self.pending_task = []
        self.world = 26

    def zone_from_xy(self, x, y):
        if (2048 > x >= 0) and (2048 > y >= 0):
            return int(x/32) + int(y/32)*64
        return -1
        
    def zone_adjacent(self, zone):
        fx = lambda x: [x-64, x , x +64]
        out = fx(zone-1) + fx(zone) + fx(zone+1)
        return [x for x in out if  4096 > x >=0 ]
    
    @property
    def field_enter(self):
        data =  {"token": self.token}
        encrypted_data = self.service.encryption(data)
        ret = f'42["/field/enter/v3", "{encrypted_data}"]'
        logging.info("send %s",ret)
        return ret
    
    @property
    def zone_leave(self):
        data = {"world":self.world, "zones": json.dumps(self.last_zone)}
        ret=  f'42["/zone/leave/list/v2", "{json.dumps(data)}"]'
        logging.info("send %s",ret)
        return ret

    def zone_enter(self, zonelist:list):
        new_zone  = zonelist
        self.last_zone = new_zone
        data = {"world":self.world, "zones": json.dumps(self.last_zone),"compType":3}
        encrypted_data = self.service.encryption(data)
        ret = f'42["/zone/enter/list/v4", "{encrypted_data}"]'
        logging.info("send %s", ret)
        return ret

    async def field_enter_out(self, data):
        try:
            js = json.loads(data)
            encrypted_data = js[-1]
            out = self.service.decryption(encrypted_data)
            return out
        except Exception as e:
            logging.warning(f"Failed to decompress data: {e}", exc_info=True)

    async def field_object(self, data):
        """Handles decompression and processing of compressed data."""
        try:
            js = json.loads(data)
            compressed_data = js[-1]['packs']
            compressed_bytes = bytes(compressed_data)
            with gzip.GzipFile(fileobj=io.BytesIO(compressed_bytes)) as f:
                decompressed_data = f.read()
            
            out = self.service.decryption(decompressed_data)

            idx = len(self.loc2)+1
            for k in self.last_zone:
                self.loc[k] = idx
            self.loc2[idx] = out
            
        except Exception as e:
            logging.warning(f"Failed to decompress data: {e}", exc_info=True)

    async def create_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession() 

    async def connect(self):
        """Connects to the WebSocket with retry logic."""
        await self.create_session()
        while True:
            try:
                async with self.session.ws_connect(self.url, heartbeat=1.0, autoping=True) as ws:
                    await self.listen(ws)
            except WSClosedException:
                logging.warning("WS closed, retrying in 5 seconds")
            except aiohttp.ClientConnectorError:
                logging.warning("WS connection error, retrying in 5 seconds")
            except aiohttp.WSServerHandshakeError as e:
                logging.warning(f"Handshake failed: {e}, retrying in 5 seconds")
            except Exception as e:
                logging.warning(f"Unexpected exception: {e}", exc_info=True)
            await asyncio.sleep(5)  # Wait before retrying

    async def listen(self, ws):
        """Handles incoming WebSocket messages."""
        async for msg in ws:
            # logging.info(msg.data)
            if msg.type == aiohttp.WSMsgType.CLOSED:
                raise WSClosedException("WebSocket connection closed by server.")
            elif msg.data == '40':
                # initialize
                await ws.send_str(self.field_enter)
            elif msg.data.startswith('42'):
                if '/field/enter/v3' in msg.data:
                    data = msg.data[2:]
                    js = await self.field_enter_out(data)
                    # receive response from initialize
                    await ws.send_str(self.zone_leave)
                    await ws.send_str(self.zone_enter([0, 64, 1, 65]))
                    await ws.send_str(self.zone_leave)
                    await ws.send_str(self.zone_enter(js['loc']))

                elif '/field/objects/v4' in msg.data:
                    # real loop starts
                    data = msg.data[2:]
                    await self.field_object(data)
                    await ws.send_str("2") 
            elif msg.data == '3':
                if not self.pending_task:
                    logging.info("no pending task")
                    await asyncio.sleep(2)
                    await ws.send_str("2") 
                else:
                    #TODO: clean pending task
                    await ws.send_str(self.zone_leave)
                    await ws.send_str(self.zone_enter([0, 64, 1, 65])) # change this to new zone
            else:
                logging.warning("unhandled msg")
                

    def main(self):
        try:            
            self.loop.create_task(self.connect())
            self.loop.run_forever()
        except:
            logging.error('wss something wrong?', exc_info=True)
        finally:
            self.loop.run_until_complete(self.session.close())
            self.loop.close()

if __name__ == '__main__':
    a = LokService()
    wss = lok_wss(a)
    wss.main()