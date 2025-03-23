function previewFingerprint(event) {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function(e) {
        const previewImage = document.getElementById('imagePreview');
        previewImage.src = e.target.result;
        previewImage.style.display = 'block';
      };
      reader.readAsDataURL(file);
    }
  }

  document.getElementById('fingerprint').addEventListener('change', previewFingerprint);

  function submitDetails() {
    const name = document.getElementById('name').value;
    const mobile = document.getElementById('mobile').value;
    const gender = document.getElementById('gender').value;
    const age = document.getElementById('age').value;
    const fingerprintInput = document.getElementById('fingerprint');
    const fingerprintFile = fingerprintInput.files[0];

    if (!name || !mobile || !gender || !age || !fingerprintFile) {
        alert("Please fill in all fields");
        return;
    }

    const formData = new FormData();
    formData.append('file', fingerprintFile);

    fetch('/predict', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert("Prediction failed: " + data.error);
            return;
        }

        const resultSection = document.getElementById('resultSection');
        const resultTableBody = document.getElementById('resultTableBody');

        resultTableBody.innerHTML = `
            <tr><td>Name</td><td>${name}</td></tr>
            <tr><td>Mobile</td><td>${mobile}</td></tr>
            <tr><td>Gender</td><td>${gender}</td></tr>
            <tr><td>Age</td><td>${age}</td></tr>
            <tr><td>Predicted Blood Group</td><td>${data.predicted_label}</td></tr>
            <tr><td>Confidence</td><td>${(data.confidence * 100).toFixed(2)}%</td></tr>
        `;

        resultSection.style.display = 'block';
    })
    .catch(error => {
        console.error('Error:', error);
        alert("An error occurred. Please try again");
    });
  }