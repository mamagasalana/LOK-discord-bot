import aiohttp
import asyncio
import logging
import json
import gzip
import io
class WSClosedException(Exception):
    pass

logging.basicConfig(filename=f'logs/wss.log', level=logging.INFO, format='%(levelname)s %(asctime)s %(message)s')

from src.services.lok_service import LokService

a = LokService()
a.login()
token = a.accessToken

URL = f"wss://socf-lok-live.leagueofkingdoms.com/socket.io/?EIO=4&transport=websocket&token={token}"
async def run():
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(URL, heartbeat=1.0, autoping=True) as ws:
                    while True:
                        msg = await ws.receive()
                        if msg.type == aiohttp.WSMsgType.CLOSED:
                            raise WSClosedException
                        elif msg.data== '40':
                            # TODO: this input configuration could consist the x, y location
                            # sample from the game
                            await ws.send_str('42["/zone/leave/list/v2", {"world":66, "zones":"[0,64,1,65]"}]')
                            await ws.send_str('42["/zone/enter/list/v4", "VVZDX0cIDEdCAgUcDFQbWlVGRlJHIwcLCBYCRw0FB0hcVUkCHwMWFk0YAwxRW0lMBAIHAh1MDQAZV1FQTBgHAB8WKRYcFwcHCAhgSkBLDE4HTQ=="]')
                        elif msg.data.startswith('42'):
                            js = json.loads(msg.data[2:])
                            compressed_data = js[-1]['packs']
                            compressed_bytes = bytes(compressed_data)
                            with gzip.GzipFile(fileobj=io.BytesIO(compressed_bytes)) as f:
                                decompressed_data = f.read()
                            # TODO: do your stuff with decompressed data
                        else:
                            logging.info(msg.data)
        except WSClosedException:
            logging.warning('WS closed, retry in 5 seconds')
            await asyncio.sleep(5)
        except aiohttp.client_exceptions.ClientConnectorError:
            logging.warning('WS connection error, retry in 5 seconds')
            await asyncio.sleep(5)
        except:
            logging.warning('Unexpected exception', exc_info=True)
            await asyncio.sleep(5)


loop = asyncio.get_event_loop()
loop.create_task(run())
loop.run_forever()
