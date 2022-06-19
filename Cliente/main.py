import sys
import socket
import ssl
import os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from pathlib import Path


homedir = Path.home()
dfldir = str(homedir)
cantSub = 0
sub=0
dwnDir = str(homedir) + '/' + 'Downloads'


# Funciones de conexion
def conectar():
    global server_address
    global context

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssock = context.wrap_socket(sock, server_hostname=dir_ip)
    ssock.connect(server_address)
    return ssock


context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.verify_mode = ssl.CERT_REQUIRED
context.load_cert_chain('clientCert.pem', 'claveClient.pem')
context.load_verify_locations('certCA.pem')

dir_ip = 'localhost'
serv_port = 12400
server_address = (dir_ip, serv_port)

# nombre = input("Nombre Fichero Enviar: ")


def transmitir(ssock, nombre):
    global cantSub

    file_size = os.path.getsize(nombre)
    name = os.path.basename(nombre)
    nameLen = len(name).to_bytes(4, 'big', signed=False)
    byteslengthFich = file_size.to_bytes(4, 'big', signed=False)

    f = open(nombre, 'rb')

    ssock.send(nameLen)
    ssock.send(byteslengthFich)

    name = name.encode()
    ssock.send(name)

    amount_sent = 0

    while amount_sent < file_size:
        d = f.read(1460)
        numbytes = ssock.send(d)
        amount_sent += numbytes
        pb['value'] += (numbytes/cantSub) * 200
        clientui.update()

    f.close()

    while ssock.recv(1) == 0:
        pass


def subirTodo():
    global cantSub
    global sub

    nFich = libx.size()
    if(nFich) == 0:
        return

    insrt['state'] = DISABLED
    dlt['state'] = DISABLED
    sbr['state'] = DISABLED

    ssock = conectar()
    pb['value'] = 0
    pb.grid(row=4, column=2, columnspan=2, sticky=N)
    clientui.update()
    try:
        ssock.send('U'.encode())
        n = nFich.to_bytes(4, 'big', signed=False)
        ssock.send(n)

        sub = 0
        while libx.size() != 0:
            fich = libx.get(0)
            sDat['text'] = 'Subiendo archivo ' + str(sub+1) + '/' + str(nFich) + "\n" + fich
            transmitir(ssock, fich)
            libx.delete(0)
            sub += 1

        sDat['text'] = 'Se han subido los archivos con éxito'

    except:
        sDat['text'] = 'Se ha producido un error durante la transmision\nSe han mandado ' + str(sub) + " archivos"
    finally:
        ssock.close()
        cantSub = 0
        tmF['text'] = ''
        sub = 0
        pb.stop()
        pb.grid_forget()
        insrt['state'] = NORMAL
        dlt['state'] = NORMAL
        sbr['state'] = NORMAL
        clientui.update()


def info():
    ssock = conectar()
    try:
        ssock.send('I'.encode())
        meta = open('.metadatos', 'wb')
        tam = ssock.recv(4)
        tam = int.from_bytes(tam, byteorder='big', signed=False)

        amount_received = 0
        while amount_received < tam:
            data = ssock.recv(tam - amount_received)
            amount_received += len(data)
            meta.write(data)
            clientui.update()

        meta.close()
        meta = open('.metadatos', 'r')
        for line in meta.readlines():
            libx.insert(END, line)

    finally:
        meta.close()
        os.remove('.metadatos')
        ssock.close()


def eliminar():
    fichElim = []
    if len(libx.curselection()) == 0:
        return

    while len(libx.curselection()) != 0:
        ind = libx.curselection()[0]
        fich = libx.get(ind)
        fichElim.append(fich[:-1])
        libx.delete(ind)

    ssock = conectar()
    try:
        ssock.send('R'.encode())
        cant = len(fichElim).to_bytes(4, 'big', signed=False)
        ssock.send(cant)

        for fich in fichElim:
            long = len(fich)
            lF = long.to_bytes(4, 'big', signed=False)
            ssock.send(lF)
            ssock.send(str(fich).encode())

            while ssock.recv(1) == 0:
                pass

    finally:
        ssock.close()


