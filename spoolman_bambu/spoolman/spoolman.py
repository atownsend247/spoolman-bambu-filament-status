import requests
import logging
import datetime
import json

from spoolman_bambu import env, state

logger = logging.getLogger(__name__)


class Spoolman:
    def __init__(self, timeout=5):
        """
        Initializes the URLHealthChecker instance.

        :param timeout: Timeout in seconds for the request.
        """
        self.base_url = f"http://{env.get_spoolman_ip()}:{env.get_spoolman_port()}"
        self.timeout = timeout
        self.status = "disconnected"
        self.last_status_check = None
        self.external_bambu_spools = None
        self.vendor_id = None

        logger.info("Spoolman instance configured: %s %s", self.base_url, self.status)

    def initialise(self):
        logger.info("Spoolman pre-flight checks starting...")
        # TODO: This is buggy when you have a new instance of Spoolman and it hasn't fetched the external DB
        self.check_and_set_vendor()
        self.check_and_set_extra_field()
        self.get_external_filament()
        logger.info("Spoolman pre-flight checks completed")

    def get_status(self):
        return self.status

    def check_health(self):
        timestamp = datetime.datetime.now()
        """
        Performs a health check on the URL.

        :return: A dictionary containing the status code, response time, and status message.
        """
        url = f"{self.base_url}/api/v1/health"
        try:
            response = requests.get(url, timeout=self.timeout)
            response_time = response.elapsed.total_seconds()

            self.set_last_status_check(timestamp)
            if response.status_code == 200:

                status_message = "Healthy"
                self.status = "connected"
                logger.info("Spoolman instance health: %s %s", url, self.status)
            else:
                status_message = f"Unhealthy (Status Code: {response.status_code})"
                logger.error(
                    "Spoolman instance health: %s %s",
                    url,
                    self.status,
                )

        except requests.exceptions.RequestException as e:
            return {"status_code": None, "response_time": None, "status_message": f"Error: {str(e)}"}

    def get_vendors(self):
        url = f"{self.base_url}/api/v1/vendor"
        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error("Spoolman vendors: %s %s", url, response.status_code)

        except requests.exceptions.RequestException as e:
            return {"status_code": None, "status_message": f"Error: {str(e)}"}

    def get_fields(self, entity_type):
        url = f"{self.base_url}/api/v1/field/{entity_type}"
        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error("Spoolman field %s: %s %s", entity_type, url, response.status_code)

        except requests.exceptions.RequestException as e:
            return {"status_code": None, "status_message": f"Error: {str(e)}"}

    def get_spools(self):
        url = f"{self.base_url}/api/v1/spool"
        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error("Spoolman spools: %s %s", url, response.status_code)

        except requests.exceptions.RequestException as e:
            return {"status_code": None, "status_message": f"Error: {str(e)}"}

    def patch_spool(self, spool_id, spool_data):
        url = f"{self.base_url}/api/v1/spool/{spool_id}"
        # logger.info("Patch spool %s: %s", spool_id, json.dumps(spool_data))
        try:
            response = requests.patch(url, json=spool_data, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error("Spoolman spools: %s %s %s", url, response.status_code, response.json())
                return None

        except requests.exceptions.RequestException as e:
            return {"status_code": None, "status_message": f"Error: {str(e)}"}

    def create_spool(self, spool_data):
        url = f"{self.base_url}/api/v1/spool"
        logger.info("Create spool %s", json.dumps(spool_data))
        try:
            response = requests.post(url, json=spool_data, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error("Spoolman create spool: %s %s %s", url, response.status_code, response.json())
                return None

        except requests.exceptions.RequestException as e:
            return {"status_code": None, "status_message": f"Error: {str(e)}"}

    def get_internal_filament(self):
        url = f"{self.base_url}/api/v1/filament"
        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                logger.info("Spoolman filaments: %s %s", url, response.status_code)
                return response.json()
            else:
                logger.error("Spoolman filaments: %s %s", url, response.status_code)

        except requests.exceptions.RequestException as e:
            return {"status_code": None, "status_message": f"Error: {str(e)}"}

    def create_internal_filament(self, filament_data):
        url = f"{self.base_url}/api/v1/filament"
        logger.info(f"Spoolman Creating Spoolman internal filament...")

        try:
            response = requests.post(url, json=filament_data, timeout=self.timeout)

            if response.status_code == 200:
                logger.info("Spoolman create internal filament: %s %s", url, response.status_code)
                logger.info(f"Spoolman create internal filament: {response.json()}")
                return response.json()
            else:
                logger.error("Spoolman create internal filament: %s %s %s", url, response.status_code, response.json())

        except requests.exceptions.RequestException as e:
            return {"status_code": None, "status_message": f"Error: {str(e)}"}

    def get_external_filament(self):
        url = f"{self.base_url}/api/v1/external/filament"
        # If this is not cached go and fetch it
        if self.external_bambu_spools is None:
            try:
                response = requests.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    logger.info("Spoolman external filaments: %s %s", url, response.status_code)
                    self.external_bambu_spools = cache_external_filaments(response.json())

                    return self.external_bambu_spools
                else:
                    logger.error("Spoolman external filaments: %s %s", url, response.status_code)

            except requests.exceptions.RequestException as e:
                return {"status_code": None, "status_message": f"Error: {str(e)}"}
        # Otherwise just return the pre-filtered cache
        else:
            return self.external_bambu_spools

    def check_and_set_extra_field(self):
        spoolmanCustomTag = env.get_spoolman_tag()
        logger.info(f"Spoolman Check Spoolman extra field tag[{spoolmanCustomTag}] is present...")

        fields = self.get_fields("spool")

        found = False
        for field in fields:
            if field["name"] == spoolmanCustomTag:
                found = True

        if found != True:
            logger.info(f"Spoolman extra field tag[{spoolmanCustomTag}] not found creating...")
            self.create_extra_field()
        else:
            logger.info(f"Spoolman extra field tag[{spoolmanCustomTag}] is found continue")

    def create_extra_field(self):
        spoolmanCustomTag = env.get_spoolman_tag()
        url = f"{self.base_url}/api/v1/field/spool/tag"
        logger.info(f"Spoolman Creating Spoolman extra field tag[{spoolmanCustomTag}] ...")

        try:
            response = requests.post(url, json={"name": spoolmanCustomTag, "field_type": "text"}, timeout=self.timeout)

            if response.status_code == 200:
                logger.info("Spoolman extra tag: %s %s", url, response.status_code)
                logger.info(f"Spoolman extra field tag: {spoolmanCustomTag} successfully created")
                return response.json()
            else:
                logger.error("Spoolman extra tag: %s %s %s", url, response.status_code, response.json())

        except requests.exceptions.RequestException as e:
            return {"status_code": None, "status_message": f"Error: {str(e)}"}

    def check_and_set_vendor(self):
        logger.info("Spoolman Check Bambu Lab vendor is present...")
        vendors = self.get_vendors()

        found = False
        for vendor in vendors:
            if vendor["name"] == "Bambu Lab":
                self.vendor_id = vendor["id"]
                found = True

        if found != True:
            logger.info("Spoolman Bambu Lab vendor not found creating...")
            self.vendor_id = self.create_vendor()["id"]

    def get_vendor_id(self):
        return self.vendor_id

    def create_vendor(self):
        url = f"{self.base_url}/api/v1/vendor"
        try:
            response = requests.post(
                url,
                json={"name": "Bambu Lab", "external_id": "Bambu Lab", "empty_spool_weight": 250},
                timeout=self.timeout,
            )

            if response.status_code == 200:
                logger.info("Spoolman create vendor: %s %s", url, response.status_code)
                return response.json()
            else:
                logger.error("Spoolman external filaments: %s %s %s", url, response.status_code)

        except requests.exceptions.RequestException as e:
            return {"status_code": None, "status_message": f"Error: {str(e)}"}

    def get_last_status_check(self):
        return self.last_status_check

    def set_last_status_check(self, timestamp):
        self.last_status_check = timestamp


def cache_external_filaments(filaments, prefix="bambulab_"):
    bambu_filaments = []
    for filament in filaments:
        if filament["id"].startswith(prefix):
            bambu_filaments.append(filament)

    logger.info("Spoolman external cached filaments count: %s", len(bambu_filaments))
    return bambu_filaments
