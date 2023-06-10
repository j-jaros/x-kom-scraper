document.querySelector("button").addEventListener('click', ()=>{
    window.open("/sprawdz-podzespoly", "_self")
})
async function title_animation() {
    const w_text_wrapper = document.querySelector("h1")
    let text = w_text_wrapper.textContent
    text = text.split("")
    console.log(text)
    w_text_wrapper.innerHTML = ""

    for (const letter of text){
        const element = document.createElement('span')
        element.textContent = letter
        w_text_wrapper.appendChild(element)
        await new Promise(r=>setTimeout(r, 70))
    }
    document.querySelector("p").classList.value = 'visible'
}

title_animation()