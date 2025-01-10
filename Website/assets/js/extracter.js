async function extractCompanyInfo(scraperData) {
    if (!scraperData) {
        alert("Invalid scraper data provided.");
        return null;
    }

    const apiUrl = 'https://a.picoapps.xyz/ask-ai?prompt=' + encodeURIComponent(`You are a Callbot, extract company information from this data: ${scraperData}`);

    try {
        const response = await fetch(apiUrl, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            alert(`AI API request failed with status ${response.status}`);
            throw new Error(`AI API request failed with status ${response.status}`);
        }

        const data = await response.json();
        if (!data.response) {
            alert("AI failed to extract company information.");
            return null;
        }
        // alert("Company information extracted successfully!"); //Added success alert
        return data.response;

    } catch (error) {
        alert("An error occurred while extracting company information. Please try again later.");
        console.error("Error extracting company info using AI:", error);
        return null;
    }
}

async function extractCompanyInfoFromFile(file) {
    const resultContainer = document.getElementById('companydata');

    if (!file) {
        alert("Invalid file provided.");
        return null;
    }

    resultContainer.textContent = 'Extracting... Please wait.';

    const reader = new FileReader();
    reader.onload = async (e) => {
        const fileContent = e.target.result;
        const apiUrl = 'https://a.picoapps.xyz/ask-ai?prompt=' + encodeURIComponent(`You are a Callbot, extract company information from this data: ${fileContent}`);

        try {
            const response = await fetch(apiUrl, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                alert(`AI API request failed with status ${response.status}`);
                throw new Error(`AI API request failed with status ${response.status}`);
            }

            const data = await response.json();
            if (!data.response) {
                alert("AI failed to extract company information.");
                return null;
            }
            alert("Company information extracted successfully!");
            // return data.response;
            resultContainer.textContent = data.response;


        } catch (error) {
            alert("An error occurred while extracting company information. Please try again later.");
            console.error("Error extracting company info using AI:", error);
            return null;
        }
    };
    reader.readAsText(file);
}
