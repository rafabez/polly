// Language detection and switching
function detectLanguage() {
    const savedLang = localStorage.getItem('polly-lang');
    if (savedLang) {
        return savedLang;
    }
    
    const browserLang = navigator.language || navigator.userLanguage;
    return browserLang.startsWith('pt') ? 'pt' : 'en';
}

function setLanguage(lang) {
    localStorage.setItem('polly-lang', lang);
    if (lang === 'pt') {
        document.body.classList.add('lang-pt');
    } else {
        document.body.classList.remove('lang-pt');
    }
}

function toggleLanguage() {
    const currentLang = document.body.classList.contains('lang-pt') ? 'pt' : 'en';
    const newLang = currentLang === 'pt' ? 'en' : 'pt';
    setLanguage(newLang);
}

// Initialize language on page load
document.addEventListener('DOMContentLoaded', () => {
    const lang = detectLanguage();
    setLanguage(lang);
});

// Copy code functionality
function copyCode(elementId) {
    const codeElement = document.getElementById(elementId);
    const code = codeElement.textContent;
    
    navigator.clipboard.writeText(code).then(() => {
        // Find the button that was clicked
        const button = event.target;
        const originalText = button.textContent;
        
        // Change button text temporarily
        const isPortuguese = document.body.classList.contains('lang-pt');
        button.textContent = isPortuguese ? 'COPIADO!' : 'COPIED!';
        button.style.background = '#00ff00';
        button.style.color = '#000000';
        
        // Reset after 2 seconds
        setTimeout(() => {
            button.textContent = originalText;
            button.style.background = '';
            button.style.color = '';
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy:', err);
        const isPortuguese = document.body.classList.contains('lang-pt');
        alert(isPortuguese ? 'Falha ao copiar. Por favor, copie manualmente.' : 'Failed to copy code. Please copy manually.');
    });
}

// Terminal typing effect on load
window.addEventListener('load', () => {
    const terminalBody = document.querySelector('.terminal-body code');
    if (terminalBody) {
        terminalBody.style.opacity = '0';
        setTimeout(() => {
            terminalBody.style.transition = 'opacity 0.5s';
            terminalBody.style.opacity = '1';
        }, 500);
    }
});

// Add glitch effect on hover for logo
const logo = document.querySelector('.logo');
if (logo) {
    logo.addEventListener('mouseenter', () => {
        logo.style.animation = 'glitch 0.3s';
    });
    
    logo.addEventListener('animationend', () => {
        logo.style.animation = '';
    });
}

// Add glitch animation
const style = document.createElement('style');
style.textContent = `
    @keyframes glitch {
        0% { transform: translate(0); }
        20% { transform: translate(-2px, 2px); }
        40% { transform: translate(-2px, -2px); }
        60% { transform: translate(2px, 2px); }
        80% { transform: translate(2px, -2px); }
        100% { transform: translate(0); }
    }
`;
document.head.appendChild(style);
