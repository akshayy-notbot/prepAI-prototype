// --- Global State ---
let interviewId = null;
let sessionId = null;  // New: Store session ID from backend
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
        // Handle both old database format and new Gemini API format
        const questionText = question.question_text || question.question || question;
        addMessageToChat(questionText, 'ai');
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
    showScreen('onboardingSkills');
    populateSkillsOptions();
}

function populateSkillsOptions() {
    const skillsContainer = document.getElementById('skills-options');
    const role = interviewConfig.role;
    
    // Define skills for each role
    const roleSkills = {
        'Product Manager': [
            'Product Sense',
            'User Research',
            'Data Analysis',
            'Strategic Thinking',
            'Execution',
            'Stakeholder Management',
            'Metrics & KPIs',
            'User Experience Design'
        ],
        'Software Engineer': [
            'System Design',
            'Algorithms & Data Structures',
            'Code Quality',
            'Testing & Debugging',
            'Performance Optimization',
            'Security',
            'API Design',
            'Database Design'
        ],
        'Data Analyst': [
            'Data Visualization',
            'Statistical Analysis',
            'SQL & Data Querying',
            'Business Intelligence',
            'A/B Testing',
            'Data Storytelling',
            'Machine Learning Basics',
            'Data Quality & Governance'
        ]
    };
    
    const skills = roleSkills[role] || [];
    
    skillsContainer.innerHTML = skills.map(skill => `
        <label class="flex items-center space-x-3 cursor-pointer">
            <input type="checkbox" value="${skill}" class="form-checkbox h-5 w-5 text-blue-600 rounded">
            <span class="text-gray-700">${skill}</span>
        </label>
    `).join('');
}

document.getElementById('skills-next-btn').addEventListener('click', () => {
    const selectedSkills = Array.from(document.querySelectorAll('#skills-options input:checked'))
        .map(input => input.value);
    
    if (selectedSkills.length === 0) {
        alert('Please select at least one skill to practice.');
        return;
    }
    
    interviewConfig.skills = selectedSkills;
    showScreen('dashboard');
    
    // Update dashboard display
    document.getElementById('dashboard-role-company').textContent = `For a ${interviewConfig.role} role (${interviewConfig.seniority} level).`;
    document.getElementById('key-skills-list').innerHTML = interviewConfig.skills.map(skill => `<li>${skill}</li>`).join('');
});

document.getElementById('go-to-interview-prep-btn').addEventListener('click', () => showScreen('interviewPrep'));
document.getElementById('start-interview-btn').addEventListener('click', startInterview);

// Make the function globally accessible for the onclick attributes in the HTML
window.handleExperienceSelect = handleExperienceSelect;

// --- Core API Interaction Logic ---
async function startInterview() {
    showScreen('interview');
    addMessageToChat("Hello! I'm your AI interviewer. I'm just getting the first question ready...", 'ai');

    try {
        // Generate questions using Gemini API directly
        const generatedQuestions = await generateQuestionsWithGemini();
        
        if (generatedQuestions && generatedQuestions.length > 0) {
            questions = generatedQuestions;
            interviewId = Date.now(); // Generate a simple ID for tracking
            
            console.log(`Interview started with ID: ${interviewId}`);
            displayCurrentQuestion();
        } else {
            throw new Error('Failed to generate questions');
        }

    } catch (error) {
        console.error(error);
        addMessageToChat('Error: Could not start the interview. Please check your API key and try again.', 'ai');
    }
}

// New function to generate questions using Gemini API
async function generateQuestionsWithGemini() {
    const API_BASE_URL = "https://prepai-api.onrender.com"; // Live Render backend
    
    console.log('🔍 Starting question generation...');
    console.log('📡 API URL:', API_BASE_URL);
    console.log('📋 Request payload:', {
        role: interviewConfig.role,
        seniority: interviewConfig.seniority,
        skills: interviewConfig.skills
    });
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/generate-questions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                role: interviewConfig.role,
                seniority: interviewConfig.seniority,
                skills: interviewConfig.skills
            })
        });

        console.log('📥 Response status:', response.status);
        console.log('📥 Response headers:', response.headers);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Response error text:', errorText);
            throw new Error(`Server responded with ${response.status}: ${errorText}`);
        }

        const data = await response.json();
        console.log('✅ Response data:', data);
        
        // Store session ID for database tracking
        if (data.session_id) {
            sessionId = data.session_id;
            console.log('🆔 Session ID stored:', sessionId);
        }
        
        if (data.questions && Array.isArray(data.questions)) {
            console.log('✅ Questions received:', data.questions.length);
            return data.questions;
        } else {
            console.error('❌ Invalid response format:', data);
            throw new Error('Invalid response format from server');
        }

    } catch (error) {
        console.error('❌ Error generating questions:', error);
        console.error('❌ Error details:', {
            name: error.name,
            message: error.message,
            stack: error.stack
        });
        throw error;
    }
}

