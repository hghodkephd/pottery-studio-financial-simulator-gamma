#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameter Schema Foundation - Use this as the template for parameter_schema.py

This is the architectural blueprint. ChatGPT will use this to convert all 150 parameters.
"""

from dataclasses import dataclass, field
from typing import Any, Optional, List, Dict, Union, Callable
from enum import Enum


class ParameterTier(Enum):
    """
    Parameter importance tiers for progressive disclosure UI.
    
    ESSENTIAL: 8-12 params always visible (rent, price, capacity, loan terms)
    IMPORTANT: 15-20 params in collapsed sections (revenue toggles, member mix)
    ADVANCED: 120+ params hidden by default (fine-tuning, elasticity, etc.)
    """
    ESSENTIAL = "essential"
    IMPORTANT = "important"
    ADVANCED = "advanced"


class ParameterType(Enum):
    """Parameter data types for widget rendering and validation"""
    FLOAT = "float"
    INT = "int"
    BOOL = "bool"
    SELECT = "select"
    TEXT = "text"


@dataclass
class Parameter:
    """
    Complete parameter specification - single source of truth.
    
    This replaces COMPLETE_PARAM_SPECS from the old app.
    Every parameter is defined once here, used everywhere.
    
    Attributes:
        name: Unique parameter identifier (e.g., "RENT", "PRICE")
        type: Data type for validation and widget selection
        default: Default value (must match type)
        
        # UI Display
        label: Human-readable label for UI
        help: Tooltip/help text explaining the parameter
        tier: UI visibility tier (essential/important/advanced)
        group: Logical grouping (e.g., "business_fundamentals", "pricing")
        
        # Validation
        min: Minimum allowed value (for numeric types)
        max: Maximum allowed value (for numeric types)
        step: Step size for sliders
        options: Valid choices (for SELECT type)
        
        # Relationships
        depends_on: Parameters this depends on (e.g., archetype probs must sum to 1)
        affects: What this parameter influences (for impact indicators)
        
        # Advanced
        visible_when: Function to determine if param should show (context-aware hiding)
        presets: Named preset values (e.g., "conservative": 0.03, "aggressive": 0.08)
        why_it_matters: Extended educational content for "expert explains" mode
        typical_range: Guidance on typical values
        example: Concrete example to illustrate usage
    """
    
    # Core attributes (REQUIRED)
    name: str
    type: ParameterType
    default: Any
    
    # UI attributes
    label: str = ""
    help: str = ""
    tier: ParameterTier = ParameterTier.ADVANCED
    group: str = ""
    
    # Validation attributes
    min: Optional[float] = None
    max: Optional[float] = None
    step: Optional[float] = None
    options: Optional[List[str]] = None
    
    # Relationship tracking
    depends_on: List[str] = field(default_factory=list)
    affects: List[str] = field(default_factory=list)
    
    # Advanced features
    visible_when: Optional[Callable[[Dict[str, Any]], bool]] = None
    presets: Optional[Dict[str, Any]] = None
    why_it_matters: str = ""
    typical_range: str = ""
    example: str = ""
    
    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        """
        Validate a value against this parameter's constraints.
        
        Returns:
            (is_valid, error_message)
            - (True, None) if valid
            - (False, "error description") if invalid
        """
        # Type checking and range validation
        if self.type == ParameterType.FLOAT:
            try:
                value = float(value)
            except (ValueError, TypeError):
                return False, f"{self.label} must be a number"
            
            if self.min is not None and value < self.min:
                return False, f"{self.label} must be >= {self.min}"
            if self.max is not None and value > self.max:
                return False, f"{self.label} must be <= {self.max}"
        
        elif self.type == ParameterType.INT:
            try:
                value = int(value)
            except (ValueError, TypeError):
                return False, f"{self.label} must be an integer"
            
            if self.min is not None and value < self.min:
                return False, f"{self.label} must be >= {self.min}"
            if self.max is not None and value > self.max:
                return False, f"{self.label} must be <= {self.max}"
        
        elif self.type == ParameterType.SELECT:
            if self.options and value not in self.options:
                return False, f"{self.label} must be one of: {', '.join(self.options)}"
        
        elif self.type == ParameterType.BOOL:
            if not isinstance(value, bool):
                return False, f"{self.label} must be True or False"
        
        return True, None
    
    def to_streamlit_widget(self, current_value: Any = None, key: str = None):
        """
        Generate appropriate Streamlit widget for this parameter.
        
        Args:
            current_value: Current parameter value (uses default if None)
            key: Unique widget key for Streamlit
            
        Returns:
            New value from widget
        """
        import streamlit as st
        
        if current_value is None:
            current_value = self.default
        
        if key is None:
            key = f"param_{self.name}"
        
        # Build help text
        help_text = self.help
        if self.min is not None and self.max is not None:
            help_text += f" (Range: {self.min}-{self.max})"
        
        # Render appropriate widget
        if self.type == ParameterType.BOOL:
            return st.checkbox(
                self.label,
                value=bool(current_value),
                help=help_text,
                key=key
            )
        
        elif self.type == ParameterType.INT:
            return st.slider(
                self.label,
                min_value=int(self.min) if self.min is not None else 0,
                max_value=int(self.max) if self.max is not None else 1000,
                value=int(current_value),
                step=int(self.step) if self.step is not None else 1,
                help=help_text,
                key=key
            )
        
        elif self.type == ParameterType.FLOAT:
            return st.slider(
                self.label,
                min_value=float(self.min) if self.min is not None else 0.0,
                max_value=float(self.max) if self.max is not None else 1.0,
                value=float(current_value),
                step=float(self.step) if self.step is not None else 0.01,
                help=help_text,
                key=key
            )
        
        elif self.type == ParameterType.SELECT:
            options = self.options or []
            try:
                index = options.index(current_value) if current_value in options else 0
            except (ValueError, TypeError):
                index = 0
            
            return st.selectbox(
                self.label,
                options=options,
                index=index,
                help=help_text,
                key=key
            )
        
        elif self.type == ParameterType.TEXT:
            return st.text_input(
                self.label,
                value=str(current_value),
                help=help_text,
                key=key
            )
        
        return current_value


# =============================================================================
# USAGE EXAMPLES (for ChatGPT to follow)
# =============================================================================

# Example 1: Essential parameter (always visible)
EXAMPLE_ESSENTIAL = Parameter(
    name="RENT",
    type=ParameterType.FLOAT,
    default=3500,
    min=1000,
    max=15000,
    step=100,
    tier=ParameterTier.ESSENTIAL,
    group="business_fundamentals",
    label="Monthly Base Rent ($)",
    help="Fixed monthly rent payment for studio space. Directly impacts fixed costs and loan sizing.",
    affects=["loan_7a_size", "cash_flow", "breakeven"],
    why_it_matters="Rent is typically your largest fixed cost. It affects your breakeven point, loan sizing (7a loan needs to cover several months of rent), and overall profitability. Most studios spend 20-30% of revenue on rent.",
    typical_range="Urban: $4000-8000/mo, Suburban: $2500-4500/mo, Rural: $1500-3000/mo",
    example="A 2000 sqft studio in suburban area might pay $3500/month ($1.75/sqft)"
)

# Example 2: Important parameter with presets
EXAMPLE_IMPORTANT = Parameter(
    name="HOBBYIST_PROB",
    type=ParameterType.FLOAT,
    default=0.35,
    min=0.0,
    max=1.0,
    step=0.05,
    tier=ParameterTier.IMPORTANT,
    group="member_behavior",
    label="Hobbyist Mix (%)",
    help="Fraction of members who are casual hobbyists. Must sum to 1.0 with other archetypes.",
    depends_on=["COMMITTED_ARTIST_PROB", "PRODUCTION_POTTER_PROB", "SEASONAL_USER_PROB"],
    affects=["revenue_per_member", "churn_rate", "capacity_utilization"],
    presets={
        "community_studio": 0.35,
        "beginner_friendly": 0.50,
        "professional": 0.15
    },
    why_it_matters="Hobbyists are casual users who visit 1x/week, use moderate clay, and have higher churn (4-5%/month). They're important for filling capacity but generate less revenue per member than committed artists.",
    typical_range="Community studios: 30-40%, Beginner-focused: 40-60%, Professional: 10-20%"
)

# Example 3: Advanced parameter with conditional visibility
EXAMPLE_ADVANCED = Parameter(
    name="NO_ACCESS_POOL",
    type=ParameterType.INT,
    default=20,
    min=0,
    max=1000,
    step=10,
    tier=ParameterTier.ADVANCED,
    group="market_dynamics",
    label="No-Access Market Pool Size",
    help="People in your market with no current pottery access. Most motivated to join.",
    visible_when=lambda config: config.get("MEMBERSHIP_MODE") == "calculated",
    why_it_matters="This pool represents your highest-intent prospects - people who want to do pottery but have no access. They convert at the highest rate but are also the smallest pool. Size depends on local population and existing studio density.",
    typical_range="Urban with no other studios: 50-100, Suburban: 20-50, Saturated market: 5-20"
)

# Example 4: Boolean toggle
EXAMPLE_BOOL = Parameter(
    name="WORKSHOPS_ENABLED",
    type=ParameterType.BOOL,
    default=True,
    tier=ParameterTier.IMPORTANT,
    group="workshops",
    label="Enable Workshop Revenue Stream",
    help="Whether studio offers short pottery workshops for beginners.",
    affects=["revenue", "member_acquisition"],
    why_it_matters="Workshops are a key revenue stream and member acquisition funnel. They typically have 40-60% margins and 10-15% of participants convert to members.",
    example="A 2-hour workshop for 10 people at $75/person = $750 revenue, ~$250 costs = $500 profit"
)

# Example 5: Select dropdown
EXAMPLE_SELECT = Parameter(
    name="LOAN_504_TERM_YEARS",
    type=ParameterType.SELECT,
    default="20",
    options=["5", "7", "10", "15", "20", "25"],
    tier=ParameterTier.ESSENTIAL,
    group="financing",
    label="SBA 504 Loan Term (years)",
    help="Loan term for equipment/build-out financing. Longer terms = lower monthly payment.",
    affects=["monthly_debt_service", "total_interest"],
    presets={
        "aggressive": "10",
        "standard": "20",
        "conservative": "25"
    }
)


# =============================================================================
# CONVERSION RULES (for ChatGPT)
# =============================================================================
"""
To convert from old COMPLETE_PARAM_SPECS to new Parameter() format:

