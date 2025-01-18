
from db.resources.mine import Mine, UserLocation
from typing import Union

class ResourceFinder:
    @staticmethod
    def set_user_location(discord_id, x, y):
        entry = [{'_id': discord_id, 'x': x, 'y': y,}]
        qry = UserLocation.insert_many(entry).on_conflict_replace()
        qry.execute()

    @staticmethod
    def get_mine(mine_id= 20100105, level=1):
        """
        crystal mine id 'fo_20100105'
        """
        r = Mine.select().where(#(Mine.expiry > datetime.datetime.now()) 
                                # & (Mine.date > dt)
                                 (Mine.code ==mine_id)
                                & (Mine.level >=level)
                                & (Mine.occupied== False))
        return r
    
    @staticmethod
    def get_charm(charm_id, level=1):
        r = Mine.select().where(#(Mine.expiry > datetime.datetime.now()) 
                                # & (Mine.date > dt)
                                 (Mine.charmcode ==charm_id)
                                & (Mine.level >=level))
        return r
    
    @staticmethod
    def get_mine_for_user(discord_user_id, mine_id: Union[list, list[int]], levels: Union[list, list[int]]):
        mines = Mine.select().where(
            (
                (Mine.code.in_(mine_id)) if isinstance(levels, list) else (Mine.code == mine_id)
            )
                &
            (
                (Mine.level.in_(levels)) if isinstance(levels, list) else (Mine.level >= levels)
            )
        )
        u = UserLocation.select().where(UserLocation._id == discord_user_id).first()
        
        if not mines:
            return 
        
        if u:
            get_distance = lambda x, y: ((x-u.x )**2+(y-u.y)**2)**0.5
            sorted_mines = sorted(mines, key=lambda x: get_distance(x.x, x.y))
            for idx in range(0, len(sorted_mines), 10):
                yield sorted_mines[idx: idx+10]
        else:
            for idx in range(0, len(mines), 10):
                yield mines[idx: idx+10]

    @staticmethod
    def get_charm_for_user(discord_user_id, charm_id: Union[list, list[int]], levels: Union[list, list[int]]):
        charms = Mine.select().where(
            (
                (Mine.charmcode.in_(charm_id)) if isinstance(levels, list) else (Mine.charmcode == charm_id)
            )
            &
            (
                (Mine.level.in_(levels)) if isinstance(levels, list) else (Mine.level >= levels)
            )
        )
        u = UserLocation.select().where(UserLocation._id == discord_user_id).first()
        
        if not charms:
            return 
        
        if u:
            get_distance = lambda x, y: ((x-u.x )**2+(y-u.y)**2)**0.5
            sorted_charms = sorted(charms, key=lambda x: get_distance(x.x, x.y))
            for idx in range(0, len(sorted_charms), 10):
                yield sorted_charms[idx: idx+10]
        else:
            for idx in range(0, len(charms), 10):
                yield charms[idx: idx+10]