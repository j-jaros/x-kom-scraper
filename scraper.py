# © 2023 Julian Jaros (julianjaros.pl)

import re
import requests
from bs4 import BeautifulSoup
from components import mobo, cpu, ram, drive, psu, case, cpu_cooler, gpu, fullFilled, unrecognized

HEADERS = {
    'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) "
                  "AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1"}

COMPONENTS_TYPE = {'zasilacz-do-komputera': psu, 'karta-graficzna': gpu,
                   'pamiec-ram': ram, 'procesory': cpu,
                   'procesor-': cpu, 'plyta-glowna': mobo, 'dysk': drive,
                   'chlodzenie-procesora': cpu_cooler,
                   'obudowa-do-komputera': case}

COMPONENTS_PARAMETERS_KEYS = {
    'main_element': 'sc-1s1zksu-0 sc-1s1zksu-1 hHQkLn sc-13p5mv-0 iFAJlN',
    'title_element': 'sc-13p5mv-1 iFeWkh',
    'second_title_element': 'sc-13p5mv-1 funteP',
    'data_element': 'sc-13p5mv-3 UfEQd'
}

CLASSES = [COMPONENTS_TYPE[x] for x in COMPONENTS_TYPE]
DATA_RETRIEVE_REGEX = re.compile(f'<div class="{COMPONENTS_PARAMETERS_KEYS["data_element"]}">(.*?)</div>')

local = False


def scraper(url):
    if not local:
        response = requests.get(url, headers=HEADERS).text
    else:
        with open("./old/dokument.html", "r") as f:
            response = f.read()

    soup = BeautifulSoup(response, 'html.parser')

    # tworzymy liste wszystkich elementow na liscie i dodajemy im klasy.
    list_elements = list(map(str, soup.find_all("div", {'class': 'sc-1yjqabt-7 ibTjKM'})))
    for element in list_elements:
        element = " ".join(element.split())
        link = re.findall(r'href="(.*?)"', element)[0]
        title = re.search(r'<a[^>]*>(.*?)</a>', element).group(1)

        recognition = recognize(link)
        if recognition is None:
            unrecognized.append({title: link})
        else:
            COMPONENTS_TYPE[recognition].title = title
            COMPONENTS_TYPE[recognition].url = f"https://x-kom.pl{link}"

    for component in CLASSES:
        if component.title is not None:
            response = requests.get(component.url, headers=HEADERS)
            component_soup = BeautifulSoup(response.text, 'html.parser')
            params_list = list(
                map(str, component_soup.find_all("div", {'class': COMPONENTS_PARAMETERS_KEYS['main_element']})))

            for params in params_list:
                title = re.findall(rf'<div class="{COMPONENTS_PARAMETERS_KEYS["title_element"]}">(.*?)</div', params)
                if not title:
                    title = re.findall(rf'<div class="{COMPONENTS_PARAMETERS_KEYS["second_title_element"]}">(.*?)</div',
                                       params)
                title = title[0]
                update_component_data(component, title, params)

    check_compatibility()
    display_result()


"""    print("MOBO: ", vars(mobo), "\n\n")
    print("CPU: ", vars(cpu), "\n\n")
    print("RAM: ", vars(ram), "\n\n")
    print("DRIVE: ", vars(drive), "\n\n")
    print("PSU: ", vars(psu), "\n\n")
    print("CASE: ", vars(case), "\n\n")
    print("CPUCOOLER: ", vars(cpu_cooler), "\n\n")
    print("GPU: ", vars(gpu), "\n\n")
    print("FULLFILLED: ", vars(fullFilled), "\n\n")"""


def display_result():
    for component in [mobo, cpu, ram, drive, psu, case, cpu_cooler, gpu]:
        name = str(component.__class__.__name__).lower()
        attr = getattr(fullFilled, name)
        if attr is None:
            print(f"\033[0;31mKomponent {name} nie został wykryty.\033[0m")
        elif not attr:
            reasons = component.reason
            reason_str = ""
            for reason in reasons:
                reason_str += f"\n\033[0;33m{list(reason.keys())[0]}: {reason[list(reason.keys())[0]]}\033[0m"
            print(f"\033[0;31mKomponent {name} nie jest kompatybilny: {reason_str}\033[0m")
        else:
            print(f"\033[1;32mKomponent {name} jest kompatybilny!\033[0m")


