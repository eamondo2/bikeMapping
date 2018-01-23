import requests
import json
import os.path
import MySQLdb
import math
import matplotlib.pyplot as plt
import numpy as np
import time

timeoutCount = 0.0

#simple point class
class Point:
    def __init__ (self, x, y, valid=False):
        self.x = x
        self.y = y
        self.valid = valid
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
    global timeoutCount
    global gpsResults
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
    json_data = json.loads(response.text)
    #API timeout error handling
    if "error_message" in json_data:
        print("timeout %s" %(timeoutCount))
        time.sleep(7.5 * timeoutCount)
        timeoutCount += .15
        gpsResults.append(Point(gpsDat.x, gpsDat.y, False))
        return False
    else:
        timeoutCount = 1
        if len(json_data["data"]["attributes"]["nearby_locked_bikes"]) == 0:
            gpsResults.append(Point(gpsDat.x, gpsDat.y, False))
        else:
            gpsResults.append(Point(gpsDat.x, gpsDat.y, True))
        return json_data
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
def nearbyBikeStrip (json_data):
    arr = list()
    if ("data" not in json_data) or (len(json_data["data"]["attributes"]["nearby_locked_bikes"]) == 0):
        return
    for k in json_data["data"]["attributes"]["nearby_locked_bikes"]:
        arr.append(dataSet(k["id"], k["type"], k["attributes"]["status"], k["attributes"]["plate_number"], k["attributes"]["latitude"], k["attributes"]["longitude"], k["attributes"]["last_activity_at"], k["attributes"]["type_name"], k["attributes"]["battery_level"] ))
        
    return arr

def pointPush ( gpsPoints, connData):
    print("PUSH POINT")
    x = connData.cursor()
    insStr = ("INSERT INTO samplePts "
            " (latitude, longitude, validData )"
            " VALUES (%s, %s, %s ) ")
    for p in gpsPoints:
        try:
            x.execute(insStr, (p.x, p.y, p.valid))
        except:
            connData.rollback()
            print("FAIL")
            break
    connData.commit()

    


def sqlDataPush ( dataSet, batchID, connData):
        if dataSet is None or len(dataSet) == 0:
            return
        print("PUSH DATA")
        x = connData.cursor()
        insStr = ("INSERT INTO bikeData "
            " (superset, id, type, status, platenum, latitude, longitude, last_activity, type_name, battery_level )"
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) " )
        for a in dataSet:
            try:
                x.execute(insStr , (batchID, a.idnum, a.typedat, a.status, a.pnum, a.latitude, a.longitude, a.last_act, a.type_name, a.bat_level))
                #connData.commit()
            
            except:
                connData.rollback()
                print("FAIL")
                break
        connData.commit()

def coordGenerate( centerGPS, radius, stepIntervalDist ):
    points = list()

    numCircles = radius / stepIntervalDist
    curAngle = 0


    ppcircle = 6
    
    oldCirc = 1
    
    for a in np.arange(0, numCircles, 1):
        curRadius = (radius / numCircles ) * a
        curCirc = 2 * math.pi * curRadius
        degPerPt = 360 / ppcircle
        ppcircle *= (curCirc if curCirc != 0 else 1)/oldCirc
        oldCirc = (curCirc if curCirc != 0 else 1)

        print("%s %s %s %s" %(curRadius, curCirc, ppcircle, degPerPt))

        if not a == 0:
            for v in np.arange(0, ppcircle, 1):

                x = math.cos(curAngle) * curRadius
                y = math.sin(curAngle) * curRadius

                p = Point(centerGPS.x + x, centerGPS.y + y)
                points.append(p)

                curAngle += degPerPt
        else:
            points.append(Point(centerGPS.x, centerGPS.y))
    return points
        



#Entry point.
def main():
    global timeoutCount
    global gpsResults
    gpsResults = list()
    timeoutCount = 1
    auth = loadAuth("localAuthDetails")
    gdat = Point(35.785116,-78.734439)
    connData = MySQLdb.connect(auth.host, auth.user, auth.passwd, auth.db)
    #
    #
    #
    #Generates the set of sampling points. given starting gps coordinates and a radius, along with a stepping interval
    pts = coordGenerate(gdat, 3, 0.25)
    x = list()
    y = list()
    cnt = 0
    for a in pts:
        x.append(a.x)
        y.append(a.y)
        cnt+=1
    print("%s points total" %(cnt))
    total = cnt
    cnt = 0
    plt.scatter(x, y)
    plt.show()
    for a in pts:
        #fastest rate we can sample the API at without becoming locked out.
        time.sleep(0.75)
        response = getResponse(auth, a)
        while response == False:
            response = getResponse(auth, a)
        dataList = nearbyBikeStrip(response)
        sqlDataPush(dataList, cnt, connData)
        print("%s | %s of %s" % (a, cnt, total))
        
        cnt+=1
    pointPush(gpsResults, connData)
    

if __name__ == "__main__":
    main()

