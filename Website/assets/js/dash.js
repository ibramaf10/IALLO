// Tabs logic
const tabs = document.querySelectorAll('.tab');
const container = document.getElementById('contenaire');

const content = {
    model: `
                <h3>Model</h3>
                <div class="form-group">
                    <label for="firstMessage">First Message</label>
                    <input type="text" id="firstMessage" placeholder="Enter the first message...">
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
                    <label for="model">Model</label>
                    <select id="model">
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
                    <label for="mail">Company Email:</label>
                    <input type="text" id="toEmail" placeholder="Enter Your Company Email">
                </div>
                <div class="form-group">
                    <label for="mail">Support Email:</label>
                    <input type="text" id="ccEmail" placeholder="Enter Your Support Email">
                </div>
                <button type="button" onclick="sendEmail()">Test Email</button>`
};

// Default content for the "Model" tab
container.innerHTML = content.model;

tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelector('.tab.active').classList.remove('active');
        tab.classList.add('active');
        container.innerHTML = content[tab.id.toLowerCase()] || '<h3>Coming Soon</h3>';
    });
});
