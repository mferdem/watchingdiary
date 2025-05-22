document.addEventListener('DOMContentLoaded', () => {
  const currentYear = new Date().getFullYear();
  const startDecade = 1920;
  const endDecade = Math.floor(currentYear / 10) * 10;

  const decadeButtonsDiv = document.getElementById('decadeButtons');
  const yearButtonsDiv = document.getElementById('yearButtons');

  const selectedYear = parseInt(decadeButtonsDiv.dataset.selectedYear || '0');
  const selectedDecade = parseInt(decadeButtonsDiv.dataset.selectedDecade || '0');

  // --- PATH DETECTION ---
  function getBasePath() {
    // /movies/list, /movies/grid gibi
    const path = window.location.pathname;
    // Eğer /movies/list veya /movies/grid ile başlıyorsa
    if (path.startsWith('/movies/grid')) return '/movies/grid';
    if (path.startsWith('/movies/list')) return '/movies/list';
    // Default
    return '/movies/list';
  }

  function goToFilter(param, value) {
    const basePath = getBasePath();
    const url = `${basePath}?${param}=${value}`;
    window.location.href = url;
  }

  function createYearButtons(decade) {
    yearButtonsDiv.innerHTML = '';

    for (let i = 0; i < 10; i++) {
      const year = decade + i;
      if (year > currentYear) break;

      const chip = document.createElement('span');
      chip.className = 'filter-chip';
      chip.textContent = year;
      chip.dataset.year = year;

      if (year === selectedYear) chip.classList.add('active');

      chip.addEventListener('click', () => {
        goToFilter('year', year);
      });

      yearButtonsDiv.appendChild(chip);
    }
  }

  for (let decade = startDecade; decade <= endDecade; decade += 10) {
    const chip = document.createElement('span');
    chip.className = 'filter-chip';
    chip.textContent = `${decade}s`;
    chip.dataset.decade = decade;

    if (decade === selectedDecade) chip.classList.add('active');

    chip.addEventListener('click', () => {
      goToFilter('decade', decade);
    });

    decadeButtonsDiv.appendChild(chip);
  }

  // Otomatik decade expand
  if (selectedYear) {
    const initialDecade = Math.floor(selectedYear / 10) * 10;
    const defaultChip = [...document.querySelectorAll('#decadeButtons .filter-chip')]
      .find(c => parseInt(c.dataset.decade) === initialDecade);
    if (defaultChip) {
      defaultChip.classList.add('active');
      createYearButtons(initialDecade);
    }
  } else if (selectedDecade) {
    createYearButtons(selectedDecade);
  }
});
