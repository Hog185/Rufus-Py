from PyQt6.QtCore import QObject, pyqtSignal
import pyudev

class UsbMonitor(QObject):
    device_added = pyqtSignal(str)
    device_removed = pyqtSignal(str)
    device_list_updated = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.context = pyudev.Context()  
        self.monitor = pyudev.Monitor.from_netlink(self.context)
        self.monitor.filter_by(subsystem='block')
        self.devices = {}
        
        self._load_existing()
        
        self.observer = pyudev.MonitorObserver(
            self.monitor,
            callback=self._event
        )
        self.observer.start()
        
    def _load_existing(self):
        for device in self.context.list_devices(subsystem='block', DEVTYPE='disk'):
            if device.get('ID_BUS') == 'usb':
                node = device.device_node
                label = device.get('ID_FS_LABEL') or device.get('ID_MODEL') or node
                self.devices[node] = label
        self.device_list_updated.emit(self.devices)
        
    def _event(self, device):
        action = device.action
        if device.get('DEVTYPE') != 'disk':
            return
        if device.get('ID_BUS') != 'usb':
            return
        
        node = device.device_node
        action = device.action
        
        if action == "add":
            label = device.get('ID_FS_LABEL') or device.get('ID_MODEL') or node
            self.devices[node] = label
            self.device_added.emit(node)
        elif action == "remove":
            if node in self.devices:
                del self.devices[node]
                self.device_removed.emit(node)
                
        self.device_list_updated.emit(self.devices)
