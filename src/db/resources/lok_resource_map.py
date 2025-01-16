LOK_RESOURCE_MAP = {
 'Farm' :20100101,
 'Lumber' : 20100102,
 'Quarry' :20100103,
 'Gold': 20100104,
 'Crystal' : 20100105,
 'DSA' : 20100106,
 ###monster###
 'Orc': 20200101,
 'Skeleton': 20200102,
 'Golem': 20200103,
 'TreasureGoblin': 20200104,
 'Deathkar': 20200201,
 ###charm###
 'Normal': 20500101, 
 'Magic': 20500102,
 'Epic': 20500103,
 'Legend': 20500104,
}

CHARM_MAP = {
    'Harvester': 1,
    'Lumberjack': 2,
    'Stonecraft': 3,
    'Goldmine': 4,
    'Scholar': 5,
    'Resource': 6,  # gathering
    'Builder': 7,
    'Trainer': 8,
    'Stamina': 9,  # hp
    'Attacker': 10,
    'Speed': 11,
    'Load': 12,
    'Energy': 13,  # action point
    'Defender': 14,
}

LOK_RESOURCE_MAP_INVERSE = {v:k for k,v in LOK_RESOURCE_MAP.items()}

HEADER_MAP = {
    '201001': 'r', #resource
    '202001': 'm', #monster
    '205001': 'c', #charm
}

COMMAND_ABBREVIATION = {}
for k,v in LOK_RESOURCE_MAP.items():
    header=str(v)[:6]
    if header in HEADER_MAP:
        if HEADER_MAP.get(header) == 'c':
            continue
        new_id = '%s%s' % (HEADER_MAP.get(header), k[0].lower())
        COMMAND_ABBREVIATION[new_id] = v
