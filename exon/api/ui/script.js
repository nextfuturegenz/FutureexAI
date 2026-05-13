// exon/api/ui/script.js
// Author: Ashish Pal
// Purpose: Chat interface logic with SSE streaming

let sessionId = "web_" + Date.now();
const apiBase = window.location.origin;
let currentTheme = localStorage.getItem("theme") || "dark";

function setTheme(theme) {
    if (theme === "light") {
        document.body.classList.add("light");
    } else {
        document.body.classList.remove("light");
    }
    localStorage.setItem("theme", theme);
    currentTheme = theme;
}
setTheme(currentTheme);

document.getElementById("themeToggleBtn").addEventListener("click", () => {
    setTheme(currentTheme === "dark" ? "light" : "dark");
});

async function updateStatus() {
    try {
        const res = await fetch(apiBase + "/status");
        const data = await res.json();
        document.getElementById("emotion").innerText = data.emotion || "?";
        document.getElementById("intensity").innerText = data.emotion_intensity.toFixed(2);
        document.getElementById("confidence").innerText = (data.confidence || 0.5).toFixed(2);
        document.getElementById("memoryCount").innerText = data.memory_count;

        const goals = data.active_goals || [];
        const goalsContainer = document.getElementById("goalsList");
        if (goals.length === 0) {
            goalsContainer.innerHTML = "<li>No active goals</li>";
        } else {
            goalsContainer.innerHTML = goals.map(g => `
                <li>
                    ${escapeHtml(g.description)}
                    <div class="progress-bar"><div class="progress-fill" style="width: ${(g.progress || 0)*100}%"></div></div>
                </li>
            `).join("");
        }
    } catch(e) { console.error(e); }
}

async function fetchMemories() {
    try {
        const res = await fetch(apiBase + "/memories?limit=5");
        const data = await res.json();
        const memories = data.memories || [];
        const container = document.getElementById("memoryList");
        if (memories.length === 0) {
            container.innerHTML = "No memories yet.";
        } else {
            container.innerHTML = memories.map(m => `
                <div class="memory-item">
                    <div><strong>You:</strong> ${escapeHtml((m.user || "").substring(0, 80))}${(m.user || "").length > 80 ? "..." : ""}</div>
                    <div><strong>Exon:</strong> ${escapeHtml((m.assistant || "").substring(0, 80))}${(m.assistant || "").length > 80 ? "..." : ""}</div>
                    <small>${m.emotion || "neutral"} · ${new Date(m.timestamp).toLocaleTimeString()}</small>
                </div>
            `).join("");
        }
    } catch(e) { console.error(e); }
}

async function fetchThoughts() {
    try {
        const res = await fetch(apiBase + "/thoughts?limit=5");
        const data = await res.json();
        const thoughts = data.thoughts || [];
        const container = document.getElementById("thoughtsList");
        if (thoughts.length === 0) {
            container.innerHTML = "No autonomous thoughts yet.";
        } else {
            container.innerHTML = thoughts.map(t => `<div class="thought-item">💭 ${escapeHtml(t)}</div>`).join("");
        }
    } catch(e) { console.error(e); }
}

async function sendMessage() {
    const input = document.getElementById("messageInput");
    const text = input.value.trim();
    if (!text) return;
    input.value = "";
    input.disabled = true;
    document.getElementById("sendBtn").disabled = true;

    addMessage(text, "user");
    const thinkingDiv = addThinking();

    try {
        const persona = document.getElementById("personaSelect").value;
        const response = await fetch(apiBase + "/chat/stream", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: text,
                persona: persona,
                session_id: sessionId
            })
        });
        removeThinking(thinkingDiv);
        if (!response.ok) throw new Error("Network error");

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let exBubble = null;

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split("\n");
            for (const line of lines) {
                if (line.startsWith("data: ")) {
                    const data = line.slice(6);
                    if (data === "[DONE]") continue;
                    try {
                        const parsed = JSON.parse(data);
                        if (parsed.token) {
                            if (!exBubble) {
                                exBubble = addExonMessage("");
                            }
                            exBubble.innerHTML = `<div>${exBubble.innerText + parsed.token}</div>`;
                            const chatDiv = document.getElementById("chatMessages");
                            chatDiv.scrollTop = chatDiv.scrollHeight;
                        } else if (parsed.error) {
                            if (!exBubble) exBubble = addExonMessage("Error: " + parsed.error);
                            else exBubble.innerHTML = `<div>Error: ${parsed.error}</div>`;
                        }
                    } catch (e) { /* ignore malformed JSON */ }
                }
            }
        }
        updateStatus();
        fetchMemories();
        fetchThoughts();
    } catch(e) {
        removeThinking(thinkingDiv);
        addMessage("Error: Could not reach Exon consciousness.", "exon");
    } finally {
        input.disabled = false;
        document.getElementById("sendBtn").disabled = false;
        input.focus();
    }
}

function addMessage(text, sender, emotion = null) {
    const messagesDiv = document.getElementById("chatMessages");
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${sender === "user" ? "user-message" : "exon-message"}`;
    msgDiv.innerHTML = `<div>${escapeHtml(text)}</div>`;
    if (emotion && sender === "exon") {
        msgDiv.innerHTML += `<div class="message-meta">🤖 ${escapeHtml(emotion)}</div>`;
    }
    messagesDiv.appendChild(msgDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    return msgDiv;
}

function addExonMessage(text) {
    const messagesDiv = document.getElementById("chatMessages");
    const msgDiv = document.createElement("div");
    msgDiv.className = "message exon-message";
    msgDiv.innerHTML = `<div>${escapeHtml(text)}</div>`;
    messagesDiv.appendChild(msgDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    return msgDiv;
}

function addThinking() {
    const messagesDiv = document.getElementById("chatMessages");
    const div = document.createElement("div");
    div.className = "thinking";
    div.innerText = "Exon is thinking...";
    messagesDiv.appendChild(div);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    return div;
}

function removeThinking(div) {
    if (div && div.remove) div.remove();
}

function exportConversation() {
    const messages = document.querySelectorAll("#chatMessages .message");
    let exportText = `Exon Conversation Export\nID: ${sessionId}\nDate: ${new Date().toISOString()}\n\n`;
    messages.forEach(msg => {
        const isUser = msg.classList.contains("user-message");
        const content = msg.querySelector("div").innerText;
        const meta = msg.querySelector(".message-meta");
        const emotion = meta ? meta.innerText.replace("🤖 ", "") : "";
        exportText += `${isUser ? "User" : "Exon"}: ${content}\n`;
        if (emotion) exportText += `[Emotion: ${emotion}]\n`;
        exportText += "\n";
    });
    const blob = new Blob([exportText], { type: "text/plain" });
    const a = document.createElement("a");
    const url = URL.createObjectURL(blob);
    a.href = url;
    a.download = `exon_conversation_${sessionId}.txt`;
    a.click();
    URL.revokeObjectURL(url);
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>]/g, function(m) {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}

// Polling
setInterval(() => {
    updateStatus();
    fetchMemories();
    fetchThoughts();
}, 5000);

updateStatus();
fetchMemories();
fetchThoughts();

document.getElementById("sendBtn").addEventListener("click", sendMessage);
document.getElementById("messageInput").addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
});
document.getElementById("exportBtn").addEventListener("click", exportConversation);