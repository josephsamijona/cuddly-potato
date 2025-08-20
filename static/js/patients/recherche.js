// Script pour la recherche de patients en temps réel
// À placer dans votre fichier static/js/patients/recherche.js

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('id_query');
    const searchResults = document.getElementById('search-results');
    const resultsContainer = document.getElementById('results-container');
    let searchTimeout;

    // Fonction pour effectuer la recherche AJAX
    function performSearch() {
        const query = searchInput.value.trim();
        
        // Ne rien faire si la requête est vide ou trop courte
        if (query.length < 2) {
            searchResults.innerHTML = '';
            resultsContainer.style.display = 'none';
            return;
        }

        // Afficher un indicateur de chargement
        searchResults.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"></div></div>';
        resultsContainer.style.display = 'block';

        // Effectuer la requête AJAX
        fetch(`/patients/recherche/?query=${encodeURIComponent(query)}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            // Vider les résultats précédents
            searchResults.innerHTML = '';
            
            if (data.length === 0) {
                searchResults.innerHTML = '<div class="alert alert-info">Aucun patient trouvé.</div>';
                return;
            }

            // Créer la table de résultats
            const table = document.createElement('table');
            table.className = 'table table-hover';
            
            // En-tête de la table
            const thead = document.createElement('thead');
            thead.innerHTML = `
                <tr>
                    <th>ID</th>
                    <th>Nom</th>
                    <th>Prénom</th>
                    <th>Date de naissance</th>
                    <th>Actions</th>
                </tr>
            `;
            table.appendChild(thead);

            // Corps de la table avec les résultats
            const tbody = document.createElement('tbody');
            
            data.forEach(patient => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${patient.id_patient}</td>
                    <td>${patient.nom}</td>
                    <td>${patient.prenom}</td>
                    <td>${patient.date_naissance}</td>
                    <td>
                        <a href="${patient.url}" class="btn btn-sm btn-primary">
                            <i class="fas fa-eye"></i> Voir
                        </a>
                    </td>
                `;
                tbody.appendChild(tr);
            });
            
            table.appendChild(tbody);
            searchResults.appendChild(table);
        })
        .catch(error => {
            console.error('Erreur lors de la recherche:', error);
            searchResults.innerHTML = '<div class="alert alert-danger">Une erreur est survenue lors de la recherche.</div>';
        });
    }

    // Écouteur d'événement pour la saisie dans le champ de recherche
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            // Utiliser un délai pour éviter trop de requêtes
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(performSearch, 300);
        });

        // Écouteur pour la soumission du formulaire
        const searchForm = document.getElementById('search-form');
        if (searchForm) {
            searchForm.addEventListener('submit', function(e) {
                e.preventDefault();
                performSearch();
            });
        }
    }
});