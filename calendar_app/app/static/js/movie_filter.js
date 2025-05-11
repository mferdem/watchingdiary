document.addEventListener('DOMContentLoaded', () => {
    const currentYear = new Date().getFullYear();
    const startDecade = 1900;
    const endDecade = Math.floor(currentYear / 10) * 10;
  
    const decadeButtonsDiv = document.getElementById('decadeButtons');
    const yearButtonsDiv = document.getElementById('yearButtons');
  
    const selectedYear = parseInt(decadeButtonsDiv.dataset.selectedYear || '0');
  
    for (let decade = startDecade; decade <= endDecade; decade += 10) {
      const chip = document.createElement('span');
      chip.className = 'filter-chip';
      chip.textContent = `${decade}s`;
      chip.dataset.decade = decade;
  
      chip.addEventListener('click', () => {
        document.querySelectorAll('#decadeButtons .filter-chip').forEach(el => el.classList.remove('active'));
        chip.classList.add('active');
        createYearButtons(decade);
      });
  
      decadeButtonsDiv.appendChild(chip);
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
          window.location.href = `/movies?year=${year}`;
        });
  
        yearButtonsDiv.appendChild(chip);
      }
    }
  
    // Eğer seçili yıl varsa açılışta ilgili dekadı otomatik aç
    if (selectedYear) {
      const initialDecade = Math.floor(selectedYear / 10) * 10;
      const defaultChip = [...document.querySelectorAll('#decadeButtons .filter-chip')]
        .find(c => parseInt(c.dataset.decade) === initialDecade);
      if (defaultChip) {
        defaultChip.classList.add('active');
        createYearButtons(initialDecade);
      }
    }
  });
  