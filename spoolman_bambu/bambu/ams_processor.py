import logging
import datetime
import json

from spoolman_bambu import env, state
from spoolman_bambu.exceptions import ItemCreateError, ItemUpdateError

logger = logging.getLogger(__name__)

# DEFAULT_UPDATE_INTERVAL = 3600

processing_prefix = " - "
processing_empty_prefix = "   "

app_state = state.get_current_state()

spoolman_custom_tag = env.get_spoolman_tag()
spoolman_custom_tag_api = spoolman_custom_tag.lower()


def tray_validator(tray) -> bool:
    # Check if we have a valid tray with more than 1 key being id
    if len(tray.keys()) == 1 and "id" in tray:
        logger.info(f"{processing_empty_prefix}  - Tray is empty skipping...")
        return False

    # If or
    # - remaining filament is less than 0
    # - tray_uuid invalid (all 0's)
    # - tray_colour invalid (all 0's)
    if (
        tray["remain"] <= 0
        or tray["tray_uuid"] == "00000000000000000000000000000000"
        or tray["tray_color"] == "00000000"
    ):
        logger.info(f"{processing_empty_prefix}  - Tray is invalid or empty skipping...")
        return False

    return True


def process_ams(printer_id, last_ams_data, ams_data, time):
    amsId = env.convert_id_to_char(ams_data["id"])
    spoolman_instance = app_state.get_spoolman()

    # logger.info(f"Processing AMS Spool {last_ams_data}")
    logger.info(f"Processing AMS Spool {amsId not in last_ams_data.keys()}")
    logger.info(f"Processing AMS Spool {amsId in last_ams_data.keys()}")
    if amsId in last_ams_data.keys():
        logger.info(f"Processing AMS Spool {last_ams_data[amsId] != ams_data}")

    # if last ams data not cached yet or the cached data has changed since last checked process
    if amsId not in last_ams_data.keys() or (amsId in last_ams_data.keys() and last_ams_data[amsId] != ams_data):
        spoolman_spools = spoolman_instance.get_spools()
        spoolman_internal_filaments = spoolman_instance.get_internal_filament()
        spoolamn_external_filaments = spoolman_instance.get_external_filament()

        logger.info(f"Processing AMS")
        logger.info(f" {printer_id} AMS: [{amsId}] (Temp: {ams_data['temp']}'C Hum: {ams_data['humidity']}%)")

        # TODO: Check if the data has changed since the last check?
        logger.info(f" Tray data {ams_data['tray']}")

        for tray in ams_data["tray"]:
            trayId = tray["id"]
            logger.info(f"{processing_prefix} AMS Spool for {printer_id} AMS Tray: [{amsId}{trayId}]")

            # Sanity check tray data and ignore any basically empty spools
            if tray_validator(tray):

                # Adjust PETG Translucent color stats, so its accessable in Spoolman
                if tray["tray_sub_brands"] == "PETG Translucent" and tray["tray_color"] == "00000000":
                    tray["tray_color"] = "FFFFFF00"

                logger.info(
                    f"{processing_empty_prefix}  {amsId}{trayId} {tray['tray_sub_brands']} {tray['tray_color']} ({tray['remain']}%) [[{tray['tray_uuid']}]]..."
                )

                # Check if this spool exists in external spoolman
                external_filament_match = check_spool_matches_external(spoolamn_external_filaments, tray)
                # Check if this spool already exists in spoolman
                internal_filament_matches = check_spool_matches_internal(
                    spoolman_internal_filaments, external_filament_match, tray
                )

                active_spool_found = False
                unclaimed_spool_found = None
                unclaimed_spool_found_index = None
                claimed_spool_found = None
                claimed_spool_found_index = None
                # Iterate over the active spools in spoolman and look for matches with the info above
                for spool_index, spool in enumerate(spoolman_spools):
                    # See if we matched anything
                    # TODO: sanity check should always be 1 match?
                    if len(internal_filament_matches) > 0:
                        # Check if the matched filament matches the current spool
                        if internal_filament_matches[0]["external_id"] == spool["filament"]["external_id"]:
                            # Check if the tag[TAG] extra data is either empty/unclaimed or it is set and it matches the
                            # currently being processed AMS tray
                            # If matching spool has been found but no tag key set claim it
                            if spoolman_custom_tag_api not in spool["extra"].keys():
                                logger.info(
                                    f"{processing_empty_prefix}  - Checking tags IF unclaimed: {spool['extra']}"
                                )
                                # spoolman_spools[spool_index] = update_existing_spool(spool, tray, time)
                                unclaimed_spool_found_index = spool_index
                                unclaimed_spool_found = spool
                                active_spool_found = True
                            elif (
                                spoolman_custom_tag_api in spool["extra"].keys()
                                and spool["extra"][spoolman_custom_tag_api] == '""'
                            ):
                                logger.info(
                                    f"{processing_empty_prefix}  - Checking tags ELIF unclaimed: {spool['extra']}"
                                )
                                # spoolman_spools[spool_index] = update_existing_spool(spool, tray, time)
                                unclaimed_spool_found_index = spool_index
                                unclaimed_spool_found = spool
                                active_spool_found = True
                            # if matching spool has tag set
                            elif (
                                spoolman_custom_tag_api in spool["extra"].keys()
                                and spool["extra"][spoolman_custom_tag_api] == f"\"{tray['tray_uuid']}\""
                            ):
                                logger.info(
                                    f"{processing_empty_prefix}  - Checking tags ELIF claimed: {spool['extra']}"
                                )
                                # spoolman_spools[spool_index] = update_existing_spool(spool, tray, time)
                                claimed_spool_found_index = spool_index
                                claimed_spool_found = spool
                                active_spool_found = True
                            else:
                                logger.info(f"{processing_empty_prefix}  - Checking tags ELSE: {spool['extra']}")

                # This is not currently in spoolman
                if not active_spool_found:
                    if len(internal_filament_matches) == 0:
                        logger.info(f"{processing_empty_prefix}  - Create internal filament and spool...")
                        new_spool = create_new_filament_and_spool(external_filament_match, tray, printer_id, time)
                    else:
                        logger.info(f"{processing_empty_prefix}  - Create spool...")
                        new_spool = create_new_spool(internal_filament_matches[0], tray, printer_id, time)
                    # Append new spool to the list, not that it should matter as will be re-fetched in next iteration
                    spoolman_spools.append(new_spool)
                # At least one match has been found
                else:
                    # Check and update the claimed spool first
                    if claimed_spool_found is not None:
                        logger.info(f"{processing_empty_prefix}  - Update existing claimed spool...")
                        spoolman_spools[claimed_spool_found_index] = update_existing_spool(
                            claimed_spool_found, tray, printer_id, time
                        )
                    # use an unclaimed spool
                    elif claimed_spool_found is None and unclaimed_spool_found is not None:
                        logger.info(f"{processing_empty_prefix}  - Claim unclaimed spool...")
                        spoolman_spools[unclaimed_spool_found_index] = update_existing_spool(
                            unclaimed_spool_found, tray, printer_id, time
                        )

            logger.info(f"{processing_empty_prefix}  Processed AMS Spool for {printer_id} AMS: {amsId}{trayId}")
            logger.info("")
            logger.info("")
        last_ams_data[amsId] = ams_data

    # otherwise skip processing as it is the same
    else:
        logger.info(f"Processing AMS {printer_id} AMS: [{amsId}] skipped as data has not changed")


