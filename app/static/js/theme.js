// Theme management for DelightMate
document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const moonIcon = document.querySelector('.moon-icon');
    const sunIcons = document.querySelectorAll('.sun-icon');
    
    // Initialize theme from localStorage
    initTheme();
    
    // Theme toggle handler
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            toggleTheme();
        });
    }
    
    // Initialize theme
    function initTheme() {
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
        document.body.style.backgroundColor = 'var(--bg-color)';
        document.body.style.color = 'var(--text-color)';
        updateThemeIcon(savedTheme);
    }
    
    // Toggle between light and dark themes
    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        document.body.style.backgroundColor = 'var(--bg-color)';
        document.body.style.color = 'var(--text-color)';
        localStorage.setItem('theme', newTheme);
        
        updateThemeIcon(newTheme);
    }
    
    // Update theme icon based on current theme
    function updateThemeIcon(theme) {
        if (!moonIcon || !sunIcons.length) return;
        
        if (theme === 'dark') {
            moonIcon.style.display = 'block';
            sunIcons.forEach(icon => icon.style.display = 'none');
        } else {
            moonIcon.style.display = 'none';
            sunIcons.forEach(icon => icon.style.display = 'block');
        }
    }
});
