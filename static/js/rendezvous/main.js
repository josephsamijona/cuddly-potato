// Script pour la gestion des rendez-vous
// À placer dans votre fichier static/js/rendezvous/main.js

document.addEventListener('DOMContentLoaded', function() {
    // Vérification de disponibilité lors de la sélection d'une date/heure
    setupDisponibiliteCheck();
    
    // Mise à jour rapide du statut des rendez-vous
    setupStatusUpdate();
    
    // Initialisation des éléments d'interface
    setupDateTimePickers();
});

/**
 * Configure la vérification de disponibilité des médecins
 */
function setupDisponibiliteCheck() {
    const medecinSelect = document.getElementById('id_medecin');
    const dateInput = document.getElementById('id_date_heure_0');
    const heureInput = document.getElementById('id_date_heure_1');
    const dureeInput = document.getElementById('id_duree');
    const disponibiliteInfo = document.getElementById('disponibilite-info');
    
    // Si les éléments n'existent pas, on ne fait rien
    if (!medecinSelect || !dateInput || !heureInput || !dureeInput || !disponibiliteInfo) {
        return;
    }
    
    // Fonction pour vérifier la disponibilité
    function checkDisponibilite() {
        const medecinId = medecinSelect.value;
        const date = dateInput.value;
        const heure = heureInput.value;
        const duree = dureeInput.value;
        const rdvId = document.getElementById('rdv-id') ? document.getElementById('rdv-id').value : '';
        
        // Vérifier que tous les champs sont remplis
        if (!medecinId || !date || !heure || !duree) {
            disponibiliteInfo.innerHTML = '';
            return;
        }
        
        // Afficher un indicateur de chargement
        disponibiliteInfo.innerHTML = '<div class="spinner-border spinner-border-sm text-primary" role="status"></div> Vérification...';
        
        // Effectuer la requête AJAX
        const url = `/rendezvous/check-disponibilite/?medecin=${medecinId}&date=${date}&heure=${heure}&duree=${duree}&rdv_id=${rdvId}`;
        
        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.disponible) {
                disponibiliteInfo.innerHTML = '<div class="alert alert-success">✓ ' + data.message + '</div>';
            } else {
                disponibiliteInfo.innerHTML = '<div class="alert alert-danger">✗ ' + data.message + '</div>';
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            disponibiliteInfo.innerHTML = '<div class="alert alert-warning">Erreur lors de la vérification</div>';
        });
    }
    
    // Écouter les changements des champs concernés
    medecinSelect.addEventListener('change', checkDisponibilite);
    dateInput.addEventListener('change', checkDisponibilite);
    heureInput.addEventListener('change', checkDisponibilite);
    dureeInput.addEventListener('change', checkDisponibilite);
}

/**
 * Configure la mise à jour rapide du statut des rendez-vous
 */
function setupStatusUpdate() {
    const statusButtons = document.querySelectorAll('.status-update-btn');
    
    statusButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const rdvId = this.dataset.rdvId;
            const newStatus = this.dataset.status;
            const returnTo = this.dataset.returnTo || 'list';
            const csrf = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
            
            // Préparer les données du formulaire
            const formData = new FormData();
            formData.append('statut', newStatus);
            formData.append('csrfmiddlewaretoken', csrf);
            
            // Effectuer la requête AJAX
            fetch(`/rendezvous/${rdvId}/statut/?return_to=${returnTo}`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Mettre à jour l'interface
                    const statusBadge = document.querySelector(`#rdv-status-${rdvId}`);
                    if (statusBadge) {
                        // Mettre à jour le badge de statut
                        const statusClasses = {
                            'PLANIFIE': 'bg-info',
                            'CONFIRME': 'bg-primary',
                            'TERMINE': 'bg-success',
                            'ANNULE': 'bg-danger'
                        };
                        
                        // Supprimer les classes existantes
                        statusBadge.classList.remove('bg-info', 'bg-primary', 'bg-success', 'bg-danger');
                        
                        // Ajouter la nouvelle classe
                        if (statusClasses[newStatus]) {
                            statusBadge.classList.add(statusClasses[newStatus]);
                        }
                        
                        // Mettre à jour le texte
                        statusBadge.textContent = button.textContent.trim();
                    }
                    
                    // Désactiver les boutons si le statut est terminal
// Désactiver les boutons si le statut est terminal
                    if (newStatus === 'TERMINE' || newStatus === 'ANNULE') {
                        statusButtons.forEach(btn => {
                            if (btn.dataset.rdvId === rdvId) {
                                btn.disabled = true;
                            }
                        });
                    }
                    
                    // Afficher un message de succès
                    const messageContainer = document.getElementById('messages-container');
                    if (messageContainer) {
                        const alertDiv = document.createElement('div');
                        alertDiv.className = 'alert alert-success alert-dismissible fade show';
                        alertDiv.innerHTML = `
                            ${data.message}
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        `;
                        messageContainer.appendChild(alertDiv);
                        
                        // Faire disparaître le message après 3 secondes
                        setTimeout(() => {
                            alertDiv.classList.remove('show');
                            setTimeout(() => alertDiv.remove(), 150);
                        }, 3000);
                    }
                } else {
                    // Afficher un message d'erreur
                    alert("Erreur lors de la mise à jour du statut: " + data.message);
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                alert("Une erreur est survenue lors de la mise à jour du statut.");
            });
        });
    });
}

