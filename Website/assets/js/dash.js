function switchTab(tabElement, templateId) {
    // Update tab styles
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    tabElement.classList.add('active');
    
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.style.display = 'none';
    });

    // Show the selected tab content
    document.getElementById(templateId).style.display = 'block';
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Show initial tab (Model)
    const modelTab = document.getElementById('model');
    switchTab(modelTab, 'modelContent');
});