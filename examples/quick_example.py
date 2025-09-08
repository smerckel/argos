### Example that prints the last known information of id 260603.

from argos import argosClient

api = argosClient.ArgosPlatformInfo(credentials="/home/lucas/.local/share/argos/argos_login.txt")
api.retrieve(platformId=260603, number_of_days_from_now=20)
info = api.get_info(latest_only=True)
payload = info['payload']
print(payload)
