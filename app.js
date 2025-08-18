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

// Input Elements
const roleInput = document.getElementById('role-input');
const skillsOptions = document.getElementById('skills-options');
const chatInput = document.getElementById('chat-input');
const chatWindow = document.getElementById('chat-window');
const feedbackOutput = document.getElementById('feedback-output');
const sendBtn = document.getElementById('send-btn');

// --- Navigation & Helper Functions ---
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
        // No more questions, end the interview
        endInterview();
    }
}


// --- Onboarding Flow (Adapted from your HTML) ---
document.getElementById('start-onboarding-btn').addEventListener('click', () => showScreen('onboardingRole'));

document.getElementById('role-next-btn').addEventListener('click', () => {
    if (!roleInput.value.trim()) { alert('Please select a role.'); return; }
    interviewConfig.role = roleInput.value.trim();
    showScreen('onboardingExperience');
});

function handleExperienceSelect(level) {
    interviewConfig.seniority = level;
    // For our MVP, let's pre-select some skills and go to the next step
    // In a real app, you'd populate the skills screen dynamically.
    interviewConfig.skills = ["Product Sense", "Metrics"]; 
    showScreen('dashboard');
    document.getElementById('dashboard-role-company').textContent = `For a ${interviewConfig.role} role (${interviewConfig.seniority} level).`;
    document.getElementById('key-skills-list').innerHTML = interviewConfig.skills.map(skill => `<li>${skill}</li>`).join('');
}
// Attach this function to the buttons in your HTML (it was there before)
window.handleExperienceSelect = handleExperienceSelect; 

document.getElementById('go-to-interview-prep-btn').addEventListener('click', () => showScreen('interviewPrep'));
document.getElementById('start-interview-btn').addEventListener('click', startInterview);


// --- Core API Interaction Logic ---

/**
 * API Call 1: Start the interview
 * This is the main function that contacts our backend.
 */
async function startInterview() {
    showScreen('interview');
    addMessageToChat("Hello! I'm your AI interviewer. I'm just getting the first question ready...", 'ai');

    try {
        const response = await fetch('http://127.0.0.1:8000/api/interviews', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(interviewConfig)
        });

        if (!response.ok) throw new Error(`Failed to start interview. Server responded with ${response.status}`);

        const data = await response.json();
        interviewId = data.interview_id;
        questions = data.questions;
        
        console.log(`Interview started with ID: ${interviewId}`);
        displayCurrentQuestion();

    } catch (error) {
        console.error(error);
        addMessageToChat('Error: Could not start the interview. Please ensure the backend server is running and try again.', 'ai');
    }
}

/**
 * Handles user submitting an answer
 */
function handleUserResponse() {
    const answer = chatInput.value.trim();
    if (!answer) return;

    addMessageToChat(answer, 'user');
    
    // Save the Q&A to our transcript
    const currentQuestion = questions[currentQuestionIndex];
    transcript.push({
        question: currentQuestion.question_text,
        answer: answer
    });

    chatInput.value = '';
    chatInput.disabled = true;
    sendBtn.disabled = true;

    currentQuestionIndex++;
    
    // Display the next question after a short delay
    setTimeout(displayCurrentQuestion, 1000);
}

sendBtn.addEventListener('click', handleUserResponse);
chatInput.addEventListener('keydown', (e) => { 
    if (e.key === 'Enter' && !e.shiftKey && !e.target.disabled) {
        e.preventDefault();
        handleUserResponse();
    }
});
document.getElementById('end-interview-btn').addEventListener('click', endInterview);


/**
 * API Call 2 & 3: Complete interview and poll for report
 * This function will be fully implemented in Step 4
 */
async function endInterview() {
    showScreen('analysis');
    console.log("Interview ended. Preparing to send transcript for analysis.");
    console.log("Final Transcript:", transcript);

    // --- THIS PART WILL BE BUILT IN STEP 4 ---
    // For now, we simulate the process and show a placeholder.
    
    // 1. Call the 'complete' endpoint (won't work yet)
    // await fetch(`http://127.0.0.1:8000/api/interviews/${interviewId}/complete`, {
    //     method: 'POST',
    //     headers: { 'Content-Type': 'application/json' },
    //     body: JSON.stringify({ transcript: transcript })
    // });

    // 2. Poll the 'report' endpoint (won't work yet)
    // pollForReport();

    // --- SIMULATION FOR STEP 3 ---
    setTimeout(() => {
        showScreen('feedback');
        feedbackOutput.innerHTML = `
            <h3 class="text-xl font-semibold">Analysis Complete (Placeholder)</h3>
            <p>Your interview transcript has been recorded. The backend logic to analyze it and generate a report will be built in Step 4.</p>
            <pre class="mt-4 p-4 bg-gray-100 rounded text-sm whitespace-pre-wrap">${JSON.stringify(transcript, null, 2)}</pre>
        `;
    }, 5000); // Wait 5 seconds to simulate analysis
}

// Initial Load
showScreen('homepage');