def create_new_filament_and_spool(filament, tray, printer_id, current_time):
    spoolman_instance = app_state.get_spoolman()
    internal_filament_id = None

    new_filament_data = {
        "name": filament["name"],
        "material": tray["tray_sub_brands"],
        "density": filament["density"],
        "diameter": filament["diameter"],
        "spool_weight": 250,
        "weight": 1000,
        "settings_extruder_temp": filament["extruder_temp"],
        "settings_bed_temp": filament["bed_temp"],
        "color_hex": filament["color_hex"],
        "external_id": filament["id"],
        "spool_type": filament["spool_type"],
        "color_hexes": filament["color_hexes"],
        "finish": filament["finish"],
        "multi_color_direction": filament["multi_color_direction"],
        "pattern": filament["pattern"],
        "translucent": filament["translucent"],
        "glow": filament["glow"],
        "vendor_id": app_state.get_spoolman().get_vendor_id(),
    }

    # logger.info(f"New Filament data: {json.dumps(new_filament_data)}")
    filament = spoolman_instance.create_internal_filament(new_filament_data)

    if filament is not None:
        logger.info(f"{processing_empty_prefix}  - New Filament created successfully: {filament['id']}")
        return create_new_spool(filament, tray, printer_id, current_time)
    else:
        raise ItemCreateError("Item failed to be created")


