// Данные по странам с локальными картинками из вашей папки
const countriesData = {
  france: {
    title: "Франция",
    images: ["france1.jpg", "france2.jpg", "france3.jpg"],
    desc: "Страна изысканной кухни, высокой моды и богатой истории. Франция предлагает неповторимую атмосферу парижских улочек, лазурный берег и романтические пейзажи.",
    sights: ["Эйфелева башня и Марсово поле", "Музей Лувр", "Собор Парижской Богоматери", "Версальский дворец"]
  },
  italy: {
    title: "Италия",
    images: ["italy1.jpg", "italy2.jpg", "italy3.jpg"],
    desc: "Родина великого искусства, колыбель античной цивилизации и гастрономический рай. Италия покоряет своими древними памятниками и живописным побережьем.",
    sights: ["Колизей и Римский форум", "Каналы и мосты Венеции", "Пизанская башня", "Амальфитанское побережье"]
  },
  egypt: {
    title: "Египет",
    images: ["egypt1.jpg", "egypt2.jpg", "egypt3.jpg"],
    desc: "Загадочная страна фараонов, величественных пирамид и песчаных пустынь, сочетающаяся с роскошными курортами Красного моря.",
    sights: ["Великие Пирамиды Гизы и Сфинкс", "Карнакский храм в Луксоре", "Долина Царей", "Коралловые рифы Красного моря"]
  },
  japan: {
    title: "Япония",
    images: ["japan1.jpg", "japan2.jpg", "japan3.jpg"],
    desc: "Удивительная страна контрастов, где яркая гик-культура Акихабары и неоновые мегаполисы сочетаются с тихими буддийскими пагодами, цветущей сакурой и живописными водопадами.",
    sights: ["Пагода Сэйганто-дзи и водопад Нати", "Район Акихабара и Сибуя в Токио", "Священная гора Фудзи", "Святилище Фусими Инари в Киото"]
  }
};

let selectedCountry = "";

// Функция открытия модального окна
function openDetailsModal(key) {
  const country = countriesData[key];
  if (!country) return;

  selectedCountry = country.title;

  // Подстановка картинок в коллаж
  document.getElementById('collageImg1').src = country.images[0];
  document.getElementById('collageImg2').src = country.images[1];
  document.getElementById('collageImg3').src = country.images[2];

  // Текстовые данные
  document.getElementById('modalCountryTitle').innerText = country.title;
  document.getElementById('modalCountryDesc').innerText = country.desc;

  // Достопримечательности
  const sightsList = document.getElementById('modalSightsList');
  sightsList.innerHTML = "";
  country.sights.forEach(sight => {
    const li = document.createElement('li');
    li.innerText = sight;
    sightsList.appendChild(li);
  });

  document.getElementById('modalBookActionBtn').onclick = function() {
    closeModal('detailsModal');
    openBookingModal(country.title);
  };

  const modal = document.getElementById('detailsModal');
  modal.classList.add('active');
}

// Открытие окна бронирования
function openBookingModal(countryName) {
  selectedCountry = countryName;
  document.getElementById('bookingCountryName').innerText = countryName;
  
  const modal = document.getElementById('bookingModal');
  modal.classList.add('active');
}

// Закрытие модального окна
function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('active');
  }
}

// Отправка формы бронирования
function handleBookingSubmit(event) {
  event.preventDefault();
  const name = document.getElementById('fullName').value;
  const date = document.getElementById('travelDate').value;
  const phone = document.getElementById('phone').value;

  alert(`Спасибо, ${name}!\n\nВаша заявка на тур в страну (${selectedCountry}) успешно отправлена.\nДата поездки: ${date}\nТелефон: ${phone}`);

  closeModal('bookingModal');
  event.target.reset();
}

// Закрытие при клике мимо окна
window.addEventListener('click', function(event) {
  if (event.target.classList.contains('modal')) {
    event.target.classList.remove('active');
  }
});