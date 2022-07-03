from cgitb import text
from tkinter import filedialog
from kivy.config import Config
Config.set('graphics', 'width', '600')
Config.set('graphics', 'height', '150')
Config.set('graphics', 'resizable', False)

import socket
import ssl
import os
import sys
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

from kivy.properties import StringProperty

from kivy.metrics import dp

from servidor import Servidor

class ServidorArranc(Screen):
    root = None
    et = ""
    lbl = None
    def __init__(self, root, **kw):
        super().__init__(**kw)
        self.root = root

        self.lbl = Label(pos_hint={'center_y': 0.65, 'center_x':0.5})
        bt = Button(text="Apagar", on_press=self.apagar, size_hint=(0.27, 0.2),
                    pos_hint={'center_y': 0.25, 'center_x':0.5})
        self.add_widget(self.lbl)
        self.add_widget(bt)

    def inicio(self):
        dIP = self.root.servidor.dir_ip
        port = self.root.servidor.port
        et = "Servidor escuchando en la dirección " + str(dIP) + ":" + str(port) + "\n"
        et += "Cerrar esta ventana supone apagar el servidor"
        self.lbl.text = et

    def apagar(self, instance):
        self.lbl.text = "Apagando"
        self.root.servidor.cerrar()
        self.root.servidor.join()
        App.get_running_app().stop()

class ServidorInterf(Screen):
    root = None
    dfldir = os.path.dirname(__file__)
    
    tiIP = ""
    tiPort = ""
    etErr = ""

    def __init__(self, root, **kwargs):
        super().__init__(**kwargs)
        self.root = root

        self.orientation = "vertical"
        self.width = dp(595)
        self.height = dp(145)
        self.padding = 5


        etIP = Label(text="Dirección IP: ", size_hint=(None,None), height=dp(30), pos=(dp(17),dp(113)))
        self.tiIP = TextInput(write_tab=False, multiline=False, hint_text="127.0.0.1", size_hint=(None,None),
                                height=dp(30), width=dp(200), pos=(dp(135), dp(113)))

        #blPort = BoxLayout(height=dp(40), width=dp(500))
        etPort = Label(text="Puerto: ", size_hint=(None,None), height=dp(30), pos=(dp(0),dp(83)))
        self.tiPort = TextInput(write_tab=False, multiline=False, hint_text="12400", size_hint=(None,None),
                                height=dp(30), width=dp(200), pos=(dp(135), dp(83)), input_filter='int')

        self.etErr = Label(height=dp(75), width=dp(580), pos=(dp(0),dp(-35)))
        bInt = Button(text="Arrancar", size_hint=(0.27, 0.2), on_press=self.iniciar, 
                        pos_hint={'center_y': 0.62, 'right':0.9})
        bDir = Button(text="Directorio", size_hint=(0.27, 0.2), on_release=self.escogerDir,
                        pos_hint={'center_y': 0.85, 'right':0.9})

        self.add_widget(etIP)
        self.add_widget(etPort)
        self.add_widget(self.etErr)
        self.add_widget(self.tiIP)
        self.add_widget(self.tiPort)
        self.add_widget(bInt)
        self.add_widget(bDir)

    # Función que comprueba que la dirección IP introducida es correcta
    def checkIP(self, dirIP):
        if len(dirIP) <= 0:
            return False
        
        elementos = dirIP.split('.')
        if not len(elementos) == 4:
            return False

        for e in elementos:
            ei = int(e)
            bien = ei >= 0 and ei <= 255
            if not bien:
                return False
        
        return True
    
    def iniciar(self, instance):
        ipT = self.tiIP.text

        elementos = ipT.split()
        if len(elementos) > 1:
            self.etErr.text = "El campo IP tiene más de una dirección"
            return

        puerto = self.tiPort.text
        elementos = puerto.split()
        if len(elementos) > 1:
            self.etErr.text = "Se ha dado más de un puerto"
            return

        if not self.checkIP(ipT):
            self.etErr.text = "El campo IP no es válido o está vacío"
            return

        puerto = int(puerto)
        if puerto < 0:
            self.etErr.text = "El puerto dado no es correcto"

        self.etErr.text = "Iniciando"

        self.root.servidor = Servidor(ipT, puerto)
        self.root.servidor.setDir(self.dfldir + "/FicherosServidor")
        self.root.servidor.start()

        sig = self.root.get_screen("Arrancado")
        sig.inicio()
        self.root.switch_to(sig)

    def escogerDir(self, instance):
        dir = filedialog.askdirectory(initialdir=self.dfldir, title="Selecciona directorio del servidor")
        self.dfldir = dir


class Manejador(ScreenManager):
    servidor = None
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(ServidorInterf(self, name='Inicio'))
        self.add_widget(ServidorArranc(self, name="Arrancado"))

class ServidorApp(App):
    def build(self):
        return Manejador()

ServidorApp().run()