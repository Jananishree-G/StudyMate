"""
Custom CSS styles for StudyMate
"""

def get_custom_css():
    """Return custom CSS for StudyMate"""
    return """
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Root variables for consistent theming */
    :root {
        --primary-color: #6366f1;
        --primary-dark: #4f46e5;
        --secondary-color: #06b6d4;
        --accent-color: #f59e0b;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --background-color: #0f172a;
        --surface-color: #1e293b;
        --surface-light: #334155;
        --text-primary: #f8fafc;
        --text-secondary: #cbd5e1;
        --text-muted: #94a3b8;
        --border-color: #475569;
        --shadow-color: rgba(0, 0, 0, 0.3);
        --gradient-primary: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        --gradient-secondary: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
        --gradient-accent: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
    }
    
    /* Main app styling */
    .stApp {
        background: var(--background-color);
        color: var(--text-primary);
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom header */
    .main-header {
        background: var(--gradient-primary);
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 25px var(--shadow-color);
    }
    
    .main-header h1 {
        color: white;
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        font-weight: 300;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: var(--surface-color);
        border-right: 1px solid var(--border-color);
    }
    
    .sidebar-content {
        padding: 1rem;
    }
    
    /* Card components */
    .custom-card {
        background: var(--surface-color);
        border: 1px solid var(--border-color);
        border-radius: 1rem;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px var(--shadow-color);
        transition: all 0.3s ease;
    }
    
    .custom-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px var(--shadow-color);
        border-color: var(--primary-color);
    }
    
    .feature-card {
        background: var(--surface-color);
        border: 1px solid var(--border-color);
        border-radius: 1rem;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .feature-card:hover {
        background: var(--surface-light);
        transform: translateY(-4px);
        box-shadow: 0 12px 30px var(--shadow-color);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    /* Button styling */
    .stButton > button {
        background: var(--gradient-primary);
        color: white;
        border: none;
        border-radius: 0.75rem;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4);
        background: var(--primary-dark);
    }
    
    /* Secondary button */
    .secondary-button {
        background: var(--gradient-secondary) !important;
        box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3) !important;
    }
    
    .secondary-button:hover {
        box-shadow: 0 8px 20px rgba(6, 182, 212, 0.4) !important;
    }
    
    /* Success button */
    .success-button {
        background: var(--success-color) !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        background: var(--surface-color);
        border: 2px dashed var(--border-color);
        border-radius: 1rem;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div:hover {
        border-color: var(--primary-color);
        background: var(--surface-light);
    }
    
    /* Chat interface styling */
    .chat-container {
        background: var(--surface-color);
        border-radius: 1rem;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid var(--border-color);
    }
    
    .chat-message {
        background: var(--surface-light);
        border-radius: 1rem;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid var(--primary-color);
    }
    
    .user-message {
        background: var(--gradient-primary);
        color: white;
        border-left: 4px solid var(--accent-color);
        margin-left: 2rem;
    }
    
    .assistant-message {
        background: var(--surface-light);
        border-left: 4px solid var(--secondary-color);
        margin-right: 2rem;
    }
    
    /* Metrics styling */
    .stMetric {
        background: var(--surface-color);
        border: 1px solid var(--border-color);
        border-radius: 1rem;
        padding: 1rem;
        text-align: center;
    }
    
    .stMetric > div {
        color: var(--text-primary);
    }
    
    .stMetric [data-testid="metric-value"] {
        color: var(--primary-color);
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Progress bar styling */
    .stProgress > div > div {
        background: var(--gradient-primary);
        border-radius: 1rem;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: var(--surface-color);
        border: 1px solid var(--border-color);
        border-radius: 0.5rem;
        color: var(--text-primary);
    }
    
    .streamlit-expanderContent {
        background: var(--surface-light);
        border: 1px solid var(--border-color);
        border-top: none;
        border-radius: 0 0 0.5rem 0.5rem;
    }
    
    /* Code blocks */
    .stCode {
        background: var(--background-color);
        border: 1px solid var(--border-color);
        border-radius: 0.5rem;
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* Success/Error/Warning messages */
    .stSuccess {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid var(--success-color);
        border-radius: 0.75rem;
        color: var(--success-color);
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid var(--error-color);
        border-radius: 0.75rem;
        color: var(--error-color);
    }
    
    .stWarning {
        background: rgba(245, 158, 11, 0.1);
        border: 1px solid var(--warning-color);
        border-radius: 0.75rem;
        color: var(--warning-color);
    }
    
    .stInfo {
        background: rgba(6, 182, 212, 0.1);
        border: 1px solid var(--secondary-color);
        border-radius: 0.75rem;
        color: var(--secondary-color);
    }
    
    /* Custom animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in-up {
        animation: fadeInUp 0.6s ease-out;
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.7;
        }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .main-header p {
            font-size: 1rem;
        }
        
        .custom-card {
            padding: 1rem;
        }
        
        .feature-card {
            padding: 1.5rem;
        }
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--surface-color);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--primary-color);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-dark);
    }
    </style>
    """
