import datetime
import logging
import json
import asyncio
from db.resources.mine import Mine, UserLocation
import time
from services.lok_service import LokService

LOGIN_CONFIG = json.load(open('LOGIN.json'))
MAX_RUNNER =2 
class LokServiceManager:
    def __init__(self, debug=False):
        self.workers : dict[str, LokService]  = {}
        if debug:
            return
        for itm in LOGIN_CONFIG:
            self.workers[itm['BOT']] = LokService(itm['USER'], itm['PASSWORD'], itm['BOT'])
    
    def set_user_location(self, discord_id, x, y):
        entry = [{'_id': discord_id, 'x': x, 'y': y,}]
        qry = UserLocation.insert_many(entry).on_conflict_ignore()
        qry.execute()
            
    def get_worker_status(self) :
        return {k: worker.status for k, worker in self.workers.items()}
    
    def get_worker(self, botname) -> LokService:
        return self.workers.get(botname)

    def zone_from_xy(self, x, y):
        if (2048 > x >= 0) and (2048 > y >= 0):
            return int(x/32) + int(y/32)*64
        return -1
        
    def zone_adjacent(self, zone):
        fx = lambda x: [x-64, x , x +64]
        
        if zone % 64 == 0:
            # left edge
            out = fx(zone) + fx(zone+1)
        elif zone % 63 == 0:
            # right edge
            out = fx(zone-1) + fx(zone)
        else:
            out = fx(zone-1) + fx(zone) + fx(zone+1) 
        return [x for x in out if  4096 > x >=0 ]
    
    def check_entire_map(self, start_x = 0, start_y=2048, end_x=63, end_y=4096):
        #only covers top half of the map, y from 2048
        ret = []
        for y in range(start_y, end_y, 192):
            for x in range(start_x, end_x, 3):
                ret.append(self.zone_adjacent(x+y+65))
        
        part_size = len(ret) // len(self.workers) +1
        for idx, worker in enumerate(self.workers.values()):
            worker.wss.pending_task.extend(
                ret[idx*part_size: (idx+1)*part_size])
        
    async def start_wss(self):
        Mine.delete().execute() #empty database
        workers = list(self.workers.values())
        for idx in range(0, len(workers), MAX_RUNNER):
            func_list = []
            for worker in workers[idx: idx+MAX_RUNNER]:
                func_list.append(worker.start_wss())
            await asyncio.gather(*func_list)
            await asyncio.sleep(10)

    def get_mine(self, dt, mine_id= 20100105, level=1):
        """
        crystal mine id 'fo_20100105'
        """
        r = Mine.select().where((Mine.expiry > datetime.datetime.now()) 
                                # & (Mine.date > dt)
                                & (Mine.code ==mine_id)
                                & (Mine.level >=level)
                                & (Mine.occupied== False))
        return r
    
    def get_mine_for_user(self, discord_user_id, dt, mine_id, level):
        mines = self.get_mine(dt, mine_id, level)
        u = UserLocation.select().where(UserLocation._id == discord_user_id).first()
        
        if not mines:
            return None
        
        if u:
            get_distance = lambda x, y: ((x-u.x )**2+(y-u.y)**2)**0.5
            sorted_mines = sorted(mines, key=lambda x: get_distance(x.x, x.y))
            for idx in range(0, len(sorted_mines), 10):
                yield sorted_mines[idx: idx+10]
        else:
            for idx in range(0, len(mines), 10):
                yield mines[idx: idx+10]


if __name__ == "__main__":
    import logging
    logging.basicConfig(
        filename="logs/wss2.log",
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    import asyncio
    loop = asyncio.get_event_loop()

    if 1:
        a = LokServiceManager(True)
    else:
        a = LokServiceManager()
        a.check_entire_map()
    # Schedule the task
    # a.check_entire_map()
    
        task = loop.create_task(a.start_wss())

        # Run until the task is complete
        result = loop.run_until_complete(task)
    from db.resources.lok_resource_map import LOK_RESOURCE_MAP
    resources = 'Crystal'
    mine_id = LOK_RESOURCE_MAP.get(resources)
    level = 1
    b = a.get_mine(datetime.datetime(2024, 12,13), mine_id=mine_id, level=1)
    my_location = (287, 1078)
    dist = ([ (x.x, x.y, ((x.x-my_location[0])**2+(x.y-my_location[1])**2)**0.5)  
           for x in b if (x.level==level)])

    print(f'{resources}{level}')
    sorted_dist = sorted(dist, key=lambda x:x[-1])
    for d in sorted_dist[0:10]:
        print(d)
