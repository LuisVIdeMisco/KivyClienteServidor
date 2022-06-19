from kivy.config import Config
Config.set('graphics', 'width', '600')
Config.set('graphics', 'height', '150')

import socket
import ssl
import os
import sys
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty

class Servidor(BoxLayout):
    ruta_base = StringProperty("./FicherosServidor")
    datos_raiz = '.metadata'
    hilos = []
    dir_ip = StringProperty("")
    port = StringProperty("")
    error = StringProperty("")

    def carga(self, con, carpeta):
        if not os.path.isdir(carpeta):
            os.makedirs(carpeta, 0o777)

        global datos_raiz
        md = carpeta + "/" + self.datos_raiz
        guardados = []
        if not os.path.exists(md):
            fp = open(md, 'x')
            fp.close()
        else:
            fp = open(md, 'r')
            for line in fp.readlines():
                guardados.append(line[:-1])

        try:
            n = con.recv(4)
            cantidad = int.from_bytes(n, byteorder='big', signed=False)

            meta = open(md, 'a')

            for i in range(cantidad):
                datos = con.recv(4)
                longitud = int.from_bytes(datos, byteorder='big', signed=False)
                datos = con.recv(4)
                longitudFich = int.from_bytes(datos, byteorder='big', signed=False)

                nombre_fich = con.recv(longitud).decode()

                try:
                    if nombre_fich in guardados:
                        name, ext = nombre_fich.split('.')
                        num = 1
                        while nombre_fich in guardados:
                            nombre_fich = name + '(' + str(num) + ').' + ext
                            num += 1

                    meta.write(nombre_fich + '\n')
                    f = open(carpeta + '/' + nombre_fich, 'wb')

                    amount_received = 0
                    amount_expected = longitudFich

                    while amount_received < amount_expected:
                        data = con.recv(amount_expected - amount_received)
                        amount_received += len(data)
                        f.write(data)
                except:
                    break

                finally:
                    f.close()
                    con.send(b'1')

        finally:
            meta.close()
            con.close()


    def info(con, carpeta):
        if not os.path.isdir(carpeta):
            os.makedirs(carpeta, 0o777)

        global datos_raiz
        md = carpeta + "/" + datos_raiz
        if not os.path.exists(md):
            fp = open(md, 'x')
            fp.close()

        tam = os.path.getsize(md)
        file_size = tam.to_bytes(4, 'big', signed=False)
        con.send(file_size)

        amount_sent = 0
        meta = open(md, 'rb')
        while amount_sent < tam:
            d = meta.read(1460)
            numbytes = con.send(d)
            amount_sent += numbytes

        meta.close()
        while con.recv(1) == 0:
            pass

        con.close()


    def remove(con, carpeta):
        global datos_raiz
        md = carpeta + "/" + datos_raiz
        meta = open(md, 'r')
        guardados = []
        for line in meta.readlines():
            guardados.append(line[:-1])

        meta.close()

        n = con.recv(4)
        cantidad = int.from_bytes(n, byteorder='big', signed=False)

        for i in range(cantidad):
            datos = con.recv(4)
            longitud = int.from_bytes(datos, byteorder='big', signed=False)

            nombre_fich = con.recv(longitud).decode()
            guardados.remove(nombre_fich)

            os.remove(carpeta + '/' + nombre_fich)

            con.send(b'1')

        meta = open(md, 'w')
        meta.truncate(0)
        for line in guardados:
            meta.write(line + '\n')

        con.close()


    def download(con, carpeta):
        n = con.recv(4)
        cantidad = int.from_bytes(n, byteorder='big', signed=False)

        cantDwn = 0
        ficheros = []
        for i in range(cantidad):
            datos = con.recv(4)
            longitud = int.from_bytes(datos, byteorder='big', signed=False)

            nombre_fich = con.recv(longitud).decode()
            nombre = carpeta + '/' + nombre_fich

            long = os.path.getsize(nombre)
            cantDwn += long
            ficheros.append(nombre)

        cantDwn = cantDwn.to_bytes(4, 'big', signed=False)
        con.send(cantDwn)

        for nombre in ficheros:
            long = os.path.getsize(nombre)
            tam = long.to_bytes(4, 'big', signed=False)
            con.send(tam)

            fd = open(nombre, 'rb')

            amount_sent = 0
            while amount_sent < long:
                d = fd.read()
                numbytes = con.send(d)
                amount_sent += numbytes

            while con.recv(1) == 0:
                pass

        con.close()

    def arrancar(self):
        global dir_ip


class ServidorApp(App):
    pass

ServidorApp().run()