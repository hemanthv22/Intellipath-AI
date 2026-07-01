document.addEventListener('DOMContentLoaded', () => {
    const chatWindow = document.getElementById('chatWindow');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');

    // This array stores the history so the AI remembers context!
    let conversationHistory = [];

    // Helper to add messages to the UI
    function appendMessage(role, text) {
        const div = document.createElement('div');
        div.className = `message-bubble ${role === 'user' ? 'user-message' : 'ai-message'}`;

        // Convert basic markdown (newlines) to HTML breaks for better readability
        div.innerHTML = text.replace(/\n/g, '<br>');

        chatWindow.appendChild(div);

        // Auto-scroll to bottom
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        // 1. Show user message
        appendMessage('user', text);
        chatInput.value = '';
        chatInput.disabled = true;
        sendBtn.disabled = true;
        loadingIndicator.style.display = 'block';

        // 2. Prepare data to send
        const formData = new FormData();
        formData.append("message", text);
        formData.append("history_json", JSON.stringify(conversationHistory));

        try {
            // 3. Call Backend
            const response = await fetch('http://127.0.0.1:8000/api/assistant/chat', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            if (data.error) throw new Error(data.error);

            // 4. Update History arrays for the NEXT request
            conversationHistory.push({ role: "user", content: text });
            conversationHistory.push({ role: "assistant", content: data.reply });

            // 5. Show AI message
            appendMessage('ai', data.reply);

        } catch (error) {
            console.error("Chat Error:", error);
            appendMessage('ai', "⚠️ *Sorry, I am having trouble connecting to the server right now. Please try again later.*");
        } finally {
            chatInput.disabled = false;
            sendBtn.disabled = false;
            loadingIndicator.style.display = 'none';
            chatInput.focus();
        }
    }

    // Event Listeners
    sendBtn.addEventListener('click', sendMessage);

    // Allow pressing "Enter" to send
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});