def recognize(link):
    type_of_component = None
    for component_type in COMPONENTS_TYPE:
        if component_type in link:
            type_of_component = component_type
            break
    return type_of_component


def update_component_data(component, title, params):
    if component is mobo:
        fullFilled.mobo = True
        if title == "Gniazdo procesora":
            mobo.socket = re.findall(DATA_RETRIEVE_REGEX, params)[0]

        elif title == "Chipset":
            mobo.chipset = re.findall(DATA_RETRIEVE_REGEX, params)[0].replace("Intel ", "")

        elif title == "Typ obsługiwanej pamięci" or title == "Typ obsługiwanej pamięci OC":
            rams = re.findall(DATA_RETRIEVE_REGEX, params)
            mobo.type_of_ram = rams[0].split("-")[0]
            for _ram in rams:
                mobo.ram_timings.append(int(_ram.split("-")[1].split(" ")[0]))

        elif title == "Liczba banków pamięci":
            mobo.ram_slots = re.findall(DATA_RETRIEVE_REGEX, params)[0].split(" ")[0]

        elif title == "Maksymalna wielkość pamięci RAM":
            mobo.max_ram_size = re.findall(DATA_RETRIEVE_REGEX, params)[0].split(" ")[0]

        elif title == "Format":
            mobo.format = re.findall(DATA_RETRIEVE_REGEX, params)[0]

    elif component is cpu:
        fullFilled.cpu = True
        if title == "Gniazdo procesora (socket)":
            cpu.socket = re.findall(DATA_RETRIEVE_REGEX, params)[0]

        elif title == "Obsługiwany chipset":
            cpu.supported_chipsets = re.findall(DATA_RETRIEVE_REGEX, params)

        elif title == "Rekomendowany chipset":
            cpu.recommended_chipset = re.findall(DATA_RETRIEVE_REGEX, params)[0]

        elif title == "Architektura":
            cpu.architecture = re.findall(DATA_RETRIEVE_REGEX, params)

        elif title == "Rodzaj obsługiwanej pamięci":
            rams = re.findall(DATA_RETRIEVE_REGEX, params)

            # TODO: naprawic podwojne zapisywanie parametrow pamieci RAM
            # a potem usunac to czyszczenie list
            cpu.types_of_ram = []
            cpu.ram_timings = []

            for _ram in rams:
                ram_params = _ram.split("-")
                cpu.types_of_ram.append(ram_params[0])
                cpu.ram_timings.append(ram_params[1].split(" ")[0])

        elif title == "Pobór mocy (TDP)":
            cpu.power_consumption = re.findall(DATA_RETRIEVE_REGEX, params)[0].split(" ")[0]

    elif component is ram:
        fullFilled.ram = True
        if title == "Rodzaj pamięci":
            ram.type = re.findall(DATA_RETRIEVE_REGEX, params)[0]

        elif title == "Pojemność całkowita":
            ram.capacity = re.findall(DATA_RETRIEVE_REGEX, params)[0].split(" ")[0]

        elif title == "Liczba modułów":
            ram.bank_count = re.findall(DATA_RETRIEVE_REGEX, params)[0]

        elif title == "Taktowanie":
            ram_timings = re.findall(DATA_RETRIEVE_REGEX, params)
            ram.timing = list(map(lambda x: x.split(" ")[0], ram_timings))[0]

    elif component is drive:
        fullFilled.drive = True
        if title == "Pojemność":
            drive.capacity = re.findall(DATA_RETRIEVE_REGEX, params)[0].split(" ")[0]

        elif title == "Format":
            drive.format = re.findall(DATA_RETRIEVE_REGEX, params)[0]

        elif title == "Interfejs":
            drive.interface = re.findall(DATA_RETRIEVE_REGEX, params)[0]

    elif component is psu:
        fullFilled.psu = True
        if title == "Moc maksymalna":
            psu.power = re.findall(DATA_RETRIEVE_REGEX, params)[0].split(" ")[0]
        elif title == "Standard":
            psu.format = re.findall(DATA_RETRIEVE_REGEX, params)[0]

    elif component is case:
        fullFilled.case = True
        if title == "Standard płyty głównej":
            case.formats = re.findall(DATA_RETRIEVE_REGEX, params)

        elif title == "Standard zasilacza":
            case.psu_format = re.findall(DATA_RETRIEVE_REGEX, params)[0]

        elif title == "Miejsca na wewnętrzne dyski/napędy":
            case.drive_slots = re.findall(DATA_RETRIEVE_REGEX, params)

        elif title == "Maksymalna wysokość chłodzenia CPU":
            case.cpu_cooler_height = re.findall(DATA_RETRIEVE_REGEX, params)[0].split(" ")[0]

    elif component is cpu_cooler:
        fullFilled.cpucooler = True
        if title == "Kompatybilność":
            cpu_cooler.sockets = re.findall(DATA_RETRIEVE_REGEX, params)

        elif title == "TDP":
            cpu_cooler.tdp = re.findall(DATA_RETRIEVE_REGEX, params)

        elif title == "Wysokość":
            cpu_cooler.height = re.findall(DATA_RETRIEVE_REGEX, params)[0].split(" mm")[0]

    elif component is gpu:
        fullFilled.gpu = True
        if title == "Rodzaj złącza":
            gpu.connector = re.findall(DATA_RETRIEVE_REGEX, params)[0]

        elif title == "Złącze zasilania":
            gpu.power_connector = re.findall(DATA_RETRIEVE_REGEX, params)[0]

        elif title == "Rekomendowana moc zasilacza":
            gpu.power_consumption = re.findall(DATA_RETRIEVE_REGEX, params)[0].split(" ")[0]

        elif title == "Długość":
            gpu.length = re.findall(DATA_RETRIEVE_REGEX, params)[0].split(" ")[0]


