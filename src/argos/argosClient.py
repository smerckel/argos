import logging
import re
import os
from itertools import chain

import zeep
import xml.etree.ElementTree as ET
from . import argosMessage

logger = logging.getLogger("Argos")

CRC = 2
BESTMGS = 1



class CredentialsReader:
    """ Class to read username, password and url from file

    Parameters
    ----------
    filename : str
        Filename of configuration file

    The priority list is as follows:
     - current working directory
     - $HOME/.local/share/argos

    If the file does not exist in either directory, a FileNotFoundError is thrown.
    """
    
    PATH = os.path.join(os.environ["HOME"], ".local", "share", "argos")
    def __init__(self, filepath):
        self.filepath = filepath
        self.wsdl = None
        self.username = None
        self.password = None
        self._check_path()
        self._open_config()

    def _check_path(self):
        if not os.path.exists(CredentialsReader.PATH):
            raise FileNotFoundError(f"The path {CredentialsReader.PATH} does not exist.")

    def _open_config(self):
        tried_paths = []
        for p in [self.filepath, os.path.join(CredentialsReader.PATH, self.filepath)]:
            logger.debug(f"Trying credential file {p}...")
            try:
                with open(p, 'r') as fp:
                    self._read_config(fp)
            except FileNotFoundError:
                tried_paths.append(p)
            else:
                tried_paths=[]
                break
                
        if tried_paths:
            raise FileNotFoundError("No credential files were not found.")
                
        
    def _read_config(self, fp):
        for line in fp:
            # Strip whitespace and ignore comments
            line = line.strip()
            if line.startswith("#") or not line:
                continue

            # Match the username and password patterns
            username_match = re.match(r'^username\s*=\s*(.*)$', line, re.IGNORECASE)
            password_match = re.match(r'^password\s*=\s*(.*)$', line, re.IGNORECASE)
            wsdl_match = re.match(r'^wsdl\s*=\s*(.*)$', line, re.IGNORECASE)

            if username_match:
                self.username = self._extract_value(username_match.group(1))
            elif password_match:
                self.password = self._extract_value(password_match.group(1))
            elif wsdl_match:
                self.wsdl = self._extract_value(wsdl_match.group(1))

        # Ensure both username and password were found
        if self.wsdl is None:
            raise ValueError("The configuration file must contain at least wsdl info, and ideally also username and password.")
    
    def _extract_value(self, value):
        # Strip the surrounding quotes if present
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            return value[1:-1]
        # Check for spaces if no quotes
        if ' ' in value:
            raise ValueError(f"Invalid value '{value}'. Values without quotes cannot contain spaces.")
        return value

    def get_credentials(self):
        """ Returns username, password and url from file

        Returns
        -------
        (str, str, str)
            username, password, and url

        """
        return self.username, self.password, self.wsdl


class ArgosProgramInfo(object):
    ''' Class to retrieve information on argos programmes.

    The class offers a get_programs() method, which returns all valid program numbers.
    THe get_platforms() method returns for all known platforms for a given program number.

    Parameters
    ----------
    wsdl : string
        url of the webservice
    credentials : string or None
        filename with credentials

    The credentials file is expected to contain three lines, not starting with #
    username = "user"
    password = "something secret"
    wsdl = "https://some/web/serice/"

    The username and password are optional, but would need to supplied in the script.
    '''
   
    def __init__(self, wsdl="", credentials=None):
        if credentials:
            cr = CredentialsReader(credentials)
            self.username, self.password, wsdl = cr.get_credentials()
        else:
            self.username, self.password = None, None
        self.service = self.service_factory(wsdl)
        self.info_dict={}
        
        
    def service_factory(self, wsdl):
        client = zeep.Client(wsdl=wsdl)
        service = client.service.getPlatformList
        return service
        
    def retrieve(self, username=None, password=None):
        ''' Retrieves all information from webservice for given username and password

        Parameters
        ----------
        username : string or None
            username
        password : string or None
            password

        Returns
        -------
        None
        '''
        username = username or self.username
        password = password or self.password
        s = self.service(username=username, password=password)
        self.root = ET.fromstring(s)
        self.info_dict = self._info()


    def get_programs(self):
        ''' Gets list of program numbers

        Returns
        -------
        list of string
            program numbers
        '''
        return list(self.info_dict.keys())

    
    def get_platforms(self, programNumber):
        ''' Gets list of platform IDs

        Parameters
        ----------
        programNumber : string
            program number
        
        Returns
        -------
        list of string
            platform numbers
        '''
        platforms = list(self.info_dict[programNumber].keys())
        platforms.sort(key=lambda x : int(x))
        return platforms


    def _info(self):
        info_dict = dict()
        programs = self.root.findall('program')
        for p in programs:
            programNumber = p.find("programNumber").text
            platforms = p.findall('platform')
            platform_dict = dict([(k,v) for k,v in self._get_platform_info(platforms)])
            info_dict[programNumber] = platform_dict
        return info_dict

    
    def _get_platform_info(self, platforms):
        for p in platforms:
            key = p.find('platformId').text
            yield key, dict([(v.tag, v.text) for v in p if v.tag!='platformId'])
            
    

