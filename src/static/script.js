// /home/ubuntu/ai_content_detector/src/static/script.js

document.addEventListener(\'DOMContentLoaded\', function() {
    const uploadForm = document.getElementById(\'upload-form\');
    const textForm = document.getElementById(\'text-form\');
    const fileInput = document.getElementById(\'file-input\');
    const ocrOptions = document.getElementById(\'ocr-options\');
    const resultsSection = document.getElementById(\'results-section\');
    const loadingIndicator = document.getElementById(\'loading-indicator\');
    const errorMessage = document.getElementById(\'error-message\');
    const analysisOutput = document.getElementById(\'analysis-output\');
    const predictionSpan = document.getElementById(\'prediction\');
    const aiProbSpan = document.getElementById(\'ai-prob\');
    const humanProbSpan = document.getElementById(\'human-prob\');
    const graphCanvas = document.getElementById(\'probability-graph\'); // Get canvas element
    const highlightedTextDiv = document.getElementById(\'highlighted-text\');

    let probabilityChart = null; // Variable to hold the chart instance

    // Show/hide OCR options based on file type
    fileInput.addEventListener(\'change\', function() {
        const fileName = fileInput.value;
        const extension = fileName.split(\'.\').pop().toLowerCase();
        if ([\'png\', \'jpg\', \'jpeg\'].includes(extension)) {
            ocrOptions.style.display = \'block\';
        } else {
            ocrOptions.style.display = \'none\';
        }
    });

    // Function to generate probability graph using Chart.js
    function generateProbabilityGraph(humanProb, aiProb) {
        const ctx = graphCanvas.getContext(\'2d\');

        // Destroy previous chart instance if it exists
        if (probabilityChart) {
            probabilityChart.destroy();
        }

        probabilityChart = new Chart(ctx, {
            type: \'bar\', // Use a bar chart
            data: {
                labels: [\'Human-Written\', \'AI-Generated\'],
                datasets: [{
                    label: \'Probability\',
                    data: [humanProb * 100, aiProb * 100], // Use percentages
                    backgroundColor: [
                        \'rgba(40, 167, 69, 0.7)\', // Success color (Human)
                        \'rgba(255, 64, 129, 0.7)\'  // Accent color (AI)
                    ],
                    borderColor: [
                        \'rgba(40, 167, 69, 1)\',
                        \'rgba(255, 64, 129, 1)\'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100, // Scale from 0 to 100%
                        ticks: {
                            callback: function(value) {
                                return value + \'%\'
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false // Hide legend as labels are clear
                    },
                    title: {
                        display: true,
                        text: \'Content Source Probability\'
                    }
                }
            }
        });
    }

    // Function to handle API response
    function handleResponse(data) {
        loadingIndicator.style.display = \'none\';
        errorMessage.style.display = \'none\';
        resultsSection.style.display = \'block\';
        analysisOutput.style.display = \'block\';

        if (data.error) {
            showError(data.error);
            // Clear previous results if error occurs
            if (probabilityChart) probabilityChart.destroy();
            graphCanvas.style.display = \'none\'; // Hide canvas on error
            highlightedTextDiv.innerHTML = \'Analysis could not be completed.\';
            highlightedTextDiv.style.display = \'none\';
        } else if (data.analysis) {
            const analysis = data.analysis;
            predictionSpan.textContent = analysis.prediction;
            predictionSpan.className = analysis.prediction.toLowerCase(); // Add class for styling
            aiProbSpan.textContent = (analysis.ai_probability * 100).toFixed(2);
            humanProbSpan.textContent = (analysis.human_probability * 100).toFixed(2);

            // Generate the probability graph
            graphCanvas.style.display = \'block\'; // Show canvas
            generateProbabilityGraph(analysis.human_probability, analysis.ai_probability);

            // Update highlighted text placeholder - Acknowledge limitation
            highlightedTextDiv.style.display = \'block\'; // Show div
            highlightedTextDiv.innerHTML = \'Note: The current model provides an overall score. Highlighting specific AI-generated sentences requires different techniques or models and is not yet implemented.\';

        } else {
            showError(\'Received unexpected response from server.\');
            if (probabilityChart) probabilityChart.destroy();
            graphCanvas.style.display = \'none\';
            highlightedTextDiv.innerHTML = \'Analysis could not be completed.\';
            highlightedTextDiv.style.display = \'none\';
        }
    }

    // Function to show errors
    function showError(message) {
        resultsSection.style.display = \'block\';
        analysisOutput.style.display = \'none\';
        errorMessage.textContent = `Error: ${message}`;
        errorMessage.style.display = \'block\';
        loadingIndicator.style.display = \'none\';
        // Ensure graph/highlight areas are hidden on error
        if (probabilityChart) probabilityChart.destroy();
        graphCanvas.style.display = \'none\';
        highlightedTextDiv.style.display = \'none\';
    }

    // Function to show loading state
    function showLoading() {
        resultsSection.style.display = \'block\';
        loadingIndicator.style.display = \'block\';
        errorMessage.style.display = \'none\';
        analysisOutput.style.display = \'none\';
        // Hide graph/highlight areas while loading
        if (probabilityChart) probabilityChart.destroy();
        graphCanvas.style.display = \'none\';
        highlightedTextDiv.style.display = \'none\';
    }

    // Handle File Upload Form Submission
    uploadForm.addEventListener(\'submit\', function(event) {
        event.preventDefault();
        showLoading();

        const formData = new FormData(uploadForm);

        fetch(\'/upload\', {
            method: \'POST\',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error || `HTTP error! status: ${response.status}`) });
            }
            return response.json();
        })
        .then(data => {
            handleResponse(data);
        })
        .catch(error => {
            console.error(\'Upload Fetch Error:\', error);
            showError(error.message || \'Could not connect to the server or process the file.\');
        });
    });

    // Handle Text Input Form Submission
    textForm.addEventListener(\'submit\', function(event) {
        event.preventDefault();
        showLoading();

        const textInput = document.getElementById(\'text-input\');
        const text = textInput.value;

        fetch(\'/analyze_text\', {
            method: \'POST\',
            headers: {
                \'Content-Type\': \'application/json\',
            },
            body: JSON.stringify({ text: text })
        })
        .then(response => {
             if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error || `HTTP error! status: ${response.status}`) });
            }
            return response.json();
        })
        .then(data => {
            handleResponse(data);
        })
        .catch(error => {
            console.error(\'Text Analysis Fetch Error:\', error);
            showError(error.message || \'Could not connect to the server or analyze the text.\');
        });
    });

});