/**
 * Configure les sélecteurs de date et d'heure
 */
function setupDateTimePickers() {
    // Date picker
    const datePickers = document.querySelectorAll('.datepicker');
    if (datePickers.length > 0) {
        datePickers.forEach(picker => {
            // Si vous utilisez Flatpickr ou autre bibliothèque, initialisez-la ici
            // Exemple avec Flatpickr:
            // flatpickr(picker, {
            //     dateFormat: "Y-m-d",
            //     minDate: "today",
            //     locale: "fr"
            // });
        });
    }
    
    // Time picker
    const timePickers = document.querySelectorAll('.timepicker');
    if (timePickers.length > 0) {
        timePickers.forEach(picker => {
            // Initialisation du time picker
        });
    }
}

/**
 * Fonctions pour le calendrier des rendez-vous
 */
// Fonction pour naviguer entre les mois du calendrier
function changeMonth(year, month) {
    window.location.href = `/rendezvous/calendrier/?year=${year}&month=${month}`;
}

// Fonction pour filtrer par médecin dans le calendrier
function filterByMedecin(medecinId) {
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set('medecin', medecinId);
    window.location.href = `/rendezvous/calendrier/?${urlParams.toString()}`;
}

// Fonction pour afficher les détails d'un rendez-vous dans une modal
function showRdvDetails(rdvId) {
    // Cette fonction pourrait charger les détails du rendez-vous via AJAX
    // et les afficher dans une fenêtre modale Bootstrap
    
    fetch(`/rendezvous/details/${rdvId}/`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        // Remplir et afficher la modal avec les données
        const modal = new bootstrap.Modal(document.getElementById('rdvDetailsModal'));
        
        // Remplir les champs
        document.getElementById('modal-patient-name').textContent = data.patient_nom;
        document.getElementById('modal-date-heure').textContent = data.date_heure;
        document.getElementById('modal-medecin').textContent = data.medecin_nom;
        document.getElementById('modal-motif').textContent = data.motif;
        document.getElementById('modal-status').textContent = data.statut;
        document.getElementById('modal-notes').textContent = data.notes || 'Aucune note';
        
        // Configurer les liens d'action
        document.getElementById('modal-edit-link').href = `/rendezvous/${rdvId}/modifier/`;
        
        // Afficher la modal
        modal.show();
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert("Impossible de charger les détails du rendez-vous.");
    });
}

/**
 * Fonctions pour la vue des rendez-vous du jour
 */
// Fonction pour changer de jour dans la vue des rendez-vous du jour
function changeDay(date) {
    window.location.href = `/rendezvous/jour/?date=${date}`;
}

// Fonction pour naviguer vers aujourd'hui
function goToToday() {
    const today = new Date().toISOString().split('T')[0];
    window.location.href = `/rendezvous/jour/?date=${today}`;
}