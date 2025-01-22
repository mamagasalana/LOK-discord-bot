
import logging
import json
import asyncio
from db.resources.mine import Mine
from services.lok_service import LokService
from services.resourcefinder_service import ResourceFinder

LOGIN_CONFIG = json.load(open('src/cache/LOGIN.json'))
MAX_RUNNER =2 
class LokServiceManager:
    def __init__(self, debug=False):
        self.workers : dict[str, LokService]  = {}
        if debug:
            return
        for itm in LOGIN_CONFIG:
            self.workers[itm['BOT']] = LokService(itm['USER'], itm['PASSWORD'], itm['BOT'], itm['rest'])
                
    def get_worker_status(self) :
        return {k: worker.status for k, worker in self.workers.items()}
    
    def get_worker(self, botname) -> LokService:
        return self.workers.get(botname)

    @property
    def get_active_workers(self):
        return [worker for worker in self.workers.values() if not worker.resting]
    
    def switch_world(self, world):
        for worker in self.workers.values():
            worker.switch_world(world)

    def check_entire_map(self, start_x = 0, start_y=2048, end_x=63, end_y=4096):
        #only covers top half of the map, y from 2048
        ret = []
        for y in range(start_y, end_y, 192):
            for x in range(start_x, end_x, 3):
                ret.append(ResourceFinder.zone_adjacent(x+y+65))
        
        active_workers = self.get_active_workers
        part_size = len(ret) // len(active_workers) +1
        for idx, worker in enumerate(active_workers):
            worker.wss.pending_task.extend(
                ret[idx*part_size: (idx+1)*part_size])
        
    async def start_wss(self):
        Mine.delete().execute() #empty database

        # only run active worker
        workers = [ worker for worker in self.workers.values()
                   if worker.wss.pending_task]
        for idx in range(0, len(workers), MAX_RUNNER):
            func_list = []
            for worker in workers[idx: idx+MAX_RUNNER]:
                func_list.append(worker.start_wss())
            await asyncio.gather(*func_list)
            await asyncio.sleep(10)


if __name__ == "__main__":
    import logging
    logging.basicConfig(
        filename="logs/wss2.log",
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    import asyncio
    loop = asyncio.get_event_loop()

    if 0:
        a = LokServiceManager(True)
    else:
        a = LokServiceManager()
        a.check_entire_map()
    # Schedule the task
    # a.check_entire_map()
    
        task = loop.create_task(a.start_wss())

        # Run until the task is complete
        result = loop.run_until_complete(task)
