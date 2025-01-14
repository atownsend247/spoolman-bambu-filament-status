import logging
import random
import datetime
import json
import ssl
import time

from paho.mqtt import client as mqtt_client

from spoolman_bambu import env
from . import ams_processor

logger = logging.getLogger(__name__)


class Bambu:
    def __init__(self, printer_id, printer_ip, printer_code):
        # TODO: Make private vars private
        self.printer_id = printer_id
        self.printer_ip = printer_ip
        self.printer_code = printer_code
        self.status = "disconnected"
        self.client_id = f"python-spoolman-bambu-{self.printer_id}"
        self.last_mqtt_message = None
        self.last_mqtt_ams_message = None
        self.ams_unit_count = None
        self.ams_active_spools_count = None
        self.last_ams_data = {}

        logger.info(
            "Bambu printer instance %s:%s configured: %s::%s",
            self.printer_id,
            self.printer_ip,
            self.client_id,
            self.status,
        )

        self.client = self.createClient()
        # Enable callback functions
        self.client.on_log = self.on_log
        self.client.on_connect = self.on_connect
        self.client.on_connect_fail = self.on_connect_fail
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        # Start the connection
        logger.info(
            "Bambu printer instance %s:%s conecting...",
            self.printer_id,
            self.printer_ip,
        )
        try:
            # Ensure async connection in background thread
            self.client.connect_async(self.printer_ip, 8883, 60)
            # Start listening without blocking
            conn = self.client.loop_start()
            logger.info(
                f"Bambu printer instance %s:%s loop start... {conn}",
                self.printer_id,
                self.printer_ip,
            )

            # TODO: Improve this
            # Wait suitable amount of time for connection?
            time.sleep(5)
            if not self.client.is_connected():
                logger.info(
                    f"Bambu printer instance %s:%s failed to connect.",
                    self.printer_id,
                    self.printer_ip,
                )
        except:
            logger.info(
                f"Bambu printer instance %s:%s failed... ",
                self.printer_id,
                self.printer_ip,
            )
            raise

    def createClient(self):
        client = mqtt_client.Client(client_id=self.client_id, clean_session=True)
        client.check_hostname = False

        # set username and password
        # Username isn't something you can change, so hardcoded here
        client.username_pw_set("bblp", self.printer_code)

        # These 2 lines are required to bypass self signed certificate errors, at least on my machine
        # these things can be finicky depending on your system setup
        client.tls_set(tls_version=ssl.PROTOCOL_TLS, cert_reqs=ssl.CERT_NONE)
        client.tls_insecure_set(True)

        return client

    def on_log(client, userdata, level, buff):
        logger.info(
            "Bambu printer instance %s:%s on_log broker %s",
            self.printer_id,
            self.printer_ip,
            buff,
        )

    def on_connect(self, client, userdata, flags, rc):
        logger.info(
            "Bambu printer instance %s:%s on_connect broker %s",
            self.printer_id,
            self.printer_ip,
            rc,
        )
        if rc == 0:
            logger.info(
                "Bambu printer instance %s:%s conected to broker",
                self.printer_id,
                self.printer_ip,
            )
            self.status = "connected"
            # Bambu requires you to subscribe promptly after connecting or it forces a discconnect
            self.client.subscribe(f"device/{self.printer_id}/report")
        else:
            logger.info(
                "Bambu printer instance %s:%s connection to broker failed",
                self.printer_id,
                self.printer_ip,
            )

    def on_connect_fail(self, userdata):
        self.status = "disconnected"
        logger.info(
            "Bambu printer instance %s:%s on_connect_fail broker failed",
            self.printer_id,
            self.printer_ip,
        )

    def on_message(self, client, userdata, msg):
        current_time = datetime.datetime.now()
        doc = json.loads(msg.payload)
        self.set_last_mqtt_message(current_time)
        # logger.info(f"{self.printer_id}: {doc}")

        # Validate we have the correct message
        if "print" in doc and "ams" in doc["print"] and "ams" in doc["print"]["ams"]:
            self.set_last_mqtt_ams_message(current_time)

            # Note is double nested for some reason
            amsUpdate = doc["print"]["ams"]["ams"]

            # Set the currently connected AMS units
            self.ams_unit_count = len(amsUpdate)

            # For each AMS unit process these individually
            for ams_unit in amsUpdate:
                ams_unit_id = env.convert_id_to_char(ams_unit["id"])
                # Initialise the internal comparison
                if ams_unit_id not in self.last_ams_data.keys():
                    self.last_ams_data[ams_unit_id] = {}

                # Send for further processing per AMS unit
                ams_processor.process_ams(self.printer_id, self.last_ams_data[ams_unit_id], ams_unit, current_time)

                self.last_ams_data[ams_unit_id] = ams_unit

    def on_disconnect(self, client, userdata, rc):
        logger.info(f"Bambu printer instance disconnected from MQTT Broker {self.printer_id} {rc}")
        self.status = "disconnected"

    def get_printer_id(self):
        return self.printer_id

    def get_printer_ip(self):
        return self.printer_ip

    def get_status(self):
        return self.status

    def get_last_mqtt_message(self):
        return self.last_mqtt_message

    def set_last_mqtt_message(self, current_time):
        self.last_mqtt_message = current_time

    def get_last_mqtt_ams_message(self):
        return self.last_mqtt_ams_message

    def set_last_mqtt_ams_message(self, current_time):
        self.last_mqtt_ams_message = current_time

    def get_ams_unit_count(self):
        return self.ams_unit_count

    def get_ams_active_spools_count(self):
        return self.get_ams_active_spools_count

    def disconnect(self):
        self.client.disconnect()
