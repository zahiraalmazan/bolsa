#!/usr/bin python

#LIBRERIAS A UTILIZAR
from flask import Flask, render_template, request, session,redirect,url_for
from pymongo import MongoClient
import urllib, re
import ast

#VARIABLES DE USO GENERAL
app = Flask(__name__, template_folder='Template')
conexion = MongoClient()
basedatos = conexion.pruebas
bolsaBD = basedatos.bolsaBD
users = basedatos.usuarios


@app.route('/')
def index():
	return render_template('userpass.html')
	return;

#Inicio de sesion	
@app.route('/userpass' , methods=['POST','GET'])
def userpass():
	if request.method == 'POST':
		#coges los datos de usuario y contrasena de la pagina web
		usuario= request.form['email']
		contrasena=request.form['password']
		userpassBD=users.find({})
		print "user leido : "+str(usuario)+" pass: "+str(contrasena)
		#comparo con mongo
		for aux3 in userpassBD:
			if usuario == aux3['user'] and contrasena == aux3['pass']: #si Oki -> bolsa()
				session['user'] = aux3['user']; #creamos sesion
				dict = calculo_bolsa();
				return render_template('bolsa.html', dict = dict)
		return render_template('userpass.html')
	return;
#Coger los datos (cotizacion, porcentaje, fecha y hora) de la base de datos de MongoDB
def calculo_bolsa():
	bols = bolsaBD.find({}).sort("hora", 1).sort("fecha", -1).limit(20)
	dict = {}
	for bolsa in bols:
		dict[bolsa['cotizacion']]=bolsa;
	return dict

#Pagina principal
@app.route('/bolsa')
def bolsa():
	if session.has_key('user') == False:
		return redirect(url_for('index'));
	else:
		dict = calculo_bolsa()
		return render_template('bolsa.html', dict = dict)
		
#Mostrar todos los valores de porcentaje de Inditex por encima de un valor introducido por el usuario	
@app.route('/umbral', methods=['POST'])
def umbral():
	if session.has_key('user') == False:
		return redirect(url_for('index'));
	else:
		if request.method == 'POST':
			umbralclient= request.form['umbral']
			umbralBD=bolsaBD.find({})
			dict2 ={}
			dict3 ={}
			for aux in umbralBD:
				if float(umbralclient) <= float(aux['porcentaje'].replace('%','').replace(',','.')):
					dict2[aux['cotizacion']]=aux;
				elif (((-1)*float(umbralclient)) >= float(aux['porcentaje'].replace('%','').replace(',','.'))):
					dict3[aux['cotizacion']]=aux;
		
		return render_template('respuesta_max_min.html', dict2=dict2, dict3=dict3)
		
#Mostrar todos los valores por encima y por debajo de un umbral fijado por el usuario	
@app.route('/cotizacion', methods=['POST'])
def cotizacion():
	if session.has_key('user') == False:
		return redirect(url_for('index'));
	else:
		if request.method == 'POST':
			cotizacion_umbral= request.form['cotizacion'] #Cojo el valor de umbral del usuario
			cotizacionBD=list(bolsaBD.find({}).sort("fecha",1).limit(1)) #Hacemos una lista con el primer valor de cotizacion que haya en la base de datos
			cotizaciones=bolsaBD.find({}).sort("fecha",1); #Cogemos todos los valores de la base de datos ordenados por fecha ascendente
			#print(cotizacionBD[0]['cotizacion'])
			dict4 ={}
			dict5 ={}
			#Calculamos los valores techo y suelo con el umbral del usuario sobre el primer valor de cotizacion de la base de datos
			valor_techo = (1+(float(cotizacion_umbral)))*(float(cotizacionBD[0]['cotizacion'].replace(',','.')))
			valor_suelo = (1-(float(cotizacion_umbral)))*(float(cotizacionBD[0]['cotizacion'].replace(',','.')))
			#print "valor_techo = "+str(valor_techo)
			#print "valor_suelo = " +str(valor_suelo)
			for valores in cotizaciones:
				if float(valor_suelo) >= float(valores['cotizacion'].replace(',','.')): #Todos los valores que esten por debajo del valor suelo, se ponen en el diccionario
					dict5[valores['cotizacion']]=valores;
				elif float(valor_techo) <= float(valores['cotizacion'].replace(',','.')): #Todos los valores que esten por encima del valor techo, se ponen en el diccionario
					dict4[valores['cotizacion']]=valores;		
		return render_template('respuesta_cotizacion.html', dict4=dict4, dict5=dict5)

#Mostrar las graficas de Cotizacion y Porcentaje de ThingSpeak
@app.route('/grafica', methods=['POST'])
def grafica():
	if session.has_key('user') == False:
		return redirect(url_for('index'));
	else:
		return render_template('grafica.html')

#Calculo del valor medio de todos los datos almacenados
@app.route('/valormedio', methods=['POST', 'GET'])
def valormedio():
	if session.has_key('user') == False:
		return redirect(url_for('index'));
	else:
		#Primera forma: con los datos de MongoDB
		busqueda = bolsaBD.find({})
		suma = 0
		total = 0
		suma2 = 0
		total2 = 0
		for datos in busqueda:
			suma = suma + float(datos['cotizacion'].replace(',','.').replace('%','')) #sumatorio de todos los valores
			total = total + 1 #numero total de datos
		salida = float(suma/total) #Calculo de la media (suma/numero total)
		
		#Segunda forma: con los datos de ThingSpeak
		valores=urllib.urlopen('https://api.thingspeak.com/channels/177987/fields/1.json')
		leer =ast.literal_eval(str(valores.read()))
		suma2 = 0
		total2 = 0
		for dato in leer['feeds']:
			if dato['field1'] != 'Cotizacion':
				suma2 = suma2 + float(dato['field1']) #sumatorio de todos los datos
				total2 = total2 + 1 #numeros total de datos
		
		salida2 = float(suma2/total2)#Calculo de la media (suma/numero total)
		
		return render_template('valormedio.html', salida=salida, salida2=salida2)

######## salida y eleminzacion de session ##########		
@app.route('/exit')
def exit():
	session.pop('user', None);
	return redirect(url_for('index'));

if __name__ == '__main__':
	app.secret_key = str("Zahira")
	app.run(host='0.0.0.0', port = 80, debug = True)