function handleUserResponse() {
    const answer = chatInput.value.trim();
    if (!answer) return;

    addMessageToChat(answer, 'user');
    
    const currentQuestion = questions[currentQuestionIndex];
    // Handle both old database format and new Gemini API format
    const questionText = currentQuestion.question_text || currentQuestion.question || currentQuestion;
    
    transcript.push({
        question: questionText,
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

    // Use the live Render backend URL
    const API_BASE_URL = "https://prepai-api.onrender.com"; 
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/interviews/${interviewId}/complete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                transcript: transcript,
                session_id: sessionId  // Pass session ID for database tracking
            })
        });

        if (!response.ok) {
            throw new Error('Analysis request failed');
        }

        const result = await response.json();
        console.log('📊 Analysis result:', result);

        showScreen('feedback');
        
        // Format the feedback in a user-friendly way
        if (result.data) {
            const data = result.data;
            feedbackOutput.innerHTML = `
                <div class="space-y-6">
                    <div class="text-center">
                        <h3 class="text-2xl font-bold text-gray-900 mb-2">Interview Analysis Complete!</h3>
                        ${data.overall_score ? `<div class="text-4xl font-bold text-blue-600">${data.overall_score}/5</div>` : ''}
                    </div>
                    
                    ${data.overall_summary ? `
                        <div class="bg-blue-50 p-4 rounded-lg">
                            <h4 class="font-semibold text-blue-800 mb-2">Overall Summary</h4>
                            <p class="text-blue-700">${data.overall_summary}</p>
                        </div>
                    ` : ''}
                    
                    ${data.scores && data.scores.length > 0 ? `
                        <div class="bg-gray-50 p-4 rounded-lg">
                            <h4 class="font-semibold text-gray-800 mb-3">Detailed Scores</h4>
                            <div class="space-y-3">
                                ${data.scores.map(score => `
                                    <div class="flex justify-between items-start">
                                        <div class="flex-1">
                                            <div class="font-medium text-gray-700">${score.criterion}</div>
                                            <div class="text-sm text-gray-600 mt-1">${score.justification}</div>
                                        </div>
                                        <div class="ml-4 text-2xl font-bold text-blue-600">${score.score}/5</div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                    
                    ${data.key_strengths && data.key_strengths.length > 0 ? `
                        <div class="bg-green-50 p-4 rounded-lg">
                            <h4 class="font-semibold text-green-800 mb-2">Key Strengths</h4>
                            <ul class="list-disc list-inside text-green-700 space-y-1">
                                ${data.key_strengths.map(strength => `<li>${strength}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    
                    ${data.areas_for_improvement && data.areas_for_improvement.length > 0 ? `
                        <div class="bg-yellow-50 p-4 rounded-lg">
                            <h4 class="font-semibold text-yellow-800 mb-2">Areas for Improvement</h4>
                            <ul class="list-disc list-inside text-yellow-700 space-y-1">
                                ${data.areas_for_improvement.map(area => `<li>${area}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    
                    ${data.recommendations && data.recommendations.length > 0 ? `
                        <div class="bg-purple-50 p-4 rounded-lg">
                            <h4 class="font-semibold text-purple-800 mb-2">Recommendations</h4>
                            <ul class="list-disc list-inside text-purple-700 space-y-1">
                                ${data.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    
                    <div class="text-center pt-4">
                        <button onclick="location.reload()" class="bg-blue-600 text-white font-bold py-3 px-6 rounded-lg hover:bg-blue-700 transition duration-300">
                            Start a New Interview
                        </button>
                    </div>
                </div>
            `;
        } else {
            // Fallback to raw JSON if structure is unexpected
            feedbackOutput.innerHTML = `
                <h3 class="text-xl font-semibold">Analysis Complete!</h3>
                <pre class="mt-4 p-4 bg-gray-100 rounded text-sm whitespace-pre-wrap">${JSON.stringify(result, null, 2)}</pre>
            `;
        }

    } catch (error) {
        console.error('❌ Analysis error:', error);
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