def create_new_spool(filament, tray, printer_id, current_time):
    spoolman_instance = app_state.get_spoolman()

    new_spool_data = {
        "filament_id": filament["id"],
        "initial_weight": calculate_spool_remaining_weight(tray["tray_weight"], tray["remain"]),
        "first_used": current_time.isoformat(),
        "location": printer_id,
        "extra": {f"{spoolman_custom_tag_api}": f"\"{tray['tray_uuid']}\""},
    }

    spool = spoolman_instance.create_spool(new_spool_data)

    if spool is not None:
        logger.info(f"{processing_empty_prefix}  - New Spool created successfully: {spool['id']}")
        return spool
    else:
        raise ItemCreateError("Item failed to be created")


def update_existing_spool(spool, tray, printer_id, current_time):
    spoolman_instance = app_state.get_spoolman()
    remaining_weight = calculate_spool_remaining_weight(tray["tray_weight"], tray["remain"])

    # Sanity check if anything has actually changed otherwise no point patching
    if spool["remaining_weight"] != remaining_weight:
        logger.info(
            f"{processing_empty_prefix}  - Patch spool {spool['id']} weight:{remaining_weight}, {spoolman_custom_tag}:{tray['tray_uuid']}, last:{current_time}"
        )
        spool_patch_data = {
            "remaining_weight": remaining_weight,
            "last_used": current_time.isoformat(),
            "location": printer_id,
            "extra": {f"{spoolman_custom_tag_api}": f"\"{tray['tray_uuid']}\""},
        }

        # If claiming a spool and first_used isn't set update it
        if "first_used" not in spool.keys() or spool["first_used"] is None or spool["first_used"] == "":
            spool_patch_data["first_used"] = current_time.isoformat()

        # Patch the current spool with the updated values and update it in the internal array
        # Note extra field spoolman_custom_tag, for success request needs to be lower case
        updated_spool = spoolman_instance.patch_spool(spool["id"], spool_patch_data)
        if updated_spool is not None:
            return updated_spool
        else:
            raise ItemUpdateError("Item failed to be updated")
    else:
        # Ignore the update and just return the spool as is
        logger.info("Weight has not changed skipping update")
        return spool


def check_spool_matches_internal(internal_filaments, external_filament_match, tray):
    bambu_internal_spools = []

    for filament in internal_filaments:
        # logger.info(f"Check internal filament: {filament}")
        # logger.info(f"Check internal filament: {external_filament_match}")
        # Check if it matches the same filament that we are looking for
        if filament["external_id"] == external_filament_match["id"]:
            # TODO: Further checks to ensure it has the same tray_uuid or tray_uuid is not set
            bambu_internal_spools.append(filament)

    logger.info(f"{processing_empty_prefix}  - Found {len(bambu_internal_spools)} matching internal spools...")
    # logger.info(f"Found {bambu_internal_spools}")
    return bambu_internal_spools


def check_spool_matches_external(external_filaments, tray):
    mutation_checks = [
        f"bambulab_{tray['tray_sub_brands'].lower()}",
        f"bambulab_{tray['tray_sub_brands'].lower().replace(' ', '_')}",
        f"bambulab_{(tray['tray_sub_brands'].lower().split(' ')[0]).replace(' ', '_')}",
    ]
    for id_check in mutation_checks:
        for filament in external_filaments:
            if filament["id"].startswith(id_check):

                # Check if using single colour or multi
                if filament["color_hex"] is not None:
                    if filament["color_hex"].lower() == tray["tray_color"][:6].lower():
                        # logger.info(f"Found {filament}")
                        return filament


def calculate_spool_remaining_weight(tray_weight, remaining):
    return (remaining / 100) * float(tray_weight)
