/**
 * FMS - Fleet Management System
 * JavaScript principal
 * PNUD Côte d'Ivoire - 2025
 */

document.addEventListener('DOMContentLoaded', function() {
    // Activer tous les tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Activer tous les popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });

    // Fermeture automatique des alertes après 5 secondes
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Animation des cartes sur la page d'accueil
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });

    // Gestion du mode sombre (si implémenté)
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            // Sauvegarder la préférence dans localStorage
            if (document.body.classList.contains('dark-mode')) {
                localStorage.setItem('darkMode', 'enabled');
            } else {
                localStorage.setItem('darkMode', 'disabled');
            }
        });

        // Vérifier si le mode sombre est activé dans localStorage
        if (localStorage.getItem('darkMode') === 'enabled') {
            document.body.classList.add('dark-mode');
        }
    }

    // Validation des formulaires côté client
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Fonction pour afficher un message de confirmation avant suppression
    window.confirmDelete = function(event, itemName) {
        if (!confirm(`Êtes-vous sûr de vouloir supprimer ${itemName} ?`)) {
            event.preventDefault();
        }
    };

    // Fonction pour prévisualiser une image avant upload
    const imageInput = document.getElementById('imageInput');
    const imagePreview = document.getElementById('imagePreview');
    
    if (imageInput && imagePreview) {
        imageInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = 'block';
                }
                reader.readAsDataURL(file);
            }
        });
    }

    // Gestion des filtres de tableau
    const tableFilter = document.getElementById('tableFilter');
    if (tableFilter) {
        tableFilter.addEventListener('keyup', function() {
            const filterValue = this.value.toLowerCase();
            const table = document.querySelector('.filterable-table');
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(filterValue)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
});
