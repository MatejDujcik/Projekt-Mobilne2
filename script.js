fetch('http://localhost:3000/api/test')
  .then(response => response.json())
  .then(data => {
    console.log(data.message); // očakávame: Funguje to zo servera
  })
  .catch(error => console.error('Chyba:', error));