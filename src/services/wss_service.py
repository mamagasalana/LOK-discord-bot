import aiohttp
import asyncio
import logging
import json
import gzip
import io
from services.crypto_service import crypto
from db.resources.mine import Mine
from services.resourcefinder_service import ResourceFinder
import datetime
from collections import deque
import time
from config.logger import setup_logger
import base64
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
    def __init__(self, service:crypto, world=24, logger_name='wss', sleep_interval: int =0):
        """
        sleep_interval : time taken between user movement simulation
        """
        self.service = service
        self.session = None # Reuse session
        self.loop = asyncio.get_event_loop()
        self.sleep_interval = sleep_interval 

        self.last_zone = []
        self.wip_zone = deque()
        self.pending_task = deque()
        self.world = int(world)
        self.signal_stop = False
        self.signal_remaining = 999
        self.logger = setup_logger(logger_name, "logs/wss.log", level=logging.DEBUG)

    @property
    def bot_origin_world(self):
        header, payload, signature = self.token.split('.')
        payload += '=' * ((4 - len(payload) % 4) % 4)  # Pad with '=' to make the base64 string length a multiple of 4
        payload = base64.urlsafe_b64decode(payload)  # Decode base64
        decoded_jwt = json.loads(payload)  # Convert JSON to Python dictionary
        return int(decoded_jwt['worldId'])
    
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
    def field_leave(self):
        ret = '42["/field/leave", {"token":"%s"}]' % self.token
        self.logger.debug("send %s" % ret)
        return ret
    
    @property
    def world_visit(self):
        data = {'token': self.token, 'worldId': self.world}
        encrypted_data = self.service.encryption(data)
        ret = f'42["/world/visit/v3", "{encrypted_data}"]'
        self.logger.debug("send %s" % ret)
        return ret
    
    
    def zone_leave(self, world:int):
        ret= '42["/zone/leave/list/v2", {"world":%s, "zones":"%s"}]' % (world, json.dumps(self.last_zone))
        self.logger.debug("send %s" % (ret))
        return ret

    def zone_enter(self, zonelist:list, world:int):
        self.wip_zone.append(zonelist)
        self.last_zone = zonelist
        data = {"world":world, "zones": json.dumps(self.last_zone),"compType":3}
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
                    charmcode = -1
                    if 'param' in x:
                        if 'charmCode' in x['param']:
                            charmcode = int(str(x['param']['charmCode'])[:-2])
                    out2.append({
                        'expiry': datetime.datetime.strptime(x.get('expired')[:19], '%Y-%m-%dT%H:%M:%S'),
                        'date': datetime.datetime.now(),
                        '_id': x.get('_id'),
                        'level': x.get('level'),
                        'code': x.get('code'),
                        'extra': json.dumps(x),
                        'charmcode' : charmcode,
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
        finally:
            self.signal_remaining -=1

    async def create_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession() 

    async def send_custom_ping(self, ws):
        while True:
            await asyncio.sleep(25)  
            try:
                await ws.send_str('2')  # Send custom ping
            except asyncio.CancelledError:
                print("Ping task cancelled.")
                return
            except Exception as e:
                print(f"Failed to send ping: {e}")
                return  
            
    async def send_user_movement(self, ws):
        if int(self.world) != self.bot_origin_world:
            # switch world if world not 26
            while self.signal_remaining:
                await asyncio.sleep(0.1)

            await ws.send_str(self.field_leave)
            await ws.send_str(self.world_visit)
            self.signal_remaining = 999

        while self.pending_task:
            await asyncio.sleep(self.sleep_interval)  

            while self.signal_remaining:
                await asyncio.sleep(0.1)

            try:
                newzone = self.pending_task.popleft()
                await ws.send_str(self.zone_leave(self.world))
                await ws.send_str(self.zone_enter(newzone, self.world))
                self.signal_remaining +=1
            except asyncio.CancelledError:
                print("All task cancelled.")
                return
            except Exception as e:
                print(f"Failed to send ping: {e}")
                return  
            
    async def connect(self):
        """Connects to the WebSocket with retry logic."""
        await self.create_session()
        SUCCESS = False
        while not self.signal_stop:
            for zone in self.wip_zone:
                self.pending_task.appendleft(zone)
            self.wip_zone.clear()
            self.last_zone = []

            try:
                async with self.session.ws_connect(self.url, headers=WSS_HEADER, heartbeat=None, autoping=False) as ws:
                    ping_task = asyncio.create_task(self.send_custom_ping(ws))
                    movement_task = asyncio.create_task(self.send_user_movement(ws)) 
                    SUCCESS = await self.listen(ws)
                    
            except WSClosedException:
                logging.warning("WS closed, retrying in 5 seconds")
            except aiohttp.ClientConnectorError:
                logging.warning("WS connection error, retrying in 5 seconds")
            except aiohttp.WSServerHandshakeError as e:
                logging.warning(f"Handshake failed: {e}, retrying in 5 seconds")
            except Exception as e:
                logging.warning(f"Unexpected exception: {e}", exc_info=True)
            finally:
                if 'ping_task' in locals():
                    ping_task.cancel()
                if 'movement_task' in locals():
                    movement_task.cancel()

            await asyncio.sleep(2)  # Wait before retrying

        return SUCCESS
    
    async def listen(self, ws):
        """Handles incoming WebSocket messages."""

        async for msg in ws:
            self.logger.debug(msg.data[:40])

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
                #this is 'pong' from 2
                pass

            elif msg.data.startswith('42'):
                if '/field/enter/v3' in msg.data:
                    data = msg.data[2:]
                    js = await self.field_enter_out(data)
                    # receive response from initialize
                    world = js['loc'][0]
                    await ws.send_str(self.zone_leave(world))
                    await ws.send_str(self.zone_enter([0, 64, 1, 65], world))
                    await ws.send_str(self.zone_leave(world))
                    castle_location = ResourceFinder.zone_adjacent(ResourceFinder.zone_from_xy(js['loc'][1], js['loc'][2]))
                    await ws.send_str(self.zone_enter(castle_location, world))
                    self.signal_remaining = 2

                elif '/world/visit/v3' in msg.data:
                    data = msg.data[2:]
                    js = await self.field_enter_out(data)
                    world = js['loc'][0]
                    self.last_zone = []   #reset upon world switch
                    await ws.send_str(self.zone_leave(world))
                    castle_location = ResourceFinder.zone_adjacent(ResourceFinder.zone_from_xy(js['loc'][1], js['loc'][2]))
                    await ws.send_str(self.zone_enter(castle_location, world))
                    self.signal_remaining = 1

                elif '/field/objects/v4' in msg.data:
                    data = msg.data[2:]
                    await self.field_object(data)

                elif '/march/objects' in msg.data:
                    if not self.pending_task and not self.signal_remaining:
                        self.signal_stop = True
                        logging.info("wss finish updating mine database")
                        break

            else:
                logging.warning("unhandled msg")

        return True
    async def main(self):
        self.signal_stop = False
        SUCCESS = await self.connect()  
        await self.session.close()
        return SUCCESS

if __name__ == '__main__':
    user = "teezai4"
    CACHED_LOGIN = f"src/cache/{user}.json"
    with open(CACHED_LOGIN, 'r') as ifile:
        js = json.load(ifile)
    accessToken = js.get("token")
    regionHash = js.get("regionHash")
    a = crypto()
    a.update_salt(regionHash)
    a.update_token(accessToken)
    wss = LOKWSS(a, world=24, logger_name=user, sleep_interval=1)
    # wss = LOKWSS(a, logger_name=user, sleep_interval=1)
    wss.pending_task.extend([ [0, 64, 1, 65], [2060, 2124, 2188, 2061, 2125, 2189, 2062, 2126, 2190]])
    # asyncio.run(wss.main())