OLD FORMAT:
"RENT": {
    "type": "float",
    "min": 1000,
    "max": 15000,
    "step": 100,
    "default": 3500,
    "label": "Monthly Base Rent ($)",
    "desc": "Fixed monthly rent payment...",
    "group": "business_fundamentals"
}

NEW FORMAT:
"RENT": Parameter(
    name="RENT",
    type=ParameterType.FLOAT,
    default=3500,
    min=1000,
    max=15000,
    step=100,
    tier=ParameterTier.ESSENTIAL,  # <-- ASSIGN BASED ON IMPORTANCE
    group="business_fundamentals",
    label="Monthly Base Rent ($)",
    help="Fixed monthly rent payment...",  # <-- "desc" becomes "help"
    affects=["loan_7a_size", "cash_flow"],  # <-- ADD RELATIONSHIPS
    why_it_matters="...",  # <-- ADD EDUCATIONAL CONTENT
    typical_range="..."    # <-- ADD GUIDANCE
)

MAPPING RULES:
1. "type": "float" → type=ParameterType.FLOAT
2. "type": "int" → type=ParameterType.INT
3. "type": "bool" → type=ParameterType.BOOL
4. "type": "select" → type=ParameterType.SELECT
5. "type": "text" → type=ParameterType.TEXT
6. "desc" → help
7. Add name= explicitly
8. Assign tier= based on this guide (below)
9. Add affects=[] (can be empty for now)
10. Add why_it_matters="" (can be empty for now)

