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


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("\n on message: "+msg.topic+" "+str(msg.payload))

def on_log(client, userdata, level, buf):
    print("\n log:client = "+ str(client))
    print("\n log:level ="+str(level))
    print("\n log:buffer "+str(buf))

def on_subscribe(client, userdata, msg, qos_l):
    print("\non_sub: client ="+str(client))
    print("\non_sub: msg ="+str(msg))
    print("\non_sub: qos level ="+str(qos_l))

try:
    client = mqtt.Client("newSub",True)
    client.on_subscribe = on_subscribe
    client.on_connect = on_connect
    client.on_message = on_message
#    client.on_log = on_log
#    client.connect("iot.eclipse.org", 1883, 60)
    client.connect("test.mosquitto.org", 1883, 60)
#    client.loop_start() # the loop() method periodically
                        # check the callback events

    loop_flag=1
    counter=0
#    while loop_flag==1:
#        print("\nwaiting for callback to occour ", counter)
#        time.sleep(0.1) # pause for 1/10 seconds
#        counter+=1
    res=client.subscribe("IoT_unisa/test2", 1)
    print("\n sub results =", res)
    while True:
        client.loop(2)
        # print("\nsleep...")
        # time.sleep(1)


except Exception as e:
    print('exception ', e)
finally:
    client.loop_stop()
    client.unsubscribe("/IoT_unisa/test2")
    client.disconnect()
    
