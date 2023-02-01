import tornado.ioloop
import pyrestful.rest
from math import cos, asin, sqrt
from pyrestful import mediatypes
from pyrestful.rest import get
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json
import requests
import re
from datetime import time
import datetime
from dateutil import parser
import calendar

def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295
    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p)*cos(lat2*p) * (1-cos((lon2-lon1)*p)) / 2
    return 12742 * asin(sqrt(a))

def closest(data, v):
    return sorted(data, key=lambda p: distance(v['lat'],v['lon'],p['properties']['Latitude'],p['properties']['Longitude']))


class EchoService(pyrestful.rest.RestHandler):
     @get(_path="/find/{lat}/{lng}", _produces=mediatypes.APPLICATION_JSON)
     def sayHello(self, lat, lon):
          # ref = db.reference('features')
          # tempDataList1 = ref.get()
          with open("data.json", "r") as data:
               tempDataList = json.load(data)
          tempDataList1 = tempDataList["features"] 
          result = list(closest(tempDataList1, {"lat": float(lat), "lon": float(lon)}))
          print('Results shown')
          return result[:1]
     
     @get(_path="/calc/{lat}/{lng}", _produces=mediatypes.APPLICATION_JSON)
     def sayHello2(self, lat, lon):
          print("hit")
          
          r = self.sayHello(lat,lon)
          # r = [{"type": "Feature", "properties": {"POTEAU_ID_POT": 105972, "POSITION_POP": 7, "PANNEAU_ID_PAN": 970816, "PANNEAU_ID_RPA": 2707, "DESCRIPTION_RPA": "\\P 08h-16h DIM. 1 JANV. AU 1 DEC.", "CODE_RPA": "SV-JB", "FLECHE_PAN": 3, "TOPONYME_PAN": null, "DESCRIPTION_CAT": "STATIONNEMENT", "POTEAU_VERSION_POT": 3, "DATE_CONCEPTION_POT": "2013-08-01", "PAS_SUR_RUE": null, "DESCRIPTION_REP": "R\u00e9el", "DESCRIPTION_RTP": "1- Tige et base", "X": 298141.219, "Y": 5042984.5, "Longitude": -73.585245, "Latitude": 45.526746, "NOM_ARROND": "Plateau-Mont-Royal"}, "geometry": {"type": "Point", "coordinates": [-73.58524523082008, 45.52674605015391]}}]
          # print(r[0].json())
          # print(json.dumps(r[0]))

          # r = [{'type': 'Feature', 'properties': {'POTEAU_ID_POT': 216045, 'POSITION_POP': 7, 'PANNEAU_ID_PAN': 801933, 'PANNEAU_ID_RPA': 3, 'DESCRIPTION_RPA': '\\A 22h-07h', 'CODE_RPA': 'AD-NM', 'FLECHE_PAN': 3, 'TOPONYME_PAN': None, 'DESCRIPTION_CAT': 'STATIONNEMENT', 'POTEAU_VERSION_POT': 1, 'DATE_CONCEPTION_POT': '2011-03-14', 'PAS_SUR_RUE': None, 'DESCRIPTION_REP': 'En conception', 'DESCRIPTION_RTP': '11- Pot. bois/feux', 'X': 280726.416, 'Y': 5040782.962, 'Longitude': -73.808078, 'Latitude': 45.506552, 'NOM_ARROND': 'Pierrefonds - Roxboro'}, 'geometry': {'type': 'Point', 'coordinates': [-73.80807808245741, 45.506552078840514]}}]
          r2 = requests.get("http://api.geonames.org/timezoneJSON?lat={}&lng={}&username=skhemel".format(lat,lon))
          print(r2.json())
          timen = r2.json()["time"]
          dobj = parser.parse(timen)
          now_hour = int(timen[11:13])
          now_min = int(timen[14:16])
          now_year = int(timen[0:4])
          now_month = int(timen[5:7])
          now_date = int(timen[8:10])

          days = {
               "lundi" : 0,
               "mardi" : 1,
               "mercredi" : 2,
               "jeudi" : 3,
               "vendredi" : 4,
               "samedi" : 5,
               "dimanche" : 6,
               "lun" : 0,
               "mar" : 1,
               "mer" : 2,
               "jeu" : 3,
               "ven" : 4,
               "sam" : 5,
               "dim" : 6
          }

          months = {
               "janv" : 1,
               "fevr" : 2,
               "mars" : 3,
               "avril" : 4,
               "mai" : 5,
               "juin" : 6,
               "juil" : 7,
               "aout" : 8,
               "sept" : 9,
               "okt" : 10,
               "nov" : 11,
               "dec" : 12,
               "janvier" : 1,
               "fevrier" : 2,
               "juillet" : 7,
               "septembre" : 9,
               "octobre" : 10,
               "novembre" : 11,
               "decembre" : 12
          }

          drpa = r[0]['properties']["DESCRIPTION_RPA"]
	  #return {'result':drpa}
          # drpa = "\\P RESERVE S3R 09h-23h"
          ans = 1


          # drpa = "\\P 08h-10h LUN. AU VEN. 1 AVRIL AU 1 DEC." 
          
          
          # regex = r"\\\\[AP]\s(\d+)h[:]?(\d*)-(\d+)h[:]?(\d*)"
          # regex = r"\\\\[AP]\s(\d+)h[:]?(\d*)-(\d+)h[:]?(\d*)\s?(?P<fday>([a-zA-Z]+)?)[.]?\s?(?P<isAUone>AU)?\s?(?P<tday>([a-zA-Z]+)?)?[.]?\s?(?P<fdate>(\d*))?\s?(?P<fmonth>([a-zA-Z]+)?)?\s?(?P<isAUtwo>AU)?\s?(?P<tdate>(\d*))?\s?(?P<tmonth>([a-zA-Z]+)?)?"
          regex = r"\\\\[AP]\s(\d+)h[:]?(\d*)-(\d+)h[:]?(\d*)\s?(?P<fday>([a-zA-Z]+)?)[.]?\s?(?P<isAUone>AU)?\s?(?P<tday>([a-zA-Z]+)?)?[.]?\s?(?P<fdate>(\d*))?\s?(?P<fmonth>([a-zA-Z]+)?)?[.]?\s?(?P<isAUtwo>AU)?\s?(?P<tdate>(\d*))?\s?(?P<tmonth>([a-zA-Z]+)?)?[.]?"
          regex2 = r"\\\\[AP]\s(\w+)\s(\w+)\s(\d+)h[:]?(\d*)-(\d+)h[:]?(\d*)" 

          print(drpa)
          new_drpa = repr(drpa)[1:-1]
          m = re.match(regex,new_drpa)
          n = re.match(regex2,new_drpa)

          # print("Grps - ",m.group(1))
          if m:
               try:
                    start_hour = int(m.group(1))
               except ValueError:
                    start_hour = 0
               
               try:
                    start_min = int(m.group(2))
               except ValueError:
                    start_min = 0

               try:
                    end_hour = int(m.group(3))
               except ValueError:
                    end_hour = 0

               try:
                    end_min = int(m.group(4))
               except ValueError:
                    end_min = 0
               
               print(start_hour, start_min, end_hour, end_min)

               begin_time = time(start_hour,start_min)
               end_time = time(end_hour,end_min)
               check_time = time(now_hour,now_min)
               print(begin_time,end_time,check_time)

               if begin_time < end_time:
                    ans = check_time >= begin_time and check_time <= end_time
               else: # crosses midnight
                    ans = check_time >= begin_time or check_time <= end_time 
               
               if ans!=0:
                    if m.group("fday"):
                         try :
                              fday = days[m.group("fday").lower()]
                              nday = dobj.weekday()
                              
                              if m.group("isAUone"):
                                   tday = days[m.group("tday").lower()]
                                   print("Here")
                                   if fday < tday:
                                        ans = ans and (nday >= fday and nday <= tday)
                                   else:
                                        ans = ans and (nday >= fday or nday <= tday)
                              else:
                                   ans = ans and (fday == nday)
                         except KeyError:
                              print("Can't find the from day.")
                    
                    if m.group("fdate"):
                         print("There")
                         fdate = int(m.group("fdate"))
                         fmonth = months[m.group("fmonth").lower()]

                         tdate = int(m.group("tdate"))
                         tmonth = months[m.group("tmonth").lower()]
                         print("there2")
                         fd = datetime.datetime(now_year,fmonth,fdate)
                         td = datetime.datetime(now_year,tmonth,tdate)

                         if td < fd:
                              td = datetime.datetime(now_year+1,tmonth,tdate)
                         print("there3")
                         if fd <= dobj <= td:
                              ans = ans and True
                         else : 
                              ans = False
                         
          elif n:
               try:
                    start_hour = int(n.group(3))
               except ValueError:
                    start_hour = 0
               
               try:
                    start_min = int(n.group(4))
               except ValueError:
                    start_min = 0

               try:
                    end_hour = int(n.group(5))
               except ValueError:
                    end_hour = 0

               try:
                    end_min = int(n.group(6))
               except ValueError:
                    end_min = 0
               
               print(start_hour, start_min, end_hour, end_min)

               begin_time = time(start_hour,start_min)
               end_time = time(end_hour,end_min)
               check_time = time(now_hour,now_min)
               print(begin_time,end_time,check_time)

               if begin_time < end_time:
                    ans = (check_time >= begin_time and check_time <= end_time)
               else: # crosses midnight
                    ans = (check_time >= begin_time or check_time <= end_time)

          return {'result' : ans}


if __name__ == '__main__':
     try:
          print("Start the echo service")
          # cred = credentials.Certificate("/home/theweblover007/Upwork/project/firebase-key.json")
          # firebase_admin.initialize_app(cred, {'databaseURL': 'https://parkai-7d6aa.firebaseio.com'})
          app = pyrestful.rest.RestService([EchoService])
          app.listen(8080)
          tornado.ioloop.IOLoop.instance().start()
     except KeyboardInterrupt:
          print("\nStop the echo service")
