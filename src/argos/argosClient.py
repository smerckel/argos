import logging
import re
import os

import zeep
import xml.etree.ElementTree as ET
from . import argosMessage

logger = logging.getLogger("Argos")




class CredentialsReader:
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

        self.service = self.service_factory(wsdl)

        
    def service_factory(self, wsdl):
        client = zeep.Client(wsdl=wsdl)
        service = client.service.getXml
        return service


        
    def retrieve(self, platformId, username=None, password=None, number_of_days_from_now=1, satellitePassNumber=0):
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
        s = self.service(username=username, password=password, platformId=platformId, displayRawData=False, displayImageLocation=True, nbDaysFromNow=number_of_days_from_now)
        logger.debug(f"String returned from getXml call:\n{s}")

        self.root = ET.fromstring(s)

        s = self.service(username=username, password=password, platformId=platformId, displayRawData=True, displayImageLocation=False, nbDaysFromNow=number_of_days_from_now)
        logger.debug(f"String returned from getXml call:\n{s}")
        self.rootData = ET.fromstring(s)
        return self.info()
        
        
    def info(self, satellitePassNumber=0, require_crc_check=True):
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

    def 

    def infoLocation(self, satellitePassNumber=0):
        info_dict = dict()
        programs = self.root.findall('program')
        found = False
        for p in programs:
            if p.find('platform').find('platformId').text == self.platformId:
                found = True
                break
        if found:
            satellitePasses = p.find('platform').findall('satellitePass')
            satellitePasses.reverse()
            self.number_of_satellite_passes = len(satellitePasses)
            for i, sp in enumerate(satellitePasses):
                messages = sp.findall('message')
                best_messages = self._find_best_messages(messages)
                best_message= self._select_best_message(best_messages, require_crc_check)
                if (i==satellitePassNumber):
                    info_dict = best_message
                    break
        else:
            self.number_of_satellite_passes = 0
        return info_dict
    
    def infoData(self, satellitePassNumber=0, require_crc_check=True):
        info_dict = dict()
        programs = self.root.findall('program')
        found = False
        for p in programs:
            if p.find('platform').find('platformId').text == self.platformId:
                found = True
                break
        if found:
            satellitePasses = p.find('platform').findall('satellitePass')
            satellitePasses.reverse()
            self.number_of_satellite_passes = len(satellitePasses)
            for i, sp in enumerate(satellitePasses):
                messages = sp.findall('message')
                best_messages = self._find_best_messages(messages)
                best_message= self._select_best_message(best_messages, require_crc_check)
                if (i==satellitePassNumber):
                    info_dict = best_message
                    break
        else:
            self.number_of_satellite_passes = 0
        return info_dict

    def _select_best_message(self, message_list, require_crc_check):
        ''' Selects best message from a list of message dictionaries.

        For a given list of message dictionaries, the newest one that has a CRC check is returned.
        If no message has a positive CRC, the newest message is returned.
        '''
        ml = message_list.copy()
        if require_crc_check:
            for m in ml:
                if m['crc']:
                    break
            if not m['crc']:
                logger.info("None of the available messages for this pass has a valid CRC. The newest is returned.")
                m = ml[0]
        else:
            m = ml[0]
        return m
        
    def _find_best_messages(self, messages):
        ''' Finds best message for a given transmission window

        Returns the best message of a given transmission window based on the time of the message and the time
        of the stronges signal.
        '''
       
        best_messages = []
        for message in messages:
            bestDate = message.find('bestDate').text
            collect = message.findall('collect')
            rawData = None
            for _collect in collect:
                _date = _collect.find('date')
                if _date.text == bestDate:
                    rawData = _collect.find('rawData').text
            if rawData:
                data = self.argos_message_decoder(rawData)
                data['date'] = bestDate
                best_messages.append(data)
        return best_messages
        
