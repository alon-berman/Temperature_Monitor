import paho.mqtt.client as mqtt
import logging
from time import sleep
import requests
import sys

class BusinessMonitor:
    def __init__(self, cloud_server, cloud_port, mqtt_username, mqtt_password, temperature_thresh, topic_out,
                 business_name="Test", log_level=0, debug_mode=False, temp_stabilization_thresh=1):
        self.cloud_server = cloud_server
        self.cloud_port = cloud_port
        self.mqtt_username = mqtt_username
        self.mqtt_password = mqtt_password
        self.business_name = business_name
        self.temperature_thresh = temperature_thresh  # min_temp, max_temp
        self.temp_stabilization_thresh = temp_stabilization_thresh
        self.prev_temp = 0
        self.log_level = log_level
        self.debug_mode = debug_mode
        self.mqtt_client = self.connect_mqtt()
        self.topic = topic_out
        self.init()
        self.listen()

    # Define event callbacks
    def on_connect(self, client, userdata, flags, rc):
        print("rc: " + str(rc))

    def on_message(self, client, obj, msg):
        curr_temp = float(msg.payload)
        print(curr_temp)
        if abs(curr_temp - self.prev_temp) > self.temp_stabilization_thresh:
            print('Waiting for temp to stabilize...')
            sys.stdout.flush()

        else:
            if self. temperature_thresh[0] <= curr_temp <= self.temperature_thresh[1]:
                print('business as usual')
                sys.stdout.flush()

            else:
                print('Temperature is not within the thresholds!')
        # print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        self.prev_temp = curr_temp
        print('message received')

    def on_publish(self, client, obj, mid):
        print("mid: " + str(mid))

    def on_subscribe(self, client, obj, mid, granted_qos):
        print("Subscribed: " + str(client) + str(mid) + " " + str(granted_qos))

    def on_log(self, string):
        print(string)

    def connect_mqtt(self):
        print('connecting MQTT server ...')
        mqttc = mqtt.Client()
        # Assign event callbacks
        mqttc.on_message = self.on_message
        mqttc.on_connect = self.on_connect
        mqttc.on_publish = self.on_publish
        mqttc.on_subscribe = self.on_subscribe

        if self.debug_mode:
            mqttc.on_log = self.on_log

        # Connect
        mqttc.username_pw_set(self.mqtt_username, self.mqtt_password)
        mqttc.connect(self.cloud_server, self.cloud_port)
        return mqttc

    def test_mqtt_connection(self):
        # Start subscribe, with QoS level 0
        self.mqtt_client.subscribe(self.topic, 0)

        # Publish a message
        self.mqtt_client.publish(self.topic, "Connection Test")

        # Continue the network loop, exit when an error occurs
        rc = 0
        while rc == 0:
            rc = self.mqtt_client.loop()
        print("rc: " + str(rc))

    def init(self):
        self.mqtt_client.subscribe(self.topic, )


    def listen(self):
        while True:
            self.mqtt_client.loop()
            sleep(3)

    def send_note(self):
        report = dict()
        report['measured_temp'] = self.prev_temp
        try:
            requests.post('https://maker.ifttt.com/trigger/notify/with/key/zjH2Qk3YYziQ_hSqCYnVl', data=report)
        except:
            logging.warning('could not send notification')


if __name__ == '__main__':
    monitor = BusinessMonitor("soldier.cloudmqtt.com", 17125, "lnacmzld", "ad9LXazYZ4Za", [-4, 50], "/temperature/out",
                              debug_mode=True)
    print('done')