class ArgosPlatformInfo(object):
    ''' Class to retrieve Argos platform information, in particular the payload.

    Parameters
    ----------
    wsdl : string
        url of the webservice
    credentials : string or None
        filename with credentials

    The credentials file is expected to contain three lines, not starting with #
    username = "user"
    password = "something secret"
    wsdl = "https://some/web/serice/"

    The username and password are optional, but would need to supplied in the script.
    '''
    
    def __init__(self, wsdl=None, credentials=None):
        if credentials:
            cr = CredentialsReader(credentials)
            self.username, self.password, wsdl = cr.get_credentials()
        else:
            self.username, self.password = None, None
        self.service = self.service_factory(wsdl)
        self.argos_message_decoder = argosMessage.ArgosMessageDecoder()
        self.number_of_satellite_passes = None
        self.decoder = argosMessage.ArgosMessageDecoder()
        self.service = self.service_factory(wsdl)

        
    def service_factory(self, wsdl):
        client = zeep.Client(wsdl=wsdl)
        service = client.service.getXml
        return service


        
    def retrieve(self, platformId, username=None, password=None, number_of_days_from_now=1):
        ''' Retrieves all information from webservice for given username and password

        Parameters
        ----------
        platformId : string
            platform identifier
        username : string
            username
        password : string
            password
        number_of_days_from_now : int (optional) Default : 1
            the number of days in the past for which data is to be retrieved. Maximum value is 20.
        
        Returns
        -------
        dict
           dictionary with payload information 
        '''
        username = username or self.username
        password = password or self.password
        if username is None or password is None:
            raise ValueError('No credentials are supplied. Cannot continue.')
        self.platformId=platformId
        s = self.service(username=username, password=password, platformId=platformId, displayRawData=True, displayLocation=True, nbDaysFromNow=number_of_days_from_now)
        logger.debug(f"String returned from getXml call:\n{s}")

        self.root = ET.fromstring(s)
        
        
    def get_info(self, latest_only=False, minimum_quality_flag=CRC):
        ''' Selects information for specific satellite pass.

        Parameters
        ----------
        number_of_days_from_now : int (optional) Default : 1
            the number of days in the past for which data is to be retrieved. Maximum value is 20.
        
        Returns
        -------
        dict
           dictionary with payload information 
        '''
        if not self.number_of_satellite_passes is None:
            if satellitePassNumber >= self.number_of_satellite_passes:
                logger.error(f"Cannot return requested satellite pass. There are only {self.number_of_satellite_passes} available")
                return dict()
        satellitePasses = self.root.find("program").find("platform").findall("satellitePass")

        locations = [sp.find('location') for sp in satellitePasses]
        messages = [sp.findall('message') for sp in satellitePasses]
        bestMsgDates = [sp.find('bestMsgDate') for sp in satellitePasses]

        results = []
        for location, mesgList, bestMsgDate in zip(locations, messages, bestMsgDates):
            try:
                argos_location = dict(latitude=location.find("latitude").text,
                                      longitude=location.find("longitude").text,
                                      date=location.find("locationDate").text)
            except AttributeError:
                argos_location = None
            best_payload, quality_flag = self._select_best_payload(mesgList, bestMsgDate)
            if quality_flag:
                gps_location = self.decoder(best_payload)
            else:
                gps_location = {}
            if quality_flag >= minimum_quality_flag:
                results.append(dict(argos_location = argos_location,
                                    gps_location = gps_location,
                                    gps_location_qf = quality_flag)
                               )
        results.reverse()
        if latest_only:
            return results[0]
        else:
            return results
    

            

    def _select_best_payload(self, messages, bestMsgDate):
        bestMsgDateStr = bestMsgDate.text
        payloads = [m.find('collect').find('rawData').text for m in messages]
        dates = [m.find('collect').find('date').text for m in messages]
        crcs = [self.decoder.checksum_8bit(p) for p in payloads]
        # best option crc True and date = bestMsgDateStr
        best_payloads = [p for p,crc,date in zip(payloads, crcs, dates) if crc and date==bestMsgDateStr]
        if best_payloads:
            return best_payloads[0], 3
        # Take any with crc==True
        best_payloads = [p for p,crc in zip(payloads, crcs) if crc]
        if best_payloads:
            return best_payloads[0], 2
        # Take best date
        best_payloads = [p for p,date in zip(payloads, dates) if date==bestMsgDateStr]
        if best_payloads:
            return best_payloads[0], 1
        return None, 0
