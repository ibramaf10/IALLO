// Tabs logic
const tabs = document.querySelectorAll('.tab');
const container = document.getElementById('contenaire');

const content = {
    model: `
                <h3>Model</h3>
                <div class="form-group">
                    <label for="callbotname">Callbot Name</label>
                    <input type="text" id="callbotname" placeholder="Enter Callbot Name.">
                </div>
                <div class="form-group">
                    <label for="welcomemessage">First Message</label>
                    <input type="text" id="welcomemessage" placeholder="Enter the first message...">
                </div>
                <div class="form-group">
                    <label for="systemPrompt">System Prompt</label>
                    <textarea id="systemPrompt" rows="3" placeholder="Enter the system prompt..."></textarea>
                </div>
                <div class="form-group">
                    <label for="modelProvider">Provider</label>
                    <select id="modelProvider">
                        <option value="openai">OpenAI</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="modelType">Model</label>
                    <select id="modelType">
                        <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                        <option value="gpt-4">GPT-4</option>
                    </select>
                </div>
                <div class="sliders">
                    <div class="slider">
                        <label for="temperature">Temperature</label>
                        <input type="range" id="temperature" min="0" max="1" step="0.1" value="0.7">
                    </div>
                    <div class="slider">
                        <label for="tokens">Max Tokens</label>
                        <input type="range" id="tokens" min="100" max="1000" step="50" value="250">
                    </div>
                </div>
            `,
    transcriber: `
                <h3>Transcription</h3>
                <div class="form-group">
                    <label for="provider">Provider</label>
                    <select id="provider">
                        <option value="deepgram">Deepgram</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="language">Language</label>
                    <input type="text" id="language" value="en" placeholder="Enter language...">
                </div>
                <div class="pro-tip">
                    Pro tip: If you want to support both English and Spanish, you can set the language to multi and use ElevenLabs Turbo 2.5 in the Voice tab.
                </div>
                <div class="form-group">
                    <label for="modelTranscriber">Model</label>
                    <select id="modelTranscriber">
                        <option value="nova2">Nova 2</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                <div class="toggle">
                    <input type="checkbox" id="denoising" checked>
                    <label for="denoising">Background Denoising Enabled</label>
                </div>
            `,
    voice: `
                <h3>Voice</h3>
                <div class="form-group">
                    <label for="voiceProvider">Provider</label>
                    <select id="voiceProvider">
                        <option value="elevenlabs">ElevenLabs</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="voice">Voice</label>
                    <select id="voice">
                        <option value="New York Man">New York Man</option>
                        <option value="Wise Men">Wise Men</option>
                        <option value="other">Other</option>
                    </select>
                </div>`,
    functions: `          
                <h3>Functions</h3>
                <div class="form-group">
                    <label for="toEmail">Company Email:</label>
                    <input type="text" id="toEmail" placeholder="Enter Your Company Email">
                </div>
                <div class="form-group">
                    <label for="ccEmail">Support Email:</label>
                    <input type="text" id="ccEmail" placeholder="Enter Your Support Email">
                </div>
                <button type="submit" onclick="sendEmail()">Test Email</button>`,
    data: `
                <h3>Data</h3>
                <div class="form-group">
                    <label for="company">Company Name:</label>
                    <input type="text" id="company" placeholder="Enter Your Company Name">
                </div>
                <div class="form-group">
                    <label for="companywebsite">Company WebSite URL:</label>
                    <input type="text" id="companywebsite" placeholder="https://example.com">
                    <button type="submit" onclick="scrapeWebsite()">Scrape Company data</button>
                </div>
                <div class="form-group">
                    <label for="companydata">Company Data:</label>
                    <textarea rows="5" id="companydata" placeholder="Or Enter it manually..."></textarea>
                </div>
                <div class="form-group">
                    <label for="companydatafile">Upload Company Data:</label>
                    <input type="file" id="companydatafile" accept=".json,.txt,.csv">
                    <button type="button" onclick="extractCompanyInfoFromFile(document.getElementById('companydatafile').files[0])">Extract Company Info from File</button>
                </div>`
};

function saveFormData() {
    const formData = {};
    const inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        formData[input.id] = input.value;
    });
    const fileInput = document.getElementById('companydatafile');
    if (fileInput && fileInput.files.length > 0) {
        formData[fileInput.id] = fileInput.files[0].name; // Store filename for reference
    }
    return formData;
}

// Default content for the "Model" tab
container.innerHTML = content.model;

tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        sessionStorage.setItem('formData', JSON.stringify(saveFormData())); // Save data before switching tabs
        document.querySelector('.tab.active').classList.remove('active');
        tab.classList.add('active');
        container.innerHTML = content[tab.id.toLowerCase()] || '<h3>Coming Soon</h3>';
    });
});

// Add event listeners to all input elements to save to sessionStorage on change
const allInputs = document.querySelectorAll('input, select, textarea, file');
allInputs.forEach(input => {
    input.addEventListener('change', () => {
        sessionStorage.setItem('formData', JSON.stringify(saveFormData()));
    });
});


// Load data from session storage on page load
window.addEventListener('load', () => {
    const storedData = sessionStorage.getItem('formData');
    if (storedData) {
        const formData = JSON.parse(storedData);
        for (const key in formData) {
            const element = document.getElementById(key);
            if (element) {
                if (key === 'companydatafile') {
                    // Handle file upload -  This part would need further implementation to actually handle the file upload.
                    // For now, it just displays the filename.
                    console.log("File to upload:", formData[key]);
                } else {
                    element.value = formData[key];
                }
            }
        }
    }
});
