const socket = io.connect('http://127.0.0.1:5000/');

socket.on('connect', function() {
    console.log('Connexion établie');
});

socket.on('new_data', function(data) {
    console.log('Message reçu: ', data);
});



// Sélectionner l'élément du bouton
const manualMod_toggle = document.getElementById('toggle-container');

const sliders = {};

["servo-1", "servo-2", "angleRotation", "sensibility", "delayUpdate"].forEach((sliderId, i) => {
   sliders[sliderId] = {
       slider: document.getElementById(`${sliderId}__slider`),
       label:  document.getElementById(`${sliderId}__label`),
       manualModRequired: ["servo-1", "servo-2"].includes(sliderId)
   }
});

const cells = document.getElementsByClassName('cell');

const cellsByDirection = {};
["up", "down", "left", "right"].forEach((direction, i) => {
    cellsByDirection[direction] = document.getElementsByClassName(direction);
});

const sensorsLabels = Array.from({ length: 4 }, (_, i) =>
    document.getElementById(`sensor_${i + 1}`)
);

function update_manualMod(hasManualMod) {
    Object.values(sliders).forEach((sliderData) => {
       sliderData.slider.disabled = sliderData.manualModRequired ? !hasManualMod : hasManualMod
    });
    if (hasManualMod) manualMod_toggle.classList.remove('active');
    else manualMod_toggle.classList.add('active');
}

function update_sensors(data) {
    for (let i = 1; i <= 4; i++) {
        const signal = data.phototransistors[`sensor_${i}`];
        sensorsLabels[i - 1].textContent = (signal * 5 / 1024).toFixed(2);
    }

    Array.from(cells).forEach((cell) => {
        cell.classList.remove("active");
    });

    ["servo_1", "servo_2"].forEach((servo) => {

        const direction = data.servomotors[servo].direction;

        if (direction && cellsByDirection[direction]) {
            const elements = Array.from(cellsByDirection[direction]);
            if (elements.length > 0) {
                elements.forEach((element) => {
                    element.classList.add("active");
                });
            }
        }
    });

}

function update_sliders(data, pageJustLoaded=false) {
    ["servo-1", "servo-2"].forEach((servoId, i) => {
        const angle = data.servomotors[servoId.replace(/-/g, '_')].angle;
        const slider = sliders[servoId];
        slider.slider.value = angle;
        slider.label.textContent = angle;
    });

    if (pageJustLoaded) {
        ["sensibility", "delayUpdate", "angleRotation"].forEach((sliderId) => {
            const value = data.system[sliderId];
            const slider = sliders[sliderId]
            slider.slider.value = value;
            slider.label.textContent = value;
        });
    }

}



let pageJustLoaded = true;

// Évènement qui se fait au chargement de la page
window.addEventListener('load', function() {
    pageJustLoaded = true;
});



// Évènement qui se fait lorsque le bouton qui active ou non le mode manuel est cliqué
manualMod_toggle.addEventListener('click', function() {

    manualMod_toggle.classList.toggle('active'); // Ajoute ou retire la classe 'active'
    const hasManualMod = !manualMod_toggle.classList.contains('active')
    data.system.manual = hasManualMod ? 1 : 0;
    update_manualMod(data.system.manual);

    // Envoyer la nouvelle valeur au serveur via WebSocket
    socket.emit('from_website', {
        type: "ws",
        data: {
            edit: "manualMod",
            value: data.system.manual
        }
    });

});


let ignoreWebSocketUpdateUntil = 0;

Object.entries(sliders).forEach(([sliderId, sliderData], i) => {
    const slider = sliderData.slider;
    slider.addEventListener('input', function() {
        ignoreWebSocketUpdateUntil = Date.now() + 100;
        console.log("passs")
        sliderData.label.textContent = this.value;
    });
    slider.addEventListener('change', function() {
        ignoreWebSocketUpdateUntil = Date.now() + 100;
        const value = this.value;
        socket.emit('from_website', {
            type: "ws",
            data: {
                edit: sliderId,
                value: value
            }
        });
    });
});

// Stocke les graphiques
const Charts = {}

