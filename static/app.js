let chatHistory = [];
let sessionId = null; // always start fresh — no sessionStorage


function showChat() {
    document.querySelectorAll(".nav-item").forEach(i => i.classList.remove("active"));
    event.target.classList.add("active");
    document.getElementById("chat-box").style.display = "flex";
    document.getElementById("history-section").style.display = "none";
    document.getElementById("upload-section").style.display = "none";
    document.getElementById("about-section").style.display = "none";
    document.getElementById("input-bar").style.display = "block";
}

async function showHistory() {
    document.querySelectorAll(".nav-item").forEach(i => i.classList.remove("active"));
    event.target.classList.add("active");
    document.getElementById("chat-box").style.display = "none";
    document.getElementById("history-section").style.display = "flex";
    document.getElementById("upload-section").style.display = "none";
    document.getElementById("about-section").style.display = "none";
    document.getElementById("input-bar").style.display = "none";

    const response = await fetch("/sessions");
    const sessions = await response.json();
    const historyList = document.getElementById("history-list");

    if (sessions.length === 0) {
        historyList.innerHTML = "<p style='color:#888;font-size:13px;'>No conversations yet.</p>";
        return;
    }

    historyList.innerHTML = sessions.map(s => `
        <div onclick="loadSession('${s.session_id}')" style="padding:12px 16px; background:white; border:1px solid #e0e0e0; border-radius:10px; margin-bottom:8px; cursor:pointer; transition:background 0.15s;">
            <div style="font-size:13px; font-weight:500; color:#333;">${s.first_question.slice(0, 50)}${s.first_question.length > 50 ? '...' : ''}</div>
            <div style="font-size:11px; color:#888; margin-top:4px;">${s.total_messages} messages · ${s.started}</div>
        </div>
   `).join("");
}

async function loadSession(sid) {
    const response = await fetch(`/history/${sid}`);
    const history = await response.json();

    document.getElementById("history-section").style.display = "none";
    document.getElementById("chat-box").style.display = "flex";
    document.getElementById("input-bar").style.display = "block";

    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML = "";
    chatHistory = [];

    history.forEach(chat => {
        addUserMessage(chat.question);
        addBotMessage(chat.answer, chat.sources);
        chatHistory.push({question: chat.question, answer: chat.answer});
    });

    sessionId = sid;
    sessionStorage.setItem("sessionId", sid);
}

function showUpload() {
    document.querySelectorAll(".nav-item").forEach(i => i.classList.remove("active"));
    event.target.classList.add("active");
    document.getElementById("chat-box").style.display = "none";
    document.getElementById("history-section").style.display = "none";
    document.getElementById("upload-section").style.display = "flex";
    document.getElementById("about-section").style.display = "none";
    document.getElementById("input-bar").style.display = "none";
}

function showAbout() {
    document.querySelectorAll(".nav-item").forEach(i => i.classList.remove("active"));
    event.target.classList.add("active");
    document.getElementById("chat-box").style.display = "none";
    document.getElementById("history-section").style.display = "none";
    document.getElementById("upload-section").style.display = "none";
    document.getElementById("about-section").style.display = "flex";
    document.getElementById("input-bar").style.display = "none";
}

async function askQuestion() {
    const input = document.getElementById("question");
    const question = input.value.trim();
    if (!question) return;

    addUserMessage(question);
    input.value = "";

    const chatBox = document.getElementById("chat-box");
    const typing = document.createElement("div");
    typing.className = "msg-row";
    typing.id = "typing";
    typing.innerHTML = `
        <div class="avatar bot">AI</div>
        <div class="typing">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>`;
    chatBox.appendChild(typing);
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                question,
                chat_history: chatHistory,
                session_id: sessionId
            })
        });

        const data = await response.json();
        document.getElementById("typing")?.remove();

        if (data.session_id) {
            sessionId = data.session_id;
            sessionStorage.setItem("sessionId", sessionId);
        }

        const seen = new Set();
        const uniqueSources = data.sources.filter(s => {
            if (seen.has(s.url)) return false;
            seen.add(s.url);
            return true;
        });

        addBotMessage(data.answer, uniqueSources);
        chatHistory.push({question, answer: data.answer});

    } catch (error) {
        document.getElementById("typing")?.remove();
        addBotMessage("Something went wrong. Please try again.", []);
    }
}

function addUserMessage(text) {
    const chatBox = document.getElementById("chat-box");
    const div = document.createElement("div");
    div.className = "msg-row user";
    div.innerHTML = `
        <div class="avatar user">S</div>
        <div class="bubble user">${text}</div>`;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function addBotMessage(text, sources) {
    const chatBox = document.getElementById("chat-box");

    let sourcesHTML = "";
    if (sources && sources.length > 0) {
        sourcesHTML = `<div class="sources">
            <div class="sources-label">Sources</div>
            ${sources.map(s => `<a class="source-link" href="${s.url}" target="_blank">▶ ${s.title}</a>`).join("")}
        </div>`;
    }

    const div = document.createElement("div");
    div.className = "msg-row";
    div.innerHTML = `
        <div class="avatar bot">AI</div>
        <div class="bubble bot">${text}${sourcesHTML}</div>`;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function uploadFile() {
    const fileInput = document.getElementById("file-input");
    const status = document.getElementById("upload-status");

    if (!fileInput.files[0]) {
        status.textContent = "Please select a file first!";
        status.style.color = "red";
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    status.textContent = "Uploading and processing...";
    status.style.color = "#1a73e8";

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            status.textContent = data.error;
            status.style.color = "red";
        } else {
            status.textContent = data.message;
            status.style.color = "green";
            fileInput.value = "";
        }
    } catch (error) {
        status.textContent = "Upload failed. Please try again.";
        status.style.color = "red";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("question").addEventListener("keypress", function(e) {
        if (e.key === "Enter") askQuestion();
    });
});