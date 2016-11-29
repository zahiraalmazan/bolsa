import urllib.request, urllib.parse, re,time

while True: 
	response = urllib.request.urlopen('http://www.infobolsa.es/cotizacion/inditex/')
	paghtml = response.read().decode('utf-8')
	
	
	patron='<div class="price flop center">(.*)</div>'
	cotiz=re.search(patron,str(paghtml))
	print (cotiz.group(1))
	
	patron2='<div class="difP flop center">(.*)%</div>'
	porcentaje=re.search(patron2,str(paghtml))
	print(porcentaje.group(1))
	
	patron3='<td class="hour">(.*)</td>'
	hora = re.search(patron3,str(paghtml))
	print(hora.group(1))
	
	patron4='<td class="date center">(.*)</td>'
	fecha = re.search(patron4,str(paghtml))
	print(fecha.group(1))

	
	#ThingSpeak
	datos = urllib.parse.urlencode({'key': '1AI85IMYVGGR6SJ1', 'field1': cotiz.group(1).replace(',','.'), 'field2': porcentaje.group(1).replace(',','.')})
	datos_bin = datos.encode('utf-8')
	pagina = urllib.request.urlopen('https://api.thingspeak.com/update.json', data=datos_bin)

	#MongoDB
	from pymongo import MongoClient
	conexion = MongoClient()
	basedatos=conexion.pruebas
	bolsaBD = basedatos.bolsaBD
	bolsaBD.insert({'cotizacion':cotiz.group(1), 'porcentaje':porcentaje.group(1), 'hora':hora.group(1), 'fecha':fecha.group(1)})	
	time.sleep(120)

