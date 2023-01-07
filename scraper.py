import re
import requests
from bs4 import BeautifulSoup


def scraper(url, outsource=1):
    headers = {
        'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) "
                      "AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1"}
    fullfilled_requirements = {'motherboard': False, 'cpu': False, 'ram': False, 'drive': False, 'psu': False,
                               'case': False,
                               'cpu_cooler': False, 'gpu': False}

    components_type = {'zasilacz-do-komputera': 'psu', 'pasta-termoprzewodzaca': 'cream', 'karta-graficzna': 'gpu',
                       'pamiec-ram': 'ram', 'procesory': 'cpu',
                       'procesor-': 'cpu', 'plyta-glowna': "mobo", 'dysk': 'drive',
                       'chlodzenie-procesora': "cpu_cooler",
                       'obudowa-do-komputera': 'case'}

    components = {'mobo': None, 'cpu': None, 'ram': None, 'drive': None, 'psu': None, 'case': None, "cpu_cooler": None,
                  'gpu': None, 'unknowns': []}

    components_parameters_keys = {
        'main_element': 'sc-1s1zksu-0 sc-1s1zksu-1 hHQkLn sc-13p5mv-0 iFAJlN',
        'title_element': 'sc-13p5mv-1 iFeWkh',
        'second_title_element': 'sc-13p5mv-1 funteP',
        'data_element': 'sc-13p5mv-3 UfEQd'
    }

    components_parameters = {
        'mobo':
            {
                'socket': None,
                'chipset': None,
                'type_of_ram': None,
                'ram_timings': [],
                'ram_slots': None,
                'max_ram_size': None,
                'inner_connectors': [],
                'outer_connectors': [],
                'raid': [],
                'multi-gpu': None,
                'multi-gpu-technology': None,
                'builtin-graphics-support': None,
                'format': None
            },
        'cpu':
            {
                'socket': None,
                'chipset-list': [],
                'builtin-graphics': None,
                'type_of_ram': None,
                'ram_timings': [],
                'tdp': None
            },
        'ram':
            {
                'type_of_ram': None,
                'total_capacity': None,
                'number_of_banks': None,
                'timing': None,
            },
        'drive':
            {
                'capacity': None,
                'format': None,
                'interface': None,
                # 'read_speed': None,
                # 'write_speed': None,
            },
        'psu':
            {
                'max_power': None,
                'format': None,
                'connectors': [],
            },
        'case':
            {
                'formats': [],
                'psu_format': None,
                'inner_drive_slots': [],
                'extend_cards_slot': None,
                'max_gpu_length': None,
                'max_cpu_cooler_height': None,
            },
        'cpu_cooler':
            {
                'sockets': [],
                'tdp': None,
                'height': None,
            },
        'gpu':
            {
                'connector': None,
                'power_connector': None,
                'power_required': None,
                'gpu_length': None,
                'format': None
            }
    }

    if outsource:
        response_obj = requests.get(url, headers=headers)
        if response_obj.status_code == 404:
            return 'not_found'
        elif response_obj.status_code != 200:
            return 'error_occurred'

        response = str(response_obj.text)
    else:
        with open("dokument.html", "r") as f:
            response = f.read()

    soup = BeautifulSoup(response, 'html.parser')

    # tworzymy liste wszystkich elementow na liscie i dodajemy im klasy.
    list_elements = list(map(str, soup.find_all("div", {'class': 'sc-1yjqabt-7 ibTjKM'})))

    for element in list_elements:
        element = " ".join(element.split())
        link = re.findall(r'href="(.*?)"', element)[0]
        title = re.search(r'<a[^>]*>(.*?)</a>', element).group(1)

        type_of_component = "unknown"
        for component_type in components_type:
            if component_type in link:
                type_of_component = component_type
                break

        if type_of_component == "unknown":
            components['unknowns'].append({"title": title, "part_url": f"https://x-kom.pl{link}"})
        else:
            components[components_type[type_of_component]] = {"title": title, "part_url": f"https://x-kom.pl{link}",
                                                              "parameters": {}}

    component = "mobo"
    response = requests.get(components[component]['part_url'], headers=headers)
    part_soup = BeautifulSoup(response.text, 'html.parser')
    params_list = list(map(str, part_soup.find_all("div", {'class': components_parameters_keys['main_element']})))

    for params in params_list:
        if component == "mobo":
            title = re.findall(rf'<div class="{components_parameters_keys["title_element"]}">(.*?)</div', params)
            if not title:
                title = re.findall(rf'<div class="{components_parameters_keys["second_title_element"]}">(.*?)</div',
                                   params)
            title = title[0]
            #print(title)
            data_retrieve_regex = re.compile(f'<div class="{components_parameters_keys["data_element"]}">(.*?)</div>')
            if title == "Gniazdo procesora":
                components_parameters[component]['socket'] = re.findall(data_retrieve_regex, params)[0]
            elif title == "Chipset":
                components_parameters[component]['chipset'] = re.findall(data_retrieve_regex, params)[0]
            elif title in ["Typ obsługiwanej pamięci", "Typ obsługiwanej pamięci OC"]:
                rams = re.findall(data_retrieve_regex, params)
                components_parameters[component]['type_of_ram'] = rams[0].split("-")[0]
                for ram in rams:
                    components_parameters[component]['ram_timings'].append(ram.split("-")[1].split(" ")[0])
            elif title == "Liczba banków pamięci":
                components_parameters[component]['ram_slots'] = re.findall(data_retrieve_regex, params)[0].split(" ")[0]
            elif title == "Maksymalna wielkość pamięci RAM":
                components_parameters[component]['max_ram_size'] = \
                re.findall(data_retrieve_regex, params)[0].split(" ")[0]
            elif title == "Wewnętrzne złącza":
                inner_connectors = re.findall(data_retrieve_regex, params)
                for connector in inner_connectors:
                    try:
                        connector_count = connector.split("- ")[1].split(" ")[0]
                    except:
                        connector_count = 1
                    connector = connector.split(" -")[0]
                    components_parameters[component]['inner_connectors'].append(
                        {'connector': connector, 'count': int(connector_count)})
            elif title == "Zewnętrzne złącza":
                outer_connectors = re.findall(data_retrieve_regex, params)
                for connector in outer_connectors:
                    try:
                        connector_count = connector.split("- ")[1].split(" ")[0]
                    except:
                        connector_count = 1
                    connector = connector.split(" -")[0]
                    components_parameters[component]['outer_connectors'].append(
                        {'connector': connector, 'count': int(connector_count)})
            elif title == "Obsługa układów graficznych w procesorach":
                integrated_gpu = re.findall(data_retrieve_regex, params)[0]
                if integrated_gpu == "Tak":
                    integrated_gpu = True
                else:
                    integrated_gpu = False
                components_parameters[component]['builtin-graphics-support'] = integrated_gpu
            elif title == "Format":
                components_parameters[component]['format'] = re.findall(data_retrieve_regex, params)[0]
            """
            if title in ['Gniazdo procesora']:
                components_parameters[component]['socket'] = re.findall(data_retrieve_regex, params)[0]
                data = re.findall(data_retrieve_regex, params)[0]
                print(data)
            elif title in ['Chipset']:
                components_parameters[component]['chipset'] = re.findall(data_retrieve_regex, params)[0]
            """

    for param in components_parameters['mobo']:
        print(f"{param}: {components_parameters['mobo'][param]}")

    return components


if __name__ == "__main__":
    scraper(input("Wprowadz link: "))
