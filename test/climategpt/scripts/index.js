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

    // Fetch available experiments and populate the dropdown
    async function fetchExperiments() {
        const response = await fetch('/experiments');
        const data = await response.json();
        const experimentsSelect = document.getElementById('experiments');
        data.experiments.forEach(experiment => {
            const option = document.createElement('option');
            option.value = experiment;
            option.textContent = experiment;
            experimentsSelect.appendChild(option);
        });
    }

    // Fetch data for a specific country and experiment
    async function fetchCountryData(experiment, countryCode) {
        const response = await fetch(`/country_data?experiment=${experiment}&country_code=${countryCode}`);
        const data = await response.json();
        const countryDataDiv = document.getElementById('countryData');
        if (data.error) {
            alert(data.error);
        } else {
            countryDataDiv.textContent = JSON.stringify(data.country_data, null, 2);
            return data.country_data;
        }
    }

    // Fetch GPT analysis
    async function fetchGptAnalysis(countryName, experiment, countryData, userQuestion) {
        const response = await fetch('/gpt_analysis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                country_name: countryName,
                experiment: experiment,
                country_data: countryData,
                user_question: userQuestion
            })
        });
        const data = await response.json();
        const gptAnalysisDiv = document.getElementById('gptAnalysis');
        if (data.error) {
            alert(data.error);
        } else {
            gptAnalysisDiv.textContent = data.analysis;
        }
    }

    // Event listener for fetch data button
    const fetchDataBtn = document.getElementById('fetchDataBtn');
    fetchDataBtn.addEventListener('click', async () => {
        const experimentsSelect = document.getElementById('experiments');
        const countryCodeInput = document.getElementById('countryCode');
        const userQuestionInput = document.getElementById('userQuestion');
        const experiment = experimentsSelect.value;
        const countryCode = countryCodeInput.value;
        const userQuestion = userQuestionInput.value;

        if (!experiment || !countryCode || !userQuestion) {
            alert('Please fill in all fields.');
            return;
        }

        const countryData = await fetchCountryData(experiment, countryCode);
        if (countryData) {
            await fetchGptAnalysis(countryCode, experiment, countryData, userQuestion);
        }
    });
    // Fetch GPT analysis
    async function fetchGptAnalysis(countryName, experiment, countryData, userQuestion) {
        const response = await fetch('/gpt_analysis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                country_name: countryName,
                experiment: experiment,
                country_data: countryData,
                user_question: userQuestion
            })
        });
        const data = await response.json();
        const gptAnalysisDiv = document.getElementById('gptAnalysis');
        if (data.error) {
            alert(data.error);
        } else {
            gptAnalysisDiv.innerHTML = `<h2>GPT Analysis:</h2><p>${data.analysis}</p><h3>Follow-up Questions:</h3><ul>${data.follow_up_questions.map(q => `<li>${q}</li>`).join('')}</ul>`;
        }
    }
    // Handle language change
    const languageSelector = document.querySelector('.language-selector');
    let currentLanguage = 'en'; // Default language

    languageSelector.addEventListener('change', (event) => {
        currentLanguage = event.target.value;
        updateLanguage();
    });

    // Update the text based on the selected language
    function updateLanguage() {
        const textElements = document.querySelectorAll('[data-text-key]');
        textElements.forEach(element => {
            const key = element.getAttribute('data-text-key');
            element.textContent = text[currentLanguage][key];
        });
    }

    // Initial language update
    updateLanguage();

    // Initialize the page by fetching experiments
    fetchExperiments();
});