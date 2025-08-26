// Configuration file for PrepAI Platform
// Update these values based on your deployment environment

const CONFIG = {
    // Development Environment
    development: {
        API_BASE_URL: "http://localhost:8000",
        ENVIRONMENT: "development"
    },
    
    // Production Environment (Render)
    production: {
        API_BASE_URL: "https://prepai-api.onrender.com", // Your Render backend URL
        ENVIRONMENT: "production"
    },
    
    // GitHub Pages Environment
    githubPages: {
        API_BASE_URL: "https://prepai-api.onrender.com", // Your Render backend URL
        ENVIRONMENT: "production"
    }
};

// Auto-detect environment
function getCurrentConfig() {
    try {
        const hostname = window.location.hostname;
        const protocol = window.location.protocol;
        
        console.log('🔧 Config: Detecting environment for hostname:', hostname);
        
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            console.log('🔧 Config: Using development environment');
            return CONFIG.development;
        } else if (hostname.includes('github.io')) {
            console.log('🔧 Config: Using GitHub Pages environment');
            return CONFIG.githubPages;
        } else if (hostname.includes('onrender.com') || hostname.includes('github.io') || hostname.includes('prepai')) {
            console.log('🔧 Config: Using production environment');
            return CONFIG.production;
        } else {
            console.log('🔧 Config: Defaulting to production environment');
            return CONFIG.production; // Default to production for safety
        }
    } catch (error) {
        console.error('❌ Config: Error detecting environment:', error);
        console.log('🔧 Config: Falling back to production environment');
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
    try {
        window.PREPAI_CONFIG = currentConfig;
        window.PREPAI_CONFIG_FULL = CONFIG;
        
        console.log('🔧 Config: Configuration loaded successfully');
        console.log('🔧 Config: PREPAI_CONFIG set:', !!window.PREPAI_CONFIG);
        console.log('🔧 Config: API_BASE_URL:', window.PREPAI_CONFIG?.API_BASE_URL);
        console.log('🔧 Config: ENVIRONMENT:', window.PREPAI_CONFIG?.ENVIRONMENT);
    } catch (error) {
        console.error('❌ Config: Error setting configuration:', error);
        // Fallback: try to set basic config
        try {
            window.PREPAI_CONFIG = CONFIG.production;
            window.PREPAI_CONFIG_FULL = CONFIG;
            console.log('🔧 Config: Fallback configuration set');
        } catch (fallbackError) {
            console.error('❌ Config: Critical error setting fallback configuration:', fallbackError);
        }
    }
}
