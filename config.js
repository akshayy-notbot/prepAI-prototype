// Configuration file for PrepAI Platform
// Update these values based on your deployment environment

const CONFIG = {
    // Development Environment
    development: {
        API_BASE_URL: "http://localhost:8000",
        WS_BASE_URL: "ws://localhost:8000",
        ENVIRONMENT: "development"
    },
    
    // Production Environment (Render)
    production: {
        API_BASE_URL: "https://your-service-name.onrender.com", // UPDATE THIS with your actual Render URL
        WS_BASE_URL: "wss://your-service-name.onrender.com",   // UPDATE THIS with your actual Render URL
        ENVIRONMENT: "production"
    },
    
    // GitHub Pages Environment
    githubPages: {
        API_BASE_URL: "https://your-service-name.onrender.com", // UPDATE THIS with your actual Render URL
        WS_BASE_URL: "wss://your-service-name.onrender.com",   // UPDATE THIS with your actual Render URL
        ENVIRONMENT: "production"
    }
};

// Auto-detect environment
function getCurrentConfig() {
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;
    
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return CONFIG.development;
    } else if (hostname.includes('github.io')) {
        return CONFIG.githubPages;
    } else {
        return CONFIG.production;
    }
}

// Export configuration
const currentConfig = getCurrentConfig();

// For use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CONFIG, getCurrentConfig, currentConfig };
} else {
    // Browser environment
    window.PREPAI_CONFIG = currentConfig;
    window.PREPAI_CONFIG_FULL = CONFIG;
}
