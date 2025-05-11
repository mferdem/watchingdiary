document.addEventListener('DOMContentLoaded', () => {
  const activityType = document.getElementById('activityType');
  const nameGroup = document.getElementById('nameGroup');
  const nameInput = document.getElementById('nameInput');

  const sections = {
    film: document.getElementById('filmFields'),
    dizi: document.getElementById('diziFields'),
    maç: document.getElementById('matchFields'),
    konser: document.getElementById('concertFields')
  };

  const hideAllSections = () => {
    Object.values(sections).forEach(el => el.classList.add('d-none'));
  };

  activityType.addEventListener('change', () => {
    const val = activityType.value;
    hideAllSections();

    if (sections[val]) {
      sections[val].classList.remove('d-none');
    }
  });

  // Film için "sinemada izlendi" kontrolü
  const filmCheck = document.getElementById('filmInCinema');
  const filmCinemaFields = document.getElementById('filmCinemaFields');
  if (filmCheck) {
    filmCheck.addEventListener('change', () => {
      filmCinemaFields.classList.toggle('d-none', !filmCheck.checked);
    });
  }

  // Maç için "statta izlendi" kontrolü
  const stadiumCheck = document.getElementById('matchInStadium');
  const stadiumFields = document.getElementById('stadiumFields');
  if (stadiumCheck) {
    stadiumCheck.addEventListener('change', () => {
      stadiumFields.classList.toggle('d-none', !stadiumCheck.checked);
    });
  }

  // Maç bilgilerine göre name inputunu otomatik doldur
  const team1 = document.getElementById('team1');
  const score1 = document.getElementById('score1');
  const team2 = document.getElementById('team2');
  const score2 = document.getElementById('score2');

  const updateMatchName = () => {
    const t1 = team1.value.trim();
    const t2 = team2.value.trim();
    const s1 = score1.value.trim();
    const s2 = score2.value.trim();
    if (t1 && t2 && s1 !== '' && s2 !== '') {
      nameInput.value = `${t1} ${s1}-${s2} ${t2}`;
    } else {
      nameInput.value = '';
    }
  };

  [team1, score1, team2, score2].forEach(el => {
    if (el) el.addEventListener('input', updateMatchName);
  });
});