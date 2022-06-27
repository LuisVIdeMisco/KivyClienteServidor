from cgitb import text
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
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

from kivy.properties import StringProperty

from kivy.metrics import dp

import Servidor

class ServidorInterf(BoxLayout):
    ruta_base = StringProperty("./FicherosServidor")
    datos_raiz = '.metadata'
    hilos = []
    #dir_ip = StringProperty("")
    #port = StringProperty("")
    #error = StringProperty("Error")
    
    tiIP = ""
    tiPort = ""
    etErr = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 0.2

        blIP = BoxLayout(height=dp(40), width=dp(500))
        etIP = Label(text="Dirección IP: ")
        self.tiIP = TextInput(multiline=False, hint_text="127.0.0.1")
        blIP.add_widget(etIP)
        blIP.add_widget(self.tiIP)

        blPort = BoxLayout(height=dp(40), width=dp(500))
        etPort = Label(text="Puerto: ")
        self.tiPort = TextInput(multiline=False, hint_text="12400")
        blPort.add_widget(etPort)
        blPort.add_widget(self.tiPort)

        blInt = BoxLayout(height=dp(40))
        self.etErr = Label()
        bInt = Button(text="Arrancar", size_hint=(0.25, 0.7), on_press=self.iniciar)
        blInt.add_widget(self.etErr)
        blInt.add_widget(bInt)

        self.add_widget(blIP)
        self.add_widget(blPort)
        self.add_widget(blInt)
    
    def iniciar(self, instance):
        self.etErr.text = "Iniciando"
        print(self.tiIP.text)

class Manejador(ScreenManager):
    pass

class ServidorApp(App):
    def build(self):
        return ServidorInterf()

ServidorApp().run()