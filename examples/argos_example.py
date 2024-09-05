from  argos import argosClient

# Find out what programNumber and platforms are available.

# The examples assume you have an account with CLS and a programNumber.
# You will need to create a file with your credentials
# username = "joe"
# password = "123"
# wsdl = "https://url"
#
# or you can supply the wsdl to the constructor and use your username
# and password in the script (retrieve method). This is not recommended.
#
# Due to the wishes of CLS, the wsdl path is not disclosed, but can be
# requested from CLS.
#
# In the examples below the argos_login.txt contains this info. It can
# be in the current working directory, or it can be placed in
# ~/.locall/share/argos.

api = argosClient.ArgosProgramInfo(credentials="argos_login.txt")
api.retrieve()

# or alternatively:
# api = argosClient.ArgosProgramInfo(wsdl="...")
# api.retrieve(username='joe',password='donald')

programs = api.get_programs()
platforms = api.get_platforms(programs[0])

print(f"The programs available are {programs}.")
print(f"The platforms available in the first program are {platforms}.")


api = argosClient.ArgosPlatformInfo(credentials="argos_login.txt")
info = api.retrieve(platformId='260603', number_of_days_from_now=20)
for k, v in info.items():
    print(f"{k:>20s} : {v}")

# Now we have also the number of satellitePasses for the period
# specified, after calling the retrieve() method once. We have a best
# guess for the position for every satellite pass.

# if the CRC value is True, then the values are almost certain correct
# and correspond to what the GPS on the glider outputted. If the CRC
# value is False, then the message got through with errors, and the
# values have to be considered "in context".

for i in range(api.number_of_satellite_passes):
    info = api.info(satellitePassNumber=i)
    print(f"{info['date']:20s} {info['lat']:10.3f} {info['lon']:10.3f} CRC:{info['crc']}")

# It may be that if your platform has not sent any argos messages
# during the last 20 days, then there is nothing to show. Below is some example output.
    