def check_compatibility():
    if mobo.format not in case.formats:
        fullFilled.mobo = False
        mobo.reason.append({'case': 'bad_format'})

    if cpu.socket != mobo.socket:
        fullFilled.cpu = False
        cpu.reason.append({'mobo': 'bad_socket'})

    if mobo.chipset not in cpu.supported_chipsets:
        fullFilled.cpu = False
        cpu.reason.append({'mobo': 'bad_chipset'})

    if int(gpu.length) > int(case.gpu_length):
        fullFilled.gpu = False
        gpu.reason.append({'case': 'exceeded_length'})

    if int(ram.bank_count) > int(mobo.ram_slots):
        fullFilled.ram = False
        ram.reason.append({'mobo': 'exceeded_bank_count'})

    if int(ram.capacity) > int(mobo.max_ram_size):
        fullFilled.ram = False
        ram.reason.append({'mobo': 'exceeded_max_ram_size'})

    if int(ram.timing) not in list(map(int, mobo.ram_timings)):
        fullFilled.ram = False
        ram.reason.append({'mobo': 'bad_timing'})

    if int(ram.timing) not in list(map(int, cpu.ram_timings)):
        fullFilled.ram = False
        ram.reason.append({'cpu': 'bad_timing'})

    if ram.type != mobo.type_of_ram:
        fullFilled.ram = False
        ram.reason.append({'mobo': 'bad_type'})

    if ram.type not in cpu.types_of_ram:
        fullFilled.ram = False
        ram.reason.append({'cpu': 'bad_type'})

    if int(psu.power) < int(gpu.power_consumption + cpu.power_consumption):
        fullFilled.psu = False
        psu.reason.append({'power': 'not_enough_power'})

    if psu.format != case.psu_format:
        fullFilled.psu = False
        psu.reason.append({'case': 'bad_format'})

    if mobo.socket not in cpu_cooler.sockets:
        fullFilled.cpucooler = False
        cpu_cooler.reason.append({'mobo': 'bad_socket'})

    if int(cpu_cooler.tdp) > int(cpu.power_consumption):
        fullFilled.cpucooler = False
        cpu_cooler.reason.append({'cpu': 'not_enough_tdp'})

    if int(cpu_cooler.height) > int(case.cpu_cooler_height):
        fullFilled.cpucooler = False
        cpu.reason.append({'case': 'exceeded_height'})


scraper('https://www.x-kom.pl/lista/dxuvrm6en')
