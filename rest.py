# curl -X GET http://localhost:8888/Etudiant
# curl -X POST http://localhost:8888/Etudiant/\?Nom\=Cionaire\&Prenom\=Dick\&idAd\=2

import http.server, urllib.parse, sqlite3, os
import requests, json, threading, socketserver
import subprocess

tab_c = {}


from threading import Timer,Thread,Event

class perpetualTimer():

   def __init__(self,t,hFunction):
      self.t=t
      self.hFunction = hFunction
      self.thread = Timer(self.t,self.handle_function)

   def handle_function(self):
      self.hFunction()
      self.thread = Timer(self.t,self.handle_function)
      self.thread.start()

   def start(self):
      self.thread.start()

   def cancel(self):
      self.thread.cancel()

def printer():
    print ('Réinitialisation du compteur de requêtes')
    global tab_c
    tab_c = {}



class MyHandler(http.server.BaseHTTPRequestHandler):
	def __init__(self, *args, **kwargs):
		self.mysql = MySQL('logement.db')
		super(MyHandler, self).__init__(*args, **kwargs)

	def do_GET(self):

		print("Infos client: IP:", self.client_address[0], "Port :", self.client_address[1])
		print("GET fait sur le port ", self.server.server_port)

		"""Respond to a GET request."""
		res = urllib.parse.urlparse(self.path)
		data = ""
		# Creation du fichier html lors d'une requete chart
		if self.path == "/chart":
			#f = open("factures.html", "w")
			s = self.mysql.factures_html()

			data = data + "<html>\n  <head>\n    <script type=\"text/javascript\" src=\"https://www.gstatic.com/charts/loader.js\"></script>\n    <script type=\"text/javascript\">\n      google.charts.load('current', {'packages':['corechart']});\n      google.charts.setOnLoadCallback(drawChart);\n\n       function drawChart() {\n\n        var data = google.visualization.arrayToDataTable([\n          ['Type de facture', 'Montant'],\n"

			for i in range(len(s)):
				data = data + "          ['"
				str_tmp = str(s[i][0]) + " " + str(s[i][2])
				data = data + str_tmp
				data = data + "', "
				data = data + str(s[i][1])
				data = data + "],\n"


			data = data + "        ]);\n\n        var options = {\n          title: 'Factures'\n        };\n\n        var chart = new google.visualization.PieChart(document.getElementById('piechart'));\n\n        chart.draw(data, options);\n      }\n\n    </script>\n  </head>\n  <body>\n    <div id=\"piechart\" style=\"width: 900px; height: 500px;\"></div>\n  </body>\n</html>"

			#f.write(data)
			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()
			self.wfile.write(bytes(str(data)+'\n', 'UTF-8'))

		elif self.path == '/favicon.ico':
			return

		if self.path == '/add':
			s = self.mysql.capteurs()
			s = len(s) + 1
			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()

			width = "width=100%"

			with open('add_debut.html', 'r') as f:
				html = f.read()


			nomPieces = self.mysql.nom_pieces()
			imgPieces = self.mysql.img_pieces()

			html += '<form action="index.html" method="post">\n'
			html += '<input type="text" name="id" value='+str(s)+' hidden><br>\n'
			html += '<input type="date" name="Date_insertion" hidden id="theDate"><br>\n'
			html += '<input type="text" name="Port" hidden value='+next_free_port()+'><br>\n'
			html += '<input type="text" name="Status" hidden value="1"><br><br><br>\n'

			html += '<div class="titre">'
			html += '<h1>Pour commencer, selectionnez la pièce </h1><br>'
			html += '</div>'
			html += '<br>'


			html += '<div class="column">'
			html += '<div class="hiddenradio">'

			html += '<div class="col-sm-4">'
			html += '<div class="containerx">'
			html += '<label>'
			html += '<input type="radio" name="idp" value="0" checked="checked"><img src="' + imgPieces[0][0] + '"' + width + '><div class="overlayx">' + nomPieces[0][0] + '</div>'
			html += '</label>'
			html += '</div>'
			html += '</div>'

			l = len(nomPieces)

			for i in range(1, l):
				html += '<div class="col-sm-4">'
				html += '<div class="containerx">'
				html += '<label>'
				html += '<input type="radio" name="idp" value="' + str(i) + '"><img src="' + imgPieces[i][0] + '"' + width + '><div class="overlayx">' + nomPieces[i][0] + '</div>'
				html += '</label>'
				html += '</div>'
				html += '</div>'


			html += '</div>'
			html += '</div>'


			html += '<div class="titre">'
			html += '<h1>Choisissez ensuite le type de capteur</h1><br>'
			html += '</div>'
			html += '<br>'


			html += '<div class="column">'
			html += '<div class="hiddenradio">'


			nomTypes = self.mysql.nom_types()
			imgTypes = self.mysql.img_types()


			html += '<div class="col-sm-4">'
			html += '<div class="containerx">'
			html += '<label>'
			html += '<input type="radio" name="idt" value="0" checked="checked"><img src="' + imgTypes[0][0] + '"' + width + '><div class="overlayx">' + nomTypes[0][0] + '</div>'
			html += '</label>'
			html += '</div>'
			html += '</div>'

			l = len(nomTypes)

			for i in range(1, l):
				html += '<div class="col-sm-4">'
				html += '<div class="containerx">'
				html += '<label>'
				html += '<input type="radio" name="idt" value="' + str(i) + '"><img src="' + imgTypes[i][0] + '"' + width + '><div class="overlayx">' + nomTypes[i][0] + '</div>'
				html += '</label>'
				html += '</div>'
				html += '</div>'


			html += '</div>'
			html += '</div>'


			html += '<div class="titre">'
			html += '<h1>Enfin, indiquez la référence associée</h1><br>'
			html += '</div>'
			html += '<br>'

			html += '<div class="customcolumn">'
			html += 'Référence commerciale   : <input type="text" name="Ref_commerc"><br>\n'
			html += '</div>'

			html += '<div class="container">'
			html += '<div class="center">'
			html += '<input type="submit" value="Terminer l\'insertion du capteur">\n'
			html += '</div>'
			html += '</div>'

			html += '</form>\n'
			html += '<script> var date = new Date();var day = date.getDate();var month = date.getMonth() + 1;var year = date.getFullYear();if (month < 10) month = "0" + month;if (day < 10) day = "0" + day;var today = year + "-" + month + "-" + day;document.getElementById("theDate").value = today;</script>\n'
			html += '</body>\n'
			html += '</html>\n'
			self.wfile.write(bytes(str(html)+'\n', 'UTF-8'))

		elif self.path == '/':
			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()
			with open('accueil.html', 'r') as f:
				html = f.read()
				self.wfile.write(bytes(str(html)+'\n', 'UTF-8'))


		elif self.path == '/capteurs':
			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()
			#with open('capteurs.html', 'r') as f:
				#html = f.read()
				#self.wfile.write(bytes(str(html)+'\n', 'UTF-8'))


			with open('capteurs_debut.html', 'r') as f:
				my_str = f.read()
				#self.wfile.write(bytes(str(html)+'\n', 'UTF-8'))


			#print (my_str)

			s = self.mysql.capteurs()
			nomPieces = self.mysql.nom_pieces()
			print (s)
			print (nomPieces)

			for i in range(len(s)):
				if s[i][6] == 0:
					type = "Thermomètre"
				elif s[i][6] == 1:
					type = "Hygromètre"
				elif s[i][6] == 2:
					type = "Pluviomètre"
				elif s[i][6] == 3:
					type = "Anémomètre"
				elif s[i][6] == 4:
					type = "Baromètre"
				elif s[i][6] == 5:
					type = "Luxmètre"


				if s[i][4] == 1:
					status = " (ONLINE)"
				else:
					status = " (OFFLINE)"

				my_str = my_str + "<div class=\"col-sm-4\"><h3>Capteur #" + str(s[i][0]) + status + "</h3><p>" + type + "</p><p>Insertion le " + s[i][1] + "</p><p>Port #" + str(s[i][2]) + "</p><p>Référence commerciale: " + s[i][3] + "</p><p>Localisation : " + nomPieces[s[i][5]][0] + "</p></div>"


			with open('capteurs_fin.html', 'r') as f:
				my_str = my_str + f.read()

			self.wfile.write(bytes(str(my_str)+'\n', 'UTF-8'))




		elif self.path[0:13] == '/consommation':
			print("On entre dans conso filtre")
			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()


			#req = "select Type_fact, Montant, Date_fact from Facture ORDER BY Type_fact;"

			valide = False
			titre = ''

			try:
				print("S13 = ",self.path[13])
				if self.path[13] == '?':

					Deb_a = int(self.path[18:22])
					Deb_m = int(self.path[23:25])
					Deb_j = int(self.path[26:28])

					Fin_a = int(self.path[33:37])
					Fin_m = int(self.path[38:40])
					Fin_j = int(self.path[41:43])

					valide = True
					if Fin_a < Deb_a:
						valide = False
						titre = 'Factures du ' + str(Deb_j) + '/' + str(Deb_m) + '/' + str(Deb_a) + ' au ' + str(Fin_j) + '/' + str(Fin_m) + '/' + str(Fin_a) + ' : dates invalides, réinitialisation de la période'
					elif Fin_a == Deb_a:
						if Fin_m < Deb_m:
							valide = False
							titre = 'Factures du ' + str(Deb_j) + '/' + str(Deb_m) + '/' + str(Deb_a) + ' au ' + str(Fin_j) + '/' + str(Fin_m) + '/' + str(Fin_a) + ' : dates invalides, réinitialisation de la période'
						elif Fin_m == Deb_m:
							if Fin_j < Deb_j:
								valide = False
								titre = 'Factures du ' + str(Deb_j) + '/' + str(Deb_m) + '/' + str(Deb_a) + ' au ' + str(Fin_j) + '/' + str(Fin_m) + '/' + str(Fin_a) + ' : dates invalides, réinitialisation de la période'
			except:
				pass

			with open('consommation_debut.html', 'r') as f:
				my_str = f.read()

			s = self.mysql.factures_html()
			cpt = 0
			tab_type = []
			tab_cumul = []
			cumul_type = 0
			type_courant = 0
			for i in range(len(s)):
				if valide:
					aaaa = int(s[i][2][0:4])
					mm = int(s[i][2][5:7])
					jj = int(s[i][2][8:10])

					if aaaa > Fin_a or aaaa < Deb_a:
						continue
					elif (mm > Fin_m and aaaa >= Fin_a) or (mm < Deb_m and aaaa <= Deb_a):
						continue
					elif (jj > Fin_j and aaaa >= Fin_a and mm >= Fin_m) or (jj < Deb_j and aaaa <= Deb_a and mm <= Deb_m):
						continue

				if i == 0 or str(tab_type) == "[]":
					tab_type.append(s[0][0])
					tab_cumul.append(s[0][1])
				elif tab_type[type_courant] == s[i][0]:
					tab_cumul[type_courant] += s[i][1]
				elif tab_type[type_courant] != s[i][0]:
					type_courant +=1
					tab_type.append(s[i][0])
					tab_cumul.append(s[i][1])
					cumul_type = tab_cumul[type_courant]



			for i in range(len(tab_type)):

				cpt = cpt + 1
				my_str = my_str + "          ['"
				str_tmp = tab_type[i] + ": " + str(round(tab_cumul[i], 2)) + "€"
				my_str = my_str + str_tmp
				my_str = my_str + "', "
				my_str = my_str + str("{:10.2f}".format(tab_cumul[i]))
				my_str = my_str + "],\n"


			if valide and titre == '':
				titre = 'Factures du ' + str(Deb_j) + '/' + str(Deb_m) + '/' + str(Deb_a) + ' au ' + str(Fin_j) + '/' + str(Fin_m) + '/' + str(Fin_a)
				if cpt == 0:
					my_str = my_str + "          ['"
					str_tmp = str("Vide")
					my_str = my_str + str_tmp
					my_str = my_str + "', "
					my_str = my_str + "0"
					my_str = my_str + "],\n"
					titre = titre + ' : aucune facture!'

			elif not valide and titre == '':
				titre = 'Toutes les factures'

			my_str = my_str + "]);\nvar options = {\ntitle: \'" + titre + "\'\n};"

			with open('consommation_fin.html', 'r') as f:
				my_str = my_str + f.read()
			self.wfile.write(bytes(str(my_str)+'\n', 'UTF-8'))

			#conso = open("affichage_conso_finale.html", "w")
			#conso.write(my_str)

		elif self.path[0:10] == '/economies':
			print("On entre dans economies")
			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()

			valide = False
			titre = ''

			try:
				print("S13 = ",self.path[10])
				if self.path[10] == '?':

					Deb_a = int(self.path[15:19])
					Deb_m = int(self.path[20:22])
					Deb_j = int(self.path[23:25])

					Fin_a = int(self.path[30:34])
					Fin_m = int(self.path[35:37])
					Fin_j = int(self.path[38:40])

					valide = True
					if Fin_a < Deb_a:
						valide = False
						titre = 'Economies réalisées du ' + str(Deb_j) + '/' + str(Deb_m) + '/' + str(Deb_a) + ' au ' + str(Fin_j) + '/' + str(Fin_m) + '/' + str(Fin_a) + ' : dates invalides, réinitialisation de la période'
					elif Fin_a == Deb_a:
						if Fin_m < Deb_m:
							valide = False
							titre = 'Economies réalisées du ' + str(Deb_j) + '/' + str(Deb_m) + '/' + str(Deb_a) + ' au ' + str(Fin_j) + '/' + str(Fin_m) + '/' + str(Fin_a) + ' : dates invalides, réinitialisation de la période'
						elif Fin_m == Deb_m:
							if Fin_j < Deb_j:
								valide = False
								titre = 'Economies réalisées du ' + str(Deb_j) + '/' + str(Deb_m) + '/' + str(Deb_a) + ' au ' + str(Fin_j) + '/' + str(Fin_m) + '/' + str(Fin_a) + ' : dates invalides, réinitialisation de la période'
			except:
				pass

			with open('economies_debut.html', 'r') as f:
				my_str = f.read()

			s = self.mysql.factures_html()
			cpt = 0
			tab_type = []
			tab_cumul = []
			cumul_type = 0
			type_courant = 0
			econ = 0
			for i in range(len(s)):
				if valide:
					aaaa = int(s[i][2][0:4])
					mm = int(s[i][2][5:7])
					jj = int(s[i][2][8:10])

					if aaaa > Fin_a or aaaa < Deb_a:
						continue
					elif (mm > Fin_m and aaaa >= Fin_a) or (mm < Deb_m and aaaa <= Deb_a):
						continue
					elif (jj > Fin_j and aaaa >= Fin_a and mm >= Fin_m) or (jj < Deb_j and aaaa <= Deb_a and mm <= Deb_m):
						continue

				if i == 0 or str(tab_type) == "[]":
					tab_type.append(s[0][0])
					if tab_type[type_courant] == 'EAU':
						econ = 0.14

					elif tab_type[type_courant] == 'ELEC':
						econ = 0.43

					elif tab_type[type_courant] == 'GAZ':
						econ = 0.27

					else:
						econ = 0.04

					tab_cumul.append(s[0][1]*econ)

				elif tab_type[type_courant] == s[i][0]:
					tab_cumul[type_courant] += s[i][1]*econ
				elif tab_type[type_courant] != s[i][0]:
					type_courant +=1
					tab_type.append(s[i][0])
					if tab_type[type_courant] == 'EAU':
						econ = 0.14

					elif tab_type[type_courant] == 'ELEC':
						econ = 0.43

					elif tab_type[type_courant] == 'GAZ':
						econ = 0.27

					else:
						econ = 0.04
					tab_cumul.append(s[i][1]*econ)
					cumul_type = tab_cumul[type_courant]


			total_eco = 0

			for i in range(len(tab_type)):

				cpt = cpt + 1
				my_str = my_str + "          ['"
				str_tmp = tab_type[i] + ": " + str(round(tab_cumul[i], 2)) + "€"
				my_str = my_str + str_tmp
				my_str = my_str + "', "
				my_str = my_str + str("{:10.2f}".format(tab_cumul[i]))
				my_str = my_str + "],\n"
				total_eco = total_eco + tab_cumul[i]


			if valide and titre == '':
				titre = 'Economies réalisées du ' + str(Deb_j) + '/' + str(Deb_m) + '/' + str(Deb_a) + ' au ' + str(Fin_j) + '/' + str(Fin_m) + '/' + str(Fin_a)
				if cpt == 0:
					my_str = my_str + "          ['"
					str_tmp = str("Vide")
					my_str = my_str + str_tmp
					my_str = my_str + "', "
					my_str = my_str + "0"
					my_str = my_str + "],\n"
					titre = titre + ' : aucune économie réalisée!'
				else:
					titre = titre + ' : ' + str("{:10.2f}".format(total_eco)) + '€'

			elif not valide and titre == '':
				titre = 'Toutes les économies réalisées : ' + str("{:10.2f}".format(total_eco)) + '€'

			my_str = my_str + "]);\nvar options = {\ntitle: \'" + titre + "\'\n};"

			with open('economies_fin.html', 'r') as f:
				my_str = my_str + f.read()
			self.wfile.write(bytes(str(my_str)+'\n', 'UTF-8'))

			#eco = open("affichage_economies_finale.html", "w")
			#eco.write(my_str)


		elif self.path == '/configuration':
			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()

			html = ""
			with open('configuration_debut.html', 'r') as f:
				html = f.read()

			s = self.mysql.logement()
			addr = s[0][4]
			ville = s[0][5]
			cp = s[0][6]
			lat = str(s[0][7])
			long = str(s[0][8])

			html += lat + "," + long + "], 11);\nL.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {\n\tmaxZoom: 18,\n\tattribution: 'Map data &copy; <a href=\"https://www.openstreetmap.org/copyright\">OpenStreetMap</a> contributors, ' + 'Imagery © <a href=\"https://www.mapbox.com/\">Mapbox</a>',\n\tid: 'mapbox/streets-v11',\n\ttileSize: 512,\n\tzoomOffset: -1\n}).addTo(mymap);\nL.marker([" + lat + ", " + long + "]).addTo(mymap)\n\t.bindPopup(\"<b>" + addr + "</b><br />" + ville + " " + cp

			with open('configuration_fin.html', 'r') as f:
				html += f.read()

			self.wfile.write(bytes(str(html)+'\n', 'UTF-8'))


		#previsions meteo
		elif self.path == "/forecast":
			print("forecast")

			response = requests.get("http://api.openweathermap.org/data/2.5/forecast?q=Paris&units=metric&appid=1114cb60d0c578c918d954721342d1d7")


			s = Json_handling.decode(response.json())
			print (s['list'][0]) # affichage premiere prevision
			print (s['list'][0]['weather'])

			my_str = ''

			for i in range(len(s['list'])):
				my_str = my_str + '\n' + s['list'][i]['dt_txt'] +'\n' + s['list'][i]['weather'][0]['description'] + '\n' + 'Humidity: ' + str(s['list'][i]['main']['humidity']) + '%' + '\n' + 'Temperature: ' + str(s['list'][i]['main']['temp']) + '°C' + '\n' + 'Wind: ' + str(s['list'][i]['wind']['speed']) + ' m/s' + '\n'


			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()
			self.wfile.write(bytes('Forecast:\n\n' + my_str + '\n', 'UTF-8'))

		else:
			rep = self.mysql.select(res.path)

			if len(rep) > 0 :
				self.send_response(200)
				self.send_header("Content-type", "text/html")
				self.end_headers()
				self.wfile.write(bytes(str(rep)+'\n', 'UTF-8'))
			else:
				self.send_response(404)
				self.send_header("Content-type", "text/html")
				self.end_headers()

	def do_POST(self):
		print("##################")
		ip = str(self.client_address[0])

		if str(ip) in tab_c:
			tab_c[ip] = tab_c[ip] + 1
			print(ip, " : requêtes effectuées : ", tab_c[ip])
		else:
			tab_c[ip] = 1
			print(ip, " : requêtes effectuées : ", tab_c[ip])

		print("##################")

		print("Infos client: IP:", self.client_address[0], "Port :", self.client_address[1])
		print("POST fait sur le port ", self.server.server_port)