TIER ASSIGNMENT GUIDE:

ESSENTIAL (tier=ParameterTier.ESSENTIAL) - Only these 8-12:
- RENT
- MAX_MEMBERS
- PRICE
- OWNER_DRAW
- LOAN_504_TERM_YEARS
- LOAN_7A_TERM_YEARS
- RUNWAY_MONTHS
- MONTHS (simulation horizon)
- N_SIMULATIONS

IMPORTANT (tier=ParameterTier.IMPORTANT) - These ~20:
- WORKSHOPS_ENABLED
- CLASSES_ENABLED
- EVENTS_ENABLED
- DESIGNATED_STUDIOS_ENABLED
- WHEELS_CAPACITY
- HANDBUILDING_CAPACITY
- GLAZE_CAPACITY
- OPEN_HOURS_PER_WEEK
- HOBBYIST_PROB
- COMMITTED_ARTIST_PROB
- PRODUCTION_POTTER_PROB
- SEASONAL_USER_PROB
- INSURANCE_COST
- UTILITIES_BASE_COST
- CLAY_PRICE_PER_BAG
- FIRING_BASE_RATE
- REFERENCE_PRICE
- LOAN_504_ANNUAL_RATE
- LOAN_7A_ANNUAL_RATE
- IO_MONTHS_504
- IO_MONTHS_7A

ADVANCED (tier=ParameterTier.ADVANCED) - Everything else (~120+ parameters)
- All churn rates by archetype
- All session hours/frequencies
- All clay usage ranges
- All workshop details
- All class details
- All event details
- All market dynamics
- All seasonality
- All economic factors
- All elasticity
- etc.
"""