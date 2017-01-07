#import urllib.request,urllib.parse,re,time,datetime
import urllib, urllib2, re, time, datetime

while True:
	response=urllib2.urlopen('http://www.infobolsa.es/cotizacion/inditex/')
	paghtml=response.read().decode('utf-8')
	
	patron='<div class="price flop center">(.*)</div>'
	cotiz=re.search(patron,paghtml)
	print(cotiz.group(1))
	
	patron2='<div class="difP flop center">(.*)%</div>'
	porcentaje=re.search(patron2,paghtml)
	print(porcentaje.group(1))
	
	#	patron3='<div class="time left">(.*)</div>'
	#	hora = re.search(patron3,str(paghtml))
	#	print(hora.group(1))
  	
	#	patron4='<td class="date">(.*)</td>'
	#	fecha = re.search(patron4,str(paghtml))
	#	print(fecha.group(1))


	hora = datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')
	fecha=datetime.datetime.fromtimestamp(time.time()).strftime('%d-%m-%y')

	#ThingSpeak
	datos=urllib.urlencode({'key':'1AI85IMYVGGR6SJ1','field1':cotiz.group(1).replace(',','.'),'field2':porcentaje.group(1).replace(',','.')})
	datos_bin=datos.encode('utf-8')
	pagina=urllib2.urlopen('https://api.thingspeak.com/update.json',data=datos_bin)

	#MongoDB
	from pymongo import MongoClient
	conexion=MongoClient('mongodb://zahiramongo:jCp47l38lR3w7i4eBCd8wI6LnaSQIedEO7YXeUdJVkkLaJvZ9NwJmbiUaQzWR6OFkKCaZtwF1LU7HEF44mx2pg==@zahiramongo.documents.azure.com:10250/?ssl=true')
	basedatos=conexion.pruebas
	bolsaBD=basedatos.bolsaBD
	bolsaBD.insert({'cotizacion':cotiz.group(1),'porcentaje':porcentaje.group(1),'hora':hora,'fecha':fecha})	
	time.sleep(120)

