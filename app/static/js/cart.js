function updateQuantity(button, change) {
    const input = button.parentElement.querySelector('input');
    let newValue = parseInt(input.value) + change;
    newValue = Math.max(parseInt(input.min), Math.min(parseInt(input.max), newValue));

    if (input.value != newValue) {
        input.value = newValue;
        button.closest('form').submit();
    }
}

function validateShippingAddress(event) {
    const address = document.getElementById('shipping_address').value.trim();
    if (!address) {
        event.preventDefault();
        alert('Please enter a shipping address');
        return false;
    }
    return confirm('Are you sure you want to place this order?');
}

function clearCart() {
    if (confirm('Are you sure you want to clear your cart?')) {
        // 使用硬编码的 URL
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/cart/clear';
        document.body.appendChild(form);
        form.submit();
    }
}

document.querySelectorAll('input[name="quantity"]').forEach(input => {
    input.addEventListener('change', function() {
        this.closest('form').submit();
    });
});