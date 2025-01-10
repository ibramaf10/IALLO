async function scrapeWebsite() {
    const url = document.getElementById('url').value;
    const resultContainer = document.getElementById('companydata');
    resultContainer.textContent = 'Scraping... Please wait.';

    try {
        // Make the API request
        const response = await fetch(`https://api-scraper-nine.vercel.app/api/scrape?url=${encodeURIComponent(url)}`);

        if (!response.ok) {
            throw new Error('Failed to scrape the website. Make sure the URL is correct.');
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
            resultContainer.textContent = textContent;
        } else {
            resultContainer.textContent = 'No HTML found. Please try a different URL.';
        }
    } catch (error) {
        resultContainer.textContent = `Error: ${error.message}`;
    }
}
