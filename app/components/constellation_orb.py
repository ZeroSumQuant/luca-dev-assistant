"""
Constellation Orb Component
A reusable orb component from the Agent Manager constellation view.
This version has a cleaner look without the prominent aura rings.
"""

import streamlit as st
import streamlit.components.v1 as components


def render_constellation_orb(
    orb_type="luca",
    size=120,
    scale=1.0,
    position={"left": "50%", "top": "50%"},
    show_label=True,
    label_text="LUCA",
    clickable=True,
    selected=False,
):
    """
    Render a constellation-style orb component.

    Args:
        orb_type: Type of orb ('luca', 'coder', 'tester', 'doc', 'analyst')
        size: Base size of the orb in pixels
        scale: Scale factor (e.g., 0.65 for smaller agents)
        position: Dict with 'left' and 'top' position values
        show_label: Whether to show the label below the orb
        label_text: Text to display in the label
        clickable: Whether the orb is clickable
        selected: Whether the orb is in selected state
    """

    # Color gradients for different orb types
    orb_colors = {
        "luca": {
            "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "shadow_color": "102, 126, 234",
        },
        "coder": {
            "gradient": "linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%)",
            "shadow_color": "0, 210, 255",
        },
        "tester": {
            "gradient": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
            "shadow_color": "240, 147, 251",
        },
        "doc": {
            "gradient": "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
            "shadow_color": "250, 112, 154",
        },
        "analyst": {
            "gradient": "linear-gradient(135deg, #30cfd0 0%, #330867 100%)",
            "shadow_color": "48, 207, 208",
        },
    }

    colors = orb_colors.get(orb_type, orb_colors["luca"])

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            
            body {{
                margin: 0;
                padding: 20px;
                background: transparent;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }}
            
            .orb-container {{
                position: relative;
                cursor: {'pointer' if clickable else 'default'};
                transition: all 0.3s ease;
                transform: scale({scale});
            }}
            
            .logo-container {{
                position: relative;
                width: {size}px;
                height: {size}px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                background: {colors['gradient']};
                box-shadow: 0 10px 40px rgba({colors['shadow_color']}, 0.6),
                            0 0 80px rgba({colors['shadow_color']}, 0.3),
                            inset 0 0 20px rgba(255, 255, 255, 0.2);
                overflow: visible;
                animation: pulse-glow 3.6s ease-in-out infinite, rotate-hue 10s linear infinite;
            }}
            
            .logo-container::before,
            .logo-container::after {{
                content: '';
                position: absolute;
                border-radius: 50%;
                background: radial-gradient(circle, rgba({colors['shadow_color']}, 0.4) 0%, transparent 70%);
                animation: pulse-glow 3.6s ease-in-out infinite;
            }}
            
            .logo-container::before {{
                width: 140%;
                height: 140%;
                top: -20%;
                left: -20%;
                animation-delay: 0s;
            }}
            
            .logo-container::after {{
                width: 180%;
                height: 180%;
                top: -40%;
                left: -40%;
                animation-delay: 0.5s;
                opacity: 0.5;
            }}
            
            @keyframes pulse-glow {{
                0%, 100% {{
                    transform: scale(1);
                    opacity: 0.8;
                }}
                50% {{
                    transform: scale(1.05);
                    opacity: 1;
                }}
            }}
            
            @keyframes rotate-hue {{
                0% {{ filter: hue-rotate(0deg) brightness(1.1); }}
                100% {{ filter: hue-rotate(360deg) brightness(1.1); }}
            }}
            
            .orb-inner {{
                position: relative;
                width: 100%;
                height: 100%;
                border-radius: 50%;
                background: radial-gradient(circle at 30% 30%, 
                    rgba(255, 255, 255, 0.8) 0%, 
                    rgba(255, 255, 255, 0.4) 10%, 
                    transparent 40%);
                animation: swirl 20s linear infinite;
            }}
            
            .orb-inner::before {{
                content: '';
                position: absolute;
                width: 50%;
                height: 50%;
                top: 10%;
                left: 15%;
                background: radial-gradient(circle, rgba(255, 255, 255, 0.6) 0%, transparent 70%);
                border-radius: 50%;
                filter: blur(10px);
                animation: shimmer 2.4s ease-in-out infinite;
            }}
            
            .orb-inner::after {{
                content: '';
                position: absolute;
                width: 30%;
                height: 30%;
                bottom: 20%;
                right: 20%;
                background: radial-gradient(circle, rgba(255, 255, 255, 0.4) 0%, transparent 70%);
                border-radius: 50%;
                filter: blur(8px);
                animation: shimmer 2.4s ease-in-out infinite reverse;
            }}
            
            .orb-particles {{
                position: absolute;
                width: 100%;
                height: 100%;
                border-radius: 50%;
            }}
            
            .orb-particles::before,
            .orb-particles::after {{
                content: '';
                position: absolute;
                width: 4px;
                height: 4px;
                background: white;
                border-radius: 50%;
                box-shadow: 0 0 10px rgba(255, 255, 255, 0.8);
                animation: orbit 7.2s linear infinite;
            }}
            
            .orb-particles::after {{
                animation-delay: -3s;
                width: 3px;
                height: 3px;
            }}
            
            @keyframes swirl {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            
            @keyframes shimmer {{
                0%, 100% {{
                    opacity: 0.5;
                    transform: scale(0.8);
                }}
                50% {{
                    opacity: 1;
                    transform: scale(1.1);
                }}
            }}
            
            @keyframes orbit {{
                0% {{
                    transform: rotate(0deg) translateX(40px) rotate(0deg);
                    opacity: 0;
                }}
                10% {{
                    opacity: 1;
                }}
                90% {{
                    opacity: 1;
                }}
                100% {{
                    transform: rotate(360deg) translateX(40px) rotate(-360deg);
                    opacity: 0;
                }}
            }}
            
            .orb-label {{
                position: absolute;
                top: 100%;
                left: 50%;
                transform: translateX(-50%);
                margin-top: 20px;
                color: {'#ff00ff' if selected else 'rgba(255, 255, 255, 0.8)'};
                font-size: {'20px' if orb_type == 'luca' else '16px'};
                font-weight: {'600' if orb_type == 'luca' else '500'};
                white-space: nowrap;
                text-align: center;
                {'letter-spacing: 2px;' if orb_type == 'luca' else ''}
                {'text-shadow: 0 0 20px rgba(255, 0, 255, 0.8);' if selected else ''}
                {'display: none;' if not show_label else ''}
            }}
            
            .selected-glow {{
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 200px;
                height: 200px;
                background: radial-gradient(circle, rgba(255, 0, 255, 0.3) 0%, transparent 70%);
                opacity: {1 if selected else 0};
                transition: opacity 0.3s ease;
                pointer-events: none;
            }}
        </style>
    </head>
    <body>
        <div class="orb-container">
            <div class="logo-container">
                <div class="orb-inner"></div>
                <div class="orb-particles"></div>
            </div>
            <div class="selected-glow"></div>
            <div class="orb-label">{label_text}</div>
        </div>
    </body>
    </html>
    """

    return components.html(html_content, height=size * 2 + 100)


# Standalone test function
def show_orb_gallery():
    """Display a gallery of all orb types for testing."""
    st.set_page_config(page_title="Constellation Orb Gallery", layout="wide")

    st.title("Constellation Orb Gallery")
    st.markdown("A collection of orb styles from the Agent Manager constellation view.")

    # Create columns for different orb types
    cols = st.columns(5)

    orb_configs = [
        ("luca", "LUCA", 1.0),
        ("coder", "Coder", 0.65),
        ("tester", "Tester", 0.65),
        ("doc", "Doc Writer", 0.65),
        ("analyst", "Analyst", 0.65),
    ]

    for col, (orb_type, label, scale) in zip(cols, orb_configs):
        with col:
            st.markdown(f"### {label}")
            render_constellation_orb(
                orb_type=orb_type,
                size=120,
                scale=scale,
                label_text=label,
                selected=False,
            )

    # Show selected state
    st.markdown("### Selected State")
    cols2 = st.columns(5)

    for col, (orb_type, label, scale) in zip(cols2, orb_configs):
        with col:
            render_constellation_orb(
                orb_type=orb_type,
                size=120,
                scale=scale,
                label_text=label,
                selected=True,
            )


if __name__ == "__main__":
    show_orb_gallery()