def descargar():
    global dwnDir
    fichDwn = []
    if len(libx.curselection()) == 0:
        return

    efr['state'] = DISABLED
    selDir['state'] = DISABLED
    dwn['state'] = DISABLED

    for i in range(len(libx.curselection())):
        ind = libx.curselection()[i]
        fich = libx.get(ind)
        fichDwn.append(fich[:-1])

    ssock = conectar()
    baj = 0
    pb['value'] = 0
    pb.grid(row=4, column=2, columnspan=2, sticky=N)
    clientui.update()
    try:
        sDat['text'] = 'Calculando datos a descargar...'
        ssock.send('D'.encode())
        cant = len(fichDwn).to_bytes(4, 'big', signed=False)
        ssock.send(cant)

        for fich in fichDwn:
            long = len(fich)
            lF = long.to_bytes(4, 'big', signed=False)
            ssock.send(lF)
            ssock.send(str(fich).encode())

        datos = ssock.recv(4)
        cantDwn = int.from_bytes(datos, byteorder='big', signed=False)

        for fich in fichDwn:
            fd = open(dwnDir + '/' + fich, 'wb')
            tam = ssock.recv(4)
            tam = int.from_bytes(tam, byteorder='big', signed=False)

            amount_received = 0
            sDat['text'] = 'Descargando archivo ' + str(baj + 1) + '/' + str(len(fichDwn)) + "\n" + fich
            while amount_received < tam:
                data = ssock.recv(1460)
                amount_received += len(data)
                fd.write(data)
                pb['value'] += (len(data) / cantDwn) * 200
                clientui.update()

            baj += 1
            fd.close()
            ssock.send(b'1')

        tmF['text'] = 'Se han descargado todos los archivos con exito'

    except:
        sDat['text'] = 'Se ha producido un error durante la descarga\nSe han descargado ' + str(baj) + " archivos"
    finally:
        ssock.close()
        pb.stop()
        pb.grid_forget()
        dwn['state'] = NORMAL
        efr['state'] = NORMAL
        selDir['state'] = NORMAL
        clientui.update()


def actualizarTam():
    global cantSub

    medida = ''
    if cantSub / 1024 < 1:
        medida = str(cantSub) + 'Bytes'
    elif cantSub / (1024 ** 2) < 1:
        medida = "{:.2f}".format(cantSub / 1024) + 'KB'
    elif cantSub / 1024 ** 3 < 1:
        medida = "{:.2f}".format(cantSub / 1024 ** 2) + 'MB'
    else:
        medida = "{:.2f}".format(cantSub / 1024 ** 3) + 'GB'

    if cantSub > 0:
        tmF['text'] = "Se han seleccionado " + medida + " a subir al servidor"
    else:
        tmF['text'] = ''
        cantSub = 0

    sDat['text'] = ''


def insrtLista():
    global dfldir
    global cantSub

    dire = dfldir
    ficheros = filedialog.askopenfilenames(initialdir=dire, title="Selecciona ficheros a subir")

    if len(ficheros) == 0:
        return

    presentes = varFic.get()
    for fich in ficheros:
        if not fich in presentes:
            libx.insert(END, fich)
            cantSub += os.path.getsize(fich)

    # Actualizamos la carpeta
    ult = ficheros[-1]
    pos = len(ult) - 1
    while pos >= 0:
        if ult[pos] == '\\' or ult[pos] == '/':
            dfldir = ult[0:pos - 1]
            break
        else:
            pos -= 1

    # Actualizamos los datos
    actualizarTam()


def eliminarSel():
    global cantSub

    if len(libx.curselection()) == 0:
        return

    while len(libx.curselection()) != 0:
        ind = libx.curselection()[0]
        fich = libx.get(ind)
        cantSub -= os.path.getsize(fich)
        libx.delete(ind)

    actualizarTam()


def dirDesc():
    global dwnDir
    dir = filedialog.askdirectory(initialdir=dwnDir, title='Selecciona directorio donde guardar ficheros descargados')
    dwnDir = dir


def comenzar(mandato):
    if mandato == 'U':
        clientui.after(1, lambda: subirTodo())
    elif mandato == 'R':
        clientui.after(1, lambda: eliminar())
    elif mandato == 'D':
        clientui.after(1, lambda: descargar())


