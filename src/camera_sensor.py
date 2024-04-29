import json
import utils


class Camera_sensor:

    def __init__(self, name):
        self.__name = name
        self.confidence_threshold = self.load_config_confidence_threshold()
        self.parameters = self.get_parameters()

    def getName(self):
        return self.__name

    def setName(self, name):
        self.__name = name

    def load_config_confidence_threshold(self):
        parameters = utils.load_config_parameters("config.json")
        try:
            return parameters[self.__name]["confidence_threshold"]
        except KeyError as err:
            print(
                f"\033[31mError: Can't load the confidence threshold. {err} doesn't exist in config file.\033[0m"
            )
            return None

    def get_parameters(self):

        try:
            parameters = utils.load_config_parameters("config.json")
            return parameters[self.__name]
        except KeyError as err:
            print(
                f"\033[31mError: Can't load the parameters. {err} doesn't exist in config file.\033[0m"
            )
            return None

    def get_confidence_threshold(self):
        return self.confidence_threshold

    def set_confidence_threshold(self, confidence_threshold):
        self.confidence_threshold = confidence_threshold

    def __str__(self) -> str:
        return f"""\033[1;32mcamera_name: {self.__name}\nconfidence_threshold: {self.confidence_threshold}\033[0m"""

    def get_all_objects(self):
        return utils.load_VCD_objects()

    def get_valid_objects_file(self):
        # under construction
        """
        Check for objects that follow the rules.
        Args:

        Returns:
            list of detected objects

        """
        objects = utils.load_json_objects(self.parameters["file_path"])[0]
        objects = objects["value"]["openlabel"]["objects"]

        if objects is None:
            return None

        valid_objects = []
        for object_id, object in objects.items():
            if utils.check_object_data(
                object["object_data"], self.confidence_threshold
            ):
                valid_objects.append(object)
        return valid_objects

    def get_valid_objects(self, message):
        # under construction
        """
        Check for objects that follow the rules.
        Args:

        Returns:
            list of detected objects

        """

        objects = message["openlabel"]["objects"]

        if objects is None:
            return None

        valid_objects = []
        for object_id, object in objects.items():
            if utils.check_object_data(
                object["object_data"], self.confidence_threshold
            ):
                valid_objects.append(object)
        return valid_objects
