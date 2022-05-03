from pypozyx import (POZYX_POS_ALG_UWB_ONLY, 
                     POZYX_3D, 
                     Coordinates, 
                     POZYX_SUCCESS, 
                     PozyxConstants,
                     version,
                     SingleRegister, 
                     DeviceList, 
                     PozyxRegisters)
from time import sleep

class ReadyToLocalize(object):
    """Continuously calls the Pozyx positioning function and prints its position."""

    def __init__(self, pozyx, sio, anchors, algorithm=POZYX_POS_ALG_UWB_ONLY, dimension=POZYX_3D, height=1000, remote_id=None, web=True):
        self.pozyx = pozyx
        self.sio = sio

        self.anchors = anchors
        self.algorithm = algorithm
        self.dimension = dimension
        self.height = height
        self.remote_id = remote_id

        self.web = web

    def setup(self):
        """Sets up the Pozyx for positioning by calibrating its anchor list."""
        print("------------POZYX POSITIONING V{} -------------".format(version))
        print("")
        print("- System will manually configure tag")
        print("")
        print("- System will auto start positioning")
        print("")
        if self.remote_id is None:
            self.pozyx.printDeviceInfo(self.remote_id)
        else:
            for device_id in [None, self.remote_id]:
                self.pozyx.printDeviceInfo(device_id)
        print("")
        print("------------POZYX POSITIONING V{} -------------".format(version))
        print("")

        self.setAnchorsManual(save_to_flash=False)
        self.printPublishConfigurationResult()

    def loop(self):
        """Performs positioning and displays/exports the results."""
        position = Coordinates()
        status = self.pozyx.doPositioning(
            position, self.dimension, self.height, self.algorithm, remote_id=self.remote_id)
        if status == POZYX_SUCCESS:
            self.printPublishPosition(position)
        else:
            self.printPublishErrorCode("positioning")

    def printPublishPosition(self, position):
        """Prints the Pozyx's position and possibly sends it as a socketio packet"""
        network_id = self.remote_id
        if network_id is None:
            network_id = 0
        print("POS ID {}, x(mm): {pos.x} y(mm): {pos.y} z(mm): {pos.z}".format(
            "0x%0.4x" % network_id, pos=position))

        pos_x = int(position.x) / 1000
        pos_y = int(position.y) / 1000

        if self.web:
            self.sio.emit('position', {'x': pos_x, 'y': pos_y})
      

    def printPublishErrorCode(self, operation):
        """Prints the Pozyx's error and possibly sends it as a socketio packet"""
        error_code = SingleRegister()
        network_id = self.remote_id
        if network_id is None:
            self.pozyx.getErrorCode(error_code)
            print("LOCAL ERROR %s, %s" % (operation, self.pozyx.getErrorMessage(error_code)))
            if self.web:
                self.sio.emit('error', self.pozyx.getErrorMessage(error_code))
            return
        status = self.pozyx.getErrorCode(error_code, self.remote_id)
        if status == POZYX_SUCCESS:
            print("ERROR %s on ID %s, %s" %
                  (operation, "0x%0.4x" % network_id, self.pozyx.getErrorMessage(error_code)))
            if self.web:
                self.sio.emit('error', self.pozyx.getErrorMessage(error_code))

        else:
            self.pozyx.getErrorCode(error_code)
            print("ERROR %s, couldn't retrieve remote error code, LOCAL ERROR %s" %
                  (operation, self.pozyx.getErrorMessage(error_code)))
            if self.web:
                self.sio.emit('error', self.pozyx.getErrorMessage(error_code))
            # should only happen when not being able to communicate with a remote Pozyx.

    def setAnchorsManual(self, save_to_flash=False):
        """Adds the manually measured anchors to the Pozyx's device list one for one."""
        status = self.pozyx.clearDevices(remote_id=self.remote_id)
        for anchor in self.anchors:
            status &= self.pozyx.addDevice(anchor, remote_id=self.remote_id)
        if len(self.anchors) > 4:
            status &= self.pozyx.setSelectionOfAnchors(PozyxConstants.ANCHOR_SELECT_AUTO, len(self.anchors),
                                                       remote_id=self.remote_id)

        if save_to_flash:
            self.pozyx.saveAnchorIds(remote_id=self.remote_id)
            self.pozyx.saveRegisters([PozyxRegisters.POSITIONING_NUMBER_OF_ANCHORS], remote_id=self.remote_id)
        return status

    def printPublishConfigurationResult(self):
        """Prints and potentially publishes the anchor configuration result in a human-readable way."""
        list_size = SingleRegister()

        self.pozyx.getDeviceListSize(list_size, self.remote_id)
        print("List size: {0}".format(list_size[0]))
        if list_size[0] != len(self.anchors):
            self.printPublishErrorCode("configuration")
            return
        device_list = DeviceList(list_size=list_size[0])
        self.pozyx.getDeviceIds(device_list, self.remote_id)
        print("Calibration result:")
        print("Anchors found: {0}".format(list_size[0]))
        print("Anchor IDs: ", device_list)

        if self.web:
            web_anchors = []
        for i in range(list_size[0]):
            anchor_coordinates = Coordinates()
            self.pozyx.getDeviceCoordinates(device_list[i], anchor_coordinates, self.remote_id)
            print("ANCHOR, 0x%0.4x, %s" % (device_list[i], str(anchor_coordinates)))
            if self.web:
                web_anchors.append(
                    {
                        "name": "0x%0.4x".format(device_list[i]), 
                        "x": float(anchor_coordinates.x) / 1000, 
                        "y": float(anchor_coordinates.y) / 1000
                    }
                )

        if self.web:
            self.sio.emit('anchors', {'anchors': web_anchors})
        sleep(0.025)

    def printPublishAnchorConfiguration(self):
        """Prints and potentially publishes the anchor configuration"""
        for anchor in self.anchors:
            print("ANCHOR,0x%0.4x,%s" % (anchor.network_id, str(anchor.coordinates)))
