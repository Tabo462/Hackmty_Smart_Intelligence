// Initialize chat functionality
function initChat(chatWindow) {
    const chatBody = chatWindow.querySelector('.card-body');
    const chatInput = chatWindow.querySelector('.card-footer input');
    const chatSendButton = chatWindow.querySelector('.card-footer button');

    // Function to add a message to the chat body
    function addChatMessage(sender, message) {
        const messageElement = document.createElement('p');
        // Basic formatting - sanitize message slightly
        const cleanMessage = message.replace(/</g, "&lt;").replace(/>/g, "&gt;");
        messageElement.innerHTML = `<b>${sender}:</b> ${cleanMessage}`;
        chatBody.appendChild(messageElement);
        // Scroll to the bottom
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    // Function to handle sending a message
    async function sendMessage() {
        const userMessage = chatInput.value.trim();
        if (!userMessage) return; // Don't send empty messages

        // 1. Display user message immediately
        addChatMessage('You', userMessage);
        chatInput.value = ''; // Clear input
        chatSendButton.disabled = true; // Disable button while waiting

        // 2. Send message to backend
        try {
            const response = await fetch('http://127.0.0.1:8000/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: userMessage }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            // 3. Display assistant's reply
            addChatMessage('Assistant', data.reply);

        } catch (error) {
            console.error('Error sending chat message:', error);
            addChatMessage('System', `Sorry, error: ${error.message}`);
        } finally {
            chatSendButton.disabled = false; // Re-enable button
            chatInput.focus(); // Focus input for next message
        }
    }

    // Event listeners
    chatSendButton.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
}