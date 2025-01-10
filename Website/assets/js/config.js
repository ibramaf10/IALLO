async function createConfigJson() {
    const company = document.getElementById('company')?.value;
    const companywebsite = document.getElementById('companywebsite')?.value;
    const companydata = document.getElementById('companydata')?.value;
    const toEmail = document.getElementById('toEmail')?.value;
    const ccEmail = document.getElementById('ccEmail')?.value;
    const callbotname = document.getElementById('callbotname')?.value;
    const welcomemessage = document.getElementById('welcomemessage')?.value;
    const modelProvider = document.getElementById('modelProvider')?.value;
    const modelType = document.getElementById('modelType')?.value;
    const temperature = document.getElementById('temperature')?.value;
    const tokens = document.getElementById('tokens')?.value;
    const provider = document.getElementById('provider')?.value;
    const language = document.getElementById('language')?.value;
    const modelTranscriber = document.getElementById('model')?.value;
    const denoising = document.getElementById('denoising')?.checked;
    const voiceProvider = document.getElementById('voiceProvider')?.value;
    const voice = document.getElementById('voice')?.value;


    let missingFields = [];
    if (!company) missingFields.push("Company Name");
    if (!companywebsite) missingFields.push("Company Website");
    if (!companydata) missingFields.push("Company Data");
    if (!toEmail) missingFields.push("Company Email");
    if (!ccEmail) missingFields.push("CC Email");
    if (!callbotname) missingFields.push("Callbot Name");
    if (!welcomemessage) missingFields.push("Welcome Message");


    // if (missingFields.length > 0) {
    //     alert("Please fill in the following fields: " + missingFields.join(", "));
    //     return;
    // }

    const config = {
        company: company,
        companywebsite: companywebsite,
        companydata: companydata,
        companyemail: toEmail,
        companyemailcc: ccEmail,
        callbotname: callbotname,
        welcomemessage: welcomemessage,
        modelProvider: modelProvider,
        modelType: modelType,
        temperature: temperature,
        tokens: tokens,
        provider: provider,
        language: language,
        modelTranscriber: modelTranscriber,
        denoising: denoising,
        voiceProvider: voiceProvider,
        voice: voice
    };

    const jsonString = JSON.stringify(config, null, 2); // Use 2 spaces for indentation
    try {
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'config.json';
        a.click();
        URL.revokeObjectURL(url);
        alert('Config saved successfully!');
    } catch (error) {
        alert(`Failed to save config: ${error.message}`);
    }

}