######## A adapter #####################
		if self.path == "/index.html":
			q = self.rfile.read(int(self.headers['content-length'])).decode(encoding="utf-8")
			query = urllib.parse.parse_qs(q,keep_blank_values=1,encoding='utf-8')
			path = "/Capteur"
			rep = self.mysql.insert(path,query)
			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()
			with open('index.html', 'r') as f:
				html = f.read()
				self.wfile.write(bytes(str(html)+'\n', 'UTF-8'))
			try:
				port = int(query['Port'][0])
				print ("Utilisation du port ", port)

			except:
				print("Erreur recuperation port")


			try:
				print("Ajout du port ", port)
				my_thread.new_capt_thread(port)
				print("Port ", port, " ajoute avec succes")
			except:
				print("Erreur lors de l'ajout du port ", port)

############################

		else:
			"""Respond to a POST request."""
			res = urllib.parse.urlparse(self.path)
			query = urllib.parse.parse_qs(res.query)
			rep = self.mysql.insert(res.path,query)

			path = ''

			n = 0
			for i in range(len(self.path)):
				path = path + self.path[i]
				if self.path[i] == '/':
					n = n + 1
					if n == 2:
						i = len(self.path)



			print ("PATH = ",path)

			if path == "/Capteur":

				try:
					port = int(query['Port'][0])
					print ("Utilisation du port ", port)

				except:
					print("Erreur recuperation port")


				try:
					print("Ajout du port ", port)
					my_thread.new_capt_thread(port)
					print("Port ", port, " ajoute avec succes")
				except:
					print("Erreur lors de l'ajout du port ", port)




			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()


