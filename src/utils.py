import vcd.core as core
import requests
import datetime
import json
import math
import uuid
import os


def load_VCD_objects(file_path):
    """
    It's recommended.
    Loads the object from VCD JSON format files.
    Returns the objects.
    """
    try:
        myVCD = core.VCD()
        myVCD.load_from_file(file_path)
        return myVCD.get_objects()
    except FileNotFoundError as err:
        print(err)
        return None


def load_json_objects(file_path):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            return data
    except FileNotFoundError as err:
        print(err)
        return None


def check_longitude(object_longitude):
    """
    Checks if the GPS longitude exists.

    Returns:
    Boolean
    """

    if object_longitude["name"] == "longitude" and object_longitude["val"] is not None:
        return True
    else:
        raise TypeError("The longitude is not exist")


def check_latitude(object_latitude):
    """
    Checks if the GPS latitude exists.

    Returns:
    Boolean
    """
    if object_latitude["name"] == "latitude" and object_latitude["val"] is not None:
        return True
    else:
        raise TypeError("The latitude is not exist")


def check_confidence(object_confidence):
    """
    Checks if the confidence exists.


    Returns:
    Boolean
    """
    if (
        object_confidence["name"] == "confidence"
        and object_confidence["val"] is not None
    ):
        return True
    else:
        raise TypeError("The confidence is not exist")


def filter_confidence_by_threshold(object_confidence, confidence_threshold):
    if check_confidence(object_confidence) and object_confidence["val"] >= float(
        confidence_threshold
    ):
        return True
    else:
        return False


def check_color(object_color):
    """
    Checks If the Dominant_color is valid and If the value is in the Basic colors.
    object_color: {"name": "Dominant_color", val = "gray"}

    Returns Boolean
    """

    basic_colors = [
        "black",
        "white",
        "red",
        "green",
        "yellow",
        "blue",
        "brown",
        "orange",
        "pink",
        "purple",
        "grey",
        "gray",
    ]
    if object_color["name"] == "Dominant_color" and object_color["val"] in basic_colors:
        return True
    else:
        raise TypeError("The color doesn't exist")


def check_object_data(object_data, confidence_threshold=0.2):
    """
    Checks if the object is valid and follow the criteria.
    1) The color must be in the Basic colors
    2) The confidence must be bigger than the predefined threshold
    3) The bbox must not be empty

    Returns Boolean
    """
    try:
        object_text = object_data["text"]
        object_bbox = object_data["bbox"]
        object_num = object_data["num"]
        if (
            filter_confidence_by_threshold(object_num[0], confidence_threshold)
            and check_latitude(object_num[1])
            and check_longitude(object_num[2])
        ):
            return True
        else:
            return False
    except Exception as err:
        print("Check", err)
        return False


def get_weather_data(latitude, longitude, API_key):
    """
    Does a get request to Weather API using the GPS coordinates.

    Args:
        latitude : GPS latitude
        longitude : GPS longitude
        API_key : The key to have access to the API

    Returns:
        weather data in json format.
    """
    response = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={API_key}"
    )
    return response.json()


def isDay(latitude, longitude, API_key) -> bool:
    """
    Check if is day or night.
    If it's day, then returns true, if it's night, returns false.

    Args:
        latitude: GPS latitude
        longitude: GPS longitude
        API_key: The key to have access to the API

    Returns:
        Boolean
    """

    try:
        weather_data = get_weather_data(latitude, longitude, API_key)
        sunrise = int(weather_data["sys"]["sunrise"])
        sunset = int(weather_data["sys"]["sunset"])
        timestamp = datetime.timestamp(datetime.now())

        if timestamp >= sunrise and timestamp <= sunset:
            return True
        else:
            return False
    except KeyError:
        print("No data")
        return None


def load_config_parameters(config_path) -> dict | None:
    f = open(config_path)
    parameters = json.load(f)
    try:
        return parameters
    except KeyError as err:
        print(f"Can't load the parameters. {err} doesn't exist in config file.\033")
        return None


