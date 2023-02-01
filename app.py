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

from dateutil import parser
import calendar
from datetime import datetime
import datefinder


pre_defined = """P 15 min
\P RESERVE TAXIS
\P EN TOUT TEMPS
PANONCEAU EXCEPTE PERIODE INTERDITE
\A EN TOUT TEMPS
PANONCEAU - EXCEPTE VEHICULES MUNIS D'UN PERMIS
PARCOMETRE
\P DEUX COTES
PANONCEAU ZONE DE REMORQUAGE
\P RESERVE HANDICAPES (PICTO)
\P RESERVE MOTOS
\P RESERVE TITULAIRES DE PERMIS
\P RESERVE DEBARCADERE HANDICAPES EN TOUT TEMPS
\P RESERVE AUTOBUS TOURISTIQUES
PANONCEAU DEBAR. AUTOBUS SCOLAIRE
PANONCEAU LORSQUE STATIONNEMENT PERMIS-PETITES VOITURES
PANONCEAU DEBAR. SEULEMENT
\P LIVRAISON SEULEMENT EN TOUT TEMPS
\P RESERVE CORPS DIPLOMATIQUE
PANONCEAU DEBARCADERE RESERVE HANDICAPE
PANONCEAU FLECHE A GAUCHE
PANONCEAU LIVRAISON SEULEMENT
\P RESERVE VEHICULES DU SERVICE DE LA POLICE
\P RESERVE SERVICE D'INCENDIE
\P RESERVE VEHICULES DE LA VILLE
\P EXCEPTE VEHICULES D'URGENCE
\A POMPIER URGENCE
\A RESERVE AUTOBUS
\P AUX CAMIONS
\P RESERVE AUTOBUS
INTERDICTION DE STAT. S3R (GR. R) 9H - 3H
\P DANS LE CENTRE DU PARKING
\P RESERVE VISITEURS ET EMPLOYES DE LA VILLE
\P RESERVE FIACRES
PANONCEAU "DEUX COTES"
P A ANGLE
\P AUX REMORQUES
\P RESERVE LOCATAIRES DU MARCHE
HORAIRE DE STATIONNEMENT TARIFE (PARCOFLEX)
\P RESERVE EMPLOYES DE L'EDIFICE
PANONCEAU RESERVE HANDICAPE
\A EN TOUT TEMPS DU COTE DROIT
PANONCEAU EXCEPTE AUTOBUS SCOLAIRE
\A AUX CAMIONS
PANONCEAU LUN. AU SAM.
PANONCEAU LUN. AU VEN.
\P RESERVE FOURGON CELLULAIRE SPVM
PANONCEAU  DETENTION SEULEMENT
STAT.HANDICAPEES 7H - 20H
\P EXCEPTE DEBARCADERE AUTOBUS TOURISTIQUE
\P LUNDI AU VENDREDI
\P EXCEPTE CONSEILLERS MUNICIPAUX
\P RESERVE AIRE D'ATTENTE
RAPPEL...
\P RESERVE S3R          (EN TOUT TEMPS)
SORTIE
PANONCEAU STAT. A ANGLE - LIGNE AU SOL A RESPECTER
PANONCEAU EXCEPTE TITULAIRE DE PERMIS
PANONCEAU PERMIS EN DOUBLE FILE
P VELO
\P EXCEPTE VISITEURS POSTE DE POLICE
PANONCEAU  DIMANCHE
PANONCEAU EXCEPTE USAGERS DE L'ARENA
PANONCEAU "JOURS D'ECOLE"
\P RESERVE VEHICULES MILITAIRES
\P EXCEPTE AIRE D'EMBARQUEMENT AUTOBUS TOURISTIQUES
PANONCEAU RESERVE GARDERIE
P DEBARCADERE
\A EN TOUT TEMPS DES DEUX COTES
PANONCEAU EXCEPTE AUTOBUS
PANONCEAU DE STATIONNEMENT (EXCEPTE VEH DE LA STM)
PANONCEAU PERMIS VALIDE EN PERIODE DE DENEIGEMENT
STATIONNEMENT PAYANT...
\P EXCEPTE S3R EN TOUT TEMPS
PANONCEAU PARKING NO... RENSEIGNEMENTS 872-5989
PANONCEAU TAXIS INCLUS
P EN FILE
\P AUX AUTOBUS
\P RESERVE CAMPER TENTE ROULOTTE
PANONCEAU EXCEPTÃ‰ DETENTEURS DE PERMIS SECTEUR XX
PANONCEAU SAMEDI DIMANCHE
\A EN TOUT TEMPS SUR 5m
\P EXCEPTE AUTOBUS SCOLAIRE
\P (FLÃˆCHE SEULEMENT)
\P D'ICI AU COIN
\ARRÃŠT INTERDIT ZONE D'AUTOBUS
\ARRÃŠT INTERDIT
DÃ‰BARCADÃˆRE
P RÃ‰SERVÃ‰ SEULEMENT DÃ‰TENTEURS DE PERMIS #
P RÃ‰SERVÃ‰ EN TOUT TEMPS DÃ‰TENTEURS DE PERMIS #
\P RÃˆGL. 2027
\P RÃ‰SERVÃ‰ PERSONNE HANDICAPÃ‰E
P 60 min
\ARRÃŠT INTERDIT (FLÃˆCHE)
\P RÃ‰SERVÃ‰ FAMILLE NOMBREUSE
SAUF AUTOBUS SCOLAIRES JOURS DE CLASSE
P 2H
\ARRÃŠT INTERDIT (HEURE)
P 30 MIN - POSTE DE POLICE
PERMISSION DE STATIONNER
30 MIN
LUN MER VEN
MAR JEU SAM
EXCEPTÃ‰ AUTOBUS SCOLAIRE
ESPACE RÃ‰SERVÃ‰ MER DIM
ARRÃŠT D'AUTOBUS LUNDI Ã€ VENDREDI
P 60 MIN
ZONE D'ATTENTE POUR AUTOBUS DE LA STCUM SEULEMENT
\P (STATIONNEMENT INTERDIT)
22H Ã  8H
SABBAT ET JOURS DE FÃŠTE
ESPACE RÃ‰SERVÃ‰E NAVETTE CAPREIT
50 MÃˆTRES
ARRÃŠT - D'AUTOBUS
SAUF AUTOBUS SCOLAIRE - JOURS DE CLASSE
60 MIN - VISITEUR - SEULEMENT
EXCEPTÃ‰ VÃ‰HICULES AUTORISÃ‰S
POUR LES EMPLOYÃ‰S SEULEMENT
SAUF AUTOBUS JOURS DE CLASSE
EXCEPTÃ‰ DIMANCHE ET JOURS DE FÃŠTE
DÃ‰BARCADÃˆRE DE COURTE DURÃ‰E RÃ‰SERVÃ‰ AUX FAMILLES AVEC JEUNES ENFANTS
ARRÃŠT D'AUTOBUS de 00H00 Ã€ 05H00
5 MÃˆTRES
23H00 Ã€ 7H00 EXCEPTÃ‰ VÃ‰HICULES AUTORISÃ‰S
POSTE D'ATTENTE AUTOBUS 6H Ã€ 9H30 LUNDI Ã€ VENDREDI
90 MIN
ZONE DE LIVRAISON
LUN MER VEN DIM
6 PIEDS DE CHAQUE CÃ”TÃ‰ DU TROTTOIR
REMORQUAGE Ã€ VOS FRAIS
REMORQUAGE
EXCEPTÃ‰ VÃ‰HICULES COMMUNAUTO
RÃ‰SERVÃ‰ BILBIOTHÃˆQUE
RÃ‰SERVÃ‰ INCENDIE
VISITEURS 30 MIN MAX
RÃ‰SERVÃ‰ MESSAGER
HANDICAPÃ‰S - DÃ‰BARCADÃˆRE (Bleu)
60 MIN
DÃ‰BARCADÃˆRE SEULEMENT
\P CARAVANE  HABITATION MOTORISEE  VEHICULE RECREATIF
PANONCEAU EXCEPTE VEHICULES MUNIS D'IN PERMIS (2 SECTEURS)
SORTIE DE GARAGE
30 MIN 8H Ã€ 22H
\P EN TOUT TEMPS (TEMPORAIRE - PANNEAU)
PANONCEAU CAMIONS SEULEMENT
PANONCEAU POUR CUISINE DE RUE PERMIS CR-MTL
PANONCEAU RESERVE DETENTEUR DE PERMIS DE RESIDANTS
\A EN TOUT TEMPS (ORANGE POUR TRAVAUX)
PANONCEAU 20 AOÃ›T AU 30 JUIN
STATIONNEMENT TARIFÃ‰
PANONCEAU RESERVE VEHICULES MUNIS D'UN PERMIS (2 SECTEURS)
PANONCEAU MERCREDI
Espace rÃ©servÃ© - Directeur SÃ©curitÃ© publique
Espace rÃ©servÃ© - SÃ©curitÃ© publique
PANONCEAU LUNDI
\P RESERVE BICYCLETTE
STATIONNEMENT RESERVE
P 5 MIN.
\P EXCEPTE PICTOGRAMME VOITURE ELECTRIQUE - EN RECHARGE
\P EXCEPTE PICTOGRAMME CAMION
PANONCEAU CAMIONS
PANONCEAU MARDI
PANONCEAU EXCEPTE TAXIS
PANNONCEAU IDENTIFIES MONTREAL LOGO VILLE
\P EXCEPTE PICTOGRAMME VOITURE ELECTRIQUE
\P EXCEPTE VEHICULES IDENTIFIES MONTREAL LOGO VILLE
PANONCEAU EXCEPTE VEHICULES MUNIS D'UN PERMIS
\P EXCEPTE MOTOS - MOTOCYCLES (PICTOGRAMMES)
JOURS DE CLASSE
PANONCEAU PARCOMETRES INCLUS
EXCEPTE  DEBARCADERE
\A ARRET D'AUTOBUS
STATIONNEMENT RESERVE AUX USAGERS DE L'ARENA - REMORQUAGE A VOS FRAIS
PANONCEAU EXCEPTE PERIODE DE LIVRAISON
\P EXCEPTE VISITEURS POSTE DE POLICE DE QUARTIER N024
\A EXCEPTE CAMION S.O.S.
P 30 MIN
PANONCEAU TITUL. PERMIS SEUL.
P 15 MIN. RESERVE HOTEL
\P RESERVE AUTOBUS TOURISTIQUES 2h  reserve autobus touristiques 2h
""".lower().split('\n')

