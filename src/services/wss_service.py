import aiohttp
import asyncio
import logging
import json
import gzip
import io
from services.crypto_service import crypto
from db.resources.mine import Mine
import datetime
from collections import deque
import time
from config.logger import setup_logger

class WSClosedException(Exception):
    pass

WSS_HEADER = {
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    "Cache-Control": "no-cache",
    "Connection": "Upgrade",
    "Host": "socf-lok-live.leagueofkingdoms.com",
    "Origin": "https://play.leagueofkingdoms.com",
    "Pragma": "no-cache",
    "Upgrade": "websocket",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

class LOKWSS:
    def __init__(self, service:crypto, world=26, logger_name='wss'):
        self.service = service
        self.session = None # Reuse session
        self.loop = asyncio.get_event_loop()
        
        self.last_zone = []
        self.wip_zone = deque()
        self.pending_task = deque()
        self.world = world
        self.signal_stop = False
        self.logger = setup_logger(logger_name, "logs/wss.log", level=logging.DEBUG)

    @property
    def token(self):
        return self.service.accessToken
    
    @property
    def url(self):
        return f"wss://socf-lok-live.leagueofkingdoms.com/socket.io/?EIO=4&transport=websocket&token={self.service.accessToken}"
        
    @property
    def field_enter(self):
        data =  {"token": self.token}
        encrypted_data = self.service.encryption(data)
        ret = f'42["/field/enter/v3", "{encrypted_data}"]'
        self.logger.debug("send %s" % ret)
        return ret
    
    @property
    def zone_leave(self):
        data = {"world":self.world, "zones": json.dumps(self.last_zone)}
        ret=  f'42["/zone/leave/list/v2", "{json.dumps(data)}"]'
        self.logger.debug("send %s %s" % (json.dumps(data), ret))
        return ret

    def zone_enter(self, zonelist:list):
        self.wip_zone.append(self.last_zone)
        new_zone  = zonelist
        self.last_zone = new_zone
        data = {"world":self.world, "zones": json.dumps(self.last_zone),"compType":3}
        encrypted_data = self.service.encryption(data)
        ret = f'42["/zone/enter/list/v4", "{encrypted_data}"]'
        self.logger.debug("send %s %s" % (json.dumps(data), ret))
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
            zone = self.wip_zone.popleft() # done
            self.logger.debug("decompressing zone %s" % zone)

            js = json.loads(data)
            compressed_data = js[-1]['packs']
            compressed_bytes = bytes(compressed_data)
            with gzip.GzipFile(fileobj=io.BytesIO(compressed_bytes)) as f:
                decompressed_data = f.read()
            
            out = self.service.decryption(decompressed_data)
            out2 = []
            for x in out['objects']:
                if x.get('expired'):
                    out2.append({
                        'expiry': datetime.datetime.strptime(x.get('expired')[:19], '%Y-%m-%dT%H:%M:%S'),
                        'date': datetime.datetime.now(),
                        '_id': x.get('_id'),
                        'level': x.get('level'),
                        'code': x.get('code'),
                        'extra': json.dumps(x),
                        'state': x.get('state'),
                        'world': x.get('loc')[0],
                        'x': x.get('loc')[1],
                        'y': x.get('loc')[2],
                        'occupied': 'occupied' in x
                    })

            if out2:
                qry = Mine.insert_many(out2).on_conflict_ignore()
                qry.execute()
            
            

        except Exception as e:
            logging.warning(f"Failed to decompress data: {e}", exc_info=True)

    async def create_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession() 

    async def connect(self):
        """Connects to the WebSocket with retry logic."""
        await self.create_session()
        SUCCESS = False
        while not self.signal_stop:
            self.wip_zone.clear()
            if self.last_zone:
                self.pending_task.appendleft(self.last_zone)
            self.last_zone = []

            try:
                async with self.session.ws_connect(self.url, headers=WSS_HEADER, heartbeat=1.0, autoping=True) as ws:
                    SUCCESS = await self.listen(ws)
            except WSClosedException:
                logging.warning("WS closed, retrying in 5 seconds")
            except aiohttp.ClientConnectorError:
                logging.warning("WS connection error, retrying in 5 seconds")
            except aiohttp.WSServerHandshakeError as e:
                logging.warning(f"Handshake failed: {e}, retrying in 5 seconds")
            except Exception as e:
                logging.warning(f"Unexpected exception: {e}", exc_info=True)
            
            await asyncio.sleep(2)  # Wait before retrying

        return SUCCESS
    async def listen(self, ws):
        """Handles incoming WebSocket messages."""
        init = False
        start =  time.time()
        # send 2 every 30 seconds
        pause = False

        async for msg in ws:
            self.logger.debug(msg.data[:40])
            if time.time() - start >30:
                start = time.time()
                pause = True
                await ws.send_str('2')

            if msg.type == aiohttp.WSMsgType.CLOSED:
                raise WSClosedException("WebSocket connection closed by server.")
            elif msg.type == aiohttp.WSMsgType.ERROR:
                raise WSClosedException("Unknown error.")
            elif msg.data.startswith('0'):
                pass
            elif msg.data == '40':
                # initialize
                await ws.send_str(self.field_enter)
            elif msg.data == '41':
                # unauthorized, need to login and reboot session
                self.signal_stop = True
                logging.error("unauthorized, kindly restart login session")
                return False
            elif msg.data == '3':
                pause = False
                if self.pending_task:
                    newzone = self.pending_task.popleft()
                    await ws.send_str(self.zone_leave)
                    await ws.send_str(self.zone_enter(newzone))

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
                    data = msg.data[2:]
                    await self.field_object(data)

                elif '/march/objects' in msg.data:
                    if not init:
                        init = True
                    elif pause:
                        continue
                    elif self.pending_task:
                        newzone = self.pending_task.popleft()
                        await ws.send_str(self.zone_leave)
                        await ws.send_str(self.zone_enter(newzone))
                    else:
                        self.signal_stop = True
                        logging.info("wss finish updating mine database")
                        break
                        # await asyncio.sleep(1)
                        # await ws.send_str("2") 
            else:
                logging.warning("unhandled msg")

        return True
    async def main(self):
        self.signal_stop = False
        SUCCESS = await self.connect()  
        await self.session.close()
        return SUCCESS
