from  argos import argosClient

import logging
logging.basicConfig(level=logging.WARNING)
logger = argosClient.logger
logger.setLevel(logging.DEBUG)

api = argosClient.ArgosPlatformInfo(credentials="argos_login.txt")
api.retrieve(platformId='260603', number_of_days_from_now=20)

info = api.get_info(minimum_quality_flag=0)

print("Date                       latitude       longitude   CRC")
print("-----------------------------------------------------------")
for _info in info:
    if _info['gps_location']:
        print(f"{_info['gps_location']['date']:20}", end='')
        print(f"{_info['gps_location']['lat']:16.4f}", end='')
        print(f"{_info['gps_location']['lon']:16.4f}  ", end='')
        print(f"{_info['gps_location']['crc']}")
        
