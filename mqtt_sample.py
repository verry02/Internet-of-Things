import paho.mqtt.client as mqtt

#Here is a very simple example
#that subscribes to the broker $SYS topic tree and prints out the resulting messages.


# The callback for when the client receives a CONNACK response from the server.
#client:the client instance for this callback
#userdata: the private user data as set in Client()
#flags:response flags sent by the broker
#rc:the connection result

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    #0: Connection successful
    #1: Connection refused - incorrect protocol version
    #2: Connection refused - invalid client identifier
    #3: Connection refused - server unavailable
    #4: Connection refused - bad username or password
    #5: Connection refused 
    print("Flag:"+str(flags))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")
    #subscribe(topic, qos=0)
    #topic: a string specifying the subscription topic to subscribe to.
    #qos:the desired quality of service level for the subscription. Defaults to 0.

# The callback for when a PUBLISH message is received from the server.
# on_message(client, userdata, message)
# client: the client instance for this callback
# userdata: the private user data as set in Client() 
# message: an instance of MQTTMessage. This is a class with members topic, payload, qos, retain (true/false).
def on_message(client, userdata, msg):
    print("Received message " + str(msg.payload) + " on topic "
          + msg.topic + " with QoS " + str(msg.qos))

#Client(client_id=””, clean_session=True, userdata=None, protocol=MQTTv311, transport=”tcp”)
#client_id the unique client id string used when connecting to the broker.
#          If client_id is zero length or None, then one will be randomly generated.
#          In this case the clean_session parameter must be True.
#clean_session: a boolean that determines the client type.
#               If True, the broker will remove all information about this client when it disconnects.
#               If False, the client is a durable client and subscription information
#               and queued messages will be retained when the client disconnects.
#               Note that a client will never discard its own outgoing messages on disconnect.
#               Calling connect() or reconnect() will cause the messages to be resent.
#               Use reinitialise() to reset a client to its original state.
#userdata: user defined data of any type that is passed as the userdata parameter to callbacks.
#          It may be updated at a later point with the user_data_set() function.
#protocol:  the version of the MQTT protocol to use for this client.
#           Can be either MQTTv31 or MQTTv311
#transport: set to "websockets" to send MQTT over WebSockets.
#           Leave at the default of "tcp" to use raw TCP.
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

#connect(host, port=1883, keepalive=60, bind_address="")
#host: the hostname or IP address of the remote broker
#port: the network port of the server host to connect to. MQTT Defaults to 1883.
#keepalive: maximum period in seconds allowed between communications with the broker.
#If no other messages are being exchanged, this controls the rate at which the client will send ping messages to the broker
#bind_address: the IP address of a local network interface to bind this client to, assuming multiple interfaces exist
client.connect("mqtt.eclipseprojects.io", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
#It automatically handles reconnecting.
client.loop_forever()
