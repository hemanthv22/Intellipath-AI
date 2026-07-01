document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('resumeForm');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultsSection = document.getElementById('resultsSection');
    const historyContainer = document.getElementById('historyContainer');

    // Load history on page load
    loadHistory();

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const resumeFile = document.getElementById('resumeUpload').files[0];
        const jobDesc = document.getElementById('jobDescription').value;

        if (!resumeFile || !jobDesc) {
            alert("Please upload a PDF and paste a job description.");
            return;
        }

        analyzeBtn.innerText = "Analyzing... (Please wait)";
        analyzeBtn.disabled = true;

        const formData = new FormData();
        formData.append("file", resumeFile);
        formData.append("job_description", jobDesc);

        try {
            // Call your backend API
            const response = await fetch('http://127.0.0.1:8000/api/resume/analyze', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error("API request failed");

            const data = await response.json();

            // 1. Display Current Results
            document.getElementById('scoreDisplay').innerText = `${data.score}%`;
            document.getElementById('missingKeywords').innerText = data.missing.join(", ");

            const suggestionsList = document.getElementById('aiSuggestions');
            suggestionsList.innerHTML = "";
            data.suggestions.forEach(s => {
                const li = document.createElement('li');
                li.innerText = s;
                suggestionsList.appendChild(li);
            });

            resultsSection.style.display = 'block';

            // 2. Save to History
            saveToHistory(jobDesc, data);

        } catch (error) {
            console.error("Analysis Error:", error);
            alert("Failed to analyze resume. Make sure your backend is running!");
        } finally {
            analyzeBtn.innerText = "Analyze with AI";
            analyzeBtn.disabled = false;
        }
    });

    function saveToHistory(jobDesc, analysisData) {
        // Grab existing history from LocalStorage or create empty array
        let history = JSON.parse(localStorage.getItem('resumeHistory')) || [];

        // Create a new record
        const newRecord = {
            id: Date.now(),
            date: new Date().toLocaleDateString() + " " + new Date().toLocaleTimeString(),
            jobSnippet: jobDesc.substring(0, 50) + "...", // Save a snippet of the JD for the title
            fullJobDesc: jobDesc,
            score: analysisData.score,
            missing: analysisData.missing,
            suggestions: analysisData.suggestions
        };

        // Add to beginning of array (newest first)
        history.unshift(newRecord);

        // Save back to local storage
        localStorage.setItem('resumeHistory', JSON.stringify(history));

        // Re-render the history UI
        loadHistory();
    }

    function loadHistory() {
        const history = JSON.parse(localStorage.getItem('resumeHistory')) || [];

        if (history.length === 0) return; // Keep default "No history" text

        historyContainer.innerHTML = ""; // Clear container

        history.forEach(record => {
            const card = document.createElement('div');
            card.className = "glass-card";
            card.style.padding = "15px";
            card.style.display = "flex";
            card.style.justifyContent = "space-between";
            card.style.alignItems = "center";

            card.innerHTML = `
                <div>
                    <h4 style="margin-bottom: 5px; color: var(--primary-glow);">Score: ${record.score}%</h4>
                    <p style="font-size: 0.9rem; color: #ccc;">${record.jobSnippet}</p>
                    <small style="color: var(--text-muted);">${record.date}</small>
                </div>
                <div style="display: flex; gap: 10px;">
                    <button class="btn-primary" style="padding: 5px 15px; width: auto;" onclick="viewHistory(${record.id})">View</button>
                    <button class="btn-primary" style="padding: 5px 15px; width: auto; background: var(--success); border-color: var(--success);" onclick="startInterviewWith(${record.id})">Interview</button>
                </div>
            `;
            historyContainer.appendChild(card);
        });
    }

    // Expose a function to view past results
    // Update the viewHistory function to use the Modal
    window.viewHistory = function (id) {
        const history = JSON.parse(localStorage.getItem('resumeHistory')) || [];
        const record = history.find(r => r.id === id);

        if (record) {
            // Populate Modal Data
            document.getElementById('modalScore').innerText = `${record.score}%`;
            document.getElementById('modalJob').innerText = record.fullJobDesc.substring(0, 150) + "...";
            document.getElementById('modalMissing').innerText = record.missing.join(", ") || "None!";

            const suggestionsList = document.getElementById('modalSuggestions');
            suggestionsList.innerHTML = "";
            record.suggestions.forEach(s => {
                const li = document.createElement('li');
                li.innerText = s;
                suggestionsList.appendChild(li);
            });

            // Show the Modal
            document.getElementById('historyModal').style.display = 'flex';
        }
    }

    // Add function to close the modal
    window.closeModal = function () {
        document.getElementById('historyModal').style.display = 'none';
    }
    // Saves the selected ID and redirects to the Interview page
    window.startInterviewWith = function (id) {
        localStorage.setItem('selectedInterviewId', id);
        window.location.href = 'interview.html';
    }
});