import json

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Agent Manager - LUCA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Agent configuration
AGENT_CONFIG = {
    "luca": {
        "name": "LUCA",
        "role": "Lead Universal Coding Assistant",
        "description": "Orchestrates all agent activities and manages the overall development workflow.",
        "color": "main",  # Uses the main gradient
    },
    "coder": {
        "name": "Coder",
        "role": "Code Generation Specialist",
        "description": "Writes, refactors, and optimizes code across multiple languages and frameworks.",
        "color": "coder",
    },
    "tester": {
        "name": "Tester",
        "role": "Quality Assurance Engineer",
        "description": "Creates and runs tests, validates functionality, and ensures code reliability.",
        "color": "tester",
    },
    "doc_writer": {
        "name": "Doc Writer",
        "role": "Documentation Specialist",
        "description": "Creates comprehensive documentation, API references, and user guides.",
        "color": "doc",
    },
    "analyst": {
        "name": "Analyst",
        "role": "Code Analysis Expert",
        "description": "Analyzes code patterns, suggests improvements, and identifies potential issues.",
        "color": "analyst",
    },
}

# Create the full constellation view
html_content = (
    """
<!DOCTYPE html>
<html>
<head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        body {
            background: #ffffff;
            margin: 0;
            padding: 0;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        .constellation-svg {
            width: 100%;
            height: 100%;
        }

        /* Constellation lines */
        .constellation-line {
            stroke: #ff00ff;
            stroke-width: 3;
            fill: none;
            opacity: 0.8;
            filter: blur(0.5px);
            animation: laser-pulse 2s ease-in-out infinite;
        }

        .constellation-line-glow {
            stroke: #ff00ff;
            stroke-width: 8;
            fill: none;
            opacity: 0.3;
            filter: blur(4px);
            animation: laser-pulse 2s ease-in-out infinite;
        }

        .constellation-line-core {
            stroke: #ffffff;
            stroke-width: 1;
            fill: none;
            opacity: 0.9;
            animation: laser-pulse 2s ease-in-out infinite;
        }

        @keyframes laser-pulse {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 0.9; }
        }

        /* Orb containers */
        .agent-orb-container {
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .agent-orb-container.selected .agent-label {
            color: #ff00ff;
            text-shadow: 0 0 20px rgba(255, 0, 255, 0.8);
        }

        .agent-orb-container.selected .selected-glow {
            opacity: 1;
        }

        .agent-orb-wrapper {
            position: relative;
            display: inline-block;
        }

        /* Labels */
        .agent-label {
            position: absolute;
            top: 100%;
            left: 50%;
            transform: translateX(-50%);
            margin-top: 20px;
            color: rgba(0, 0, 0, 0.8);
            font-size: 16px;
            font-weight: 500;
            white-space: nowrap;
            transition: all 0.3s ease;
            text-align: center;
        }

        .agent-label-small {
            font-size: 14px;
        }

        .luca-label {
            font-size: 20px;
            font-weight: 600;
            letter-spacing: 2px;
        }

        /* Selected glow effect */
        .selected-glow {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 200px;
            height: 200px;
            background: radial-gradient(circle, rgba(255, 0, 255, 0.3) 0%, transparent 70%);
            opacity: 0;
            transition: opacity 0.3s ease;
            pointer-events: none;
        }

        /* Logo container and orb styles from main page */
        .logo-container {
            position: relative;
            width: 120px;
            height: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            background: radial-gradient(circle at 30% 30%, #ec4899 0%, #8b5cf6 50%, #6d28d9 100%);
            cursor: pointer;
            transition: all 0.4s ease;
            animation: pulse-glow 3.6s ease-in-out infinite;
            overflow: hidden;
        }

        .logo-container::before {
            content: '';
            position: absolute;
            top: -20px;
            left: -20px;
            right: -20px;
            bottom: -20px;
            background: radial-gradient(circle, rgba(139, 92, 246, 0.4) 0%, rgba(236, 72, 153, 0.3) 50%, transparent 70%);
            border-radius: 50%;
            z-index: -1;
            opacity: 0.6;
            animation: aura-pulse 3.6s ease-in-out infinite;
        }

        .logo-container::after {
            content: '';
            position: absolute;
            top: -40px;
            left: -40px;
            right: -40px;
            bottom: -40px;
            background: radial-gradient(circle, rgba(139, 92, 246, 0.2) 0%, rgba(236, 72, 153, 0.1) 40%, transparent 60%);
            border-radius: 50%;
            z-index: -2;
            opacity: 0.4;
            animation: aura-pulse 3.6s ease-in-out infinite 0.5s;
        }

        /* Agent-specific orb colors */
        .coder-orb {
            background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
            box-shadow: 0 10px 40px rgba(0, 210, 255, 0.6),
                        0 0 80px rgba(0, 210, 255, 0.3),
                        inset 0 0 20px rgba(255, 255, 255, 0.2);
        }

        .tester-orb {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            box-shadow: 0 10px 40px rgba(240, 147, 251, 0.6),
                        0 0 80px rgba(240, 147, 251, 0.3),
                        inset 0 0 20px rgba(255, 255, 255, 0.2);
        }

        .doc-orb {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            box-shadow: 0 10px 40px rgba(250, 112, 154, 0.6),
                        0 0 80px rgba(250, 112, 154, 0.3),
                        inset 0 0 20px rgba(255, 255, 255, 0.2);
        }

        .analyst-orb {
            background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);
            box-shadow: 0 10px 40px rgba(48, 207, 208, 0.6),
                        0 0 80px rgba(48, 207, 208, 0.3),
                        inset 0 0 20px rgba(255, 255, 255, 0.2);
        }

        @keyframes pulse-glow {
            0%, 100% {
                box-shadow: 0 0 30px rgba(139, 92, 246, 0.5), 0 0 60px rgba(236, 72, 153, 0.3);
            }
            50% {
                box-shadow: 0 0 40px rgba(139, 92, 246, 0.6), 0 0 80px rgba(236, 72, 153, 0.4);
            }
        }

        @keyframes aura-pulse {
            0%, 100% {
                transform: scale(1);
                opacity: 0.6;
            }
            50% {
                transform: scale(1.1);
                opacity: 0.3;
            }
        }


        .orb-inner {
            position: absolute;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            background: conic-gradient(from 0deg at 50% 50%,
                transparent 0deg,
                rgba(236, 72, 153, 0.4) 60deg,
                transparent 120deg,
                rgba(139, 92, 246, 0.4) 180deg,
                transparent 240deg,
                rgba(236, 72, 153, 0.4) 300deg,
                transparent 360deg);
            animation: swirl 5s linear infinite;
        }

        .orb-inner::before {
            content: '';
            position: absolute;
            inset: 20%;
            border-radius: 50%;
            background: radial-gradient(circle,
                rgba(255, 255, 255, 0.3) 0%,
                transparent 70%);
            animation: shimmer 3.6s ease-in-out infinite;
        }

        .orb-particles {
            position: absolute;
            width: 100%;
            height: 100%;
            border-radius: 50%;
        }

        .orb-particles::before,
        .orb-particles::after {
            content: '';
            position: absolute;
            width: 4px;
            height: 4px;
            background: white;
            border-radius: 50%;
            box-shadow: 0 0 10px rgba(255, 255, 255, 0.8);
            animation: orbit 7.2s linear infinite;
        }

        .orb-particles::after {
            animation-delay: -3s;
            width: 3px;
            height: 3px;
        }

        @keyframes swirl {
            0% {
                transform: rotate(0deg);
            }
            100% {
                transform: rotate(360deg);
            }
        }

        @keyframes shimmer {
            0%, 100% {
                opacity: 0.5;
                transform: scale(0.8);
            }
            50% {
                opacity: 1;
                transform: scale(1.1);
            }
        }

        @keyframes orbit {
            0% {
                transform: rotate(0deg) translateX(40px) rotate(0deg);
                opacity: 0;
            }
            10% {
                opacity: 1;
            }
            90% {
                opacity: 1;
            }
            100% {
                transform: rotate(360deg) translateX(40px) rotate(-360deg);
                opacity: 0;
            }
        }

        /* Info panel */
        .agent-info-panel {
            position: fixed;
            top: 50%;
            right: 40px;
            transform: translateY(-50%);
            background: rgba(255, 255, 255, 0.95);
            border: 1px solid rgba(139, 92, 246, 0.3);
            border-radius: 20px;
            padding: 1.5rem 2rem;
            width: 300px;
            color: #1a1a2e;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            opacity: 0;
            visibility: hidden;
        }

        .agent-info-panel.active {
            opacity: 1;
            visibility: visible;
        }

        .agent-info-name {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .agent-info-role {
            font-size: 14px;
            color: #ff00ff;
            margin-bottom: 1rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .agent-info-description {
            font-size: 16px;
            line-height: 1.6;
            color: rgba(0, 0, 0, 0.7);
        }
    </style>
</head>
<body>
    <div style="position: relative; width: 100%; height: 100vh; overflow: hidden;">
        <!-- Constellation lines -->
        <svg class="constellation-svg" style="position: absolute; top: 0; left: 0;">
            <g>
                <!-- Line to Coder -->
                <path class="constellation-line-glow" d="M 50 80 Q 35 60 20 40" />
                <path class="constellation-line" d="M 50 80 Q 35 60 20 40" />
                <path class="constellation-line-core" d="M 50 80 Q 35 60 20 40" />
            </g>
            <g>
                <!-- Line to Tester -->
                <path class="constellation-line-glow" d="M 50 80 Q 42.5 52.5 35 25" />
                <path class="constellation-line" d="M 50 80 Q 42.5 52.5 35 25" />
                <path class="constellation-line-core" d="M 50 80 Q 42.5 52.5 35 25" />
            </g>
            <g>
                <!-- Line to Doc Writer -->
                <path class="constellation-line-glow" d="M 50 80 Q 57.5 52.5 65 25" />
                <path class="constellation-line" d="M 50 80 Q 57.5 52.5 65 25" />
                <path class="constellation-line-core" d="M 50 80 Q 57.5 52.5 65 25" />
            </g>
            <g>
                <!-- Line to Analyst -->
                <path class="constellation-line-glow" d="M 50 80 Q 65 60 80 40" />
                <path class="constellation-line" d="M 50 80 Q 65 60 80 40" />
                <path class="constellation-line-core" d="M 50 80 Q 65 60 80 40" />
            </g>
        </svg>

        <!-- LUCA at bottom center -->
        <div class="agent-orb-container" 
             style="position: absolute; left: 50%; top: 80%; transform: translate(-50%, -50%);"
             onclick="selectAgent('luca')"
             id="agent-luca">
            <div class="logo-container luca-main">
                <div class="orb-inner"></div>
                <div class="orb-particles"></div>
            </div>
            <div class="selected-glow"></div>
            <div class="agent-label luca-label">LUCA</div>
        </div>

        <!-- Coder agent -->
        <div class="agent-orb-container"
             style="position: absolute; left: 20%; top: 40%; transform: translate(-50%, -50%);"
             onclick="selectAgent('coder')"
             id="agent-coder">
            <div class="agent-orb-wrapper" style="transform: scale(0.65);">
                <div class="logo-container coder-orb">
                    <div class="orb-inner"></div>
                    <div class="orb-particles" style="animation-delay: -1s;"></div>
                </div>
            </div>
            <div class="selected-glow"></div>
            <div class="agent-label agent-label-small">Coder</div>
        </div>

        <!-- Tester agent -->
        <div class="agent-orb-container"
             style="position: absolute; left: 35%; top: 25%; transform: translate(-50%, -50%);"
             onclick="selectAgent('tester')"
             id="agent-tester">
            <div class="agent-orb-wrapper" style="transform: scale(0.65);">
                <div class="logo-container tester-orb">
                    <div class="orb-inner"></div>
                    <div class="orb-particles" style="animation-delay: -2.5s;"></div>
                </div>
            </div>
            <div class="selected-glow"></div>
            <div class="agent-label agent-label-small">Tester</div>
        </div>

        <!-- Doc Writer agent -->
        <div class="agent-orb-container"
             style="position: absolute; left: 65%; top: 25%; transform: translate(-50%, -50%);"
             onclick="selectAgent('doc_writer')"
             id="agent-doc_writer">
            <div class="agent-orb-wrapper" style="transform: scale(0.65);">
                <div class="logo-container doc-orb">
                    <div class="orb-inner"></div>
                    <div class="orb-particles" style="animation-delay: -4s;"></div>
                </div>
            </div>
            <div class="selected-glow"></div>
            <div class="agent-label agent-label-small">Doc Writer</div>
        </div>

        <!-- Analyst agent -->
        <div class="agent-orb-container"
             style="position: absolute; left: 80%; top: 40%; transform: translate(-50%, -50%);"
             onclick="selectAgent('analyst')"
             id="agent-analyst">
            <div class="agent-orb-wrapper" style="transform: scale(0.65);">
                <div class="logo-container analyst-orb">
                    <div class="orb-inner"></div>
                    <div class="orb-particles" style="animation-delay: -5.5s;"></div>
                </div>
            </div>
            <div class="selected-glow"></div>
            <div class="agent-label agent-label-small">Analyst</div>
        </div>

        <!-- Agent info panel -->
        <div id="agentInfoPanel" class="agent-info-panel">
            <div class="agent-info-name" id="agentName"></div>
            <div class="agent-info-role" id="agentRole"></div>
            <div class="agent-info-description" id="agentDescription"></div>
        </div>
    </div>

    <script>
        let selectedAgent = null;

        // Agent data
        const agents = """
    + json.dumps(AGENT_CONFIG)
    + """;

        function selectAgent(agentId) {
            // Remove previous selection
            if (selectedAgent) {
                document.getElementById(`agent-${selectedAgent}`).classList.remove('selected');
            }

            // Add new selection
            document.getElementById(`agent-${agentId}`).classList.add('selected');

            // Update info panel
            const agent = agents[agentId];
            if (agent) {
                document.getElementById('agentName').textContent = agent.name;
                document.getElementById('agentRole').textContent = agent.role;
                document.getElementById('agentDescription').textContent = agent.description;
                document.getElementById('agentInfoPanel').classList.add('active');

                // Communicate with Streamlit
                window.parent.postMessage({
                    type: 'agent_selected',
                    agent: agentId
                }, '*');
            }

            selectedAgent = agentId;
        }

        // Auto-select LUCA on load
        window.addEventListener('DOMContentLoaded', function() {
            selectAgent('luca');
        });
    </script>
</body>
</html>
"""
)

# Display the constellation
components.html(html_content, height=800)

# Handle agent selection communication
st.markdown(
    """
<script>
    // Listen for messages from the iframe
    window.addEventListener('message', function(e) {
        if (e.data.type === 'agent_selected') {
            // Would update Streamlit session state here if needed
            console.log('Agent selected:', e.data.agent);
        }
    });
</script>
""",
    unsafe_allow_html=True,
)
