#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Start - Pottery Studio Financial Simulator

Get started in 8 simple questions. We'll set up your studio scenario and run your first simulation.
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Quick Start",
    page_icon="🚀",
    layout="wide"
)

def main():
    """Main function for Quick Start page"""
    st.title("🚀 Quick Start")

    st.markdown("""
    Get started in 8 simple questions. We'll set up your pottery studio scenario,
apply sensible defaults, and run your first Monte Carlo simulation so you can
see projected cash flow, runway, and risk in minutes.
    """)

    # TODO: Implement page content
    st.info("⚠️ Page under construction")

if __name__ == "__main__":
    main()
