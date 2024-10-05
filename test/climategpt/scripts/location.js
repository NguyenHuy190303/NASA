// Check if geolocation is supported
/*
if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(showPosition, showError);
} else {
    document.getElementById("location").innerText = "Geolocation is not supported by this browser.";
}

function showPosition(position) {
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;

    // Nominatim reverse geocoding URL
    const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=10&addressdetails=1`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            // Extract city, state, and country from the API response
            const city = data.address.city || data.address.town || data.address.village || "";
            const state = data.address.state || "";
            const country = data.address.country || "";

            // Create an array to hold non-empty parts
            const locationParts = [];

            // Only add parts to the array if they are not empty
            if (city) locationParts.push(city);
            if (state) locationParts.push(state);
            if (country) locationParts.push(country);

            // Join the parts with commas and display the final result
            const formattedLocation = locationParts.join(", ");
            document.getElementById("location").innerText = formattedLocation || "Location not available";
        })
        .catch(() => {
            document.getElementById("location").innerText = "Unable to retrieve location details.";
        });
}

function showError(error) {
    switch (error.code) {
        case error.PERMISSION_DENIED:
            document.getElementById("location").innerText = "User denied the request for Geolocation.";
            break;
        case error.POSITION_UNAVAILABLE:
            document.getElementById("location").innerText = "Location information is unavailable.";
            break;
        case error.TIMEOUT:
            document.getElementById("location").innerText = "The request to get user location timed out.";
            break;
        case error.UNKNOWN_ERROR:
            document.getElementById("location").innerText = "An unknown error occurred.";
            break;
    }
}
*/

if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(showPosition, showError);
} else {
    document.getElementById("location").innerText = "Geolocation is not supported by this browser.";
}

function showPosition(position) {
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;

    // Display location (Nominatim API)
    const locationUrl = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=10&addressdetails=1`;

    fetch(locationUrl)
        .then(response => response.json())
        .then(data => {
            const city = data.address.city || data.address.town || data.address.village || "";
            const state = data.address.state || "";
            const country = data.address.country || "";

            const locationParts = [];
            if (city) locationParts.push(city);
            if (state) locationParts.push(state);
            if (country) locationParts.push(country);

            const formattedLocation = locationParts.join(", ");
            document.getElementById("location").innerText = formattedLocation || "Location not available";

            // Now fetch weather data using Meteomatics API
            getWeather(latitude, longitude);
        })
        .catch(() => {
            document.getElementById("location").innerText = "Unable to retrieve location details.";
        });
}

// Function to fetch weather data from Meteomatics API
function getWeather(latitude, longitude) {
    const username = 'chimdindu_james';  // Replace with your Meteomatics username
    const password = '2z9Lw9O5Oq';  // Replace with your Meteomatics password
    const weatherUrl = `https://api.meteomatics.com/now/t_2m:C/${latitude},${longitude}/json`;

    fetch(weatherUrl, {
        headers: {
            'Authorization': 'Basic ' + btoa(username + ':' + password)  // Basic Auth for Meteomatics
        }
    })
        .then(response => response.json())
        .then(data => {
            const temperature = data.data[0].coordinates[0].dates[0].value;
            document.getElementById("weather").innerText = `Temperature: ${temperature}°C`;
        })
        .catch(() => {
            document.getElementById("weather").innerText = "Unable to retrieve weather data.";
        });
}

function showError(error) {
    switch (error.code) {
        case error.PERMISSION_DENIED:
            document.getElementById("location").innerText = "User denied the request for Geolocation.";
            break;
        case error.POSITION_UNAVAILABLE:
            document.getElementById("location").innerText = "Location information is unavailable.";
            break;
        case error.TIMEOUT:
            document.getElementById("location").innerText = "The request to get user location timed out.";
            break;
        case error.UNKNOWN_ERROR:
            document.getElementById("location").innerText = "An unknown error occurred.";
            break;
    }
    document.getElementById("weather").innerText = "Weather data unavailable due to location error.";
}