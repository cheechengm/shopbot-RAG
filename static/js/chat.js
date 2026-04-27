// ── State ──────────────────────────────────────────
const state = {
  history: [],
  isLoading: false,
};

// ── DOM Refs ────────────────────────────────────────
const messagesEl = document.getElementById("messages");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const statusDot = document.getElementById("status-dot");
const statusText = document.getElementById("status-text");
const uploadStatus = document.getElementById("upload-status");
const docList = document.getElementById("doc-list");
const fileInput = document.getElementById("file-input");

// ── Init ────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  loadDocumentList();
  setupDragDrop();
});

// ── Send Message ────────────────────────────────────
async function sendMessage() {
  const text = userInput.value.trim();
  if (!text || state.isLoading) return;

  appendMessage("user", text);
  state.history.push({ role: "user", content: text });

  userInput.value = "";
  autoResize(userInput);
  setLoading(true);

  const typingId = showTyping();

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, history: state.history.slice(-10) }),
    });

    const data = await res.json();
    removeTyping(typingId);

    if (data.error) {
      appendMessage("bot", `⚠️ ${data.error}`);
    } else {
      appendBotMessage(data.answer, data.sources || []);
      state.history.push({ role: "assistant", content: data.answer });
    }
  } catch (err) {
    removeTyping(typingId);
    appendMessage("bot", "⚠️ Connection error. Please check the server is running.");
  } finally {
    setLoading(false);
  }
}

function sendSuggestion(btn) {
  userInput.value = btn.textContent;
  sendMessage();
}

// ── Message Rendering ───────────────────────────────
function appendMessage(role, text) {
  const isBot = role === "bot";
  const div = document.createElement("div");
  div.className = `message ${isBot ? "bot-message" : "user-message"}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = isBot ? "🤖" : "👤";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = formatMarkdown(text);

  div.appendChild(avatar);
  div.appendChild(bubble);
  messagesEl.appendChild(div);
  scrollToBottom();
  return div;
}

function appendBotMessage(text, sources) {
  const div = appendMessage("bot", text);
  const bubble = div.querySelector(".bubble");

  if (sources && sources.length > 0) {
    const sourcesEl = document.createElement("div");
    sourcesEl.className = "sources";
    sourcesEl.innerHTML = `<span class="source-label">Sources:</span>` +
      sources.map(s => `<span class="source-chip">📄 ${s}</span>`).join("");
    bubble.appendChild(sourcesEl);
  }

  return div;
}

function showTyping() {
  const id = "typing-" + Date.now();
  const div = document.createElement("div");
  div.className = "message bot-message typing-indicator";
  div.id = id;
  div.innerHTML = `
    <div class="avatar">🤖</div>
    <div class="bubble">
      <div class="typing-dots">
        <span></span><span></span><span></span>
      </div>
    </div>`;
  messagesEl.appendChild(div);
  scrollToBottom();
  return id;
}

function removeTyping(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

// ── Markdown Formatter ──────────────────────────────
function formatMarkdown(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/^#{1,3}\s(.+)$/gm, "<strong>$1</strong>")
    .replace(/^- (.+)$/gm, "<li>$1</li>")
    .replace(/(<li>.*<\/li>)/s, "<ul>$1</ul>")
    .replace(/^\d+\. (.+)$/gm, "<li>$1</li>")
    .replace(/\n\n/g, "</p><p>")
    .replace(/\n/g, "<br>")
    .replace(/^(.+)$/, "<p>$1</p>");
}

// ── File Upload ─────────────────────────────────────
fileInput.addEventListener("change", (e) => {
  if (e.target.files[0]) uploadFile(e.target.files[0]);
});

async function uploadFile(file) {
  showUploadStatus("loading", `⏳ Processing '${file.name}'...`);

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/upload", { method: "POST", body: formData });
    const data = await res.json();

    if (data.error) {
      showUploadStatus("error", `❌ ${data.error}`);
    } else {
      showUploadStatus("success", data.message);
      loadDocumentList();
      appendMessage("bot", `📄 I've loaded **${file.name}**. You can now ask me questions about it!`);
    }
  } catch (err) {
    showUploadStatus("error", "❌ Upload failed. Server error.");
  }

  fileInput.value = "";
}

// ── Sample Data ─────────────────────────────────────
document.getElementById("load-sample-btn").addEventListener("click", async () => {
  showUploadStatus("loading", "⏳ Loading sample store data...");
  try {
    const res = await fetch("/load-sample", { method: "POST" });
    const data = await res.json();
    if (data.error) {
      showUploadStatus("error", `❌ ${data.error}`);
    } else {
      showUploadStatus("success", data.message);
      loadDocumentList();
      appendMessage("bot", "📦 I've loaded the **sample store data**! Try asking me about shipping, returns, or products.");
    }
  } catch (err) {
    showUploadStatus("error", "❌ Failed to load sample data.");
  }
});

// ── Document List ───────────────────────────────────
async function loadDocumentList() {
  try {
    const res = await fetch("/documents");
    const data = await res.json();
    renderDocList(data.documents || []);
  } catch (err) {
    console.error("Could not load documents:", err);
  }
}

function renderDocList(docs) {
  if (docs.length === 0) {
    docList.innerHTML = `<p class="empty-hint">No documents loaded yet</p>`;
    return;
  }
  docList.innerHTML = docs
    .map(d => `<div class="doc-chip"><span class="doc-dot"></span><span title="${d}">${d}</span></div>`)
    .join("");
}

// ── Clear ───────────────────────────────────────────
document.getElementById("clear-btn").addEventListener("click", async () => {
  if (!confirm("Clear all documents from the knowledge base?")) return;
  await fetch("/clear", { method: "POST" });
  loadDocumentList();
  uploadStatus.classList.add("hidden");
  appendMessage("bot", "🗑 Knowledge base cleared. Upload new documents to get started.");
});

document.getElementById("clear-chat-btn").addEventListener("click", () => {
  messagesEl.innerHTML = `
    <div class="message bot-message welcome-message">
      <div class="avatar">🤖</div>
      <div class="bubble">
        <p>Chat cleared! Ask me anything about the loaded documents.</p>
      </div>
    </div>`;
  state.history = [];
});

// ── Drag & Drop ─────────────────────────────────────
function setupDragDrop() {
  const area = document.getElementById("upload-area");
  area.addEventListener("dragover", (e) => { e.preventDefault(); area.classList.add("drag-over"); });
  area.addEventListener("dragleave", () => area.classList.remove("drag-over"));
  area.addEventListener("drop", (e) => {
    e.preventDefault();
    area.classList.remove("drag-over");
    const file = e.dataTransfer.files[0];
    if (file) uploadFile(file);
  });
}

// ── Utils ───────────────────────────────────────────
function setLoading(loading) {
  state.isLoading = loading;
  sendBtn.disabled = loading;
  statusDot.className = "status-dot" + (loading ? " thinking" : "");
  statusText.textContent = loading ? "Thinking..." : "Ready to answer questions";
}

function showUploadStatus(type, message) {
  uploadStatus.className = `upload-status ${type}`;
  uploadStatus.textContent = message;
  uploadStatus.classList.remove("hidden");
  if (type === "success") setTimeout(() => uploadStatus.classList.add("hidden"), 5000);
}

function scrollToBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function autoResize(el) {
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 120) + "px";
}

// ── Keyboard Shortcuts ──────────────────────────────
userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

userInput.addEventListener("input", () => autoResize(userInput));
