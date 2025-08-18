// --- Global State ---
let interviewId = null;
let questions = [];
let currentQuestionIndex = 0;
let transcript = [];
let interviewConfig = {}; // To store user selections

// --- Screen & Element References ---
const screens = {
    homepage: document.getElementById('homepage-screen'),
    onboardingRole: document.getElementById('onboarding-role-screen'),
    onboardingExperience: document.getElementById('onboarding-experience-screen'),
    onboardingSkills: document.getElementById('onboarding-skills-screen'),
    dashboard: document.getElementById('dashboard-screen'),
    interviewPrep: document.getElementById('interview-prep-screen'),
    interview: document.getElementById('interview-screen'),
    analysis: document.getElementById('analysis-screen'),
    feedback: document.getElementById('feedback-screen'),
};

const roleInput = document.getElementById('role-input');
const chatInput = document.getElementById('chat-input');
const chatWindow = document.getElementById('chat-window');
const feedbackOutput = document.getElementById('feedback-output');
const sendBtn = document.getElementById('send-btn');

// --- Helper Functions ---
function showScreen(screenKey) {
    Object.values(screens).forEach(screen => screen.classList.add('hidden'));
    if (screens[screenKey]) {
        screens[screenKey].classList.remove('hidden');
    }
}

function addMessageToChat(message, sender) {
    const bubble = document.createElement('div');
    bubble.classList.add('chat-bubble', sender === 'user' ? 'chat-bubble-user' : 'chat-bubble-ai', 'self-start');
    if (sender === 'user') {
        bubble.classList.add('self-end');
    }
    bubble.textContent = message;
    chatWindow.appendChild(bubble);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function displayCurrentQuestion() {
    const question = questions[currentQuestionIndex];
    if (question) {
        addMessageToChat(question.question_text, 'ai');
        chatInput.disabled = false;
        sendBtn.disabled = false;
        chatInput.focus();
    } else {
        addMessageToChat("That was the last question. Click the 'End Interview' button to get your feedback.", 'ai');
        chatInput.disabled = true;
        sendBtn.disabled = true;
    }
}

// --- Onboarding Flow ---
document.getElementById('start-onboarding-btn').addEventListener('click', () => showScreen('onboardingRole'));

document.getElementById('role-next-btn').addEventListener('click', () => {
    if (!roleInput.value.trim()) { alert('Please select a role.'); return; }
    interviewConfig.role = roleInput.value.trim();
    showScreen('onboardingExperience');
});

function handleExperienceSelect(level) {
    interviewConfig.seniority = level;
    // For our MVP, we'll pre-select skills and proceed.
    interviewConfig.skills = ["Product Sense", "Metrics"]; 
    showScreen('dashboard');
    document.getElementById('dashboard-role-company').textContent = `For a ${interviewConfig.role} role (${interviewConfig.seniority} level).`;
    document.getElementById('key-skills-list').innerHTML = interviewConfig.skills.map(skill => `<li>${skill}</li>`).join('');
}
// Make the function globally accessible for the onclick attributes in the HTML
window.handleExperienceSelect = handleExperienceSelect; 

document.getElementById('go-to-interview-prep-btn').addEventListener('click', () => showScreen('interviewPrep'));
document.getElementById('start-interview-btn').addEventListener('click', startInterview);

// --- Core API Interaction Logic ---
async function startInterview() {
    showScreen('interview');
    addMessageToChat("Hello! I'm your AI interviewer. I'm just getting the first question ready...", 'ai');

    // Replace this with your live Render URL or local URL for testing
    const API_BASE_URL = "https://prepai-api.onrender.com"; 

    try {
        const response = await fetch(`${API_BASE_URL}/api/interviews`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(interviewConfig)
        });

        if (!response.ok) throw new Error(`Server responded with ${response.status}`);

        const data = await response.json();
        interviewId = data.interview_id;
        questions = data.questions;
        
        console.log(`Interview started with ID: ${interviewId}`);
        displayCurrentQuestion();

    } catch (error) {
        console.error(error);
        addMessageToChat('Error: Could not start the interview. Please ensure the backend server is running and the API URL is correct, then refresh the page.', 'ai');
    }
}

function handleUserResponse() {
    const answer = chatInput.value.trim();
    if (!answer) return;

    addMessageToChat(answer, 'user');
    
    const currentQuestion = questions[currentQuestionIndex];
    transcript.push({
        question: currentQuestion.question_text,
        answer: answer
    });

    chatInput.value = '';
    chatInput.disabled = true;
    sendBtn.disabled = true;

    currentQuestionIndex++;
    
    setTimeout(displayCurrentQuestion, 1000);
}

async function endInterview() {
    showScreen('analysis');
    console.log("Interview ended. Sending transcript and waiting for analysis...");

    // Replace this with your live Render URL or local URL for testing
    const API_BASE_URL = "http://127.0.0.1:8000"; 
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/interviews/${interviewId}/complete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ transcript: transcript })
        });

        if (!response.ok) {
            throw new Error('Analysis request failed');
        }

        const result = await response.json();

        showScreen('feedback');
        feedbackOutput.innerHTML = `
            <h3 class="text-xl font-semibold">Analysis Complete!</h3>
            <pre class="mt-4 p-4 bg-gray-100 rounded text-sm whitespace-pre-wrap">${JSON.stringify(result.data, null, 2)}</pre>
        `;

    } catch (error) {
        console.error(error);
        alert('Could not get analysis. Please try again.');
        showScreen('interview');
    }
}

// --- Event Listeners ---
sendBtn.addEventListener('click', handleUserResponse);
chatInput.addEventListener('keydown', (e) => { 
    if (e.key === 'Enter' && !e.shiftKey && !e.target.disabled) {
        e.preventDefault();
        handleUserResponse();
    }
});
document.getElementById('end-interview-btn').addEventListener('click', endInterview);

// --- Initial Load ---
showScreen('homepage');
