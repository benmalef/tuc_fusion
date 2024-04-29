import camera_sensor
import tuc_fusion
import utils
import kafka_fusion


def main():

    cctv_objects = camera_sensor.Camera_sensor("CCTV_ZOOM").get_valid_objects()
    lwir_zoom = camera_sensor.Camera_sensor("LWIR_ZOOM").get_valid_objects()
    final_objects = tuc_fusion.Tuc_fusion().get_objects_into_consideration(
        cctv_objects, lwir_zoom
    )

    fusion_decision = utils.export_fusion_VCD(final_objects)
    kafka_fusion.publish_message(fusion_decision)


if __name__ == "__main__":
    main()
