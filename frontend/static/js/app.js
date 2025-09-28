// ProximaScore Frontend - Stap 1 JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const form = document.getElementById('proximaForm');
    const loadingSection = document.getElementById('loadingSection');
    const resultsSection = document.getElementById('resultsSection');
    const errorSection = document.getElementById('errorSection');
    const calculateBtn = document.getElementById('calculateBtn');
    
    // Initialize
    checkSystemStatus();
    
    // Form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        calculateProximaScore();
    });
    
    async function calculateProximaScore() {
        const address = document.getElementById('address').value.trim();
        const profile = document.getElementById('profile').value;
        
        if (!address) {
            showError('Voer een geldig adres in');
            return;
        }
        
        // Show loading state
        showLoading();
        calculateBtn.disabled = true;
        
        try {
            const response = await fetch('/api/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    address: address,
                    profile: profile
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Onbekende fout');
            }
            
            displayResults(data);
            
        } catch (error) {
            console.error('Calculation error:', error);
            showError(error.message || 'Er ging iets mis bij de berekening');
        } finally {
            calculateBtn.disabled = false;
        }
    }
    
    function displayResults(data) {
        hideAllSections();
        resultsSection.style.display = 'block';
        
        // Total score
        document.getElementById('totalScore').textContent = data.total_score;
        document.getElementById('scoreLocation').textContent = data.address;
        document.getElementById('scoreProfile').textContent = data.profile_display;
        
        // Categories breakdown
        const categoriesContainer = document.getElementById('categoriesContainer');
        categoriesContainer.innerHTML = '';
        
        Object.entries(data.categories).forEach(([key, category]) => {
            const categoryElement = createCategoryElement(key, category);
            categoriesContainer.appendChild(categoryElement);
        });
        
        // Technical details
        displayTechnicalDetails(data);
    }
    
    function createCategoryElement(key, category) {
        const element = document.createElement('div');
        element.className = 'category-item';
        
        // Find closest place info
        const closestPlace = category.places && category.places.length > 0 ? category.places[0] : null;
        const distanceText = closestPlace ? `${closestPlace.distance_meters}m` : 'Niet gevonden';
        const placeText = closestPlace ? closestPlace.name : 'Geen voorzieningen gevonden';
        
        element.innerHTML = `
            <div class="category-info">
                <h4>${category.display_name}</h4>
                <p>${placeText}</p>
                <p>Afstand: ${distanceText} | Gewicht: ${category.weight}%</p>
            </div>
            <div class="category-score">
                <div class="score">${category.score}</div>
                <div class="details">${getScoreQuality(category.score)}</div>
            </div>
        `;
        
        return element;
    }
    
    function getScoreQuality(score) {
        if (score >= 80) return 'Uitstekend';
        if (score >= 60) return 'Goed';
        if (score >= 40) return 'Matig';
        if (score >= 20) return 'Slecht';
        return 'Zeer slecht';
    }
    
    function displayTechnicalDetails(data) {
        const technicalDetails = document.getElementById('technicalDetails');
        technicalDetails.innerHTML = `
            <div class="tech-detail">
                <span>Coördinaten:</span>
                <strong>${data.location.lat.toFixed(6)}, ${data.location.lng.toFixed(6)}</strong>
            </div>
            <div class="tech-detail">
                <span>Berekend op:</span>
                <strong>${new Date(data.calculated_at).toLocaleString('nl-NL')}</strong>
            </div>
            <div class="tech-detail">
                <span>Versie:</span>
                <strong>${data.version}</strong>
            </div>
            <div class="tech-detail">
                <span>Geanalyseerde voorzieningen:</span>
                <strong>${Object.keys(data.categories).length}</strong>
            </div>
        `;
    }
    
    function showLoading() {
        hideAllSections();
        loadingSection.style.display = 'block';
    }
    
    function showError(message) {
        hideAllSections();
        document.getElementById('errorMessage').textContent = message;
        errorSection.style.display = 'block';
    }
    
    function hideAllSections() {
        loadingSection.style.display = 'none';
        resultsSection.style.display = 'none';
        errorSection.style.display = 'none';
    }
    
    // System status check
    async function checkSystemStatus() {
        try {
            const response = await fetch('/api/health');
            const data = await response.json();
            
            // Update status indicators
            document.getElementById('backendStatus').textContent = 
                response.ok ? 'Online' : 'Offline';
            document.getElementById('googleStatus').textContent = 
                data.google_api_configured ? 'Geconfigureerd' : 'Niet geconfigureerd';
            document.getElementById('activeCategories').textContent = 
                `${data.active_categories} van ${data.active_categories + 7}`;
                
            // Apply status styling
            updateStatusStyling('backendStatus', response.ok);
            updateStatusStyling('googleStatus', data.google_api_configured);
            
        } catch (error) {
            console.error('Status check failed:', error);
            document.getElementById('backendStatus').textContent = 'Fout';
            document.getElementById('googleStatus').textContent = 'Onbekend';
            updateStatusStyling('backendStatus', false);
            updateStatusStyling('googleStatus', false);
        }
    }
    
    function updateStatusStyling(elementId, isOk) {
        const element = document.getElementById(elementId);
        element.style.color = isOk ? '#28a745' : '#dc3545';
        element.style.fontWeight = 'bold';
    }
    
    // Global reset function
    window.resetForm = function() {
        hideAllSections();
        form.reset();
        calculateBtn.disabled = false;
    };
    
    // Auto-fill test data for development
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        // Add test button for development
        const testButton = document.createElement('button');
        testButton.type = 'button';
        testButton.textContent = 'Test met Dongen';
        testButton.style.marginLeft = '10px';
        testButton.style.backgroundColor = '#6c757d';
        testButton.style.maxWidth = '150px';
        
        testButton.addEventListener('click', function() {
            document.getElementById('address').value = 'Markt 1, Dongen';
        });
        
        calculateBtn.parentNode.appendChild(testButton);
    }
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+Enter or Cmd+Enter to calculate
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            if (!calculateBtn.disabled) {
                calculateProximaScore();
            }
        }
        
        // Escape to reset
        if (e.key === 'Escape') {
            resetForm();
        }
    });
    
    // Form validation
    const addressInput = document.getElementById('address');
    addressInput.addEventListener('input', function() {
        const value = this.value.trim();
        const isValid = value.length >= 5 && value.includes(',');
        
        if (value.length > 0 && !isValid) {
            this.style.borderColor = '#ffc107';
        } else if (isValid) {
            this.style.borderColor = '#28a745';
        } else {
            this.style.borderColor = '#ddd';
        }
    });
    
    console.log('ProximaScore frontend geïnitialiseerd');
    console.log('Gebruik Ctrl+Enter om te berekenen, Escape om te resetten');
});
