import requests
import os.path

#stores auth info
class AuthInfo:
    def __init__ (self, mregID, bAuth, xdToken ):
        self.mregID = mregID
        self.bAuth = bAuth
        self.xdToken = xdToken
#stores gps coords
class GPSDat:
    def __init__ (self, lat, long):
        self.lat = lat
        self.long = long
#Encapsulated POST request, with fills for authorization information
def getResponse (authInfo, gpsDat):

    response = requests.get(
    'https://web-production.lime.bike/api/rider/v1/views/main',
    params=[                                                                       (                                                                       'mobile_registration_id',
                                                                                                                                                    authInfo.mregID),
                                                                            (                                                                       'map_center_latitude',
                                                                                                                                                    gpsDat.lat),
                                                                            (                                                                       'map_center_longitude',
                                                                                                                                                    gpsDat.long),
                                                                            (                                                                       'user_latitude',
                                                                                                                                                    gpsDat.lat),
                                                                            (                                                                       'user_longitude',
                                                                                                                                                    gpsDat.long)],
    headers={                                                                      'Accept-Encoding': 'gzip',
                                                                           'Accept-Language': 'en-US',
                                                                           'App-Version': '1.18.1',
                                                                           'Authorization': 'Bearer ' +
                                                                                            authInfo.bAuth,
                                                                           'Connection': 'Keep-Alive',
                                                                           'User-Agent': 'okhttp/3.9.0',
                                                                           'X-Device-Token': authInfo.xdToken}

    )
    return response

def loadAuth( filePath ):
    aifo = AuthInfo
    if  not os.path.isfile(filePath):
        print("Auth file not found.")
        return -1
    else:
        f = open(filePath, "r")
        lArr = f.readlines()
        aifo.mregID = lArr[0].partition("=")[2].rstrip()
        aifo.bAuth = lArr[1].partition("=")[2].rstrip()
        aifo.xdToken = lArr[2].partition("=")[2].rstrip()
        return aifo


if __name__ == "__main__":
    gDat = GPSDat(0,0)
    print(getResponse(loadAuth("localAuthDetails"), gDat).text)

