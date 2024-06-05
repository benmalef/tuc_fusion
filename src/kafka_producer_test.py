from kafka import KafkaConsumer
from kafka import KafkaProducer
import utils
import json


def publish_message(fusion_message):

    bootstrap_server = "localhost:9199"
    topic = "VCD-detection-raw"
    message = json.dumps(fusion_message)  # fusion message
    producer = KafkaProducer(bootstrap_servers=bootstrap_server)
    producer.send(topic, bytes(message.encode("ascii")))


# message = utils.load_json_objects(
#     "/home/benmalef/Desktop/Border_Fusion_Final/data/BorderData/CCTV_VCD.json"
# )
# publish_message(message)
# path for loading messages
message = utils.load_json_objects(
    ""
)
publish_message(message)

# path for loading messages
message = utils.load_json_objects(
    ""
)
publish_message(message)
print(message)

