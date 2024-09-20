function sendMessage() {
    const userInput = document.getElementById("user-input").value;
    if (userInput.trim() === "") return;

    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML += `<p><strong>Vous:</strong> ${userInput}</p>`;

    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: userInput }),
    })
    .then(response => response.json())
    .then(data => {
        const botResponse = data.response;
        chatBox.innerHTML += `<p><strong>Chatbot:</strong> ${botResponse}</p>`;
        document.getElementById("user-input").value = "";
        chatBox.scrollTop = chatBox.scrollHeight;
    });
}