class MySQL():
	def __init__(self, name):
		self.c = None
		self.req = None
		self.conn = sqlite3.connect(name)
		self.c = self.conn.cursor()

	def __exit__(self, exc_type, exc_value, traceback):
		self.conn.close()

	def select(self,path):
		elem = path.split('/')
		if len(elem) == 2:
			req = "select * from %s" %(elem[1])
		else:
			req = "select %s from %s where id=%s" %(elem[3],elem[1],elem[2])
		return self.c.execute(req).fetchall()

	def capteurs(self):
		req = "select * from Capteur;"
		s = self.c.execute(req).fetchall()
		return s

	def logement(self):
		req = "select * from Logement;"
		s = self.c.execute(req).fetchall()
		return s

	def nom_pieces(self):
		req = "select nom from Piece;"
		s = self.c.execute(req).fetchall()
		return s

	def img_pieces(self):
		req = "select img from Piece;"
		s = self.c.execute(req).fetchall()
		return s

	def nom_types(self):
		req = "select nom from Type_capt;"
		s = self.c.execute(req).fetchall()
		return s

	def img_types(self):
		req = "select img from Type_capt;"
		s = self.c.execute(req).fetchall()
		return s

	def factures_html(self):
		req = "select Type_fact, Montant, Date_fact from Facture ORDER BY Type_fact;"
		s = self.c.execute(req).fetchall()
		return s

	def insert(self,path,query):
		print(query)
		attr = ', '.join(query.keys())
		val = ', '.join('"%s"' %v[0] for v in query.values())
		print(attr,val)
		req = "insert into %s (%s) values (%s)" %(path.split('/')[1], attr, val)
		print(req)
		self.c.execute(req)
		self.conn.commit()

