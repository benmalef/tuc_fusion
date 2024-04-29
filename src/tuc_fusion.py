import utils
import camera_sensor


class Tuc_fusion:

    def __init__(self):
        self.distance_threshold = self.load_config_distance_threshold()

    def load_config_distance_threshold(self):
        """
        Loads the distance threshold from config file.

        Returns:
            distance_threshold: distance threshold from config file
        """
        try:
            parameters = utils.load_config_parameters("config.json")["tuc_fusion"]
            distance_threshold = parameters["distance_threshold"]
            return distance_threshold
        except Exception as err:
            print(err, "\nCan't load the parameters from config file.")
            return None

    def get_distance_threshold(self):
        return self.distance_threshold

    def set_distance_threshold(self, distance_threshold):
        self.distance_threshold = distance_threshold

    def get_objects_into_consideration(
        self, sensor1_objects, sensor2_objects, fusion_vcd
    ):

        detected_objects = utils.objects_into_consideration_by_GPS_coordinates(
            sensor1_objects, sensor2_objects, fusion_vcd, self.distance_threshold
        )

        return detected_objects
