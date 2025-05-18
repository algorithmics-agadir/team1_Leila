// Fonction pour initialiser les animations et les graphiques du tableau de bord
function initDashboard(cityLabels, cityData, sweetCount, saltyCount, drinkCount) {
    // Animation des cartes statistiques
    gsap.from('.stat-card', {
        y: 20,
        opacity: 0,
        duration: 0.5,
        stagger: 0.1,
        ease: 'power3.out'
    });
    
    gsap.from('.chart-card, .table-card', {
        y: 30,
        opacity: 0,
        duration: 0.7,
        stagger: 0.15,
        delay: 0.3,
        ease: 'power3.out'
    });
    
    // Configuration du graphique de plats par ville
    const ctxDishes = document.getElementById('dishes-by-city').getContext('2d');
    const dishesChart = new Chart(ctxDishes, {
        type: 'bar',
        data: {
            labels: cityLabels,
            datasets: [{
                label: 'Nombre de plats',
                data: cityData,
                backgroundColor: '#FF6B6B',
                borderColor: '#FF6B6B',
                borderWidth: 1,
                borderRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        display: true,
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
    
    // Configuration du graphique de types de plats
    const ctxTypes = document.getElementById('dish-types').getContext('2d');
    const typesChart = new Chart(ctxTypes, {
        type: 'doughnut',
        data: {
            labels: ['Sucré', 'Salé', 'Boisson'],
            datasets: [{
                data: [sweetCount, saltyCount, drinkCount],
                backgroundColor: [
                    '#FF9F1C',
                    '#4ECDC4',
                    '#FF6B6B'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            cutout: '70%'
        }
    });
}

// La fonction sera appelée depuis le template avec les données Django 