class Json_handling():
	def decode(obj):
		return json.loads(json.dumps(obj, sort_keys=True, indent=4))

class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
	pass

def serve_on_port(port):
	server = ThreadingHTTPServer(("", port), MyHandler)
	server.serve_forever()



def timer_on_port(port):
	t = perpetualTimer(5,printer)
	t.start()




def init_capt_threads():
	data_b = sqlite3.connect('logement.db')
	c = data_b.cursor()
	c.execute('select port from Capteur')
	ports = c.fetchall()

	for p in ports:
		print(p[0])
		threading.Thread(target = serve_on_port, args=[int(p[0])]).start()

def next_free_port():
	data_b = sqlite3.connect('logement.db')
	c = data_b.cursor()
	c.execute('select port from Capteur')
	ports = c.fetchall()

	for i in range(5536, 65535):
		available = True
		for p in ports:
			if p[0] == i:
				available = False
				break
		if available:
			return str(i)
	return str(65535)

class my_thread():

	def new_capt_thread(n):
		try:
			threading.Thread(target = serve_on_port, args=[n]).start()
		except:
			print("Echec de l'ajout de thread")



if __name__ == '__main__':
	threading.Thread(target = serve_on_port, args=[5535]).start()
	init_capt_threads()
	#threading.Thread(target = timer_on_port, args=[5534]).start()
