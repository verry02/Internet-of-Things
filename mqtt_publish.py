import paho.mqtt.client as mqtt
import time

# The callback for when the client receives a
# CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    global loop_flag
    print("Connected with result code "+str(rc))
    print("\n connected with client "+ str(client))
    print("\n connected with userdata "+str(userdata))
    print("\n connected with flags "+str(flags))
    loop_flag=0

#Called when a message that was to be sent using
#    the publish() call has completed transmission to the broker.
def on_publish(client,userdata,result): #create function for callback
    print("\non_publish data published \n")
    print("\non_pub: result = ", result)

# Called when the client has log information. Define to allow debugging.
#The level variable gives the severity of the message and will be one of
#MQTT_LOG_INFO, MQTT_LOG_NOTICE,
#MQTT_LOG_WARNING, MQTT_LOG_ERR, and MQTT_LOG_DEBUG. The message itself is in buf.
def on_log(client, userdata, level, buf):
    print("\n log:client = "+ str(client))
    print("\n log:level ="+str(level))
    print("\n log:buffer "+str(buf))
    
try:
    client = mqtt.Client("C1")
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_log = on_log
    client.connect("test.mosquitto.org", 1883, 60)
# Calling loop_start() once, before or after connect*(),
#runs a thread in the background to call loop() automatically.
    client.loop_start() # the loop() method periodically
                        # check the callback events

    loop_flag=1
    counter=0
    while loop_flag==1:
        print("\nwaiting for callback to occour ", counter)
        time.sleep(0.1) # pause for 1/10 seconds
        counter+=1
    counter=0
    while counter<10:
        payload="msg"+str(counter)
        print("\ngoing to pub:" + payload)
        res=client.publish("IoT_unisa/test2",payload,2)
        print("\n\n risultato publish =" + str(res))
        counter+=1
        time.sleep(5)
    print("going to sleep....")
#    time.sleep(120)
except Exception as e:
    print('exception ', e)
finally:
    client.disconnect()
    client.loop_stop()