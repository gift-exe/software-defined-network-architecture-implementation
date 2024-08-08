from webob import Response
import json

from ryu.app.wsgi import ControllerBase, route



class MyControllerRest(ControllerBase):
    def __init__(self, req, link, data, **config):
        super(MyControllerRest, self).__init__(req, link, data, **config)
        self.my_controller = data['my_controller']

    @route('devices', '/devices', methods=['GET'])
    def get_devices(self, req, **kwargs):
        devices = self.my_controller.switches
        print(vars(devices[0]))
        device_list = [device.id for device in devices]
        device_list = json.dumps(device_list)

        return Response(content_type='application/json; charset=utf-8', body=device_list)
    
    @route('device_desc', '/device/desc/{dpid}', methods=['GET'])
    def get_device_description(self, req, dpid, **kwargs):
        dpid = int(dpid)