words_need_to_remove = [
                        's3r',
                        '1er',
                        'n024',
                        # '(',
                        # ')',
                        ]

replacable = {
      "janv" : 'january',
      "fevr" : 'february',
      "mars" : 'march',
      "avril" : 'april',
      "mai" : 'may',
      "juin" : 'june',
      "juil" : 'july',
      "aout" : 'august',
      "sept" : 'september',
      "okt" : 'october',
      "nov" : 'november',
      "dec" : 'december',
      "janvier" : 'january',
      "fevrier" : 'february',
      "juillet" : 'july',
      "septembre" : 'september',
      "octobre" : 'october',
      "novembre" : 'november',
      "decembre" : 'december',
      'au':'to',
      ' a ':'to',
      'et':'and'
      }
week_days = ['lundi','mardi','mercredi','jeudi','vendredi','samedi','dimanche',
             'lun','mar','mer','jeu','ven','sam','dim']

months_list = ['january', 'february', 'march', 'april', 
               'may', 'june', 'july', 'august', 'september', 
               'october', 'november', 'december']


predefined_results = {'\p reserve taxis':1,
                        '\p en tout temps':1,
                        # '15 min':1,
                        # 'p 15 min':1,
                        "panonceau - excepte vehicules munis d'un permis":1,
                        "\p reserve handicapes (picto)":1,
                        "\p reserve motos":1,                        
                    
                        }

    

