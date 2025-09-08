# Pytest test functions for the argos module
#
# This script contains a few functions to test the features provided
# by the argos module. One issue is that what is returned by the
# server is time dependent; today you might get a different result
# than tomorrow. As a workaround the ArgosPlatformInfo class is
# subclassed ArgosPlatformInfoNoDownload to make it return a fixed
# string instead of querying the server. This allows to check for
# non-changing results. The test to access the server is done using
# the ArgosProgramInfo class, which is more stable over time.

# Run this script from the base directory. If you need to inspect
# using the debugger, run
# pytest --pdb.
# Also
# pytest -s
# can be useful to see the output of print statements.


if not __name__ == '__main__':
    from pytest import fixture
    import pytest
else:
    import logging
    logging.basicConfig(level=logging.ERROR)
    from argos.argosClient import logger as argos_logger
    argos_logger.setLevel(logging.DEBUG)
    
    def fixture(scope="module"):
        def decorator(func):
            def inner():
                return func()
            return inner()
        return decorator


from argos.argosMessage import ArgosMessageDecoder
from argos.argosClient import ArgosProgramInfo, ArgosPlatformInfo

@fixture()
def load_hexstring_data():
    data = {"260603":  dict(encoded='66CCE95B01B820FC7C06000501B7C7FC7C510006FFFFFFFFFFFF00000001E5',
                          decoded={'present_time': 1724705115.0, 'lat': 1126.72, 'lon': -2303.94,
                                   'fixtime': 5.0, 'latInvalid': 1125.83, 'lonInvalid': -2303.19,
                                   'fixtimeInvalid': 6.0, 'latToofar': -0.01, 'lonToofar': -0.01,
                                   'fixtimeToofar': 0.0, 'U': 0.0, 'V': 0.05, 'crc': True,
                                   'ctime': 'Mon Aug 26 20:45:15 2024'}),
            "amadeus": dict(encoded='66D30466FFFFFFFFFFFF100005B9F5FC7CC80400FFFFFFFFFFFF000000007E',
                            decoded={'present_time': 1725105254.0,
                                     'lat': -0.01,
                                     'lon': -0.01,
                                     'fixtime': 4096.0,
                                     'latInvalid': 3752.85,
                                     'lonInvalid': -2302.0,
                                     'fixtimeInvalid': 1024.0,
                                     'latToofar': -0.01,
                                     'lonToofar': -0.01,
                                     'fixtimeToofar': 0.0,
                                     'U': 0.0,
                                     'V': 0.0,
                                     'crc': False,
                                     'ctime': 'Sat Aug 31 11:54:14 2024'}),
            }
    return data

@fixture()
def load_xml_data():
    data = {
            '260603': {'present_time': 1757310599.0, 'lat': 1938.13, 'lon': -6512.85, 'fixtime': 1.0, 'latInvalid': 1935.89, 'lonInvalid': -6513.08,
                       'fixtimeInvalid': 3.0, 'latToofar': -0.01, 'lonToofar': -0.01, 'fixtimeToofar': -1.0, 'U': 0.0, 'V': 0.1, 'crc': True, 'date': '2025-09-08T05:49:59Z'}
            }
    return data

class ArgosPlatformInfoNoDownload(ArgosPlatformInfo):
    def __init__(self, wsdl=None, credentials=None):
        super().__init__(wsdl, credentials)

    def service_factory(self, wsdl):
        return self._service

    def _service(self, username=None, password=None, platformId=None, displayRawData=True, displayLocation=True, nbDaysFromNow=20):
        with open(f"tests/data/service-string_{platformId}.txt") as fp:
            data = fp.read()
        return data

def test_ArgosMessageDecoder_amadeus(load_hexstring_data):
    amd = ArgosMessageDecoder()
    data = load_hexstring_data["amadeus"]
    encoded = data["encoded"]
    decoded = amd(encoded)
    for key in decoded.keys():
        if key=="date":
            continue
        assert decoded[key] == data["decoded"][key]

def test_ArgosMessageDecoder_260603(load_hexstring_data):
    amd = ArgosMessageDecoder()
    data = load_hexstring_data["260603"]
    encoded = data["encoded"]
    decoded = amd(encoded)
    for key in decoded.keys():
        if key=="date":
            continue
        assert decoded[key] == data["decoded"][key]

def test_ArgosProgramInfo():
    api = ArgosProgramInfo(credentials='argos_login.txt')
    api.retrieve()
    programNumber = api.get_programs()[0]
    platformIds = api.get_platforms(programNumber)
    assert set(platformIds) == set(['27011', '30649', '260603', '260604', '260682'])

def test_ArgosProgramInfo_missing_credentials():
    with pytest.raises(FileNotFoundError):
        api = ArgosProgramInfo(credentials='no_argos_login.txt')

def test_ArgosPlatformInfo_260603(load_xml_data):
    api = ArgosPlatformInfoNoDownload(credentials='argos_login.txt')
    api.retrieve('260603', number_of_days_from_now=15)
    payload = api.get_info(latest_only=True)['payload']
    
    assert payload['gps_location'] == load_xml_data['260603']

def test_ArgosPlatformInfo_27011(load_xml_data):
    api = ArgosPlatformInfoNoDownload(credentials='argos_login.txt')
    api.retrieve('27011', number_of_days_from_now=15)
    payload = api.get_info(latest_only=True)['payload']
    
    assert payload == {}

