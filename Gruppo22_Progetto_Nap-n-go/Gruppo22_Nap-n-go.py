# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

import network
import ntptime
import time
from machine import Pin, I2C, PWM, time_pulse_us
from umqtt.simple import MQTTClient
import ssd1306  
from time import sleep_ms 
import utime
import _thread
import ujson


#imposto l'ora per la sveglia iniziale
imposta_ora = None
imposta_minuti = None

#UTC italia ora legale
offset = + 2 * 60 * 60

sveglia_attiva = False
abilita = True

#statistiche per tener conto di quante volte la sveglia viene disattivata o rinviata
n_disattivata = 0  
n_rinviata = 0

#BUZZER
class BUZZER:
    def __init__(self, sig_pin):
        self.pwm = PWM(Pin(sig_pin, Pin.OUT))
        self.pwm.duty(0)
    def play(self, melodia, wait=150, duty=300):
        global sveglia_attiva
        
        while sveglia_attiva:
            for note in melodia:
                if not sveglia_attiva:
                    break
                if note == 0:
                    self.pwm.duty(0)
                else:
                    self.pwm.freq(note)
                    self.pwm.duty(duty)
                sleep_ms(wait)
        self.pwm.duty(0)

#inizializzo il buzzer
b= BUZZER(14)

#range di ottave utilizzate e la loro frequenza
B3=247
C4=262
CS4=277
D4=294
DS4=311
E4=330
F4=349
FS4=370
G4=392
GS4=415
A4=440
AS4=466
B4=494
C5=523
CS5=554
D5=587
DS5=622
E5=659
F5=698
FS5=740
G5=784
GS5=831
A5=880
AS5=932
B5=988
C6=1047
CS6=1109
D6=1175
DS6=1245
E6=1319

melodia = [
    E5, E4, A4, E5, E5, E4, A4, E5, E5, E4, B4, C5, D5, C5, B4, E4,
    E5, E4, A4, E5, E5, E4, A4, E5, E5, E4, B4, C5, D5, C5, B4, E4,
    E5, E4, A4, E5, F5, F4, A4, F5, G5, G4, B4, G5, E5, E4, G4,
    E5, D5, D4, F4, D5, C5, C4, FS4, C5, B4, B3, E4, GS4, B4,E4, GS4, B4, 
    
    C6, C5, F5, C6, B5, B4, F5, B5, B5, B4, E5, B5, A5, A4, E5, A5,
    A5, A4, D5, A5, GS5, GS4, D5, GS5, A5, A4, C5, E5, A5, C5, E5, A5,
    C6, C5, F5, C6, B5, B4, F5, B5, D6, D5, G5, D6, CS6, CS5, G5, CS6, 
    E6, E5, A5, E6, DS6, DS5, A5, DS6, E6, E5, B5, E6, E6, 0,0,0,
    
   ]


#DISPLAY 
i2c = I2C(0, sda=Pin(21), scl=Pin(22))
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)


#funzione per aggiornare il display con l'ora e i minuti specificati
def aggiorna_display(ora, minuti):
    oled.fill(0)
    oled.text("Ora:", 0, 0)
    oled.text("{:02d}:{:02d}".format(ora, minuti), 0, 16)
    oled.show()
    

#funzione per l'attivazione della sveglia
def sveglia():
    global sveglia_attiva, abilita, n_rinviata
    sveglia_attiva = True
    abilita = False
    oled.fill(0)
    oled.text("Buongiorno :)", 0, 0)
    oled.show()
    # Avvia il thread per la riproduzione della melodia
    _thread.start_new_thread(suona_buzzer, ())
    start_time = utime.ticks_ms()
    #se la sveglia non viene reimpostata, disattivata o rinviata, rimarrà attiva per 60 secondi e si disattiverà automaticamente mantenendo l'orario dell'impostazione della sveglia invariato
    while utime.ticks_diff(utime.ticks_ms(), start_time) < 60000 and sveglia_attiva:
        if s.distance_cm()<5:
            rinvia_sveglia()
            n_rinviata = n_rinviata + 1
    if sveglia_attiva:
        sveglia_attiva = False
        abilita = True
    return

#thread per la riproduzione della melodia
def suona_buzzer():
    global b,melodia
    b.play(melodia)
    return


#thread per l'aggiornamento real time dell'orario
def aggiorna_ora():
    global data_corrente, ora_corrente, minuto_corrente, abilita, offset
    while True:
        data_corrente = time.localtime(time.time() + offset)
        ora_corrente = data_corrente[3]
        minuto_corrente = data_corrente[4]
        if abilita:
            if ora_corrente == imposta_ora and minuto_corrente == imposta_minuti:
                sveglia()
            else:
                aggiorna_display(ora_corrente, minuto_corrente)
        sleep_ms(1000)  # attendo 1 secondo prima di aggiornare l'ora


