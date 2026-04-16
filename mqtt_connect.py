import paho.mqtt.client as mqtt
import time

# The callback for when the client receives
# a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    global loop_flag
    print("Connected with result code "+str(rc))
    print("\n connected with client "+ str(client))
    print("\n connected with userdata "+str(userdata))
    print("\n connected with flags "+str(flags))
    loop_flag=0


try:
    client = mqtt.Client()
    client.on_connect = on_connect #attach the function to callback
#    client.connect("iot.eclipse.org", 1883, 60)
    client.connect("test.mosquitto.org", 1883, 60)
#    client.loop_start() # the loop() method periodically
                        # check the for callback events
#    client.loop_forever()
    loop_flag=1
    counter=0
    while loop_flag==1:
        print("\nwaiting for callback to occour ", counter)
        time.sleep(0.1) # pause for 1/10 seconds
        counter+=1
        # the loop() method periodically
        # check the for callback events
        #These functions are the driving force behind the client.
        #If they are not called, incoming network data will not be processed
        #and outgoing network data may not be sent in a timely fashion.
        #Call regularly to process network events.
        client.loop()
except Exception as e:
    print('exception ', e)
#the finally block will always be executed,
#no matter if the try block raises an error or not.
finally:
    client.disconnect()
    #Call loop_stop() to stop the background thread.
    client.loop_stop()
    print("exit")