def intCarga():
    lblibx['text'] = "Ficheros seleccionados"
    libx.delete(0, END)
    efr.grid_forget()
    selDir.grid_forget()
    dwn.grid_forget()
    insrt.grid(row=6, rowspan=1, column=0, sticky=S, pady=5)
    dlt.grid(row=6, rowspan=1, column=1, sticky=S, pady=5)
    sbr.grid(row=5, column=2, columnspan=2)
    clt['relief'] = SUNKEN
    srv['relief'] = RAISED


def intDescarga():
    lblibx['text'] = "Ficheros del servidor"
    libx.delete(0, END)
    insrt.grid_forget()
    dlt.grid_forget()
    sbr.grid_forget()
    efr.grid(row=6, rowspan=1, column=0, sticky=S, pady=5)
    selDir.grid(row=6, rowspan=1, column=1, sticky=S, pady=5)
    dwn.grid(row=5, column=2, columnspan=2)
    clt['relief'] = RAISED
    srv['relief'] = SUNKEN
    clientui.update()
    clientui.after(1, lambda: info())


clientui = Tk()

clientui.title('Cliente')
clientui.geometry('800x600')

lblibx = Label(clientui, text="Ficheros seleccionados", font='Arial 12')
varFic = Variable(value=[])
fr = Frame(clientui)
libx = Listbox(fr, height=32, width=70, selectmode=EXTENDED, bd=4, listvariable=varFic)
scbr = Scrollbar(fr, orient='vertical', width=15)
insrt = Button(clientui, text="+\tAñadir fichero", font="Arial 12", width=20, pady=5, command=insrtLista)
dlt = Button(clientui, text="Eliminar seleccionados", font="Arial 12", width=20, pady=5, command=eliminarSel)
tmF = Label(clientui, text='', font="Arial 11", width=37, height=10)
sbr = Button(clientui, text='Subir ficheros', font='Arial 12', width=20, pady=5, command=lambda: comenzar('U'))
pb = ttk.Progressbar(clientui, orient='horizontal', length=200, mode='determinate')
sDat = Label(clientui, text='', font="Arial 11", width=37, height=10)
clt = Button(clientui, text='Mandar ficheros', font='Arial 12', width=18, pady=5, relief=SUNKEN, command=intCarga)
srv = Button(clientui, text='Descargar ficheros', font='Arial 12', width=18, pady=5, command=intDescarga)
efr = Button(clientui, text='Eliminar fichero', font='Arial 12', width=20, pady=5, command=lambda: comenzar('R'))
selDir = Button(clientui, text='Directorio descargas', font='Arial 12', width=20, pady=5, command=dirDesc)
dwn = Button(clientui, text='Descargar seleccionados', font='Arial 12', width=20, pady=5, command=lambda: comenzar('D'))

libx.config(yscrollcommand=scbr.set)
scbr.config(command=libx.yview)

lblibx.grid(row=0, column=0)
fr.grid(row=1, rowspan=5, column=0, columnspan=2, sticky=W)
libx.grid(row=1, rowspan=5, column=0, columnspan=2, sticky=W)
scbr.grid(row=1, rowspan=5, column=2, sticky=NS)
insrt.grid(row=6, rowspan=1, column=0, sticky=S, pady=5)
dlt.grid(row=6, rowspan=1, column=1, sticky=S, pady=5)
tmF.grid(row=2, column=2, columnspan=2, sticky=NE)
sbr.grid(row=5, column=2, columnspan=2)
sDat.grid(row=3, column=2, columnspan=2, sticky=E)
# pb.grid(row=4, column=2, sticky=N)
clt.grid(row=1, column=2, sticky=E)
srv.grid(row=1, column=3, sticky=W)

insrt['bg'] = '#251aff'
insrt['fg'] = 'white'
dlt['bg'] = '#b1b1b1'
sbr['bg'] = '#251aff'
sbr['fg'] = 'white'

efr['bg'] = '#251aff'
efr['fg'] = 'white'
selDir['bg'] = '#b1b1b1'
dwn['bg'] = '#251aff'
dwn['fg'] = 'white'

clientui.mainloop()