# import datetime
def time_intences(i,
        week_days = week_days,
        pre_defined = pre_defined,
        replacable = replacable,
        months_list = months_list,
        words_need_to_remove = words_need_to_remove,
        now_h = 0,
        now_min = 0,
        now_year = 0,
        now_month = 0,
        now_date = 0,
        predefined_results = predefined_results):
    
  # global week_days_found, month_found, date_found, time, day_match, month_match, date_match, time_match
  
  week_days_found, month_found, date_found,time = None, None, None,None
  day_match, month_match, date_match, time_match = None, None, None,None
  if i.lower().strip() in pre_defined:
      result_gen = 0
      if i.lower().strip() in list(predefined_results.keys()):
          result_gen = predefined_results[i.lower().strip()]
      min_drpa_found = []
      min_drpa_found = min_drpa_found + re.findall('\w+ \d+ min',i)
      min_drpa_found = min_drpa_found + re.findall('\\\\\w+ \d+ min',i)
      min_drpa_found = min_drpa_found + re.findall('\w+ \d+ minutes',i)
      min_drpa_found = min_drpa_found + re.findall('\\\\\w+ \d+ minutes',i)
      if min_drpa_found[0] == i.strip():

          result_gen = 1
      
      print('Predefined are called.')
      return {'result' : result_gen}
  
  date = datetime(now_year,now_month,now_date,now_h,now_min)
  print('Now date time:',date)
  # or_i = i
  print(i)
  i = re.sub("\(.*?\)", "", i)
  i = i.lower()
  i = i.replace('.',' ')
  
  for kl in ['minutes','min']:
    if kl in i:
      splitted = i.split()
      index = splitted.index(kl)
      to_remove = " ".join([splitted[index-1],kl])
      i = i.replace(to_remove,'')
  

  range_weekdays_ = False
  range_month_ = False
  
  for word in words_need_to_remove:
      i = i.replace(word,'')

  start = re.findall('\\\\\w+',i)
  # print(start)
  if start:
    start = start[0]
    i = re.sub('\\\\\w+','',i)

  time_  = re.findall('\d+h',i)
  time = []
  for jh in time_:
    if '30' in i:
      index_ = i.find(jh)
      index_ = index_ + len(jh)

      if '30' in i[index_:index_+3]:
        time.append(jh+'30')

      else:
        time.append(jh)
    else:
      time.append(jh)

  if time:
    # print('time',time)
    if len(time)==2:
      time = "-".join(time)
    elif len(time)==4:
      time = ["-".join(time[:2]),"-".join(time[2:])]
    elif len(time)==3:
      time = ["-".join(time[:2]),time[2]]
    elif len(time)==1:
      time = time[0]

    if isinstance(time, list):
      for jh in time:
        i = re.sub(jh,'',i)
    if not isinstance(time, list):
      i = re.sub(time,'',i)
    
    # for ss in time:
    
    #   i = re.sub(ss,'',i)
  # print(i)

  if True:
      
    result = i.replace('h','')
    for key, value in replacable.items():
      result = result.replace(key, value)

    result = re.sub("[A-Za-z]+", lambda ele: " " + ele[0] + " ", result)

    result = result.replace('to', ' to ')
    result = result.replace('  ', ' ')
    # print('result',result)

    week_days_indexes = []
    week_days_found = []
    
    for index, j in enumerate(result.split()):
      if j.strip().lower() in week_days:
        day_found = week_days.index(j.lower().strip())
        if day_found>6:
          day_found = day_found-7
        week_days_found.append(day_found)
        week_days_indexes.append(index)

        result = re.sub(j,'',result,1)
    result = result.strip()
    # print(result)
    splitted_s = result.split()
    result = []
    for index, words in enumerate(splitted_s):
        if words in months_list:
            if index!=0:
                # print(splitted_s[index-1])
                if not splitted_s[index-1].isnumeric():
                    result.append('1')
            if index == 0:
                result.append('1')
        result.append(words)
        
    result = " ".join(result)
    # print('result',result)
    # print(week_days_indexes, result)
    if len(week_days_indexes):
        # result_split = result.split()

        if 'to' in result:
            if result.split().index('to') < week_days_indexes[-1]:
                range_weekdays_ = True
                result = result.replace('to','',1)
                
        if 'to' in result:
            
            if result.split().index('to') >= week_days_indexes[-1]:
                range_month_ = True
    
    elif not len(week_days_indexes):
        week_days_indexes = [0]
        
        if 'to' in result:
            if result.split().index('to') >= week_days_indexes[-1]:

                range_month_ = True
            # result = result.replace('to','',1)


    # print('ranges',range_weekdays_,range_month_)
    matches = datefinder.find_dates(result)
    month_found = []
    date_found = []
    for ssss in matches:

      month_found.append(ssss.month)
      date_found.append(ssss.day)
      

    
    if len(week_days_found)==2:
      if range_weekdays_:
        week_days_found = list(range(week_days_found[0],week_days_found[1]+1))
        
    if len(month_found)==2:
      if range_month_:
          if month_found[1]<month_found[0]:
              month_found = list(range(month_found[0],13,1))+ list(range(1,month_found[1]+1,1))
          else:
            month_found = list(range(month_found[0],month_found[1]+1))
            
    
    if now_date != 1:
        if now_date in date_found and not str(now_date) in result:
            date_found=[nnn for nnn in date_found if i!=now_date]
    
    print('week_days_found',week_days_found)
    print('month_found',month_found)
    print('date_found',date_found)
    print('time_found',time)

    if len(week_days_found):
      day_match = False

    if len(month_found):
      month_match = False

    if len(date_found):
      date_match = False

    # month_found = [date.month for date in matches]
    
          
    if now_month in month_found:
      month_match = True
      date_match = True
      
    # if month_match:
      # if len(month_found)==2:
      #   if now_date >= date_found[0] or now_date <= date_found[0]:
      #     date_match = True

      #   if date_found[0] == date_found[1]:
      #     date_match = True

      # elif len(month_found)==1:
      #   if now_date == date_found[0]:
          # date_match = True

    weekday = date.weekday()
    if weekday in week_days_found:
      day_match = True

    if not time:
      # if not all([day_match, date_match, month_match]):
        print('date_match',date_match)
        print('day_match',day_match)
        print('month_match',month_match)
        print('time_match',None)

        check_match = []
        
        if len(week_days_found):
            check_match.append(day_match)
        if len(month_found):
            check_match.append(month_match)
        if len(date_found):
            check_match.append(date_match)
                
        if all(check_match):
            return {'result' : 1}

        return {'result' : 0}


    elif time:
      time_match = False
      now_time = (now_h*60) + now_min

      t2_min = 0
      t1_min = 0

      if isinstance(time, list):
        for t in time:
          t2_min = 0
          t1_min = 0

          t = t.split('-')

          t1 = t[0].replace('h','')
          if '30' in t1:

            t1 = int(t1.replace('30',''))
            t1_min = 30

          t1_time = (int(t1)*60)+t1_min

          if len(t)==1:
              if t1_time <= now_time:
                  time_match = True
          
          if len(t)==2:
            t2 = t[1].replace('h','')
            if '30' in t2:
              t2 = int(t2.replace('30',''))
              t2_min = 30
            
            t2_time = (int(t2)*60)+t2_min

            if t1_time <= now_time and t2_time >= now_time:
              time_match = True

          
      else:
        t = time.split('-')
        t1 = t[0].replace('h','')

        if '30' in t1:
          t1 = int(t1.replace('30',''))
          t1_min = 30

        t1_time = (int(t1)*60)+t1_min

        if len(t)==1:
          if t1_time <= now_time:
              time_match = True
        
        if len(t)==2:
          t2 = t[1].replace('h','')
          if '30' in t2:
            t2 = int(t2.replace('30',''))
            t2_min = 30
          
          t2_time = (int(t2)*60)+t2_min
          if t1_time <= now_time and t2_time >= now_time:
            time_match = True

    print('date_match',date_match)
    print('day_match',day_match)
    print('month_match',month_match)
    print('time_match',time_match)

    check_match = []
    
    if len(week_days_found):
        check_match.append(day_match)
        
    if len(month_found):
        check_match.append(month_match)
    if len(date_found):
        check_match.append(date_match)
            
    check_match.append(time_match)
    if all(check_match):
        return {'result' : 1}

    return {'result':0}
  return {'result':0}

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
          # return {'result':3}
          print("hit")
          
          r = self.sayHello(lat,lon)
          # r = [{"type": "Feature", "properties": {"POTEAU_ID_POT": 105972, "POSITION_POP": 7, "PANNEAU_ID_PAN": 970816, "PANNEAU_ID_RPA": 2707, "DESCRIPTION_RPA": "\\P 08h-16h DIM. 1 JANV. AU 1 DEC.", "CODE_RPA": "SV-JB", "FLECHE_PAN": 3, "TOPONYME_PAN": null, "DESCRIPTION_CAT": "STATIONNEMENT", "POTEAU_VERSION_POT": 3, "DATE_CONCEPTION_POT": "2013-08-01", "PAS_SUR_RUE": null, "DESCRIPTION_REP": "R\u00e9el", "DESCRIPTION_RTP": "1- Tige et base", "X": 298141.219, "Y": 5042984.5, "Longitude": -73.585245, "Latitude": 45.526746, "NOM_ARROND": "Plateau-Mont-Royal"}, "geometry": {"type": "Point", "coordinates": [-73.58524523082008, 45.52674605015391]}}]
          # print(r[0].json())
          # print(json.dumps(r[0]))

          # r = [{'type': 'Feature', 'properties': {'POTEAU_ID_POT': 216045, 'POSITION_POP': 7, 'PANNEAU_ID_PAN': 801933, 'PANNEAU_ID_RPA': 3, 'DESCRIPTION_RPA': '\\A 22h-07h', 'CODE_RPA': 'AD-NM', 'FLECHE_PAN': 3, 'TOPONYME_PAN': None, 'DESCRIPTION_CAT': 'STATIONNEMENT', 'POTEAU_VERSION_POT': 1, 'DATE_CONCEPTION_POT': '2011-03-14', 'PAS_SUR_RUE': None, 'DESCRIPTION_REP': 'En conception', 'DESCRIPTION_RTP': '11- Pot. bois/feux', 'X': 280726.416, 'Y': 5040782.962, 'Longitude': -73.808078, 'Latitude': 45.506552, 'NOM_ARROND': 'Pierrefonds - Roxboro'}, 'geometry': {'type': 'Point', 'coordinates': [-73.80807808245741, 45.506552078840514]}}]
          r2 = requests.get("http://api.geonames.org/timezoneJSON?lat={}&lng={}&username=skhemel".format(lat,lon))
          print(r2.json())
          timen = r2.json()["time"]
          # dobj = parser.parse(timen)
          now_hour = int(timen[11:13])
          now_min = int(timen[14:16])
          now_year = int(timen[0:4])
          now_month = int(timen[5:7])
          now_date = int(timen[8:10])
         
          drpa = r[0]['properties']["DESCRIPTION_RPA"]
          new_drpa = repr(drpa)[1:-1]
          print(new_drpa)
          ans = time_intences(new_drpa,
                              now_h = now_hour,
                              now_min = now_min,
                              now_year = now_year,
                              now_month = now_month,
                              now_date = now_date)
          return ans
          # # drpa = "\\P RESERVE S3R 09h-23h"
          # ans = 1


          # # drpa = "\\P 08h-10h LUN. AU VEN. 1 AVRIL AU 1 DEC." 
          
          
          # # regex = r"\\\\[AP]\s(\d+)h[:]?(\d*)-(\d+)h[:]?(\d*)"
          # # regex = r"\\\\[AP]\s(\d+)h[:]?(\d*)-(\d+)h[:]?(\d*)\s?(?P<fday>([a-zA-Z]+)?)[.]?\s?(?P<isAUone>AU)?\s?(?P<tday>([a-zA-Z]+)?)?[.]?\s?(?P<fdate>(\d*))?\s?(?P<fmonth>([a-zA-Z]+)?)?\s?(?P<isAUtwo>AU)?\s?(?P<tdate>(\d*))?\s?(?P<tmonth>([a-zA-Z]+)?)?"
          # regex = r"\\\\[AP]\s(\d+)h[:]?(\d*)-(\d+)h[:]?(\d*)\s?(?P<fday>([a-zA-Z]+)?)[.]?\s?(?P<isAUone>AU)?\s?(?P<tday>([a-zA-Z]+)?)?[.]?\s?(?P<fdate>(\d*))?\s?(?P<fmonth>([a-zA-Z]+)?)?[.]?\s?(?P<isAUtwo>AU)?\s?(?P<tdate>(\d*))?\s?(?P<tmonth>([a-zA-Z]+)?)?[.]?"
          # regex2 = r"\\\\[AP]\s(\w+)\s(\w+)\s(\d+)h[:]?(\d*)-(\d+)h[:]?(\d*)" 

          # print(drpa)
          # new_drpa = repr(drpa)[1:-1]
          # m = re.match(regex,new_drpa)
          # n = re.match(regex2,new_drpa)

          # # print("Grps - ",m.group(1))
          # if m:
          #      try:
          #           start_hour = int(m.group(1))
          #      except ValueError:
          #           start_hour = 0
               
          #      try:
          #           start_min = int(m.group(2))
          #      except ValueError:
          #           start_min = 0

          #      try:
          #           end_hour = int(m.group(3))
          #      except ValueError:
          #           end_hour = 0

          #      try:
          #           end_min = int(m.group(4))
          #      except ValueError:
          #           end_min = 0
               
          #      print(start_hour, start_min, end_hour, end_min)

          #      begin_time = time(start_hour,start_min)
          #      end_time = time(end_hour,end_min)
          #      check_time = time(now_hour,now_min)
          #      print(begin_time,end_time,check_time)

          #      if begin_time < end_time:
          #           ans = check_time >= begin_time and check_time <= end_time
          #      else: # crosses midnight
          #           ans = check_time >= begin_time or check_time <= end_time 
               
          #      if ans!=0:
          #           if m.group("fday"):
          #                try :
          #                     fday = days[m.group("fday").lower()]
          #                     nday = dobj.weekday()
                              
          #                     if m.group("isAUone"):
          #                          tday = days[m.group("tday").lower()]
          #                          print("Here")
          #                          if fday < tday:
          #                               ans = ans and (nday >= fday and nday <= tday)
          #                          else:
          #                               ans = ans and (nday >= fday or nday <= tday)
          #                     else:
          #                          ans = ans and (fday == nday)
          #                except KeyError:
          #                     print("Can't find the from day.")
                    
          #           if m.group("fdate"):
          #                print("There")
          #                fdate = int(m.group("fdate"))
          #                fmonth = months[m.group("fmonth").lower()]

          #                tdate = int(m.group("tdate"))
          #                tmonth = months[m.group("tmonth").lower()]
          #                print("there2")
          #                fd = datetime.datetime(now_year,fmonth,fdate)
          #                td = datetime.datetime(now_year,tmonth,tdate)

          #                if td < fd:
          #                     td = datetime.datetime(now_year+1,tmonth,tdate)
          #                print("there3")
          #                if fd <= dobj <= td:
          #                     ans = ans and True
          #                else : 
          #                     ans = False
                         
          # elif n:
          #      try:
          #           start_hour = int(n.group(3))
          #      except ValueError:
          #           start_hour = 0
               
          #      try:
          #           start_min = int(n.group(4))
          #      except ValueError:
          #           start_min = 0

          #      try:
          #           end_hour = int(n.group(5))
          #      except ValueError:
          #           end_hour = 0

          #      try:
          #           end_min = int(n.group(6))
          #      except ValueError:
          #           end_min = 0
               
          #      print(start_hour, start_min, end_hour, end_min)

          #      begin_time = time(start_hour,start_min)
          #      end_time = time(end_hour,end_min)
          #      check_time = time(now_hour,now_min)
          #      print(begin_time,end_time,check_time)

          #      if begin_time < end_time:
          #           ans = (check_time >= begin_time and check_time <= end_time)
          #      else: # crosses midnight
          #           ans = (check_time >= begin_time or check_time <= end_time)
          # ans = 3
          # return {'result' : int(ans)}


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