// Fonction pour générer un graphique
function generateChart(chartId, courbeTitle, y_title, y_suggestedMax, courbeTitle2=null, y_digit=null, y_unit=null) {

    const e = document.getElementById(chartId).getContext('2d');

    let datasets = [
        {
            label: courbeTitle,
            data: [],
            borderColor: 'red',
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderWidth: 2,
            tension: 0.1
        }
    ]

    if (courbeTitle2) {
        datasets.push({
            label: courbeTitle2,
            data: [],
            borderColor: 'blue',
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderWidth: 2,
            tension: 0.1
        });
    }

    // Création du graphique
    Charts[chartId] = new Chart(e, {
        type: 'line',
        data: {
            labels: [], // Labels générés automatiquement
            datasets: datasets
        },
        options: {
            responsive: false,
            maintainAspectRatio: true,
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'second', // Unité en secondes
                        tooltipFormat: 'HH:mm:ss', // Format pour l'affichage des petites boites au survol d'un point
                        displayFormats: {
                            second: 'HH:mm:ss' // Format des labels de l'axe X
                        }
                    },
                    title: {
                        display: true,
                        text: 'Heure',
                        font: {
                            size: 18,
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        font: {
                            size: 16,
                            font: 'bold'
                        }
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: y_title,
                        font: {
                            size: 18,
                            weight: 'bold'
                        }
                    },
                    beginAtZero: false,
                    suggestedMin: 0,
                    suggestedMax: y_suggestedMax,
                    ticks: {
                        font: {
                            size: 16,
                            font: 'bold'
                        },
                        callback: function (value) {
                            let y_label = "";
                            if (y_digit != null) y_label += value.toFixed(y_digit);
                            y_label += " " + y_unit;
                            return y_label
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        font: {
                            size: 20 // Taille de la police des légendes
                        }
                    }
                }
            }
        }
    });

}

generateChart("chart__powerRequired", "Puissance consommée par le circuit électronique", y_title="Puissance", y_suggestedMax=5, courbetitle2=null, y_digit=2, y_unit="mW");  // Génère un graphique pour la puissance générée par la carte Arduino.
generateChart("chart__powerGenerated", "Puissance instantanée générée par la cellule photovoltaïque", y_title="Puissance", y_suggestedMax=5, courbetitle2=null, y_digit=2, y_unit="mW"); // Génère un graphique pour la puissance générée par la cellule photovoltaïque.
generateChart("chart__meanYield", "Rendement moyen depuis que le panneau est allumé du circuit",  y_title="Rendement", y_suggestedMax=100, courbetitle2="Rendement actuel du circuit", y_digit=0, y_unit="%");



// Fonction pour ajouter un point toutes les secondes
function addDataPoint(chartId, time, point, point2) {

    let chart = Charts[chartId];

    chart.data.datasets[0].data.push({
        x: time,
        y: point
    });

    // Réduire à 1 point sur 2 si on dépasse 10 points
    if (chart.data.datasets[0].data.length > 30) {
        // Ne garder qu’un point sur deux (index pair)
        // chart.data.datasets[0].data.shift();
        chart.data.datasets[0].data = chart.data.datasets[0].data.filter((point, index) => index != 0);
    }

    if (point2) {
        chart.data.datasets[1].data.push({
            x: time,
            y: point2
        });

        if (chart.data.datasets[1].data.length > 30) {
            // Ne garder qu’un point sur deux (index pair)
            chart.data.datasets[1].data = chart.data.datasets[1].data.filter((point, index) => index != 0);
        }

    }

    chart.update();
}

const downloadButtons = document.getElementsByClassName('downloadGraphique');
Array.from(downloadButtons).forEach(downloadButton => {

    downloadButton.addEventListener('click', function() {

        const label = downloadButton.id.split('__')[1];

        const canvas = document.getElementById("chart__" + label);
        const imageUrl = canvas.toDataURL('image/png');

        // Créer un lien de téléchargement
        const link = document.createElement('a');
        link.href = imageUrl;
        link.download = `${label}.png`; // Nom du fichier téléchargé
        link.click(); // Simuler un clic pour télécharger l'image

    });

});

const downloadCSVButtons = document.getElementsByClassName('downloadCSV');
Array.from(downloadCSVButtons).forEach(downloadCSVButton => {

    downloadCSVButton.addEventListener('click', function() {

        const label = downloadCSVButton.id.split('__')[1];
        const data = Charts["chart__" + label].data.datasets[0].data; // Récupérer les données du graphique
        let csvContent = `Temps, ${downloadCSVButton.colName}\n`; // En-têtes du CSV


        data.forEach(point => {
            const time = new Date(point.x).toLocaleString(); // Format de l'heure
            const power = point.y;
            csvContent += `${time}, ${power}\n`; // Ajouter chaque ligne au CSV
        });

        // Créer un lien de téléchargement
        const link = document.createElement('a');
        const blob = new Blob([csvContent], {type: 'text/csv'});
        link.href = URL.createObjectURL(blob);
        link.download = `${label}.csv`; // Nom du fichier téléchargé
        link.click(); // Simuler un clic pour télécharger le CSV

    });

});



socket.on('new_data', function(dataReceived) {

    data = dataReceived;

    if (pageJustLoaded) {
        update_sliders(data, true);
        update_manualMod(data.system.manual);
        document.getElementsByClassName("loader-container")[0].style.display = "None";
        pageJustLoaded = false;
    }

    if (Date.now() < ignoreWebSocketUpdateUntil) return;

    update_sensors(data);


    // Si le mode manuel est désactivé
    if (!data.system.manual) {

        update_sliders(data);

    } else { // Si le mode manuel est activé

    }

    addDataPoint("chart__powerGenerated", data.time, data.powerGenerated)
    addDataPoint("chart__powerRequired", data.time, data.powerRequired)
    addDataPoint("chart__meanYield", data.time, data.meanYield, data.currentYield)

});