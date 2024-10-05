// scripts/request.js

// Function to fetch climate data from an API
async function fetchClimateData() {
    try {
        // Fetch data from the API (replace 'https://api.example.com/climate' with your actual API URL)
        const response = await fetch('https://api.example.com/climate');  // Example URL, replace with yours
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        const data = await response.json(); // Parse the JSON response

        // Update the HTML content dynamically with fetched data
        document.getElementById('weather').innerText = `${data.temperature}°C, ${data.weather_description}`;
        
        // Example of updating the search placeholder with data
        document.querySelector('.search-input').placeholder = `Current CO² Levels: ${data.co2_levels} ppm`;

    } catch (error) {
        console.error('Error fetching data:', error);
        // Handle errors by showing a fallback message
        document.getElementById('weather').innerText = 'Unable to load weather data';
    }
}

// Call the function when the page loads
window.addEventListener('DOMContentLoaded', fetchClimateData);
