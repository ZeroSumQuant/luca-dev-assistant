"""
Orb Showcase Page
Displays isolated constellation orbs for reference and reuse.
"""

import sys
from pathlib import Path

import streamlit as st

# Add parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.components.constellation_orb import render_constellation_orb

st.set_page_config(
    page_title="Orb Showcase - LUCA",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Dark background to match constellation view
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
        }
        .main > div {
            padding-top: 2rem;
        }
        h1, h2, h3 {
            color: white;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
            background-color: transparent;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: transparent;
            color: rgba(255, 255, 255, 0.6);
        }
        .stTabs [aria-selected="true"] {
            background-color: transparent;
            color: #ff00ff;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🔮 Constellation Orb Showcase")
st.markdown(
    """
    <p style='color: rgba(255, 255, 255, 0.8); font-size: 1.2rem;'>
    Isolated orb components from the Agent Manager constellation view. 
    These orbs have a cleaner appearance without prominent aura rings.
    </p>
    """,
    unsafe_allow_html=True,
)

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["All Orbs", "Individual Orbs", "Size Variations", "Code Example"])

with tab1:
    st.markdown("### Complete Agent Collection")
    
    # Display all orbs in a row
    cols = st.columns(5)
    
    orb_configs = [
        ("luca", "LUCA", 1.0, "Lead Universal Coding Assistant"),
        ("coder", "Coder", 0.65, "Code Generation Specialist"),
        ("tester", "Tester", 0.65, "Quality Assurance Engineer"),
        ("doc", "Doc Writer", 0.65, "Documentation Specialist"),
        ("analyst", "Analyst", 0.65, "Code Analysis Expert"),
    ]
    
    for col, (orb_type, label, scale, description) in zip(cols, orb_configs):
        with col:
            st.markdown(f"<p style='color: white; text-align: center;'>{description}</p>", unsafe_allow_html=True)
            render_constellation_orb(
                orb_type=orb_type,
                size=120,
                scale=scale,
                label_text=label,
                selected=False,
            )

with tab2:
    st.markdown("### Individual Orb Display")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        selected_orb = st.selectbox(
            "Select an orb:",
            options=[config[0] for config in orb_configs],
            format_func=lambda x: next(config[1] for config in orb_configs if config[0] == x),
        )
        
        show_label = st.checkbox("Show label", value=True)
        is_selected = st.checkbox("Selected state", value=False)
        size = st.slider("Size", min_value=60, max_value=200, value=120)
        scale = st.slider("Scale", min_value=0.5, max_value=1.5, value=1.0, step=0.05)
    
    with col2:
        config = next(config for config in orb_configs if config[0] == selected_orb)
        render_constellation_orb(
            orb_type=config[0],
            size=size,
            scale=scale,
            label_text=config[1],
            show_label=show_label,
            selected=is_selected,
        )

with tab3:
    st.markdown("### Size Variations")
    
    sizes = [60, 90, 120, 150, 180]
    
    for orb_type, label in [("luca", "LUCA"), ("coder", "Coder")]:
        st.markdown(f"#### {label} Orb - Different Sizes")
        cols = st.columns(len(sizes))
        
        for col, size in zip(cols, sizes):
            with col:
                st.markdown(f"<p style='color: white; text-align: center;'>{size}px</p>", unsafe_allow_html=True)
                render_constellation_orb(
                    orb_type=orb_type,
                    size=size,
                    scale=1.0,
                    label_text=label,
                    show_label=False,
                )

with tab4:
    st.markdown("### Code Example")
    st.markdown(
        """
        <p style='color: rgba(255, 255, 255, 0.8);'>
        Here's how to use the constellation orb component in your own pages:
        </p>
        """,
        unsafe_allow_html=True,
    )
    
    code_example = '''from app.components.constellation_orb import render_constellation_orb

# Basic usage - LUCA orb
render_constellation_orb(
    orb_type="luca",
    size=120,
    scale=1.0,
    label_text="LUCA",
)

# Agent orb with custom settings
render_constellation_orb(
    orb_type="coder",
    size=120,
    scale=0.65,  # Smaller scale for agent orbs
    label_text="Coder",
    selected=True,  # Show selected state
    show_label=True,
)

# Available orb types:
# - "luca": Purple gradient (main)
# - "coder": Blue gradient
# - "tester": Pink gradient
# - "doc": Yellow/pink gradient
# - "analyst": Cyan/purple gradient
'''
    
    st.code(code_example, language="python")
    
    st.markdown(
        """
        <p style='color: rgba(255, 255, 255, 0.8); margin-top: 2rem;'>
        <strong>Note:</strong> These orbs include all animations (pulse-glow, rotate-hue, swirl, orbit) 
        and are designed to work on dark backgrounds. The component automatically handles the selected 
        state with a magenta glow effect.
        </p>
        """,
        unsafe_allow_html=True,
    )