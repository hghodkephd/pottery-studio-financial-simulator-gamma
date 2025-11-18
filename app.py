#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pottery Studio Financial Simulator - Main Entry Point

A comprehensive financial modeling tool for pottery studio owners.
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Pottery Studio Simulator",
    page_icon="🏺",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application entry point"""

    st.title("🏺 Pottery Studio Financial Simulator")

    st.markdown("""
    ### Welcome to the Pottery Studio Financial Simulator

    This tool helps you model and plan your pottery studio's finances through:
    - **Monte Carlo simulation** for realistic scenario planning
    - **SBA loan analysis** with detailed DSCR calculations
    - **Revenue modeling** across memberships, classes, workshops, and events
    - **Risk assessment** with percentile-based outcomes

    #### Getting Started

    Choose your experience level:

    - **🚀 Quick Start** (Recommended for new users): Answer 8 questions, get instant results
    - **⚙️ Advanced Configuration**: Full control over 150+ parameters
    - **📊 Results Analysis**: View and compare scenarios

    Use the sidebar to navigate between pages →
    """)

    # Sidebar instructions
    with st.sidebar:
        st.markdown("### 📖 Navigation")
        st.markdown("""
        **Recommended Flow:**
        1. 🚀 Quick Start
        2. 💰 Revenue Configuration
        3. 💸 Costs & Operations
        4. 🏦 Financing Strategy
        5. 📊 Results Analysis
        """)

        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("Version: 2.0.0")
        st.markdown("Built with Streamlit")

if __name__ == "__main__":
    main()
