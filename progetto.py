
from machine import Pin, I2C, PWM, RTC, time_pulse_us #I2C per il display, PWM per il buzzer, RTC per il display e time_pulse_us per il sensore 
import ssd1306 #per il display  
import time 
from time import sleep_ms #per buzzer
import utime #per mostrare l'ora 
import network #serve per instanziare un oggetto necessario per connetterci alla wifi. #il microcontrollore potrebbe agire o da stazione di rete (host che si connette ad un AP), oppure fungere da AP.#A noi interessa la prima. #dobbiamo abilitare l'interfaccia, effettuare la scansione di AP disponibili, eventualmente connetterci ad una rete wifi con SSID. 
import ujson
from umqtt.simple import MQTTClient

led = Pin(4, Pin.OUT) #inizializzo il led
btn1 = Pin (14, Pin.IN, Pin.PULL_UP) #inizializzo il bottone 

# MQTT Server Parameters
#MQTT_CLIENT_ID = "micropython-progetto"
#MQTT_BROKER    = "test.mosquitto.org"
#MQTT_USER      = ""
#MQTT_PASSWORD  = ""
#MQTT_TOPIC     = "group22/progetto"
#MQTT_SVEGLIA   = b'group22/sveglia' 

#SENSORE
# Configura il pin del sensore ad ultrasuoni
pin_trigger = Pin(25, Pin.OUT)
pin_echo = Pin(26, Pin.IN)

#funzione per calcolare la distanza rilevata dal sensore 
def distance_cm():
    pin_trigger.value(0) # Invia un impulso di trigger di 10 us. Questo impulso viene utilizzato per "attivare" il sensore e inviare un segnale acustico verso l'oggetto da misurare.
    time.sleep_us(2) #Dopo un breve intervallo di 2 microsecondi, 
    pin_trigger.value(1) #la funzione alza il livello del pin del trigger a 1, inviando quindi un segnale di trigger al sensore ad ultrasuoni. Questo segnale innesca l'invio del segnale acustico verso l'oggetto da misurare.
    time.sleep_us(10)#Dopo un ulteriore intervallo di 10 microsecondi, 
    pin_trigger.value(0)#la funzione abbassa di nuovo il livello del pin del trigger a 0, indicando che l'impulso di trigger è terminato.
    duration_us = time_pulse_us(pin_echo, 1)# Misura la durata dell'eco. La funzione time_pulse_us restituisce la durata in microsecondi dell'impulso ricevuto dal sensore.
    distance_cm = duration_us / 58# Calcola la distanza in cm. La durata dell'eco viene quindi divisa per 58, che è la costante empirica per convertire la durata dell'eco in centimetri. Il risultato è la distanza in centimetri dall'oggetto.
    return distance_cm #La funzione restituisce il valore della distanza in centimetri


#DISPLAY
# inizializzo il display
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

#BUZZER 
class BUZZER:
    def __init__(self, sig_pin):
        self.pwm = PWM(Pin(sig_pin, Pin.OUT))
        self.playing = True #per interrompere il ciclo quando si vuole disattivare la sveglia 
        self.rimanda = False #in questa variabile salvo il primo valore utile rilevato dal sensore per rimandare la sveglia 
        self.disattiva = False #in questa variabile salvo il primo valore utile rilevato dal sensore per disattivare la sveglia
       
    #il controllo della distanza viene effettuato dopo ogni nota, basta che durante la riproduzione della sequenza almeno una volta ci si avvici al sensori o lo si tocca per pfar salvare il valore della distanza e a fine riproduzione della sequenza rinviare/disattivare la sveglia 
    def play(self, melodies, wait, duty): 
        while self.playing: # con questo while il ciclo si ripete all'in finito
            for note in melodies:
                if self.playing ==False:
                    return #esco dal ciclo e disattivo la sveglia 
                if note == 0:
                    self.pwm.duty(0) #buzzer in silenzio
                else:
                    dist = distance_cm()
                    if dist < 200 and dist >= 4: #avvicino la mano al sensore ma non lo tocco 
                        self.rimanda = True
                    if dist <=3: #perché il simulatore non è preciso, nella realtà proviamo con 0 per simulare il tocco del sensore 
                        #self.disattiva = True
                        self.playing = False

                    print("Distanza: {} cm".format(dist)) #stampo la distanza dopo ogni nota 
                    self.pwm.freq(note)
                    self.pwm.duty(duty)             
                sleep_ms(wait)
                self.pwm.duty(0)
            if self.rimanda == True:
                print ("Sveglia Rimandata")
                #msg_rimanda = ujson.dumps({ "Sveglia rimandata!"})
                #print("Reporting to MQTT topic {}: {}".format(MQTT_TOPIC, msg_rimanda))
               # client.publish(MQTT_TOPIC, msg_rimanda)
                sleep_ms (3000) #3 secondi per comodità, nella realtà convertiremo 5/10 minuti per rimandare la sveglia 
                self.rimanda = False
            if self.disattiva == True: 
                print ("Sveglia disattivata")
                #msg_disattiva = ujson.dumps({ "Sveglia disattivata!"})
                #print("Reporting to MQTT topic {}: {}".format(MQTT_TOPIC, msg_disattiva))
               # client.publish(MQTT_TOPIC, msg_disattiva)
                self.disattiva = False
                self.playing = False 
  