def calculate_GPS_distance(coordinates_1: tuple, coordinates_2: tuple):
    """
    Calculates the GPS distance
    """
    distance = math.dist(coordinates_1, coordinates_2)
    return distance


def generate_UUID():
    """
    Generates a random uuid using the library UUID and the uuid4() function
    More details, on python official documentation
    """
    object_uuid = str(uuid.uuid4())
    return object_uuid


def objects_into_consideration_by_GPS_coordinates(
    sensor1_objects, sensor2_objects, fusion_vcd, distance_threshold=0.0
):
    """
    Checks If the objects from different sensors (rgb camera) are the same.
    Firstly, calculates the distance from GPS coordinates. If the distance is smaller than the threshold,
    then the objects are the same.

    Returns: list of detected objects

    """

    fusion_objects = []

    for sensor_object1 in sensor1_objects:
        for sensor_object2 in sensor2_objects:
            if sensor_object1["type"] == sensor_object2["type"]:
                distance = calculate_GPS_distance(
                    (
                        sensor_object1["object_data"]["num"][1]["val"],  # latitude
                        sensor_object1["object_data"]["num"][2]["val"],  # longitude
                    ),
                    (
                        sensor_object2["object_data"]["num"][1]["val"],
                        sensor_object2["object_data"]["num"][2]["val"],
                    ),
                )
                if distance <= distance_threshold:
                    print("distance:", distance)
                    fusion_object = fusion_object_dominant(
                        sensor_object1,
                        sensor_object2,
                    )
                    fusion_objects.append(fusion_object)

    return fusion_objects


def fusion_object_dominant(sensor1_object, sensor2_object):
    try:
        fusion_object = {}
        # find the most dominant object
        confidence_cctv = sensor1_object["object_data"]["num"][0]["val"]
        confidence_lwir = sensor2_object["object_data"]["num"][0]["val"]
        fusion_object["type"] = sensor1_object["type"]

        if confidence_cctv >= confidence_lwir:
            fusion_object["object_data"] = sensor1_object["object_data"]  # has uuid
            fusion_object["object_data_pointers"] = sensor1_object[
                "object_data_pointers"
            ]
            fusion_object["sensor"] = "CCTV"
            fusion_object["uuid"] = sensor1_object["object_data"]["text"][0]["val"]

        else:
            fusion_object["object_data"] = sensor2_object["object_data"]
            fusion_object["object_data_pointers"] = sensor2_object[
                "object_data_pointers"
            ]
            fusion_object["sensor"] = "LWIR"
            fusion_object["uuid"] = sensor2_object["object_data"]["text"][0]["val"]

        fusion_object["uuid_CCTV"] = sensor1_object["object_data"]["text"][0]["val"]
        fusion_object["uuid_LWIR"] = sensor2_object["object_data"]["text"][0]["val"]

        return fusion_object
    except Exception as err:
        print("Error", err)

        return None


def fusion_objects_from_one_sensor(sensor_objects, sensor, fusion_stored_objects):
    fusion_objects = []
    for sensor_object in sensor_objects:
        sensor_object = fusion_object_format_one_sensor(
            sensor_object, sensor, fusion_stored_objects
        )
        fusion_objects.append(sensor_object)
    return fusion_objects


def fusion_object_format_one_sensor(sensor_object, sensor, fusion_stored_objects):
    fusion_object = {}
    if sensor == "CCTV":
        fusion_object["uuid_CCTV"] = sensor_object["object_data"]["text"][0]["val"]
        fusion_object["uuid_LWIR"] = ""
        fusion_object["sensor"] = sensor
    elif sensor == "LWIR_ZOOM":
        fusion_object["uuid_CCTV"] = ""
        fusion_object["uuid_LWIR"] = sensor_object["object_data"]["text"][0]["val"]
        fusion_object["sensor"] = sensor
    fusion_object["name"] = sensor_object["name"]
    fusion_object["type"] = sensor_object["type"]
    fusion_object["object_data"] = sensor_object["object_data"]
    fusion_object["object_data_pointers"] = sensor_object["object_data_pointers"]

    fusion_object["uuid"] = search_uuid(
        fusion_object["object_data"]["text"][0]["val"], fusion_stored_objects
    )
    return fusion_object


