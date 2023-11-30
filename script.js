document.getElementById('courseForm').addEventListener('submit', function(e) {
    e.preventDefault();  // Prevents the default form submission (which is a GET request)

    // Collecting form data
    let specialization = document.getElementById('specialization').value;
    let coursesTaken = document.getElementById('coursesTaken').value.split(',');
    let semestersLeft = document.getElementById('semestersLeft').value;
    let numCoursesRequired = document.getElementById('numCoursesRequired').value;

    const postData = {
        specialization: specialization,
        coursesTaken: coursesTaken,
        semestersLeft: semestersLeft,
        numCoursesRequired: numCoursesRequired
    };

    // Sending a POST request to Flask
    fetch('http://127.0.0.1:5000/generate_schedule', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
    })
    .catch(error => console.error('Error:', error));
});
