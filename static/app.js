const messagesEl = document.getElementById("messages");
const composer = document.getElementById("composer");
const input = document.getElementById("input");
const resetButton = document.getElementById("reset");
const demoButton = document.getElementById("demo");

let history = [];

const addMessage = (content, role) => {
  const message = document.createElement("div");
  message.className = `message message--${role}`;
  message.textContent = content;
  messagesEl.appendChild(message);
  messagesEl.scrollTop = messagesEl.scrollHeight;
};

const sendMessage = async (message) => {
  addMessage(message, "user");
  history.push({ role: "user", content: message });

  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history }),
  });

  if (!response.ok) {
    addMessage("Something went wrong. Please try again.", "assistant");
    return "";
  }

  const data = await response.json();
  addMessage(data.reply, "assistant");
  history.push({ role: "assistant", content: data.reply });
  return data.reply;
};

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const runDemo = async () => {
  const script = [
    "Hi, I was charged twice on my last invoice.",
    "The duplicate charge was on the Pro plan renewal.",
    "The account is under maria@acme.co.",
    "This is urgent because the card is at its limit.",
  ];

  demoButton.disabled = true;
  demoButton.textContent = "Running demo...";
  resetButton.click();

  for (const line of script) {
    await delay(400);
    await sendMessage(line);
  }

  demoButton.disabled = false;
  demoButton.textContent = "Run demo scenario";
};

composer.addEventListener("submit", (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) return;
  input.value = "";
  sendMessage(message);
});

resetButton.addEventListener("click", () => {
  history = [];
  messagesEl.innerHTML = "";
  addMessage("Hi! I am Kikibot. How can I help you today?", "assistant");
});

demoButton.addEventListener("click", () => {
  runDemo();
});

document.querySelectorAll(".prompt").forEach((button) => {
  button.addEventListener("click", () => {
    sendMessage(button.dataset.prompt);
  });
});

addMessage("Hi! I am Kikibot. How can I help you today?", "assistant");