#note e frequenze equivalenti
C5=523
E5=659
G5=784
C6=1047
E6=1319
G6=1568
C7=2093

# Suoneria della sveglia (sono due cicli di note)
suono = [
    E5, G5, C6, E6, 0, 0, E6, 0,
    G5, 0, C6, 0, E6, 0, G6, 0,
    C7, 0, G6, 0, E6, 0, C6, 0,
    G5, 0, E5, 0, C5, 0, 0, 0,
    E5, G5, C6, E6, 0, 0, E6, 0,
    G5, 0, C6, 0, E6, 0, G6, 0,
    C7, 0, G6, 0, E6, 0, C6, 0,
    G5, 0, E5, 0, C5, 0, 0, 0,
   ]


            
start=0 
b=BUZZER(23)

#BOTTONE
def toggleLED(btn1):
    global start
    current = time.ticks_ms()
    delta = time.ticks_diff(current, start) #differenza tra current e start. SE LA DIFF tra questi due è minore di 200 ms allora significa che ho cliccato due o più volte. 
    if delta<200:
        return 
    start=current
    led.off()   
    #msg_led = ujson.dumps({ "Luce spenta!"})
    #print("Reporting to MQTT topic {}: {}".format(MQTT_TOPIC, msg_led))
    #client.publish(MQTT_TOPIC, msg_led)
btn1.irq(handler=toggleLED, trigger=Pin.IRQ_FALLING) # viene impostata l'handler di interrupt "btn1.irq" su "toggleLED" utilizzando "Pin.IRQ_FALLING" come trigger. In questo modo, la funzione "toggleLED" viene chiamata ogni volta che viene rilevato un evento di interrupt del pin "btn1" che cade.
  

# or import from machine depending on your micropython version
rtc = RTC()
rtc.datetime((2023, 5, 12, 4, 17, 50, 0, 0)) #imposto la data corrente :anno, mese, giorno, numero di giorno della settimana, ora, minuto, secondo, millisecondo


#COMANDI CON NODERED, DA RIVEDERE, ho scritto le print solo per vedere se funziona il resto del codice, in realtà andrebbero dei comandi 
#def subCallback(topic,msg):
  #print (topic, msg)
  #if topic == MQTT_SVEGLIA:
   # if msg == b'1':
    #  toggleLED()
    #if msg ==b'rimanda':
        # b.rimanda = True
     #   print ("sveglia rimandata")
    #if msg == b'disattiva':
        #b.disattiva = True 
     #   print ("sveglia disattivata")


'''print("Connecting to WiFi", end="")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
#metodo che tenterà sempre di connettersi alla rete. dobbiamo solo controllare se è connesso oppure no. la connect sta prima del while finchè non riesche il tentativo di connessione.
sta_if.connect('Wokwi-GUEST', '') 
while not sta_if.isconnected():
  print(".", end="")
  time.sleep(0.1)
print(" Connected!")

print("Connecting to MQTT server... ", end="")
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
client.set_callback(subCallback)
client.connect()
client.subscribe(MQTT_SVEGLIA) 
print("Connected!")
'''
#SVEGLIA
while True:
        current_time = utime.time() #ottengo il tempo corrente in secondi 
        local_time = utime.localtime(current_time)#converto il tempo corrente in una tupla di componenti locali
        #localtime restituisce una tupla di 8 elementi, vedi documentazione micropython
        
        # scrivo l'ora corrente sul display
        stringa_ora= [ local_time[3], ":", local_time[4], ":", local_time[5]]

        oled.fill(0)
        oled.text("Ora locale:",0,0,1)
        for i, elemento in enumerate (stringa_ora):
            oled.text(str(elemento),(i+1)*13,17)
        
    
        stringa_data= [local_time[2], "/", local_time[1], "/", local_time[0]]

        oled.text("Data locale:",0,35,1)
        for i, elemento in enumerate (stringa_data):
            oled.text(str(elemento),(i+1)*13,50)
        oled.show()  

        oled.fill(0)

#appena scattano le 17:00:03 suona la sveglia 
        if local_time[5] == 3: 
            '''message = ujson.dumps({ "E' ora di alzarsi!"})
            print("Reporting to MQTT topic {}: {}".format(MQTT_TOPIC, message))
            client.publish(MQTT_TOPIC, message)
            '''
            led.on()
            b.play(suono,150,512)