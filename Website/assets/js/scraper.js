async function scrapeWebsite() {
    const companywebsite = document.getElementById('companywebsite').value;
    const resultContainer = document.getElementById('companydata');
    if (!companywebsite) {
        alert('Please enter a company website URL.');
        return;
    }
    // resultContainer.textContent = 'Scraping... Please wait.';

    try {
        // Make the API request
        const response = await fetch(`https://api-scraper-nine.vercel.app/api/scrape?url=${encodeURIComponent(companywebsite)}`);

        if (!response.ok) {
            const message = `Failed to scrape the website. Make sure the URL is correct. Status code: ${response.status}`;
            alert(message);
            throw new Error(message);
        }

        const data = await response.json();

        const parser = new DOMParser();
        const doc = parser.parseFromString(data.html, 'text/html');

        // Remove all <script> and <style> elements
        const scripts = doc.querySelectorAll('script');
        scripts.forEach(script => script.remove());

        const styles = doc.querySelectorAll('style');
        styles.forEach(style => style.remove());

        // Remove all spaces
        doc.body.innerHTML = doc.body.innerHTML.replace(/\s+/g, ' ');

        // Extract text content
        const textContent = doc.body.textContent || 'No text content found.';

        if (data.html) {
            // Display the scraped HTML in the <pre> element
            resultContainer.value += textContent;
            // alert('Website scraped successfully!');

            // const companyInfo = await extractCompanyInfo(textContent);
            // if (companyInfo) {
            //     resultContainer.textContent = companyInfo;
            //     alert('Website scraped and company information extracted successfully!');
            // } else {
            //     // resultContainer.textContent = 'No company information could be extracted.';
            //     alert('Website scraped, but no company information could be extracted.');
            // }
        } else {
            alert('No HTML found. Please try a different URL.');
            // resultContainer.textContent = 'No HTML found. Please try a different URL.';
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
        // resultContainer.textContent = `Error: ${error.message}`;
    }
}
