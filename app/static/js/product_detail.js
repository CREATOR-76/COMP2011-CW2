// When the page is loaded
document.addEventListener('DOMContentLoaded', function () {
    const favoriteBtn = document.getElementById('favoriteBtn'); // Get favorite button
    if (favoriteBtn) {
        updateFavoriteButton(favoriteBtn); // Check if it's a favorite
        favoriteBtn.addEventListener('click', toggleFavorite); // Add click event
    }
});

// Check and update favorite button state
function updateFavoriteButton(btn) {
    const productId = document.getElementById('productData').getAttribute('data-product-id'); // Get product ID
    fetch(`/is_favorite/${productId}`) // Check if the product is favorite
        .then((response) => response.json())
        .then((data) => {
            if (data.is_favorite) {
                btn.classList.add('btn-danger'); // Mark as favorite
                btn.classList.remove('btn-outline-danger');
            } else {
                btn.classList.add('btn-outline-danger'); // Not favorite
                btn.classList.remove('btn-danger');
            }
        });
}

// Toggle favorite state
function toggleFavorite() {
    const productId = document.getElementById('productData').getAttribute('data-product-id'); // Get product ID
    fetch(`/favorite/${productId}`, {
        method: 'POST', // Send request to toggle favorite
        headers: {
            'Content-Type': 'application/json',
        },
    })
        .then((response) => response.json())
        .then((data) => {
            const btn = document.getElementById('favoriteBtn'); // Get button
            if (data.status === 'success') {
                if (data.is_favorite) {
                    btn.classList.add('btn-danger'); // Mark as favorite
                    btn.classList.remove('btn-outline-danger');
                } else {
                    btn.classList.add('btn-outline-danger'); // Not favorite
                    btn.classList.remove('btn-danger');
                }
            }
        });
}

// Change product quantity
function updateQuantity(change) {
    const input = document.getElementById('quantity'); // Quantity input
    const maxStock = parseInt(document.getElementById('productData').getAttribute('data-product-stock')); // Stock limit
    let newValue = parseInt(input.value) + change; // Update value
    newValue = Math.max(1, Math.min(maxStock, newValue)); // Keep within range
    input.value = newValue; // Set new value
}

// Add product to cart
function addToCart() {
    const quantity = document.getElementById('quantity').value; // Get quantity
    const productId = document.getElementById('productData').getAttribute('data-product-id'); // Get product ID

    fetch(`/cart/add/${productId}`, {
        method: 'POST', // Add to cart request
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ quantity: quantity }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.status === 'success') {
                showSuccessModal('Product added to cart!'); // Show success
            } else {
                alert('Failed to add: ' + data.message); // Show error
            }
        })
        .catch((error) => {
            console.error('Error:', error); // Log error
            alert('Something went wrong');
        });
}

// Show success popup
function showSuccessModal(message) {
    const modal = document.getElementById('successModal'); // Modal element
    const modalMessage = document.getElementById('successModalMessage'); // Modal text
    modalMessage.textContent = message; // Set message

    const bootstrapModal = new bootstrap.Modal(modal); // Create modal
    bootstrapModal.show(); // Show modal
}