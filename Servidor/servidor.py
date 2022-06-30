import socket
import ssl
import os
import threading
import sys

encendido = False

class Servidor(threading.Thread):
    dir_ip = "localhost"
    port = 12400
    ruta_base = './FicherosServidor'
    datos_raiz = '.metadata'
    hilos = []

    context = ""
    sock = ""
    ssock = ""
    encendido = True

    def __init__(self, dir_ip="localhost", port=12400):
        super().__init__(daemon=True)
        self.dir_ip = dir_ip
        self.port = port
        dir = os.path.dirname(__file__)
        
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.verify_mode = ssl.CERT_REQUIRED
        self.context.load_cert_chain(dir + '/serverCert.pem', dir + '/claveServer.pem')
        self.context.load_verify_locations(dir + '/certCA.pem')

        # Creamos el socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ssock = self.context.wrap_socket(self.sock)

        server_address = (self.dir_ip, self.port)
        self.ssock.bind(server_address)

        self.ssock.listen(5)


    def setDir(self, ruta_base):
        self.ruta_base = ruta_base
        if not os.path.isdir(ruta_base):
            os.makedirs(ruta_base, 0o777)


    def carga(self, con, carpeta):
        if not os.path.isdir(carpeta):
            os.makedirs(carpeta, 0o777)

        datos_raiz = self.datos_raiz
        md = carpeta + "/" + datos_raiz
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


    def info(self, con, carpeta):
        if not os.path.isdir(carpeta):
            os.makedirs(carpeta, 0o777)

        datos_raiz = self.datos_raiz
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


    def remove(self, con, carpeta):
        datos_raiz = self.datos_raiz
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


    def download(self, con, carpeta):
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
    
    def run(self):
        ruta = self.ruta_base
        while self.encendido:
            try:
                conexion, dir_client = self.ssock.accept()
            except:
                print(sys.exc_info())
                continue

            func = conexion.recv(1).decode()

            if func == 'U':     # Upload
                # carga(conexion, ruta_base + '/' + dir_client[0])
                th = threading.Thread(target=self.carga, args=(conexion, str(ruta) + '/' + str(dir_client[0])), daemon=True)
            elif func == 'I':
                th = threading.Thread(target=self.info, args=(conexion, str(ruta) + '/' + str(dir_client[0])), daemon=True)
            elif func == 'R':
                th = threading.Thread(target=self.remove, args=(conexion, str(ruta) + '/' + str(dir_client[0])), daemon=True)
            elif func == 'D':
                th = threading.Thread(target=self.download, args=(conexion, str(ruta) + '/' + str(dir_client[0])), daemon=True)
            else:
                th = None

            if not th == None:
                self.hilos.append(th)
                th.start()

            for th in self.hilos:
                if not th.is_alive():
                    th.join()
                    self.hilos.remove(th)

    def terminar(self):
        self.encendido = False