def search_uuid(uuid, fusion_objects):
    for fusion_object in fusion_objects:
        if uuid == fusion_object["uuid_CCTV"]:
            print("The object exists")
            return fusion_object["uuid"]
        elif uuid == fusion_object["uuid_LWIR"]:
            print("The object exists")
            return fusion_object["uuid"]
    return uuid


# def fusion_object_format(sensor1_object, sensor2_object, fusion_vcd):
#     try:
#         fusion_object = {}

#         confidence_cctv = sensor1_object["object_data"]["num"][0]["val"]
#         confidence_lwir = sensor2_object["object_data"]["num"][0]["val"]
#         fusion_object["confidence_cctv"] = confidence_cctv
#         fusion_object["confidence_lwir"] = confidence_lwir

#         cctv_uuid_previous = check_if_uuids_is_same(
#             fusion_vcd, sensor1_object["object_data"]["text"][0]["val"]
#         )
#         lwir_uuid_previous = check_if_uuids_is_same(
#             fusion_vcd, sensor2_object["object_data"]["text"][0]["val"]
#         )
#         fusion_object["tracking_uuid_CCTV"] = sensor1_object["object_data"]["text"][0][
#             "val"
#         ]
#         fusion_object["tracking_uuid_LWIR"] = sensor2_object["object_data"]["text"][0][
#             "val"
#         ]

#         if confidence_cctv >= confidence_lwir:
#             fusion_object["object_data"] = sensor1_object["object_data"]
#             fusion_object["object_data_pointers"] = sensor1_object[
#                 "object_data_pointers"
#             ]

#         else:
#             fusion_object["object_data"] = sensor2_object["object_data"]
#             fusion_object["object_data_pointers"] = sensor2_object[
#                 "object_data_pointers"
#             ]

#         if cctv_uuid_previous["isSameUUID"]:
#             fusion_object["uuid"] = cctv_uuid_previous["uuid"]
#         elif lwir_uuid_previous["isSameUUID"]:
#             fusion_object["uuid"] = lwir_uuid_previous["uuid"]
#         else:
#             ## dominant uuid
#             if confidence_cctv >= confidence_lwir:
#                 fusion_object["uuid"] = sensor1_object["object_data"]["text"][0][
#                     "val"
#                 ]  # uuid
#             else:
#                 fusion_object["uuid"] = sensor2_object["object_data"]["text"][0]["val"]
#             # fusion_object["uuid"] = generate_UUID()

#         fusion_object["type"] = sensor1_object["type"]

#         return fusion_object
#     except Exception as err:
#         print(err)
#         return None


