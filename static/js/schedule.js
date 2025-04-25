document.addEventListener('DOMContentLoaded', () => {
    // проверяем на какой мы странице
    const hrefPageArr = window.location.href.split('/')
    const page = hrefPageArr[hrefPageArr.length - 2]
    if (page !== 'masterschedule') return
    // добавляем кнопку графика на страницу
    const wrapperBlock = document.querySelector('.col-12.col-md-auto.d-flex.flex-grow-1.align-items-center')
    const scheduleButton = document.createElement('button')
    scheduleButton.classList.add('shedule-button')
    scheduleButton.textContent = 'График'
    wrapperBlock.appendChild(scheduleButton)

    // добавляем модалку
    const body = document.querySelector('body')
    const modalwrapper = document.createElement('div')
    modalwrapper.classList.add('modal-wrapper')
    body.prepend(modalwrapper)

    // добавляем верхний блок
    const modalTop = document.createElement('div')
    modalTop.classList.add('modal-top')
    modalwrapper.appendChild(modalTop)
    // добавляем селекты верхнего блока
    const currentDate = new Date()
    // месяцы
    const currentMonth = currentDate.getMonth() + 1
    const months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август',
        'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
    const monthsSelect = document.createElement('select')
    monthsSelect.classList.add('months-select')
    monthsSelect.classList.add('modal-select')
    months.forEach((item, i) => {
        const index = i + 1
        const option = document.createElement('option')
        option.value = index
        option.textContent = item
        if (currentMonth === index) option.selected = true
        monthsSelect.appendChild(option)
    })
    modalTop.appendChild(monthsSelect)
    // годы
    const currentYear = currentDate.getFullYear()
    const years = [currentYear, currentYear + 1]
    const yearsSelect = document.createElement('select')
    yearsSelect.classList.add('years-select')
    yearsSelect.classList.add('modal-select')
    years.forEach(item => {
        const option = document.createElement('option')
        option.value = item
        option.textContent = item
        if (item === currentYear) option.selected = true
        yearsSelect.appendChild(option)
    })
    modalTop.appendChild(yearsSelect)
    // добавляем кнопку закрытия
    const closeButton = document.createElement('button')
    closeButton.classList.add('close-button')
    modalTop.appendChild(closeButton)
    // добавляем изображение для кнопки
    const imgClose = document.createElement('img')
    imgClose.src = '/static/imgs/closeModal.png'
    imgClose.classList.add('close-img')
    closeButton.appendChild(imgClose)

    // добавляем средний блок
    const modalMiddle = document.createElement('div')
    modalMiddle.classList.add('modal-middle')
    modalwrapper.appendChild(modalMiddle)
    // добавляем блок дней недели
    const weekDaysBlock = document.createElement('div')
    weekDaysBlock.classList.add('week-days-block')
    modalMiddle.appendChild(weekDaysBlock)
    // добавляем подпись строке дней недели
    const weekDaysBlockTitle = document.createElement('div')
    weekDaysBlockTitle.classList.add('week-days-block-title')
    weekDaysBlockTitle.textContent = 'Дни недели'
    weekDaysBlock.appendChild(weekDaysBlockTitle)
    // добавляем дни недели
    const weekDays = document.createElement('div')
    weekDays.classList.add('week-days')
    weekDaysBlock.appendChild(weekDays)
    const addWeekDays = (year, month) => {
        weekDays.innerHTML = ''
        const weekdayNamesForMonth = []
        for (let day = 1; day <= new Date(year, month, 0).getDate(); day++) {
            let currentDate = new Date(year, month - 1, day);
            let options = { weekday: 'short' };
            let currentDayName = new Intl.DateTimeFormat('ru-RU', options).format(currentDate);
            day = String(day)
            if (day.length === 1) day = 0 + day
            weekdayNamesForMonth.push({
                day: day,
                weekday: currentDayName
            });
        }

        return weekdayNamesForMonth;
    }




    // получаем инфу о сотрудниках и их графиках через апи запрос
    //для этого отправляем текущий месяц и год
    //const APIUrl = 'http://127.0.0.1:8000/api/v1/'
    const APIUrl = 'https://devsaloon.tw1.su/api/v1/'
    const getSchedules = `${APIUrl}get_schedules`
    const createNewSchedules = `${APIUrl}new_schedules`
    const getMastersWorkTimes = `${APIUrl}get_masters_work_time`
    const getSchedule = (month, year) => {
        // удаляем прошлые блоки, если они есть
        const mastersBlocks = document.querySelectorAll('.master-block')
        if (mastersBlocks) mastersBlocks.forEach(item => item.remove())
        fetch(getSchedules, {
            method: 'POST',
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify({ "month": month, "year": year }),
        })
            .then(res => res.json())
            .then(res => {
                const schedule = res.schedule
                schedule.forEach(item => {
                    const master = item.name
                    const masterID = item.id
                    const masterSchedule = item.schedule?.map(item => item.date)
                    // добавляем блок мастера
                    const masterBlock = document.createElement('div')
                    masterBlock.classList.add('master-block')
                    masterBlock.setAttribute('id', masterID)
                    modalMiddle.appendChild(masterBlock)
                    // добавляем в блок имя мастера
                    const masterName = document.createElement('div')
                    masterName.classList.add('week-days-block-title')
                    masterName.classList.add('master-days-block-title')
                    masterName.textContent = master
                    masterBlock.appendChild(masterName)
                    // добавляем блок для дней недели
                    const masterWeekDaysBlock = document.createElement('div')
                    masterWeekDaysBlock.classList.add('week-days')
                    masterBlock.appendChild(masterWeekDaysBlock)
                    let weekdayNamesForCurrentMonth = addWeekDays(year, month)
                    weekdayNamesForCurrentMonth.forEach(item => {
                        const weekDay = document.createElement('div')
                        weekDay.classList.add('week-day')
                        weekDay.textContent = item.weekday
                        weekDays.appendChild(weekDay)
                    })
                    weekdayNamesForCurrentMonth.forEach(item => {
                        const masterWeekDay = document.createElement('div')
                        masterWeekDay.classList.add('week-day')
                        masterWeekDay.classList.add('master-week-day')
                        masterSchedule?.forEach(date => {
                            const workDay = date.split('-')[2]
                            const workMonth = date.split('-')[1]
                            const workYear = date.split('-')[0]
                            if (item.day === workDay && month === Number(workMonth)
                                && year === Number(workYear)) {
                                masterWeekDay.classList.add('work')
                            }
                        })
                        masterWeekDay.textContent = item.day
                        const openWorkTimes = document.createElement('img')
                        openWorkTimes.classList.add('open-work-times')
                        openWorkTimes.src = '/static/imgs/openWorkTimes.png'
                        masterWeekDay.appendChild(openWorkTimes)
                        masterWeekDaysBlock.appendChild(masterWeekDay)
                    })
                })
            })
    }
    getSchedule(currentMonth, currentYear)



    //добавляем нижний блок
    const bottomBlock = document.createElement('div')
    bottomBlock.classList.add('bottom-block')
    modalwrapper.appendChild(bottomBlock)
    // кнопка отправки
    const sendButton = document.createElement('button')
    sendButton.classList.add('send-button')
    sendButton.classList.add('shedule-button')
    sendButton.textContent = 'Отправить'
    bottomBlock.appendChild(sendButton)

    // добавляем прослушиватели событий
    // открытие модалки
    scheduleButton.addEventListener('click', () => {
        modalwrapper.classList.add('open')
    })
    // закрытие модалки
    closeButton.addEventListener('click', () => {
        modalwrapper.classList.remove('open')
    })

    // выбор месяца и года
    monthsSelect.addEventListener('change', e => {
        const monthValue = e.target.value
        const yearValue = yearsSelect.options[yearsSelect.selectedIndex].value
        getSchedule(Number(monthValue), Number(yearValue))
    })
    yearsSelect.addEventListener('change', e => {
        const monthValue = monthsSelect.options[monthsSelect.selectedIndex].value
        const yearValue = e.target.value
        getSchedule(Number(monthValue), Number(yearValue))
    })
    ////////////////////////////////////////////////////////////////
    // модалка для показа рабочего времени
    const timeModalWrapper = document.createElement('div')
    timeModalWrapper.classList.add('time-modal-wrapper')
    timeModalWrapper.classList.add('hidden-modal-time')
    body.appendChild(timeModalWrapper)
    const timeModal = document.createElement('div')
    timeModal.classList.add('time-modal')
    timeModalWrapper.appendChild(timeModal)
    const timeModalTop = document.createElement('div')
    timeModalTop.classList.add('time-modal-top')
    timeModal.appendChild(timeModalTop)
    const timeModalMasterName = document.createElement('div')
    timeModalMasterName.classList.add('time-modal-master-name')
    timeModalTop.appendChild(timeModalMasterName)
    timeModalMasterName.textContent = 'Мастер'
    const timeModalCloseButton = document.createElement('div')
    timeModalCloseButton.classList.add('time-modal-close-button')
    timeModalTop.appendChild(timeModalCloseButton)
    const imgTimeClose = document.createElement('img')
    imgTimeClose.src = '/static/imgs/closeModal.png'
    imgTimeClose.classList.add('time-modal-close-button-img')
    timeModalCloseButton.appendChild(imgTimeClose)
    const timeModalBottom = document.createElement('div')
    timeModalBottom.classList.add('time-modal-bottom')
    timeModal.appendChild(timeModalBottom)
    timeModalCloseButton.addEventListener('click', () => {
        timeModalMasterName.textContent = ''
        timeModalBottom.innerHTML = ''
        timeModalWrapper.classList.add('hidden-modal-time')
    })
    // проставляем/удаляем рабочие дни
    modalMiddle.addEventListener('click', e => {
        // открытие модалки времени
        if (e.target.classList.contains('open-work-times')) {
            if (!e.target.closest('.work')) return
            timeModalWrapper.classList.remove('hidden-modal-time')
            const masterData = e.target.closest('.master-block')
            const masterID = masterData.id
            const selectedYear = yearsSelect.options[yearsSelect.selectedIndex].value
            const selectedMonth = monthsSelect.options[monthsSelect.selectedIndex].value
            const selectedDay = e.target.closest('.week-day').textContent
            const selectedDate = `${selectedYear}-${selectedMonth}-${selectedDay}`
            console.log(masterID)
            console.log(selectedDate)
            fetch(getMastersWorkTimes, {
                method: 'POST',
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken
                },
                body: JSON.stringify({
                    'master_id': masterID,
                    'work_day_date': selectedDate
                })
            }).then(res => res.json())
                .then(res => {
                    const masterName = res.master_name
                    const times = res.work_time
                    timeModalMasterName.textContent = masterName
                    times.forEach(item => {
                        const timeBlock = document.createElement('p')
                        timeBlock.classList.add('work-time')
                        timeBlock.textContent = item.time
                        if (item.busy) timeBlock.classList.add('busy-time')
                        timeModalBottom.appendChild(timeBlock)
                    })
                })
                .catch(err => console.log(err))
            return
        }
        if (!e.target.classList.contains('master-week-day')) return
        const masterData = e.target.closest('.master-block')
        if (!masterData) return
        const day = e.target
        if (day.classList.contains('work')) {
            day.classList.remove('work')
        } else {
            day.classList.add('work')
        }
    })

    sendButton.addEventListener('click', () => {
        const mastersBlocks = document.querySelectorAll('.master-block')
        const mastersSchedule = []
        const selectedYear = yearsSelect.options[yearsSelect.selectedIndex].value
        const selectedMonth = monthsSelect.options[monthsSelect.selectedIndex].value
        mastersBlocks.forEach(item => {
            const masterID = item.id
            const workDays = item.querySelectorAll('.work')
            const workDates = Array.from(workDays)
                .map(item => `${selectedYear}-${selectedMonth}-${item.textContent}`)
            mastersSchedule.push({ masterID, workDates })
        })
        fetch(createNewSchedules, {
            method: 'POST',
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify({ "new_schedules": mastersSchedule, selectedMonth }),
        }).then(() => window.location.reload());
    })
})