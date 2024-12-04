// Initialization
document.addEventListener('DOMContentLoaded', function () {
    const favoriteBtn = document.getElementById('favoriteBtn');
    if (favoriteBtn) {
        updateFavoriteButton(favoriteBtn);
        favoriteBtn.addEventListener('click', toggleFavorite);
    }
});

// Update the favorite button
function updateFavoriteButton(btn) {
    const productId = document.getElementById('productData').getAttribute('data-product-id');
    fetch(`/is_favorite/${productId}`)
        .then((response) => response.json())
        .then((data) => {
            if (data.is_favorite) {
                btn.classList.add('btn-danger');
                btn.classList.remove('btn-outline-danger');
            } else {
                btn.classList.add('btn-outline-danger');
                btn.classList.remove('btn-danger');
            }
        });
}

// Switch the state of the favorite
function toggleFavorite() {
    const productId = document.getElementById('productData').getAttribute('data-product-id');
    fetch(`/favorite/${productId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
        .then((response) => response.json())
        .then((data) => {
            const btn = document.getElementById('favoriteBtn');
            if (data.status === 'success') {
                if (data.is_favorite) {
                    btn.classList.add('btn-danger');
                    btn.classList.remove('btn-outline-danger');
                } else {
                    btn.classList.add('btn-outline-danger');
                    btn.classList.remove('btn-danger');
                }
            }
        });
}

// Update the amount
function updateQuantity(change) {
    const input = document.getElementById('quantity');
    const maxStock = parseInt(document.getElementById('productData').getAttribute('data-product-stock'));
    let newValue = parseInt(input.value) + change;
    newValue = Math.max(1, Math.min(maxStock, newValue));
    input.value = newValue;
}

// Add to cart
function addToCart() {
    const quantity = document.getElementById('quantity').value;
    const productId = document.getElementById('productData').getAttribute('data-product-id');

    fetch(`/cart/add/${productId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ quantity: quantity }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.status === 'success') {
                showSuccessModal('Product added to cart successfully!');
            } else {
                alert('Failed to add product to cart: ' + data.message);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('An unexpected error occurred while adding product to cart');
        });
}


// Show the success information
function showSuccessModal(message) {
    const modal = document.getElementById('successModal');
    const modalMessage = document.getElementById('successModalMessage');
    modalMessage.textContent = message;

    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
}