def export_fusion_VCD(
    fusion_objects, fusion_type, streams, fusion_stored_objects, sensor, timestamp
):
    vcd = core.VCD()
    ## Add streams
    for stream in streams:
        print(stream)
        key = list(stream.keys())
        key = key[0]
        vcd.add_stream(
            stream_name=key,
            uri=stream[key]["uri"],
            description=stream[key]["description"],
            stream_type=stream[key]["type"],
        )

    if fusion_type == "fusion_all":
        vcd.add_name("tuc_fusion")
        i = 0
        for fusion_object in fusion_objects:
            name = f"""{fusion_object["type"]}{i}"""
            # uuid_cctv = core.types.text(
            #     "tracking_uuid_CCTV", fusion_object["tracking_uuid_CCTV"]
            # )
            # uuid_LWIR = core.types.text(
            #     "tracking_uuid_LWIR", fusion_object["tracking_uuid_LWIR"]
            # )

            # confidence_cctv = core.types.num(
            #     "confidence_cctv", fusion_object["confidence_cctv"]
            # )
            # confidence_lwir = core.types.num(
            #     "confidence_lwir", fusion_object["confidence_lwir"]
            # )
            # if fusion_object["confidence_cctv"] >= fusion_object["confidence_lwir"]:
            #     uuid = core.types.text("uuid", fusion_object["tracking_uuid_CCTV"])
            #     sensor = core.types.text("sensor", "CCTV")
            # else:
            #     uuid = core.types.text("uuid", fusion_object["tracking_uuid_LWIR"])
            #     sensor = core.types.text("sensor", "LWIR")
            sensor = core.types.text("sensor", fusion_object["sensor"])
            uuid = search_uuid(fusion_object["uuid"], fusion_stored_objects)
            uuid_vcd = core.types.text("uuid", uuid)
            print(uuid)
            object_id = vcd.add_object(
                name,
                semantic_type=fusion_object["type"],
                object_data=fusion_object["object_data"],
                object_data_pointers=fusion_object["object_data_pointers"],
            )
            vcd.add_object_data(object_id, uuid_vcd)
            # vcd.add_object_data(object_id, uuid_cctv)
            # vcd.add_object_data(object_id, uuid_LWIR)
            vcd.add_object_data(object_id, sensor)
            # vcd.add_object_data(object_id, confidence_cctv)
            # vcd.add_object_data(object_id, confidence_lwir)

            # vcd.add_object_data(object_id, fusion_object["object_data_pointers"])
            # vcd.add_object_data(object_id, fusion_object["object_data"])
            i += 1

    elif fusion_type == "fusion_one":
        vcd.add_name("tuc_fusion")
        for fusion_object in fusion_objects:
            object_id = vcd.add_object(
                name=fusion_object["name"],
                semantic_type=fusion_object["type"],
                object_data=fusion_object["object_data"],
                object_data_pointers=fusion_object["object_data_pointers"],
            )
            # uuid = search_uuid(
            #     fusion_object["object_data"]["text"][0]["val"], fusion_stored_objects
            # )
            uuid_vcd = core.types.text("uuid", fusion_object["uuid"])
            # print(fusion_object)
            sensor_vcd = core.types.text("sensor", fusion_object["sensor"])
            vcd.add_object_data(object_id, uuid_vcd)
            vcd.add_object_data(object_id, sensor_vcd)

    # timestamp = int(datetime.datetime.now().timestamp())
    metadata = {
        "timestamp": timestamp,
        "json_path": f"{os.getcwd()}/{timestamp}.json",
    }
    vcd.add_metadata_properties(metadata)

    return vcd.stringify()


def check_if_uuids_is_same(fusion_vcd, input_uuid):

    try:
        fusion_vcd = json.loads(fusion_vcd)
        fusion_objects = fusion_vcd["openlabel"]["objects"]
        for fusion_object_id, fusion_object in fusion_objects.items():
            uuids_fusion = fusion_object["object_data"]["text"]
            for uuid_fusion in uuids_fusion:
                if input_uuid == uuid_fusion["val"]:
                    return {"isSameUUID": True, "uuid": uuids_fusion[0]["val"]}

        return {"isSameUUID": False, "uuid": ""}
    except Exception as err:
        print(err)
        return {"isSameUUID": False, "uuid": ""}


def producer_message_format(message, fusion_vcd):
    try:
        producer_message = {}
        # producer_message["topic"] = message.topic
        # producer_message["partition"] = message.partition
        # producer_message["offset"] = message.offset
        # producer_message["timestamp"] = message.timestamp
        # producer_message["timestampType"] = "CREATE_TIME"
        # producer_message["headers"] = message.headers
        # producer_message["key"] = message.key

        producer_message["value"] = json.loads(fusion_vcd)

        return json.dumps(producer_message)
    except Exception as err:
        return {}


def save_producer_message(message):

    try:
        file_path = json.loads(message)["value"]["openlabel"]["metadata"]["json_path"]
        with open(file_path, "w") as file:
            file.write(message)
    except Exception as err:
        print(err)
        pass


def save(file_path, content):
    with open(file_path, "w") as file:
        json.dump(content, file)


def get_streams(streams):

    # vcd = core.VCD()
    # streams = vcd.get_streams(message)
    print(streams)