#SENSORE
class Sensor:
    def __init__(self, trigger_pin, echo_pin):
        self.pin_trigger = Pin(trigger_pin, Pin.OUT)
        self.pin_echo = Pin(echo_pin, Pin.IN)
    
    #metodo per il calcolo della distanza in centimetri
    def distance_cm(self):
        self.pin_trigger.value(0)
        sleep_ms(100)
        self.pin_trigger.value(1)
        sleep_ms(100)
        self.pin_trigger.value(0)
        duration_us = time_pulse_us(self.pin_echo, 1)
        distance_cm = duration_us / 58
        return distance_cm

#inizializzo un sensore
s = Sensor(25,26)

#funzione per la reimpostazione della sveglia
def reimposta_sveglia(ora, minuti):
    global imposta_ora, imposta_minuti, sveglia_attiva, abilita
    if sveglia_attiva:
        sveglia_attiva = False
    else:
        abilita = False
    sleep_ms(100)
    oled.fill(0)
    oled.text("Reimpostando ", 0, 0) 
    oled.text("la sveglia :)", 0, 16)
    oled.show()
    imposta_ora = ora
    imposta_minuti = minuti
    sleep_ms(2000)
    abilita = True
    return

#funzione per la disattivazione della sveglia
def disattiva_sveglia():
    global imposta_ora, imposta_minuti, abilita
    sleep_ms(100)
    oled.fill(0)
    oled.text("Disattivando",0,0)
    oled.text("la sveglia :(", 0, 16)
    oled.show()
    imposta_ora = None
    imposta_minuti = None 
    sleep_ms(2000)
    abilita = True
    return

#funzione per il rinvio della sveglia, la sveglia può essere rinviata per 15 minuti
def rinvia_sveglia():
    global imposta_ora, imposta_minuti, sveglia_attiva, abilita
    if sveglia_attiva:
        sveglia_attiva = False
    else:
        abilita = False
    sleep_ms(100)
    oled.fill(0)
    oled.text("Rinviando ", 0, 0) 
    oled.text("la sveglia :)", 0, 16)
    oled.show()
    imposta_minuti += 15
    if imposta_minuti > 59:
        imposta_ora += 1
        imposta_minuti = imposta_minuti - 60
    sleep_ms(2000)
    abilita = True
    return


# MQTT Server Parameters
MQTT_CLIENT_ID = "micropython-napandgo" 
MQTT_BROKER    = "test.mosquitto.org"
MQTT_TOPIC     = "gruppo22/sensore"
MQTT_SVEGLIA   = b'gruppo22/settSveglia' 

#subCallBack per i messaggi inviati dalla dashboard
def subCallBack(topic, msg):
    global sveglia_attiva, n_disattivata
    if topic == MQTT_SVEGLIA:
        if msg == b'1':
            if sveglia_attiva:
                n_disattivata = n_disattivata + 1
                sveglia_attiva = False
                oled.fill(0)
                oled.show()
                disattiva_sveglia()      
        else:
            stringa = str(msg)
            oraS = stringa[24:26]
            minutiS = stringa[27:29]
            ora = int(oraS)
            if ora == 23:
                ora = 0
            else:
                ora = ora+1
            minuti = int(minutiS)
            reimposta_sveglia(ora, minuti)

#dati per connettersi ad internet
#wi-fi di casa
ssid = 'Infostrada-76A190'
password='jnJCYYxP6x'

#router del telefono
#ssid = 'iPhoneP'
#password = 'forzanapoli'

b.pwm.duty(0)
oled.fill(0)

#procedura di connessione 
print("Connecting to WiFi", end="")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(ssid,password)
while not sta_if.isconnected():
    print(".", end="")
    time.sleep(0.1)
print(" Connected!")

oled.text("Connected",0,0)
oled.show()

print("Connecting to MQTT server... ", end="")
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)  
client.set_callback(subCallBack)
client.connect() #effettuo connessione
client.subscribe(MQTT_SVEGLIA)
print("Connected!")


ntptime.settime()

#Sincronizzazione dell'orario
data_corrente = time.localtime(time.time() + offset)
ora_corrente = data_corrente[3]
minuto_corrente = data_corrente[4]


_thread.start_new_thread(aggiorna_ora, ())


prev_message = ""

while True:
    client.check_msg()
    message = ujson.dumps({
        "rinviata": n_rinviata,
        "disattivata": n_disattivata,
        })
    if message != prev_message:
        client.publish(MQTT_TOPIC,message)
        prev_message = message
    






