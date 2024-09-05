import arrow

class ArgosMessageDecoder(object):
    CODEC={"present_time"  :(8,'unsigned',1.),
           "lat"           :(6,'signed',0.01),
           "lon"           :(6,'signed',0.01),
           "fixtime"       :(4,'unsigned',1.),
           "latInvalid"    :(6,'signed',0.01),
           "lonInvalid"    :(6,'signed',0.01),
           "fixtimeInvalid":(4,'unsigned',1.),
           "latToofar"     :(6,'signed',0.01),
           "lonToofar"     :(6,'signed',0.01),
           "fixtimeToofar" :(4,'signed',1.),
           "U"             :(2,'signed',0.05),
           "V"             :(2,'signed',0.05)}
    CODECVAR=["present_time"  ,
              "lat"           ,
              "lon"           ,
              "fixtime"       ,
              "latInvalid"    ,
              "lonInvalid"    ,
              "fixtimeInvalid",
              "latToofar"     ,
              "lonToofar"     ,
              "fixtimeToofar" ,
              "U"             ,
              "V"             ]

    def __init__(self):
        pass

    def __call__(self, message):
        return self.parseHex(message)
        
    def parseHex(self, message):
        data = dict()
        position=0
        for k in self.CODECVAR:
            size,typ,factor=self.CODEC[k]
            hexValue=message[position:position+size]
            data[k]=self.hexToDec(hexValue,size,typ)*factor
            position+=size
        data['crc']=self.checksum_8bit(message)
        data['ctime'] = arrow.get(data['present_time']).ctime()
        return data
    
    def checksum_8bit(self, message):
        lengthMessage=len(message)
        if lengthMessage!=62:
            return False
        f=lambda x:self.hexToDec(x,2,'unsigned')
        bytes=list(map(f,[message[i:i+2] for i in range(0,lengthMessage,2)]))
        crc8=0
        for b in bytes[:-1]:
            crc8+=b
            crc8=crc8%256
        crc8=256-crc8
        return crc8==bytes[-1]
        

    def hexToDec(self,x,n,typ):
        '''returns a decimal representation of a hexadecimal number
        if signed==True, then a signed integer is returned. Then the length
        of the hexadecimal number should be given as well (n)
        ''' 
        if x=="":
            return 0
        if typ=='signed' and x[0]>'8':
            xn=int(x,16)-16**n
        else:
            xn=int(x,16)
        return(xn)

