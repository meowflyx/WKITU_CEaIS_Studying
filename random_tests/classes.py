class NetworkInterface:
    def __init__(self, interface_name, mac_address):
        self.interface_name = interface_name
        self.mac_address = mac_address
        self.is_up = False
        self.ip_address = None

    def turn_on(self):
        if self.is_up:
            print("Интерфейс уже включен!")
        else:
            self.is_up = True

    def assign_ip(self, ip_address):
        if not self.is_up:
            print("Интерфейс не включен. Для начала включите его.")
        else:
            self.ip_address = ip_address

    def __str__(self):
        return f"Interface {self.interface_name} | MAC: {self.mac_address} | Status: {self.is_up} | IP: {self.ip_address}"


enp01 = NetworkInterface("enp01", "00:1A:2B:3C:4D:5E")
print(enp01)

enp01.turn_on()
print(enp01)

enp01.assign_ip("192.168.0.2")
print(enp01)