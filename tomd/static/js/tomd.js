// Date formatting utility (from Nuxt frontend)
function datify(dateString) {
    if (dateString && dateString.length) {
        var d = new Date(Date.parse(dateString));
        var options = { year: "numeric", month: "long", day: "numeric" };
        return d.toLocaleDateString("en-us", options);
    }
    return dateString;
}

// Format dates on page load
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.date-format').forEach(function(el) {
        el.textContent = datify(el.dataset.date);
    });

    trackStripeLinks();

    // Watch for dynamically added content
    const observer = new MutationObserver(trackStripeLinks);
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});

// Track Stripe checkout links with Umami (from Nuxt frontend)
function trackStripeLinks() {
    const stripeLinks = document.querySelectorAll('a[href*="book.stripe.com"]');

    stripeLinks.forEach(link => {
        if (link.dataset.umamiTracked) return;

        link.addEventListener('click', () => {
            if (window.umami) {
                window.umami.track('Stripe Checkout Click');
            }
        });

        link.dataset.umamiTracked = 'true';
    });
}
