document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyzeGapBtn');
    const historyDropdown = document.getElementById('historyDropdown');
    const resultsContainer = document.getElementById('resultsContainer');
    let skillChartInstance = null;

    // --- Load History into Dropdown ---
    const history = JSON.parse(localStorage.getItem('resumeHistory')) || [];
    if (history.length === 0) {
        historyDropdown.innerHTML = '<option value="">No history found. Go to Resume Builder first!</option>';
        analyzeBtn.disabled = true;
    } else {
        historyDropdown.innerHTML = '';
        history.forEach(record => {
            const option = document.createElement('option');
            option.value = record.id;
            option.text = `[Score: ${record.score}%] - ${record.jobSnippet}`;
            historyDropdown.appendChild(option);
        });
    }

    // Smart Normalizer to keep scores between 0 and 10
    const normalizeScore = (val, defaultVal) => {
        let num = Number(val);
        if (isNaN(num)) return defaultVal;
        if (num > 10) return Math.min(num / 10, 10);
        return Math.max(0, num);
    };

    // --- Generate Analysis ---
    analyzeBtn.addEventListener('click', async () => {
        const selectedRecordId = historyDropdown.value;
        if (!selectedRecordId) return;

        const activeRecord = history.find(r => r.id.toString() === selectedRecordId.toString());

        analyzeBtn.innerText = "Analyzing Skill Topography... (Please wait)";
        analyzeBtn.disabled = true;

        const resumeContext = `Candidate scored ${activeRecord.score}%. Missing skills: ${activeRecord.missing.join(', ')}.`;

        const formData = new FormData();
        formData.append("resume_text", resumeContext);
        formData.append("job_desc", activeRecord.fullJobDesc);

        try {
            const response = await fetch('http://127.0.0.1:8000/api/assessment/gap', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            if (data.error) throw new Error(data.error);

            console.log("Raw AI Response:", data);

            // --- NEW: PARSE THE BOUND JSON OBJECTS ---
            let labels = [];
            let candidateData = [];
            let requiredData = [];

            if (data.skills && Array.isArray(data.skills)) {
                data.skills.forEach(skill => {
                    labels.push(skill.name || "Unknown Skill");
                    // Use actual AI numbers, default to 4/8 ONLY if the specific number is missing
                    candidateData.push(normalizeScore(skill.candidate_score || skill.current_score, 4));
                    requiredData.push(normalizeScore(skill.required_score || skill.target_score, 8));
                });
            } else {
                // Failsafe if Groq completely crashes
                labels = ["Frameworks", "Databases", "System Design", "DevOps", "Soft Skills"];
                candidateData = [4, 4, 4, 4, 4];
                requiredData = [8, 8, 8, 8, 8];
            }

            // Render Chart and UI
            resultsContainer.style.display = 'block';
            renderRadarChart(labels, candidateData, requiredData);
            renderActionPlan(data.action_plan || ["Review the missing skills listed in the Resume Builder."]);

        } catch (error) {
            console.error("Error generating gap analysis:", error);
            alert("Failed to connect to AI. Check the browser console for details.");
        } finally {
            analyzeBtn.innerText = "Generate Gap Analysis";
            analyzeBtn.disabled = false;
        }
    });

    function renderRadarChart(labels, candidateData, requiredData) {
        const ctx = document.getElementById('skillRadarChart').getContext('2d');

        if (skillChartInstance) {
            skillChartInstance.destroy();
        }

        skillChartInstance = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Your Current Skills',
                        data: candidateData,
                        backgroundColor: 'rgba(99, 102, 241, 0.4)',
                        borderColor: 'rgba(99, 102, 241, 1)',
                        pointBackgroundColor: 'rgba(99, 102, 241, 1)',
                        borderWidth: 2,
                    },
                    {
                        label: 'Job Requirement',
                        data: requiredData,
                        backgroundColor: 'rgba(34, 197, 94, 0.1)',
                        borderColor: 'rgba(34, 197, 94, 1)',
                        borderDash: [5, 5],
                        borderWidth: 2,
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                layout: {
                    // Lowered the padding so the chart can expand!
                    padding: { top: 20, bottom: 20, left: 20, right: 20 }
                },
                scales: {
                    r: {
                        min: 0,
                        max: 10,
                        angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        pointLabels: {
                            color: '#ccc',
                            font: { size: 12 } // Bumped the font size back up a bit
                        },
                        ticks: { display: false, stepSize: 2 }
                    }
                },
                plugins: {
                    legend: {
                        labels: { color: '#fff' },
                        position: 'top'
                    }
                }
            }
        });
    }

    function renderActionPlan(planArray) {
        const ul = document.getElementById('actionPlanList');
        ul.innerHTML = '';
        planArray.forEach(step => {
            const li = document.createElement('li');
            li.style.marginBottom = "10px";
            li.innerHTML = `<strong>💡 Target:</strong> ${step}`;
            ul.appendChild(li);
        });
    }
});