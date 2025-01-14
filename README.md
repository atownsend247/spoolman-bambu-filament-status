<br/>

_Sync your BambuLab AMS spools directly with Spoolman._

## How is this different to spoolman
By design spoolman acceps push events from 3D printing software like [OctoPrint](https://octoprint.org/) and [Klipper](https://www.klipper3d.org/)/[Moonraker](https://moonraker.readthedocs.io/en/latest/). As the BambuLab ecosystem (Printers/Software) is relatively closed source that makes integrations with Spoolman not possible at this time.

Spoolman Bambu Filiment Status acts as a proxy service which subscribes to BambuLab printers via MQTT and then prepares/relays this information directly into Spoolman via its APIs, thus allows filiment spool tracking via BambuLab filiment and its Spool RFID tags.

## What is spoolman
Spoolman is a self-hosted web service designed to help you efficiently manage your 3D printer filament spools and monitor their usage. It acts as a centralized database that seamlessly integrates with popular 3D printing software like [OctoPrint](https://octoprint.org/) and [Klipper](https://www.klipper3d.org/)/[Moonraker](https://moonraker.readthedocs.io/en/latest/). When connected, it automatically updates spool weights as printing progresses, giving you real-time insights into filament usage.

Please see the [Spoolman](https://github.com/Donkie/Spoolman/tree/master) repository for more information.

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