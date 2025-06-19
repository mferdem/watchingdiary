document.addEventListener('DOMContentLoaded', () => {
  const activityType = document.getElementById('activityType');
  const nameGroup = document.getElementById('nameGroup');
  const nameInput = document.getElementById('nameInput');

  const sections = {
    movie: document.getElementById('movieFields'),
    series: document.getElementById('seriesFields'),
    match: document.getElementById('matchFields'),
    concert: document.getElementById('concertFields')
  };

  const hideAllSections = () => {
    Object.values(sections).forEach(el => el.classList.add('d-none'));
  };

  // Aktivite tipi değişince ilgili alanları göster
  activityType.addEventListener('change', () => {
    const val = activityType.value;
    hideAllSections();
    if (sections[val]) {
      sections[val].classList.remove('d-none');
    }
  });

  // Movie > sinemada izlendi alanı
  const movieCheck = document.getElementById('movieInCinema');
  const movieCinemaFields = document.getElementById('movieCinemaFields');
  if (movieCheck && movieCinemaFields) {
    movieCheck.addEventListener('change', () => {
      movieCinemaFields.classList.toggle('d-none', !movieCheck.checked);
    });
  }

  // Match > statta izlendi alanı
  const stadiumCheck = document.getElementById('matchInStadium');
  const stadiumFields = document.getElementById('stadiumFields');
  if (stadiumCheck && stadiumFields) {
    stadiumCheck.addEventListener('change', () => {
      stadiumFields.classList.toggle('d-none', !stadiumCheck.checked);
    });
  }

  // Match bilgilerine göre name alanını otomatik oluştur
  const team1 = document.getElementById('team1');
  const score1 = document.getElementById('score1');
  const team2 = document.getElementById('team2');
  const score2 = document.getElementById('score2');

  const updateMatchName = () => {
    const t1 = team1?.value.trim();
    const s1 = score1?.value.trim();
    const t2 = team2?.value.trim();
    const s2 = score2?.value.trim();

    if (t1 && t2 && s1 !== '' && s2 !== '') {
      nameInput.value = `${t1} ${s1}-${s2} ${t2}`;
    } else {
      nameInput.value = '';
    }
  };

  [team1, score1, team2, score2].forEach(el => {
    if (el) el.addEventListener('input', updateMatchName);
  });

  // IMDb ID girildiğinde OMDb API'den bilgi çek
  const imdbInput = document.querySelector('input[name="imdb_id"]');
  const yearInput = document.querySelector('input[name="year"]');
  const durationInput = document.querySelector('input[name="duration"]');

  if (imdbInput && typeof OMDB_API_KEY !== 'undefined') {
    imdbInput.addEventListener('blur', function () {
      const imdbId = imdbInput.value.trim();
      const type = activityType?.value;

      if (type !== 'movie') return; // sadece film seçiliyse çalıştır
      if (!imdbId.startsWith('tt') || imdbId.length < 5) return;

      fetch(`https://www.omdbapi.com/?i=${imdbId}&apikey=${OMDB_API_KEY}`)
        .then(response => response.json())
        .then(data => {
          if (data.Response === 'True') {
            if (data.Title && nameInput) nameInput.value = data.Title;
            if (data.Year && yearInput) yearInput.value = data.Year;
            if (data.Runtime && durationInput) {
              const minutes = data.Runtime.replace(' min', '');
              durationInput.value = parseInt(minutes) || '';
            }
          }
        })
        .catch(err => console.warn('OMDb API error:', err));
    });
  }
});


const stars = document.querySelectorAll('#ratingStars .star');
const ratingInput = document.getElementById('myRatingInput');

stars.forEach(star => {
  star.addEventListener('click', () => {
    const rating = parseInt(star.dataset.value);
    ratingInput.value = rating;

    stars.forEach(s => {
      s.classList.toggle('selected', parseInt(s.dataset.value) <= rating);
    });
  });
});

const editStars = document.querySelectorAll('#editRatingStars .star');
const editRatingInput = document.getElementById('editMyRatingInput');

if (editStars.length && editRatingInput) {
  editStars.forEach(star => {
    star.addEventListener('click', () => {
      const rating = parseInt(star.dataset.value);
      editRatingInput.value = rating;

      editStars.forEach(s => {
        s.classList.toggle('selected', parseInt(s.dataset.value) <= rating);
      });
    });
  });
}