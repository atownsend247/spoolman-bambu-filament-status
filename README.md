<br/>

_Sync your BambuLab AMS spools directly with Spoolman._

## How is this different to spoolman
By design spoolman acceps push events from 3D printing software like [OctoPrint](https://octoprint.org/) and [Klipper](https://www.klipper3d.org/)/[Moonraker](https://moonraker.readthedocs.io/en/latest/). As the BambuLab ecosystem (Printers/Software) is relatively closed source that makes integrations with Spoolman not possible at this time.

Spoolman Bambu Filiment Status acts as a proxy service which subscribes to BambuLab printers via MQTT and then prepares/relays this information directly into Spoolman via its APIs, thus allows filiment spool tracking via BambuLab filiment and its Spool RFID tags.

## What is spoolman
Spoolman is a self-hosted web service designed to help you efficiently manage your 3D printer filament spools and monitor their usage. It acts as a centralized database that seamlessly integrates with popular 3D printing software like [OctoPrint](https://octoprint.org/) and [Klipper](https://www.klipper3d.org/)/[Moonraker](https://moonraker.readthedocs.io/en/latest/). When connected, it automatically updates spool weights as printing progresses, giving you real-time insights into filament usage.

Please see the [Spoolman](https://github.com/Donkie/Spoolman/tree/master) repository for more information.

## Getting started with spoolman-bambu-filament-status

By default this project provides some docker images that can be used on their own or with the included handy `docker-compose.yaml` file.

### Using docker-compose / docker
To get started the easiest way is to run or use the `docker-compose.yaml` file in this repo, if you already have a Spoolman instance running you can use the docker-compose.yaml as influence or disable the spoolman container in the compose file.

Ensure you make a copy of the `.env.example` file (Call it `.env` so its picked up and mounted by the `docker-compose.yaml` file and change it to suit your requirements at a minimum the `SPOOLMAN_BAMBU_SPOOLMAN_HOST` and `SPOOLMAN_BAMBU_SPOOLMAN_PORT` should be set or the container will fail to start.

### Configuring printers
To configure a printer you need three bits of information which can be found easily on the printers front mounted display, these are; The local IP address of the printer, the printers serial number and the pairing pass code. More information for this can be found in the .env.example but the tl;dr; is the 3 properties prefixed with the printer id e.g. `SPOOLMAN_BAMBU_PRINTER_1` where 1 can be changed for any number of printers a full example can be found below.

```bash
# Printer 1
SPOOLMAN_BAMBU_PRINTER_1_ID=01PXXAXXXXXXXXXXX
SPOOLMAN_BAMBU_PRINTER_1_IP=192.168.1.4
SPOOLMAN_BAMBU_PRINTER_1_CODE=YYYYYYYY
```

Once your `.env` is configured you can start the service and it should initiate the connection to spoolman and do some checks before connecting to the printers and you should see something similar in the logs as below:

```
User UID: 1000
User GID: 1000
Starting uvicorn...
spoolman_bambu.main        WARNING  Running in debug mode, allowing all origins.
uvicorn.error              INFO     Started server process [1]
uvicorn.error              INFO     Started server process [1]
uvicorn.error              INFO     Waiting for application startup.
uvicorn.error              INFO     Waiting for application startup.
spoolman_bambu.main        INFO     Starting Spoolman Plugin Bambu Filiment Status v0.1.0
spoolman_bambu.main        INFO     Configuration:
spoolman_bambu.main        INFO     Using data directory: /home/app/.local/share/spoolman_bambu
spoolman_bambu.main        INFO     Using logs directory: /home/app/.local/share/spoolman_bambu
spoolman_bambu.main        INFO     Using backups directory: /home/app/.local/share/spoolman_bambu/backups
spoolman_bambu.main        INFO
spoolman_bambu.spoolman.spoolman INFO     Spoolman instance configured: http://192.168.68.1:7912 disconnected
spoolman_bambu.spoolman.spoolman INFO     Spoolman instance health: http://192.168.68.1:7912/api/v1/health connected
spoolman_bambu.spoolman.spoolman INFO     Spoolman pre-flight checks starting...
spoolman_bambu.spoolman.spoolman INFO     Spoolman Check Bambu Lab vendor is present...
spoolman_bambu.spoolman.spoolman INFO     Spoolman Check Spoolman extra field tag[Tag] is present...
spoolman_bambu.spoolman.spoolman INFO     Spoolman extra field tag[Tag] is found continue
spoolman_bambu.spoolman.spoolman INFO     Spoolman external filaments: http://192.168.68.1:7912/api/v1/external/filament 200
spoolman_bambu.spoolman.spoolman INFO     Spoolman external cached filaments count: 226
spoolman_bambu.spoolman.spoolman INFO     Spoolman pre-flight checks completed
spoolman_bambu.main        INFO     Found 2 printers in env configuration, initilising them now...
spoolman_bambu.bambu.bambu INFO     Bambu printer instance 01PXXAXXXXXXXXXXX:192.168.68.2 configured: python-spoolman-bambu-01PXXAXXXXXXXXXXX::disconnected
spoolman_bambu.bambu.bambu INFO     Bambu printer instance 01PXXAXXXXXXXXXXX:192.168.68.2 conecting...
spoolman_bambu.bambu.bambu INFO     Bambu printer instance 01PXXAXXXXXXXXXXX:192.168.68.2 loop start... 0
spoolman_bambu.bambu.bambu INFO     Bambu printer instance 01PXXAXXXXXXXXXXX:192.168.68.2 failed to connect.
spoolman_bambu.bambu.bambu INFO     Bambu printer instance 01PYYAYYYYYYYYYYY:192.168.68.3 configured: python-spoolman-bambu-01PYYAYYYYYYYYYYY::disconnected
spoolman_bambu.bambu.bambu INFO     Bambu printer instance 01PYYAYYYYYYYYYYY:192.168.68.3 conecting...
spoolman_bambu.bambu.bambu INFO     Bambu printer instance 01PYYAYYYYYYYYYYY:192.168.68.3 loop start... 0
spoolman_bambu.bambu.bambu INFO     Bambu printer instance 01PYYAYYYYYYYYYYY:192.168.68.3 on_connect broker 0
spoolman_bambu.bambu.bambu INFO     Bambu printer instance 01PYYAYYYYYYYYYYY:192.168.68.3 conected to broker
spoolman_bambu.main        INFO     2 printers initilised
spoolman_bambu.task_scheduler INFO     Task: Scheduling Spoolman health check every 600 seconds.
spoolman_bambu.main        INFO     Startup complete.
uvicorn.error              INFO     Application startup complete.
uvicorn.error              INFO     Application startup complete.

```

### Features
* **Filament Management**: Keeps synced with your BambuLab AMS units so you can track filament spool useage in Spoolman
* **Multi-AMS Support**: Will handle the full set of 4 AMS units (Maximum supported) per printer connection
* **Multi-Printer Support**: Supports any amount of BambuLab PS1/X1/X1 Carbon printers (Up to hardware limitations)

### Known Issues / TODOs
* **Static IPs**: This works best when you have configured the BambuLab printer to have a static IP on the local network, please refer to your routers documentation on how to do this, otherwise you will have to update your config everytime your printer gets allocated a new IP address via DHCP.
* **AMS Support**: Only tested with P1S/X1/X1 Carbon printers with AMS units, unsure if AMS Lite units work in the same way
* **Multi-colour filament**: Currently only handles single solid colour spools.
* **Filament types**: Further testing against -CF variants required
* **API Docs**: Fix API doc generation
* **Unit Test**: The unit tests and integration test coverage can definately be improved.
* **Printer Alias**: Currently Printers are identified as their serial, should be updated to be a custom alias field
* **Bambu MQTT**: Look at loop backoff intervals for failed connections
* **Spoolman API**: Automated retries for failed API requests, better error/response handling

### Awknowledgements
* **: Heavily influenced by the [Spoolman](https://github.com/Donkie/Spoolman/tree/master) project (buy him a coffee!), written in the same language/structure as Spoolman and adding in multiple BambuLab printer support to the service via the printers internal MQTT server.
* **: Also referenced was the [bambulab-ams-spoolman-filamentstatus](https://github.com/Rdiger-36/bambulab-ams-spoolman-filamentstatus) project written in NodeJS.
* **: I am in no way associated to either the Spoolman project nor BambuLab

**Web client preview:**
TODO: add screenshots
