const abas = document.querySelectorAll('.tab');
const tabContents = document.querySelectorAll('.tab-content');

let selectedTournament = null;

abas.forEach((aba, i) => aba.addEventListener('click', () => {
    tabContents[i].classList.toggle('ativo');
    selectedTournament = aba.innerText;
}));


const buttonsSeasons = document.querySelectorAll('.button-season');

buttonsSeasons.forEach((button) => button.addEventListener('click', () => {
    document.getElementById('selectedSeason').innerText = button.innerText;
    document.getElementById('roundPopup').style.display = 'flex';
}));

function closePopup() {
    document.getElementById('roundPopup').style.display = 'none';
}


function confirmRounds() {

    const rounds = document.getElementById('roundsInput').value;
    const season = document.getElementById('selectedSeason').innerText;
    
    if (rounds < 1 || rounds > 10) {
        alert("Por favor, insira um valor entre 1 e 10.");
        return;
    }
    
    // Fazer uma requisição para o backend
    fetch(`/download/${encodeURIComponent(selectedTournament)}/${encodeURIComponent(season)}?rounds=${rounds}`, {
        method: 'GET'
    })
    .then(response => {
        if (response.ok) {
            return response.blob(); // Recebe o arquivo como Blob
        } else {
            throw new Error("Erro ao gerar o arquivo CSV.");
        }
    })
    .then(blob => {
        // Criar um link para download
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${season.replace(/ /g, '_')}_rodadas_${rounds}.csv`; // Nome do arquivo
        document.body.appendChild(a);
        a.click();
        a.remove();
    })
    .catch(error => alert(error.message));
    
    closePopup();

}
