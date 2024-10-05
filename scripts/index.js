document.addEventListener('DOMContentLoaded', function() {
    const videos = document.querySelectorAll('.video-background');
    const dots = document.querySelectorAll('.video-dot');
    let currentVideoIndex = 0;
    const videoCount = videos.length;
    let intervalId;

    // Function to switch videos
    function switchVideo(index) {
        // Remove active class from all videos and dots
        videos.forEach(video => video.classList.remove('active'));
        dots.forEach(dot => dot.classList.remove('active'));
        
        // Add active class to current video and dot
        videos[index].classList.add('active');
        dots[index].classList.add('active');
        
        // Ensure the current video is playing
        videos[index].play();
    }

    // Function to cycle to next video
    function nextVideo() {
        currentVideoIndex = (currentVideoIndex + 1) % videoCount;
        switchVideo(currentVideoIndex);
    }

    // Set up click handlers for dots
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            currentVideoIndex = index;
            switchVideo(currentVideoIndex);
            
            // Reset the interval
            clearInterval(intervalId);
            intervalId = setInterval(nextVideo, 8000);
        });
    });

    // Start the automatic cycling
    intervalId = setInterval(nextVideo, 8000);

    // Search functionality
    const searchInput = document.querySelector('.search-input');
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            console.log('Search query:', this.value);
        }
    });

    // Step 1: Get user's location
    function getUserLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(successCallback, errorCallback);
    } else {
        document.getElementById('weather').textContent = "Geolocation is not supported by this browser.";
        }
    }

    // Step 2: Success callback for geolocation
    function successCallback(position) {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        fetchWeatherData(lat, lon); // Call the function to fetch weather data
    }

    // Step 3: Error callback for geolocation
    function errorCallback(error) {
        document.getElementById('weather').textContent = `Error fetching location: ${error.message}`;
    }

    // Step 4: Fetch weather data using your proxy
    function fetchWeatherData(lat, lon) {
        const proxyUrl = `http://localhost:3000/weather?lat=${lat}&lon=${lon}`; // Point to your proxy

        fetch(proxyUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                const temp = data.data[0].coordinates[0].dates[0].value; // Adjust this based on API response structure
                document.getElementById('weather').textContent = `Current Temperature: ${temp}°C`;
            })
            .catch(error => {
                document.getElementById('weather').textContent = `Error fetching weather data: ${error.message}`;
            });
    }

    // Step 5: Trigger the location fetch on page load
    window.onload = getUserLocation;
});