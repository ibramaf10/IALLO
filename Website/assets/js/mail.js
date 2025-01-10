async function sendEmail() {
    const toEmail = document.getElementById('toEmail').value;
    const ccEmail = document.getElementById('ccEmail').value;
    const subject = "Test email sent by IAllo"
    const message = ">> testing the email for IAllo bot"

    try {
        const response = await fetch('https://mail-api-mounsef.vercel.app/api/send-email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                to: toEmail,
                cc: ccEmail,
                subject: subject,
                message: message,
            })
        });

        const result = await response.json();

        if (response.ok) {
            alert('Email sent successfully!');
        } else {
            alert('Failed to send email: ' + result.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}
