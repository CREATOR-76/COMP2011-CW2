// Check if the new user's passport legal
document.querySelector('#change-password-form').addEventListener('submit', function (e) {
    const newPassword = document.getElementById('new_password').value;
    const confirmPassword = document.getElementById('confirm_password').value;

    if (newPassword.length < 6) {
        e.preventDefault();
        alert('New password must be at least 6 characters long');
        return;
    }

    if (newPassword !== confirmPassword) {
        e.preventDefault();
        alert('New passwords do not match');
        return;
    }
});