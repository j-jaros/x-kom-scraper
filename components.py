
class Case:
    def __init__(self):
        self.formats = []
        self.psu_format = None
        self.drive_slots = []
        self.gpu_length = 0
        self.cpu_cooler_height = None

        self.title = None
        self.url = None
        self.reason = []


class Mobo:
    def __init__(self):
        self.socket = None
        self.chipset = None
        self.type_of_ram = None
        self.ram_timings = []
        self.ram_slots = 0
        self.max_ram_size = 0
        self.format = None

        self.title = None
        self.url = None
        self.reason = []


class Cpu:
    def __init__(self):
        self.socket = None
        self.supported_chipsets = []
        self.recommended_chipset = None
        self.architecture = None
        self.types_of_ram = []
        self.ram_timings = []
        self.power_consumption = 0

        self.title = None
        self.url = None
        self.reason = []


class Gpu:
    def __init__(self):
        self.connector = None
        self.power_connector = None
        self.power_consumption = 0
        self.length = 0

        self.title = None
        self.url = None
        self.reason = []


class Ram:
    def __init__(self):
        self.type = None
        self.capacity = 0
        self.bank_count = 0
        self.timing = 0

        self.title = None
        self.url = None
        self.reason = []


class Drive:
    def __init__(self):
        self.capacity = 0
        self.format = None
        self.interface = None

        self.title = None
        self.url = None
        self.reason = []


class Psu:
    def __init__(self):
        self.power = 0
        self.format = None
        self.connectors = []

        self.title = None
        self.url = None
        self.reason = []


class CpuCooler:
    def __init__(self):
        self.sockets = []
        self.tdp = 0
        self.height = 0

        self.title = None
        self.url = None
        self.reason = []


class FullFilled:
    def __init__(self):
        self.mobo = None
        self.cpu = None
        self.ram = None
        self.drive = None
        self.psu = None
        self.case = None
        self.cpucooler = None
        self.gpu = None


mobo = Mobo()
cpu = Cpu()
ram = Ram()
drive = Drive()
psu = Psu()
case = Case()
cpu_cooler = CpuCooler()
gpu = Gpu()
fullFilled = FullFilled()
unrecognized = []
