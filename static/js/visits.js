document.addEventListener('DOMContentLoaded', () => {
    // проверяем на какой мы странице
    const hrefPageArr = window.location.href.split('/')
    const page = hrefPageArr[hrefPageArr.length - 2]
    if (page !== 'visitjournal') return
    // добавляем кнопку графика на страницу
    const wrapperBlock = document.querySelector('.col-12.col-md-auto.d-flex.flex-grow-1.align-items-center')
    const scheduleButton = document.createElement('a')
    scheduleButton.href='https://devsaloon.tw1.su/visits/?id=0'
    scheduleButton.target = '_blank'
    scheduleButton.classList.add('shedule-button')
    scheduleButton.textContent = 'Журнал работ'
    wrapperBlock.appendChild(scheduleButton)




    // добавляем прослушиватели событий
    // открытие модалки
    scheduleButton.addEventListener('click', () => {
        modalwrapper.classList.add('open')
    })
})