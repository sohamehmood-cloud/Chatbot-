const chatbox = document.getElementById("chatbox");
const inputEl = document.getElementById("userInput");

function appendMessage(role, text, crisis = false) {
    const p = document.createElement('p');
    p.className = role === 'user' ? 'msg user' : 'msg bot';
    if (crisis) p.classList.add('crisis');
    p.innerHTML = `<strong>${role === 'user' ? 'You' : 'MindBuddy'}:</strong> ${text}`;
    chatbox.appendChild(p);
    chatbox.scrollTop = chatbox.scrollHeight;
}

async function sendMessage() {
    const input = inputEl.value.trim();
    if (!input) return;

    appendMessage('user', input);
    inputEl.value = '';

    // Typing indicator
    const typing = document.createElement('p');
    typing.className = 'msg typing';
    typing.textContent = 'MindBuddy is typing...';
    chatbox.appendChild(typing);
    chatbox.scrollTop = chatbox.scrollHeight;

    try {
        const res = await fetch(https:"//chatbot-xz9t.onrender.com", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: input })
        });

        const data = await res.json();
        typing.remove();
        appendMessage('bot', data.answer, data.crisis === true);
    } catch (err) {
        typing.remove();
        appendMessage('bot', 'Sorry, there was a problem connecting to the server.');
    }
}

// Allow Enter to send
inputEl.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});
