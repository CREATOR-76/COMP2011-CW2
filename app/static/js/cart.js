// Update the quantity input value and submit the form
function updateQuantity(button, change) {
    const input = button.parentElement.querySelector('input'); // Find the input near the button
    let newValue = parseInt(input.value) + change; // Calculate the new value
    newValue = Math.max(parseInt(input.min), Math.min(parseInt(input.max), newValue)); // Ensure value stays within min and max

    if (input.value != newValue) {
        input.value = newValue; // Update the input value
        button.closest('form').submit(); // Submit the form
    }
}

// Validate shipping address before submitting the order
function validateShippingAddress(event) {
    const address = document.getElementById('shipping_address').value.trim(); // Get and trim the address input
    if (!address) {
        event.preventDefault(); // Stop form submission
        alert('Please enter a shipping address'); // Alert the user
        return false;
    }
    return confirm('Are you sure you want to place this order?'); // Ask for confirmation
}

// Clear the cart after confirmation
function clearCart() {
    if (confirm('Are you sure you want to clear your cart?')) {
        const form = document.createElement('form'); // Create a form element
        form.method = 'POST'; // Set form method to POST
        form.action = '/cart/clear'; // Set the action URL to clear the cart
        document.body.appendChild(form); // Add the form to the page
        form.submit(); // Submit the form
    }
}

// Automatically submit the form when quantity is changed
document.querySelectorAll('input[name="quantity"]').forEach(input => {
    input.addEventListener('change', function() {
        this.closest('form').submit(); // Submit the form when quantity changes
    });
});