example_output=    
'''Example output:

The programs available are ['3932'].
The platforms available in the first program are ['27011', '30649', '260603', '260604', '260682'].
        present_time : 1724005010.0
                 lat : 1126.73
                 lon : -2301.2000000000003
             fixtime : 7.0
          latInvalid : 1126.57
          lonInvalid : -2301.21
      fixtimeInvalid : 8.0
           latToofar : -0.01
           lonToofar : -0.01
       fixtimeToofar : 0.0
                   U : -0.05
                   V : 0.05
                 crc : True
               ctime : Sun Aug 18 18:16:50 2024
                date : 2024-08-18T18:26:02.000Z
2024-08-18T18:26:02.000Z   1126.730  -2301.200 CRC:True
2024-08-18T19:10:29.000Z   1127.030  -2301.510 CRC:True
2024-08-18T19:04:15.000Z   1127.030  -2301.510 CRC:True
2024-08-18T23:12:31.000Z   1128.630  -2302.470 CRC:True
2024-08-18T23:09:37.000Z   1128.630  -2302.470 CRC:True
2024-08-19T00:08:39.000Z   1128.810  -2302.730 CRC:True
2024-08-19T00:17:46.000Z   1128.810  -2302.730 CRC:True
2024-08-19T02:02:13.000Z   1129.020  -2303.080 CRC:True
2024-08-19T09:55:32.000Z   1130.990  -2304.530 CRC:True
2024-08-19T11:03:31.000Z   1131.780 -55924.050 CRC:False
2024-08-19T14:26:09.000Z      0.000      0.000 CRC:False
2024-08-19T21:14:27.000Z   1134.670  -2301.300 CRC:True
2024-08-19T21:17:40.000Z   1134.670  -2301.300 CRC:True
2024-08-20T01:38:39.000Z   1135.140  -2258.960 CRC:True
2024-08-20T08:10:08.000Z   1135.240  -2256.580 CRC:True
2024-08-20T08:11:34.000Z   1135.240  -2256.580 CRC:True
2024-08-20T21:06:15.000Z   1133.830  -2255.310 CRC:False
2024-08-20T23:50:41.000Z   1134.870  -2254.270 CRC:True
2024-08-21T05:40:37.000Z      0.000      0.000 CRC:False
2024-08-21T14:24:44.000Z   1132.640  -2252.110 CRC:True
2024-08-21T20:06:44.000Z   1129.770  -2251.270 CRC:True
2024-08-21T23:05:22.000Z      0.000      0.000 CRC:False
2024-08-22T08:03:52.000Z   1124.970  -2252.090 CRC:True
2024-08-22T13:43:45.000Z   1123.810  -2253.340 CRC:True
2024-08-22T13:52:52.000Z   1123.810  -2253.340 CRC:True
2024-08-22T19:37:09.000Z   1122.790  -2254.920 CRC:True
2024-08-22T22:30:02.000Z   1122.220  -2255.990 CRC:True
2024-08-22T22:39:09.000Z   1122.220  -2255.990 CRC:True
2024-08-23T10:13:20.000Z   1121.040  -2301.400 CRC:True
2024-08-23T13:00:58.000Z   1121.390  -2302.810 CRC:True
2024-08-23T19:06:44.000Z   1123.300  -2304.680 CRC:True
2024-08-23T21:58:05.000Z   1124.640  -2305.150 CRC:True
2024-08-24T00:43:19.000Z   1126.040  -2305.450 CRC:True
2024-08-24T06:45:47.000Z   1129.700  -2305.170 CRC:True
2024-08-24T09:52:32.000Z   1131.310  -2304.630 CRC:False
2024-08-24T18:36:20.000Z   1134.600  -2301.070 CRC:True
2024-08-24T21:31:11.000Z   1134.190  -2259.770 CRC:True
2024-08-25T00:31:47.000Z   1133.900  -2257.970 CRC:True
2024-08-25T06:12:12.000Z   1132.940  -2254.760 CRC:True
2024-08-25T12:05:32.000Z   1129.660  -2253.880 CRC:False
2024-08-25T20:46:16.000Z    469.400  -2260.730 CRC:False
2024-08-25T21:14:11.000Z   1124.760  -2255.610 CRC:True
2024-08-25T23:59:13.000Z  10541.150   4879.300 CRC:False
2024-08-26T11:48:59.000Z   1124.540  -2300.310 CRC:True
2024-08-26T12:01:04.000Z   1124.540  -2300.310 CRC:True
2024-08-26T20:49:59.000Z   1126.720  -2303.940 CRC:True
2024-08-26T20:57:21.000Z   1126.720  -2303.940 CRC:True
2024-08-27T11:50:17.000Z   1133.870  -2301.710 CRC:True
2024-08-27T14:47:12.000Z   1133.570  -2259.860 CRC:True
2024-08-28T05:41:48.000Z   1129.710  -2253.850 CRC:True
2024-08-28T05:43:14.000Z   1129.710  -2253.850 CRC:True
2024-08-28T08:47:15.000Z   1128.050  -2254.020 CRC:True
2024-08-28T11:38:14.000Z   1126.320  -2254.440 CRC:True
2024-08-28T23:40:33.000Z   1124.280  -2259.110 CRC:True
2024-08-28T23:49:37.000Z   1124.280  -2259.110 CRC:True
2024-08-29T02:38:24.000Z   1124.680  -2300.790 CRC:True
2024-08-29T08:35:08.000Z      0.000      0.000 CRC:False
2024-08-29T11:36:52.000Z      0.000      0.000 CRC:False
2024-08-29T15:01:26.000Z      0.000      0.000 CRC:False
2024-08-29T17:38:29.000Z   1130.600  -2302.580 CRC:True
2024-08-31T10:04:13.000Z      0.000      0.000 CRC:False
2024-08-31T11:38:49.000Z     -0.010     -0.010 CRC:False
2024-08-31T22:50:30.000Z     -0.010     -0.010 CRC:True
2024-09-01T00:21:28.000Z   4479.410  72893.370 CRC:False
2024-09-05T11:49:10.000Z      0.000      0.000 CRC:False
2024-09-05T11:49:10.000Z      0.000      0.000 CRC:False'''

