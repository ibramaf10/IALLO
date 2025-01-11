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
document.addEventListener('DOMContentLoaded', function () {
    // Show initial tab (Model)
    const modelTab = document.getElementById('model');
    switchTab(modelTab, 'modelContent');
});

const temperatureSlider = document.getElementById('temperature');
const temperatureValue = document.getElementById('temperatureValue');
temperatureSlider.addEventListener('input', () => {
    temperatureValue.textContent = temperatureSlider.value;
});

const tokensSlider = document.getElementById('tokens');
const tokensValue = document.getElementById('tokensValue');
tokensSlider.addEventListener('input', () => {
    tokensValue.textContent = tokensSlider.value;
});

async function updateModelOptions(provider) {
    const modelTypeSelect = document.getElementById('modelType');
    modelTypeSelect.innerHTML = ''; // Clear previous options

    if (provider === 'openai') {
        modelTypeSelect.innerHTML = `
            <option value="gpt-3.5-turbo">gpt-3.5-turbo</option>
            <option value="gpt-4">gpt-4</option>
            <option value="other">Other</option>
        `;
    } else if (provider === 'google') {
        modelTypeSelect.innerHTML = `
            <option value="gemini-1.5-flash">gemini-1.5-flash</option>
            <option value="gemini-pro">gemini-pro</option>
            <option value="other">Other</option>
        `;
    } else if (provider === 'anthropic') {
        modelTypeSelect.innerHTML = `
            <option value="claude-3-opus">claude-3-opus</option>
            <option value="claude-3.5-sonnet">claude-3.5-sonnet</option>
            <option value="other">Other</option>
        `;
    } else {
        modelTypeSelect.innerHTML = `
            <option value="other">Other</option>
        `;
    }
}
