async function title_animation() {
    const w_text_wrapper = document.querySelector(".title")
    let text = w_text_wrapper.textContent
    text = text.split("")
    console.log(text)
    w_text_wrapper.innerHTML = ""

    for (const letter of text) {
        const element = document.createElement('span')
        element.textContent = letter
        w_text_wrapper.appendChild(element)
        await new Promise(r => setTimeout(r, 70))
    }
    await new Promise(r => setTimeout(r, 400))
    w_text_wrapper.innerHTML = "X-KOM SCRAPER"
}

title_animation()

function check_components() {
    const url = document.querySelector('input').value
    const xhr = new XMLHttpRequest()
    xhr.open("POST", "/api/v1/check_components", true)
    xhr.setRequestHeader("Content-Type", "application/json")
    console.log(`kliknieto przycisk, scrapuje dla linku ${url}`)
    xhr.onload = () => {
        const response = JSON.parse(xhr.responseText)
        console.log('otrzymano odpowiedz')
        console.log(response)
        switch (response['code']) {
            case 'ok':
                console.log('kod ok. wprowadzam dane')
                document.querySelector('#list_title').textContent = response['title']
                display_components(response['response'])
                display_unrecognized(response['unrecognized'])
        }
    }
    xhr.send(JSON.stringify({'url': url}))
}

function display_components(components) {
    const table = document.querySelector('table tbody')
    table.innerHTML = ''
    Object.keys(components).forEach((key) => {
        const row = document.createElement('tr')

        const component_type = document.createElement('td')
        component_type.textContent = translate_names(`${key}`)
        row.appendChild(component_type)

        const component_name = document.createElement('td')
        component_name.textContent = components[key].name
        row.appendChild(component_name)

        const component_status = document.createElement('td')
        switch (components[key].status) {
            case 2:
                component_status.textContent = 'Kompatybilne'
                row.classList.value = 'compatible'
                break
            case 1:
                component_status.textContent = 'Niekompatybilne'
                row.classList.value = 'notcompatible'
                break
            case 0:
                component_status.textContent = 'Brak na liście'
                component_name.textContent = "N/A"
                row.classList.value = 'notinlist'
                break
            case -1: {
                component_status.textContent = "Nie rozpoznano"
                row.classList.value = 'unrecognized'
                break
            }
            default:
                component_status.textContent = 'N/A'
                break
        }
        row.appendChild(component_status)
        table.appendChild(row)
    })

}

const name_table = {
    'case': 'Obudowa',
    'cpu': 'Procesor',
    'cpucooler': 'Chłodzenie procesora',
    'drive': 'Dysk',
    'gpu': 'Karta graficzna',
    'mobo': 'Płyta główna',
    'psu': 'Zasilacz',
    'ram': 'Pamięć RAM'
}

function translate_names(name) {
    console.log(`sprawdzam nazwe ${name}/${name_table.hasOwnProperty(name)}`)
    if (!(name_table.hasOwnProperty(name))) return 'N/A'

    return name_table[name]

}

document.querySelector("button").addEventListener('click', () => {
    check_components()
})