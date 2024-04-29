from kafka import KafkaConsumer
from kafka import KafkaProducer
import threading
from threading import Thread
from threading import Event
import json
import tuc_fusion
import camera_sensor
import utils
import vcd.core as core


from_topic = "VCD-detection-raw"
to_topic = "VCD-detection-raw"
# boostrap_servers = "10.52.16.65:9199"
boostrap_servers = "localhost:9199"
# from_topic = "benmalef"
# to_topic = "asd"

consumer = KafkaConsumer(
    bootstrap_servers=boostrap_servers,
    auto_offset_reset="latest",
    value_deserializer=lambda m: json.loads(m),
)
producer = KafkaProducer(bootstrap_servers=boostrap_servers)
consumer.subscribe([from_topic])


time_window = 1


stopFlag = Event()


class MyThread(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def run(self):
        while not self.stopped.wait(time_window):
            send_status()


thread = MyThread(stopFlag)

thread.start()


def send_status():
    # global json_object
    global producer
    global consumer
    global to_topic
    global cctv_valid_objects
    global lwir_valid_objects
    global fusion_decision
    global message
    global streams
    global fusion_objects
    global count
    global flag_send
    global timestamp_vcd

    fusion_timestamp = 0
    # global device_measurements
    # try:
    sensor = ""
    
    if (len(cctv_valid_objects) == 0 and len(lwir_valid_objects)) > 0:
            sensor = "LWIR_ZOOM"
            final_objects = utils.fusion_objects_from_one_sensor(
                lwir_valid_objects, sensor, fusion_objects
            )
            fusion_type = "fusion_one"
    elif (len(lwir_valid_objects) == 0 and len(cctv_valid_objects)) > 0:
            sensor = "CCTV"
            final_objects = utils.fusion_objects_from_one_sensor(
                cctv_valid_objects, sensor, fusion_objects
            )
            fusion_type = "fusion_one"

    else:
            final_objects = tuc_fusion.Tuc_fusion().get_objects_into_consideration(
                cctv_valid_objects, lwir_valid_objects, fusion_decision
            )
            fusion_type = "fusion_all"

    fusion_decision = utils.export_fusion_VCD(
            final_objects, fusion_type, streams, fusion_objects, sensor, timestamp_vcd
        )
      
    if(utils.check_objects(fusion_decision)):
        producer.send(to_topic, str(fusion_decision).encode("utf-8"))
        print("Data sent")
            # utils.save_producer_message(fusion_decision)
        print(fusion_decision)
        print(fusion_timestamp)
    else:
        print("Data no sent")

    cctv_valid_objects = []
    lwir_valid_objects = []
    streams = []
    timestamp = 0
    fusion_objects.extend(final_objects)


    if count == 5:
            print("Clear fusion objects")
            fusion_objects = []
            count = 0

    count += 1
    print("count:",count)


    # # except Exception as err:
    #     print("No data to sent", err)
    #     pass


cctv_valid_objects = []
lwir_valid_objects = []
fusion_objects = []
count = 0
flag_send = True

timestamp = {"CCTV": 0, "LWIR_ZOOM": 0}
fusion_decision = {}
message = {}
streams = []
timestamp_vcd = 0
fusion_timestamp = 0

for msg in consumer:
    try:
        flag_send = True
        message = msg
        print(msg)

        annotator = msg.value["openlabel"]["metadata"]["annotator"]
        timestamp_temp = msg.value["openlabel"]["metadata"]["timestamp"]
        timestamp_vcd = timestamp_temp
        stream = msg.value["openlabel"]["streams"]
        print(stream)
        streams.append(stream)

        if annotator == "CCTV" and timestamp_temp >= timestamp[annotator]:
            cctv_valid_objects = camera_sensor.Camera_sensor(annotator).get_valid_objects(
                msg.value
            )
            timestamp[annotator] = timestamp_temp

        elif annotator == "LWIR_ZOOM" and timestamp_temp >= timestamp[annotator]:
            lwir_valid_objects = camera_sensor.Camera_sensor(annotator).get_valid_objects(
                msg.value
            )
            timestamp[annotator] = timestamp_temp
    except Exception as err:
        print("Error", err)
        flag_send = False
        continue
