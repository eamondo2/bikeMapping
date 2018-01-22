import requests
import json
import os.path
import MySQLdb
import math
import matplotlib.pyplot as plt
import numpy as np
import time

#simple point class
class Point:
    def __init__ (self, x, y):
        self.x = x
        self.y = y
    def __str__ (self):
        return ("%s %s" % (self.x, self.y))

#stores auth info
class AuthInfo:
    def __init__ (self, mregID, bAuth, xdToken, user, passwd, host, db ):
        self.mregID = mregID
        self.bAuth = bAuth
        self.xdToken = xdToken
        self.user = user
        self.passwd = passwd
        self.host = host
        self.db = db
#stores gps coords
class GPSDat:
    def __init__ (self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
    def __str__ (self):
        return ("%s %s " % (self.latitude, self.longitude))
#dataset for bike infos
class dataSet:
    def __init__( self, idnum, typedat, status, pnum, latitude, longitude, last_act, type_name, bat_level):
        self.idnum = idnum
        self.typedat = typedat
        self.status = status
        self.pnum = pnum
        self.latitude = latitude
        self.longitude = longitude
        self.last_act = last_act
        self.type_name = type_name
        self.bat_level = bat_level

#Encapsulated POST request, with fills for authorization information
def getResponse (authInfo, gpsDat):

    response = requests.get(
    'https://web-production.lime.bike/api/rider/v1/views/main',
    params=[                                                                       (                                                                       'mobile_registration_id',
                                                                                                                                                    authInfo.mregID),
                                                                            (                                                                       'map_center_latitude',
                                                                                                                                                    gpsDat.x),
                                                                            (                                                                       'map_center_longitude',
                                                                                                                                                    gpsDat.y),
                                                                            (                                                                       'user_latitude',
                                                                                                                                                    gpsDat.x),
                                                                            (                                                                       'user_longitude',
                                                                                                                                                    gpsDat.y)],
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
#Loader function from local stored authentication keys
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
        aifo.user = lArr[3].partition("=")[2].rstrip()
        aifo.passwd = lArr[4].partition("=")[2].rstrip()
        aifo.host = lArr[5].partition("=")[2].rstrip()
        aifo.db = lArr[6].partition("=")[2].rstrip()

        f.close()
        return aifo

#gets raw JSON from response, and pulls bike data structure from it
def nearbyBikeStrip (response):
    
    json_data = json.loads(response.text)
    print(json_data)
    arr = list()
    if ("data" not in json_data) or (len(json_data["data"]["attributes"]["nearby_locked_bikes"]) == 0):
        return
    for k in json_data["data"]["attributes"]["nearby_locked_bikes"]:
        
        arr.append(dataSet(k["id"], k["type"], k["attributes"]["status"], k["attributes"]["plate_number"], k["attributes"]["latitude"], k["attributes"]["longitude"], k["attributes"]["last_activity_at"], k["attributes"]["type_name"], k["attributes"]["battery_level"] ))
        
    return arr

        


def sqlDataPush ( dataSet, batchID, aifo ):
    
        if dataSet is None or len(dataSet) == 0:
            return
        conn = MySQLdb.connect(aifo.host, aifo.user, aifo.passwd, aifo.db)
        print(conn.get_server_info())
        x = conn.cursor()
        insStr = ("INSERT INTO bikeData "
            " (superset, id, type, status, platenum, latitude, longitude, last_activity, type_name, battery_level )"
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) " )
        for a in dataSet:
            try:
                x.execute(insStr , (batchID, a.idnum, a.typedat, a.status, a.pnum, a.latitude, a.longitude, a.last_act, a.type_name, a.bat_level))
                conn.commit()
            
            except:
                conn.rollback()
                print("FAIL")
                break
        conn.close()

def coordGenerate( centerGPS, radius, stepIntervalDist ):
    points = list()

    numCircles = radius / stepIntervalDist
    print(numCircles * 6)
    curAngle = 0


    ppcircle = 6
    

    for a in range(0, int(numCircles)):
        curRadius = (radius / numCircles ) * a
        degPerPt = 360 / ppcircle
        ppcircle += 2
        if not a == 0:
            for v in range(0, ppcircle):

                x = math.cos(curAngle) * curRadius
                y = math.sin(curAngle) * curRadius

                p = Point(centerGPS.latitude + x, centerGPS.longitude + y)
                points.append(p)

                curAngle += degPerPt
        else:
            points.append(Point(centerGPS.latitude, centerGPS.longitude))
    return points
        




def main():
    auth = loadAuth("localAuthDetails")
    gdat = GPSDat(35.785116,-78.734439)
    #
    #
    #

    pts = coordGenerate(gdat, 0.5, 0.2)
    x = list()
    y = list()
    cnt = 0
    for a in pts:
        time.sleep(0.5)
        response = getResponse(auth, a)
        dataList = nearbyBikeStrip(response)
        sqlDataPush(dataList, cnt, auth)
        print(a)
        x.append(a.x)
        y.append(a.y)
        cnt+=1
    plt.scatter(x, y)
    plt.show()

if __name__ == "__main__":
    main()

