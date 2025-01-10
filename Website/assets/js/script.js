


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
