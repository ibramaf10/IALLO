


// Newsletter form submission
document.getElementById('newsletterForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const email = this.querySelector('input[type="email"]').value;

    // Here you would typically send the email to your server
    // For demo purposes, we'll just show an alert
    alert('Thank you for subscribing! You will receive our updates at: ' + email);

    // Reset form
    this.reset();
});

// Smooth scroll for footer links
document.querySelectorAll('.footer-links a').forEach(link => {
    link.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href === '#') {
            e.preventDefault();
        }
    });
});







// Form submission handling
document.getElementById('contactForm').addEventListener('submit', function (e) {
    e.preventDefault();

    // Here you would typically send the form data to your server
    // For demo purposes, we'll just show the success message
    const successMessage = document.getElementById('successMessage');
    successMessage.style.display = 'block';

    // Reset form
    this.reset();

    // Hide success message after 5 seconds
    setTimeout(() => {
        successMessage.style.display = 'none';
    }, 5000);
});

// Pricing button click handling
document.querySelectorAll('.plan-button').forEach(button => {
    button.addEventListener('click', function () {
        const planName = this.closest('.pricing-card').querySelector('.plan-name').textContent;
        if (planName === 'Enterprise') {
            // Scroll to contact form
            document.querySelector('.contact-section').scrollIntoView({
                behavior: 'smooth'
            });
        } else {
            // Here you would typically handle the subscription process
            alert(`Thank you for choosing the ${planName} plan! We'll redirect you to the payment page.`);
        }
    });
});








let isProcessing = false;
let peerConnection;
let dataChannel;

document.getElementById('mic-icon').addEventListener('click', function () {
    if (isProcessing) {
        // Stop the process

        if (peerConnection) {
            peerConnection.close();
            peerConnection = null;
        }
        const audioContainer = document.getElementById('audio-container');
        audioContainer.innerHTML = ''; // Clear audio elements
        isProcessing = false;
        navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
            stream.getTracks().forEach((track) => track.stop());
        });
        console.log('Process stopped');

        document.getElementById('mic-icon').innerHTML = `  <svg xmlns="http://www.w3.org/2000/svg" width="144px" height="144px" viewBox="-1.6 -1.6 19.20 19.20" fill="none" stroke="#000000" stroke-width="0.368" transform="rotate(0)">
                <g id="SVGRepo_bgCarrier" stroke-width="0"/>
                <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round" stroke="#CCCCCC" stroke-width="0.032"/>
                <g id="SVGRepo_iconCarrier"> 
                    <path d="M5 3C5 1.34315 6.34315 0 8 0C9.65685 0 11 1.34315 11 3V7C11 8.65685 9.65685 10 8 10C6.34315 10 5 8.65685 5 7V3Z" fill="#ffffff"/> 
                    <path d="M9 13.9291V16H7V13.9291C3.60771 13.4439 1 10.5265 1 7V6H3V7C3 9.76142 5.23858 12 8 12C10.7614 12 13 9.76142 13 7V6H15V7C15 10.5265 12.3923 13.4439 9 13.9291Z" fill="#ffffff"/> 
                </g>
        </svg> `;

    } else {

        // Start the process

        document.getElementById('mic-icon').innerHTML = `<svg width="96px" height="96px" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" stroke="#000000" stroke-width="0.20800000000000002"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <rect x="1" y="1" width="14" height="14" fill="#ffffff"></rect> </g></svg>`;
        peerConnection = new RTCPeerConnection();
        const audioContainer = document.getElementById('audio-container');

        // Handle incoming audio tracks
        peerConnection.ontrack = (event) => {
            const audioElement = document.createElement('audio');
            audioElement.srcObject = event.streams[0];
            audioElement.autoplay = true;
            audioContainer.appendChild(audioElement);
        };

        // Handle incoming messages
        dataChannel = peerConnection.createDataChannel('response');

        dataChannel.addEventListener('message', (event) => {
            const msg = JSON.parse(event.data);
            console.log(msg.delta);
        });

        // Get user audio and set up WebRTC
        navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
            stream.getTracks().forEach((track) => {
                peerConnection.addTransceiver(track, { direction: 'sendrecv' });
            });

            peerConnection.createOffer().then((offer) => {
                peerConnection.setLocalDescription(offer);


                function rot13Encrypt(inputString) {
                    var result = '';
                    for (var i = 0; i < inputString.length; i++) {
                        var charCode = inputString.charCodeAt(i);

                        if (65 <= charCode && charCode <= 90) {
                            result += String.fromCharCode(((charCode - 65 + 13) % 26) + 65);
                        }

                        else if (97 <= charCode && charCode <= 122) {
                            result += String.fromCharCode(((charCode - 97 + 13) % 26) + 97);
                        }

                        else {
                            result += inputString.charAt(i);
                        }
                    }
                    return result;
                }

                // Mimic the backend logic
                const processRTCConnection = async (offerSDP) => {
                    const DEFAULT_INSTRUCTIONS = "";
                    const url = new URL('https://api.openai.com/v1/realtime');
                    url.searchParams.set('model', 'gpt-4o-realtime-preview-2024-12-17');
                    url.searchParams.set('instructions', DEFAULT_INSTRUCTIONS);
                    url.searchParams.set('voice', 'ash');

                    const response = await fetch(url.toString(), {
                        method: 'POST',
                        body: offerSDP,
                        headers: {
                            Authorization: `Bearer ${rot13Encrypt('fx-cebw-CNUMjW3DC35SiVNtzXyxouNekO5Hz1BGegD6K2BDwOLlZkrEvC-saNwHYCDnbanMJjcUCnH-mNG3OyoxSWy7xUjIuOjMz73appCJxgL7nKPSFNql8JyDJReK-puqFGR9V6OWKWWsNdHdxcnqx1MfQHWjnjxN')}`,
                            'Content-Type': 'application/sdp',
                        },
                    });

                    if (!response.ok) {
                        throw new Error(`OpenAI API error: ${response.status}`);
                    }
                    return response.text();
                };

                processRTCConnection(offer.sdp)
                    .then((answer) => {
                        peerConnection.setRemoteDescription({
                            sdp: answer,
                            type: 'answer',
                        });
                    })
                    .catch((error) => console.error('Error connecting to API:', error));
            });
        }).catch((error) => {
            console.error('Error accessing microphone:', error);
        });

        isProcessing = true;
        console.log('Process started');
    }
});








 let lastScrollTop = 0;

  window.addEventListener('scroll', function () {
            const navbar = document.getElementById('navbar');
            let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            if (scrollTop > lastScrollTop) {
                navbar.style.top = '-100px'; // Adjust this value based on your navbar height
            } else {
                navbar.style.top = '0';
            }
            lastScrollTop = scrollTop;
        });