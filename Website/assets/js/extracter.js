async function extractCompanyInfo() {

    const scraperData = document.getElementById('companydata').value;

    document.getElementById('companydata').value = 'Enhancing Data... Please wait.';
    

    if (!scraperData) {
        alert("Invalid scraper data provided.");
        return null;
    }

    const apiUrl = 'https://a.picoapps.xyz/ask-ai?prompt=' + encodeURIComponent(`Resume and summarize all the following text data please, The Data is : ${scraperData}`);
    
    
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
        document.getElementById('companydata').value = data.response;

    } catch (error) {
        alert("An error occurred while extracting company information. Please try again later.");
        console.error("Error extracting company info using AI:", error);
        return null;
    }
}

// async function extractCompanyInfoFromFile() {
//     const resultContainer = document.getElementById('companydata');

    
//     resultContainer.textContent += 'Adding Data... Please wait.';

//     const reader = new FileReader();
//     reader.onload = async (e) => {
//         const fileContent = e.target.result;
//         const apiUrl = 'https://a.picoapps.xyz/ask-ai?prompt=' + encodeURIComponent(`You are a Callbot, extract company information from this data: ${fileContent}`);

//         try {
//             const response = await fetch(apiUrl, {
//                 method: 'GET',
//                 headers: {
//                     'Content-Type': 'application/json'
//                 }
//             });

//             if (!response.ok) {
//                 alert(`AI API request failed with status ${response.status}`);
//                 throw new Error(`AI API request failed with status ${response.status}`);
//             }

//             const data = await response.json();
//             if (!data.response) {
//                 alert("AI failed to extract company information.");
//                 return null;
//             }
//             alert("Company information added successfully!");
//             //Append new data instead of replacing it.
//             resultContainer.textContent += data.response;


//         } catch (error) {
//             alert("An error occurred while extracting company information. Please try again later.");
//             console.error("Error extracting company info using AI:", error);
//             return null;
//         }
//     };
//     reader.readAsText(file);
// }
