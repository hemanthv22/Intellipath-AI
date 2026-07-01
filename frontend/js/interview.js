document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('startInterviewBtn');
    const submitBtn = document.getElementById('submitAnswerBtn');
    const nextBtn = document.getElementById('nextBtn');
    const mcqContainer = document.getElementById('mcqContainer');
    const historyDropdown = document.getElementById('historyDropdown');

    // --- State Variables for the Quiz ---
    let quizData = [];
    let currentIndex = 0;
    let currentScore = 0;
    let selectedAnswer = "";

    // --- Load History into Dropdown ---
    const history = JSON.parse(localStorage.getItem('resumeHistory')) || [];
    if (history.length === 0) {
        historyDropdown.innerHTML = '<option value="">No history found. Go to Resume Builder first!</option>';
        startBtn.disabled = true;
    } else {
        historyDropdown.innerHTML = '';
        history.forEach(record => {
            const option = document.createElement('option');
            option.value = record.id;
            option.text = `[Score: ${record.score}%] - ${record.jobSnippet}`;
            historyDropdown.appendChild(option);
        });
        const selectedId = localStorage.getItem('selectedInterviewId');
        if (selectedId) {
            historyDropdown.value = selectedId;
            localStorage.removeItem('selectedInterviewId');
        }
    }

    // --- 1. Start the Interview & Fetch 5 Questions ---
    startBtn.addEventListener('click', async () => {
        const selectedRecordId = historyDropdown.value;
        if (!selectedRecordId) return;

        const activeRecord = history.find(r => r.id.toString() === selectedRecordId.toString());

        startBtn.innerText = "Generating 5 Questions... (This takes a few seconds)";
        startBtn.disabled = true;

        const resumeContext = `Candidate scored ${activeRecord.score}%. Missing skills: ${activeRecord.missing.join(', ')}.`;
        const formData = new FormData();
        formData.append("resume_text", resumeContext);
        formData.append("job_desc", activeRecord.fullJobDesc);

        try {
            const response = await fetch('http://127.0.0.1:8000/api/interview/generate', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            if (data.error) throw new Error(data.error);

            quizData = data.questions; // Save the 5 questions
            currentIndex = 0;
            currentScore = 0;

            // Switch UI
            document.getElementById('setupSection').style.display = 'none';
            document.getElementById('chatSection').style.display = 'flex';

            loadQuestion(); // Load the first question

        } catch (error) {
            console.error("Error generating question:", error);
            alert("Failed to connect to the AI.");
            startBtn.innerText = "Start Interview";
            startBtn.disabled = false;
        }
    });

    // --- 2. Load a Question into the UI ---
    function loadQuestion() {
        const q = quizData[currentIndex];
        selectedAnswer = ""; // Reset choice

        // Update Counters
        document.getElementById('questionCounter').innerText = `Question ${currentIndex + 1} of ${quizData.length}`;
        document.getElementById('scoreDisplay').innerText = `Score: ${currentScore}`;

        // Reset UI Elements
        document.getElementById('questionText').innerText = q.question;
        document.getElementById('feedbackBox').style.display = 'none';
        submitBtn.style.display = 'block';
        submitBtn.disabled = false;
        nextBtn.style.display = 'none';

        // Render Options
        mcqContainer.innerHTML = "";
        q.options.forEach(optionText => {
            const btn = document.createElement('button');
            btn.className = 'mcq-option';
            btn.innerText = optionText;

            btn.onclick = () => {
                if (submitBtn.disabled) return; // Prevent changing answer after submit
                document.querySelectorAll('.mcq-option').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
                selectedAnswer = optionText;
            };
            mcqContainer.appendChild(btn);
        });
    }

    // --- 3. Grade the Answer (Instant Offline Grading!) ---
    submitBtn.addEventListener('click', () => {
        if (!selectedAnswer) {
            alert("Please select an option first!");
            return;
        }

        const q = quizData[currentIndex];
        const isCorrect = selectedAnswer === q.correct_answer;

        if (isCorrect) currentScore++;

        const scoreColor = isCorrect ? "var(--success)" : "var(--danger)";
        const resultText = isCorrect ? "Correct! 🎯" : "Incorrect ❌";

        // Highlight correct and wrong answers on the buttons
        document.querySelectorAll('.mcq-option').forEach(btn => {
            if (btn.innerText === q.correct_answer) {
                btn.style.borderColor = "var(--success)";
                btn.style.background = "rgba(34, 197, 94, 0.2)";
            } else if (btn.innerText === selectedAnswer && !isCorrect) {
                btn.style.borderColor = "var(--danger)";
                btn.style.background = "rgba(239, 68, 68, 0.2)";
            }
        });

        // Show Feedback
        const feedbackBox = document.getElementById('feedbackBox');
        feedbackBox.style.display = 'block';
        feedbackBox.style.borderLeftColor = scoreColor;

        document.getElementById('feedbackText').innerHTML = `
            <strong style="font-size: 1.2rem; color: ${scoreColor};">${resultText}</strong><br>
            <strong style="color: #fff; margin-top: 10px; display: block;">Correct Answer:</strong> ${q.correct_answer}<br><br>
            <span style="color: #ccc;">${q.explanation}</span>
        `;

        // Swap Buttons
        submitBtn.style.display = 'none';
        nextBtn.style.display = 'block';

        // Change text on the last question
        if (currentIndex === quizData.length - 1) {
            nextBtn.innerText = "Finish Interview";
        }
    });

    // --- 4. Next Question Logic ---
    nextBtn.addEventListener('click', () => {
        currentIndex++;
        if (currentIndex < quizData.length) {
            loadQuestion();
        } else {
            // Show Final Screen
            document.getElementById('chatSection').style.display = 'none';
            document.getElementById('finalResultsSection').style.display = 'block';
            document.getElementById('finalScoreText').innerText = `${currentScore} / ${quizData.length}`;

            // Fun color logic for final score
            const finalScoreObj = document.getElementById('finalScoreText');
            if (currentScore >= 4) finalScoreObj.style.color = "var(--success)";
            else if (currentScore >= 3) finalScoreObj.style.color = "orange";
            else finalScoreObj.style.color = "var(--danger)";
        }
    });
});