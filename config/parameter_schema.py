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

from typing import Dict
from config.parameter_schema import Parameter, ParameterType, ParameterTier

PARAMETERS: Dict[str, Parameter] = {
    "RENT": Parameter(
        name="RENT",
        type=ParameterType.FLOAT,
        default=3500,
        min=1000,
        max=15000,
        step=100,
        tier=ParameterTier.ESSENTIAL,
        group="business_fundamentals",
        label="Monthly Base Rent ($)",
        help="Fixed monthly rent payment for studio space. Directly impacts fixed costs and loan sizing calculations. Higher rent increases breakeven time and cash requirements.",
        affects=[]
    ),

    "RENT_GROWTH_PCT": Parameter(
        name="RENT_GROWTH_PCT",
        type=ParameterType.FLOAT,
        default=0.03,
        min=0.0,
        max=0.15,
        step=0.005,
        tier=ParameterTier.ADVANCED,
        group="business_fundamentals",
        label="Annual Rent Growth Rate",
        help="Yearly rent escalation as a decimal (0.03 = 3%). Compounds annually and affects long-term cash flow projections. Many leases include 2-4% annual increases.",
        affects=[]
    ),

    "OWNER_DRAW": Parameter(
        name="OWNER_DRAW",
        type=ParameterType.FLOAT,
        default=2000,
        min=0,
        max=8000,
        step=100,
        tier=ParameterTier.ESSENTIAL,
        group="business_fundamentals",
        label="Owner Monthly Draw ($)",
        help="Monthly cash withdrawal for owner living expenses. Reduces business cash flow and affects loan sizing. Set to 0 if owner takes no regular draw.",
        affects=[]
    ),

    "OWNER_DRAW_START_MONTH": Parameter(
        name="OWNER_DRAW_START_MONTH",
        type=ParameterType.INT,
        default=1,
        min=1,
        max=24,
        step=1,
        tier=ParameterTier.ADVANCED,
        group="business_fundamentals",
        label="Owner Draw Start Month",
        help="Month when owner draw payments begin (1-based). Allows deferring owner compensation during startup phase to preserve cash.",
        affects=[]
    ),

    "PRODUCTION_POTTER_SESSIONS_PER_WEEK": Parameter(
        name="PRODUCTION_POTTER_SESSIONS_PER_WEEK",
        type=ParameterType.FLOAT,
        default=3.5,
        min=0.1,
        max=10.0,
        step=0.1,
        tier=ParameterTier.ADVANCED,
        group="member_behavior",
        label="Production Potter Sessions/Week",
        help="Average studio sessions per week for production potter members. Highest usage, may constrain capacity for other members.",
        affects=[]
    ),

    "SEASONAL_USER_SESSIONS_PER_WEEK": Parameter(
        name="SEASONAL_USER_SESSIONS_PER_WEEK",
        type=ParameterType.FLOAT,
        default=0.75,
        min=0.1,
        max=5.0,
        step=0.1,
        tier=ParameterTier.ADVANCED,
        group="member_behavior",
        label="Seasonal User Sessions/Week",
        help="Average studio sessions per week for seasonal user members. Lower usage reflects casual engagement level.",
        affects=[]
    ),

    "HOBBYIST_SESSION_HOURS": Parameter(
        name="HOBBYIST_SESSION_HOURS",
        type=ParameterType.FLOAT,
        default=1.7,
        min=0.5,
        max=8.0,
        step=0.1,
        tier=ParameterTier.ADVANCED,
        group="member_behavior",
        label="Hobbyist Hours/Session",
        help="Average hours per studio session for hobbyist members. Shorter sessions allow more members to use equipment during peak times.",
        affects=[]
    ),

    "COMMITTED_ARTIST_SESSION_HOURS": Parameter(
        name="COMMITTED_ARTIST_SESSION_HOURS",
        type=ParameterType.FLOAT,
        default=2.75,
        min=0.5,
        max=8.0,
        step=0.1,
        tier=ParameterTier.ADVANCED,
        group="member_behavior",
        label="Committed Artist Hours/Session",
        help="Average hours per studio session for committed artist members. Longer sessions reflect deeper engagement with projects.",
        affects=[]
    ),

    "PRODUCTION_POTTER_SESSION_HOURS": Parameter(
        name="PRODUCTION_POTTER_SESSION_HOURS",
        type=ParameterType.FLOAT,
        default=3.8,
        min=0.5,
        max=12.0,
        step=0.1,
        tier=ParameterTier.ADVANCED,
        group="member_behavior",
        label="Production Potter Hours/Session",
        help="Average hours per studio session for production potter members. Longest sessions due to commercial production needs.",
        affects=[]
    ),

    "SEASONAL_USER_SESSION_HOURS": Parameter(
        name="SEASONAL_USER_SESSION_HOURS",
        type=ParameterType.FLOAT,
        default=2.0,
        min=0.5,
        max=8.0,
        step=0.1,
        tier=ParameterTier.ADVANCED,
        group="member_behavior",
        label="Seasonal User Hours/Session",
        help="Average hours per studio session for seasonal user members. Moderate duration typical of casual engagement.",
        affects=[]
    ),

    "MAX_MEMBERS": Parameter(
        name="MAX_MEMBERS",
        type=ParameterType.INT,
        default=77,
        min=20,
        max=500,
        step=5,
        tier=ParameterTier.ESSENTIAL,
        group="capacity",
        label="Maximum Members (Hard Cap)",
        help="Absolute maximum members the studio can accommodate. Based on physical space, storage, and operational constraints. Acts as hard limit on growth.",
        affects=[]
    ),

    "OPEN_HOURS_PER_WEEK": Parameter(
        name="OPEN_HOURS_PER_WEEK",
        type=ParameterType.INT,
        default=112,
        min=20,
        max=168,
        step=4,
        tier=ParameterTier.IMPORTANT,
        group="capacity",
        label="Studio Open Hours/Week",
        help="Total weekly hours studio is accessible to members. Affects capacity calculations - more hours = more member capacity for same equipment.",
        affects=[]
    ),

    "CAPACITY_DAMPING_BETA": Parameter(
        name="CAPACITY_DAMPING_BETA",
        type=ParameterType.FLOAT,
        default=4.0,
        min=1.0,
        max=10.0,
        step=0.5,
        tier=ParameterTier.ADVANCED,
        group="capacity",
        label="Capacity Damping Factor",
        help="Controls how crowding reduces new member joins. Higher values = sharper drop in joins as studio gets crowded. 4.0 means severe impact near capacity.",
        affects=[]
    ),

    "UTILIZATION_CHURN_UPLIFT": Parameter(
        name="UTILIZATION_CHURN_UPLIFT",
        type=ParameterType.FLOAT,
        default=0.25,
        min=0.0,
        max=1.0,
        step=0.05,
        tier=ParameterTier.ADVANCED,
        group="capacity",
        label="Overcrowding Churn Multiplier",
        help="Additional churn when studio is over capacity. 0.25 means 25% higher churn when 100% utilized. Models member frustration with crowding.",
        affects=[]
    ),

    "WHEELS_CAPACITY": Parameter(
        name="WHEELS_CAPACITY",
        type=ParameterType.INT,
        default=8,
        min=2,
        max=30,
        step=1,
        tier=ParameterTier.IMPORTANT,
        group="capacity",
        label="Pottery Wheels Count",
        help="Number of pottery wheels available. Often the limiting factor for member capacity since wheels are used by all archetypes.",
        affects=[]
    ),

    "HANDBUILDING_CAPACITY": Parameter(
        name="HANDBUILDING_CAPACITY",
        type=ParameterType.INT,
        default=6,
        min=2,
        max=50,
        step=1,
        tier=ParameterTier.IMPORTANT,
        group="capacity",
        label="Handbuilding Stations Count",
        help="Number of handbuilding workstations. Used for sculpture, handbuilding, and surface decoration work.",
        affects=[]
    ),

    "GLAZE_CAPACITY": Parameter(
        name="GLAZE_CAPACITY",
        type=ParameterType.INT,
        default=6,
        min=2,
        max=20,
        step=1,
        tier=ParameterTier.IMPORTANT,
        group="capacity",
        label="Glazing Workstations Count",
        help="Number of glazing workstations. Bottleneck station in many studios since all fired work needs glazing.",
        affects=[]
    ),

    "WHEELS_ALPHA": Parameter(
        name="WHEELS_ALPHA",
        type=ParameterType.FLOAT,
        default=0.80,
        min=0.1,
        max=1.0,
        step=0.05,
        tier=ParameterTier.ADVANCED,
        group="capacity",
        label="Wheels Utilization Efficiency",
        help="Fraction of wheel capacity actually usable (accounting for maintenance, setup time, etc.). 0.80 = 80% effective utilization.",
        affects=[]
    ),

    "HANDBUILDING_ALPHA": Parameter(
        name="HANDBUILDING_ALPHA",
        type=ParameterType.FLOAT,
        default=0.50,
        min=0.1,
        max=1.0,
        step=0.05,
        tier=ParameterTier.ADVANCED,
        group="capacity",
        label="Handbuilding Utilization Efficiency",
        help="Fraction of handbuilding capacity actually usable. Lower than wheels due to variable project sizes and cleanup time.",
        affects=[]
    ),

    "GLAZE_ALPHA": Parameter(
        name="GLAZE_ALPHA",
        type=ParameterType.FLOAT,
        default=0.55,
        min=0.1,
        max=1.0,
        step=0.05,
        tier=ParameterTier.ADVANCED,
        group="capacity",
        label="Glazing Utilization Efficiency",
        help="Fraction of glazing capacity actually usable. Accounts for drying time, glaze prep, and safety procedures.",
        affects=[]
    ),
    "OWNER_DRAW_END_MONTH": Parameter(
        name="OWNER_DRAW_END_MONTH",
        type=ParameterType.INT,
        default=12,
        min=1,
        max=60,
        step=1,
        tier=ParameterTier.ADVANCED,
        group="business_fundamentals",
        label="Owner Draw End Month (None=60)",
        help="Last month of owner draw payments. Enter 60 for unlimited. Useful for modeling temporary owner sacrifice during startup.",
        affects=[]
    ),

    "OWNER_STIPEND_MONTHS": Parameter(
        name="OWNER_STIPEND_MONTHS",
        type=ParameterType.INT,
        default=12,
        min=0,
        max=60,
        step=1,
        tier=ParameterTier.ADVANCED,
        group="business_fundamentals",
        label="Owner Stipend Duration (months)",
        help="Total months of owner draw to reserve in cash planning. Even if draw window is longer, only this many months are included in loan sizing.",
        affects=[]
    ),

    "PRICE": Parameter(
        name="PRICE",
        type=ParameterType.FLOAT,
        default=175,
        min=80,
        max=400,
        step=5,
        tier=ParameterTier.ESSENTIAL,
        group="pricing",
        label="Monthly Membership Price ($)",
        help="Base monthly membership fee charged to all new members. Affects both revenue and member acquisition/retention through price elasticity effects.",
        affects=[]
    ),

    "REFERENCE_PRICE": Parameter(
        name="REFERENCE_PRICE",
        type=ParameterType.FLOAT,
        default=165,
        min=80,
        max=400,
        step=5,
        tier=ParameterTier.IMPORTANT,
        group="pricing",
        label="Market Reference Price ($)",
        help="Competitive baseline price for elasticity calculations. If your price is above this, expect lower join rates and higher churn. Use local market research to set this.",
        affects=[]
    ),

    "JOIN_PRICE_ELASTICITY": Parameter(
        name="JOIN_PRICE_ELASTICITY",
        type=ParameterType.FLOAT,
        default=-0.6,
        min=-3.0,
        max=0.0,
        step=0.1,
        tier=ParameterTier.ADVANCED,
        group="pricing",
        label="Join Price Elasticity",
        help="How sensitive potential members are to pricing. -0.6 means 10% price increase reduces joins by 6%. More negative = more price sensitive market.",
        affects=[]
    ),

    "CHURN_PRICE_ELASTICITY": Parameter(
        name="CHURN_PRICE_ELASTICITY",
        type=ParameterType.FLOAT,
        default=0.3,
        min=0.0,
        max=2.0,
        step=0.1,
        tier=ParameterTier.ADVANCED,
        group="pricing",
        label="Churn Price Elasticity",
        help="How pricing affects member retention. 0.3 means 10% price increase increases churn by 3%. Higher values = more price-sensitive retention.",
        affects=[]
    ),

    "HOBBYIST_PROB": Parameter(
        name="HOBBYIST_PROB",
        type=ParameterType.FLOAT,
        default=0.35,
        min=0.0,
        max=1.0,
        step=0.05,
        tier=ParameterTier.IMPORTANT,
        group="member_behavior",
        label="Hobbyist Mix %",
        help="Fraction of new members who are hobbyists. Casual users with lower usage and higher churn. Affects revenue per member and capacity utilization.",
        affects=[]
    ),

    "COMMITTED_ARTIST_PROB": Parameter(
        name="COMMITTED_ARTIST_PROB",
        type=ParameterType.FLOAT,
        default=0.40,
        min=0.0,
        max=1.0,
        step=0.05,
        tier=ParameterTier.IMPORTANT,
        group="member_behavior",
        label="Committed Artist Mix %",
        help="Fraction of new members who are committed artists. Regular users with moderate usage and churn. Core revenue base for most studios.",
        affects=[]
    ),

    "PRODUCTION_POTTER_PROB": Parameter(
        name="PRODUCTION_POTTER_PROB",
        type=ParameterType.FLOAT,
        default=0.10,
        min=0.0,
        max=1.0,
        step=0.05,
        tier=ParameterTier.IMPORTANT,
        group="member_behavior",
        label="Production Potter Mix %",
        help="Fraction of new members who are production potters. Heavy users with low churn but high capacity consumption. Valuable but space-intensive.",
        affects=[]
    ),

    "SEASONAL_USER_PROB": Parameter(
        name="SEASONAL_USER_PROB",
        type=ParameterType.FLOAT,
        default=0.15,
        min=0.0,
        max=1.0,
        step=0.05,
        tier=ParameterTier.IMPORTANT,
        group="member_behavior",
        label="Seasonal User Mix %",
        help="Fraction of new members who are seasonal users. Irregular usage with very high churn. Often driven by gift memberships or temporary interest.",
        affects=[]
    ),

    "ARCHETYPE_CHURN_HOBBYIST": Parameter(
        name="ARCHETYPE_CHURN_HOBBYIST",
        type=ParameterType.FLOAT,
        default=0.049 * 0.95,
        min=0.01,
        max=0.30,
        step=0.005,
        tier=ParameterTier.ADVANCED,
        group="member_behavior",
        label="Hobbyist Monthly Churn Rate",
        help="Base monthly churn probability for hobbyist members. Modified by tenure, pricing, and economic conditions. Typical range 3-8% monthly.",
        affects=[]
    ),

    "ARCHETYPE_CHURN_COMMITTED_ARTIST": Parameter(
        name="ARCHETYPE_CHURN_COMMITTED_ARTIST",
        type=ParameterType.FLOAT,
        default=0.049 * 0.80,
        min=0.01,
        max=0.30,
        step=0.005,
        tier=ParameterTier.ADVANCED,
        group="member_behavior",
        label="Committed Artist Monthly Churn Rate",
        help="Base monthly churn probability for committed artist members. Generally lower than hobbyists due to higher engagement.",
        affects=[]
    ),

    "ARCHETYPE_CHURN_PRODUCTION_POTTER": Parameter(
        name="ARCHETYPE_CHURN_PRODUCTION_POTTER",
        type=ParameterType.FLOAT,
        default=0.049 * 0.65,
        min=0.01,
        max=0.30,
        step=0.005,
        tier=ParameterTier.ADVANCED,
        group="member_behavior",
        label="Production Potter Monthly Churn Rate",
        help="Base monthly churn probability for production potter members. Lowest churn due to business dependency on studio access.",
        affects=[]
    ),

    "ARCHETYPE_CHURN_SEASONAL_USER": Parameter(
        name="ARCHETYPE_CHURN_SEASONAL_USER",
        type=ParameterType.FLOAT,
        default=0.049 * 1.90,
        min=0.01,
        max=0.50,
        step=0.005,
        tier=ParameterTier.ADVANCED,
        group="member_behavior",
        label="Seasonal User Monthly Churn Rate",
        help="Base monthly churn probability for seasonal user members. Highest churn due to temporary or gift-based engagement.",
        affects=[]
    ),

    "HOBBYIST_SESSIONS_PER_WEEK": Parameter(
        name="HOBBYIST_SESSIONS_PER_WEEK",
        type=ParameterType.FLOAT,
        default=1.0,
        min=0.1,
        max=5.0,
        step=0.1,
        tier=ParameterTier.ADVANCED,
        group="member_behavior",
        label="Hobbyist Sessions/Week",
        help="Average studio sessions per week for hobbyist members. Affects capacity utilization calculations and revenue from add-on services.",
        affects=[]
    ),

    "COMMITTED_ARTIST_SESSIONS_PER_WEEK": Parameter(
        name="COMMITTED_ARTIST_SESSIONS_PER_WEEK",
        type=ParameterType.FLOAT,
        default=1.5,
        min=0.1,
        max=5.0,
        step=0.1,
        tier=ParameterTier.ADVANCED,
        group="member_behavior",
        label="Committed Artist Sessions/Week",
        help="Average studio sessions per week for committed artist members. Higher usage drives more clay sales and firing fees.",
        affects=[]
    ),

    "NO_ACCESS_POOL": Parameter(
        name="NO_ACCESS_POOL",
        type=ParameterType.INT,
        default=20,
        min=0,
        max=1000,
        step=10,
        tier=ParameterTier.ADVANCED,
        group="market_dynamics",
        label="No-Access Market Pool Size",
        help="People in your market who have no current pottery access. Most motivated to join but need discovery. Size depends on local population.",
        affects=[]
    ),

    "HOME_POOL": Parameter(
        name="HOME_POOL",
        type=ParameterType.INT,
        default=50,
        min=0,
        max=1000,
        step=10,
        tier=ParameterTier.ADVANCED,
        group="market_dynamics",
        label="Home Studio Market Pool Size",
        help="People with home pottery setups. Less motivated to join due to existing access. May join for community, equipment, or firing access.",
        affects=[]
    ),

    "COMMUNITY_POOL": Parameter(
        name="COMMUNITY_POOL",
        type=ParameterType.INT,
        default=70,
        min=0,
        max=1000,
        step=10,
        tier=ParameterTier.ADVANCED,
        group="market_dynamics",
        label="Community Studio Market Pool Size",
        help="People currently using other community studios. May switch if you offer better value/location/community. Existing pottery experience.",
        affects=[]
    ),

    "NO_ACCESS_INFLOW": Parameter(
        name="NO_ACCESS_INFLOW",
        type=ParameterType.INT,
        default=3,
        min=0,
        max=50,
        step=1,
        tier=ParameterTier.ADVANCED,
        group="market_dynamics",
        label="No-Access Monthly Inflow",
        help="New people entering the no-access pool each month (moved to area, developed interest, etc.). Sustains long-term member acquisition.",
        affects=[]
    ),

    "HOME_INFLOW": Parameter(
        name="HOME_INFLOW",
        type=ParameterType.INT,
        default=2,
        min=0,
        max=50,
        step=1,
        tier=ParameterTier.ADVANCED,
        group="market_dynamics",
        label="Home Studio Monthly Inflow",
        help="People setting up home studios monthly. May eventually seek community/professional equipment. Usually pottery enthusiasts.",
        affects=[]
    ),

    "COMMUNITY_INFLOW": Parameter(
        name="COMMUNITY_INFLOW",
        type=ParameterType.INT,
        default=4,
        min=0,
        max=50,
        step=1,
        tier=ParameterTier.ADVANCED,
        group="market_dynamics",
        label="Community Studio Monthly Inflow",
        help="People joining other studios monthly. Potential switchers if dissatisfied with current studio. Higher intent but harder to reach.",
        affects=[]
    ),

    "BASELINE_RATE_NO_ACCESS": Parameter(
        name="BASELINE_RATE_NO_ACCESS",
        type=ParameterType.FLOAT,
        default=0.040,
        min=0.0,
        max=0.2,
        step=0.005,
        tier=ParameterTier.ADVANCED,
        group="market_dynamics",
        label="No-Access Monthly Join Rate",
        help="Base probability that a no-access person joins per month. Modified by marketing, pricing, capacity, and economic factors.",
        affects=[]
    ),

    "BASELINE_RATE_HOME": Parameter(
        name="BASELINE_RATE_HOME",
        type=ParameterType.FLOAT,
        default=0.010,
        min=0.0,
        max=0.1,
        step=0.005,
        tier=ParameterTier.ADVANCED,
        group="market_dynamics",
        label="Home Studio Monthly Join Rate",
        help="Base probability that a home studio person joins per month. Lower due to existing access, but may join for community/equipment.",
        affects=[]
    ),

    "BASELINE_RATE_COMMUNITY": Parameter(
        name="BASELINE_RATE_COMMUNITY",
        type=ParameterType.FLOAT,
        default=0.100,
        min=0.0,
        max=0.3,
        step=0.005,
        tier=ParameterTier.ADVANCED,
        group="market_dynamics",
        label="Community Studio Monthly Join Rate",
        help="Base probability that a person at another studio switches per month. Higher due to existing pottery commitment and switching motivations.",
        affects=[]
    ),

    "WOM_Q": Parameter(
        name="WOM_Q",
        type=ParameterType.FLOAT,
        default=0.60,
        min=0.0,
        max=2.0,
        step=0.05,
        tier=ParameterTier.ADVANCED,
        group="market_dynamics",
        label="Word-of-Mouth Amplification Factor",
        help="How much word-of-mouth boosts join rates. 0.6 with 60 members near saturation doubles join rates. Higher = stronger community effect.",
        affects=[]
    ),

    "WOM_SATURATION": Parameter(
        name="WOM_SATURATION",
        type=ParameterType.INT,
        default=60,
        min=20,
        max=200,
        step=5,
        tier=ParameterTier.ADVANCED,
        group="market_dynamics",
        label="Word-of-Mouth Saturation Point",
        help="Member count where WOM effect peaks. Beyond this, additional members provide diminishing word-of-mouth returns. Market size dependent.",
        affects=[]
    ),

    "REFERRAL_RATE_PER_MEMBER": Parameter(
        name="REFERRAL_RATE_PER_MEMBER",
        type=ParameterType.FLOAT,
        default=0.06,
        min=0.0,
        max=0.3,
        step=0.01,
        tier=ParameterTier.ADVANCED,
        group="market_dynamics",
        label="Monthly Referral Rate per Member",
        help="Probability each member generates a referral per month. 0.06 = 6% chance per member monthly. Drives organic growth through direct recommendations.",
        affects=[]
    ),

    "REFERRAL_CONV": Parameter(
        name="REFERRAL_CONV",
        type=ParameterType.FLOAT,
        default=0.22,
        min=0.0,
        max=1.0,
        step=0.05,
        tier=ParameterTier.ADVANCED,
        group="market_dynamics",
        label="Referral Conversion Rate",
        help="Probability that a referral becomes a member. Higher than cold prospects due to friend recommendation and fit pre-screening.",
        affects=[]
    ),

    "AWARENESS_RAMP_MONTHS": Parameter(
        name="AWARENESS_RAMP_MONTHS",
        type=ParameterType.INT,
        default=4,
        min=1,
        max=24,
        step=1,
        tier=ParameterTier.ADVANCED,
        group="market_dynamics",
        label="Awareness Ramp Duration (months)",
        help="Months to reach full market awareness. Longer ramp = slower initial growth but models realistic awareness building in new markets.",
        affects=[]
    ),

    "AWARENESS_RAMP_START_MULT": Parameter(
        name="AWARENESS_RAMP_START_MULT",
        type=ParameterType.FLOAT,
        default=0.5,
        min=0.1,
        max=1.0,
        step=0.05,
        tier=ParameterTier.ADVANCED,
        group="market_dynamics",
        label="Starting Awareness Level",
        help="Market awareness at launch as fraction of eventual level. 0.5 = 50% awareness at start, ramping to 100% over ramp period.",
        affects=[]
    ),

    "AWARENESS_RAMP_END_MULT": Parameter(
        name="AWARENESS_RAMP_END_MULT",
        type=ParameterType.FLOAT,
        default=1.0,
        min=0.5,
        max=2.0,
        step=0.05,
        tier=ParameterTier.ADVANCED,
        group="market_dynamics",
        label="Peak Awareness Level",
        help="Maximum market awareness as multiplier. 1.0 = normal market penetration, >1.0 = exceptional awareness (strong marketing/PR).",
        affects=[]
    ),

    "ADOPTION_SIGMA": Parameter(
        name="ADOPTION_SIGMA",
        type=ParameterType.FLOAT,
        default=0.20,
        min=0.0,
        max=1.0,
        step=0.05,
        tier=ParameterTier.ADVANCED,
        group="market_dynamics",
        label="Adoption Noise Factor",
        help="Random variation in monthly adoption (lognormal sigma). 0.20 adds realistic month-to-month variation. Higher = more volatile growth.",
        affects=[]
    ),

    "CLASS_TERM_MONTHS": Parameter(
        name="CLASS_TERM_MONTHS",
        type=ParameterType.INT,
        default=3,
        min=1,
        max=12,
        step=1,
        tier=ParameterTier.ADVANCED,
        group="market_dynamics",
        label="Class Term Length (months)",
        help="How often community studio members can switch (class graduation cycles). 3 months = quarterly switching opportunities.",
        affects=[]
    ),

    "CS_UNLOCK_FRACTION_PER_TERM": Parameter(
        name="CS_UNLOCK_FRACTION_PER_TERM",
        type=ParameterType.FLOAT,
        default=0.25,
        min=0.0,
        max=1.0,
        step=0.05,
        tier=ParameterTier.ADVANCED,
        group="market_dynamics",
        label="Community Studio Unlock Rate",
        help="Fraction of remaining CS pool eligible to switch each term. 0.25 = 25% of remaining pool becomes available every term cycle.",
        affects=[]
    ),

    "MAX_ONBOARDINGS_PER_MONTH": Parameter(
        name="MAX_ONBOARDINGS_PER_MONTH",
        type=ParameterType.INT,
        default=10,
        min=1,
        max=100,
        step=1,
        tier=ParameterTier.ADVANCED,
        group="operations",
        label="Max New Members/Month",
        help="Operational limit on monthly new member onboarding. Accounts for orientation capacity, key cutting, etc. None = unlimited.",
        affects=[]
    ),

    "DOWNTURN_PROB_PER_MONTH": Parameter(
        name="DOWNTURN_PROB_PER_MONTH",
        type=ParameterType.FLOAT,
        default=0.01,
        min=0.0,
        max=0.2,
        step=0.005,
        tier=ParameterTier.ADVANCED,
        group="economy",
        label="Monthly Downturn Probability",
        help="Probability of an economic downturn event each month. Downturns temporarily reduce joins and may increase churn.",
        affects=[]
    ),

    "DOWNTURN_SEVERITY": Parameter(
        name="DOWNTURN_SEVERITY",
        type=ParameterType.FLOAT,
        default=0.30,
        min=0.0,
        max=1.0,
        step=0.05,
        tier=ParameterTier.ADVANCED,
        group="economy",
        label="Downturn Severity Level",
        help="Fractional reduction in join and referral rates during downturns. 0.30 = 30% drop in demand during downturn months.",
        affects=[]
    ),

    "DOWNTURN_DURATION_MEAN": Parameter(
        name="DOWNTURN_DURATION_MEAN",
        type=ParameterType.FLOAT,
        default=4.0,
        min=1.0,
        max=24.0,
        step=0.5,
        tier=ParameterTier.ADVANCED,
        group="economy",
        label="Downturn Duration Mean (months)",
        help="Average duration of downturn events in months. Affects how long economic shocks last in the simulation.",
        affects=[]
    ),

    "DOWNTURN_DURATION_SD": Parameter(
        name="DOWNTURN_DURATION_SD",
        type=ParameterType.FLOAT,
        default=1.5,
        min=0.0,
        max=12.0,
        step=0.5,
        tier=ParameterTier.ADVANCED,
        group="economy",
        label="Downturn Duration Variability",
        help="Standard deviation of downturn durations. Higher values create more unpredictable economic cycles.",
        affects=[]
    ),

    "RECOVERY_BOOST": Parameter(
        name="RECOVERY_BOOST",
        type=ParameterType.FLOAT,
        default=0.10,
        min=0.0,
        max=0.5,
        step=0.01,
        tier=ParameterTier.ADVANCED,
        group="economy",
        label="Post-Downturn Recovery Boost",
        help="Increase in join probability for a few months after downturns. Captures pent-up demand and rebound effects.",
        affects=[]
    ),

    "RECOVERY_MONTHS": Parameter(
        name="RECOVERY_MONTHS",
        type=ParameterType.INT,
        default=2,
        min=0,
        max=12,
        step=1,
        tier=ParameterTier.ADVANCED,
        group="economy",
        label="Recovery Boost Duration",
        help="How many months the recovery boost lasts after a downturn.",
        affects=[]
    ),

    "SEASONALITY_JAN": Parameter(
        name="SEASONALITY_JAN",
        type=ParameterType.FLOAT,
        default=1.15,
        min=0.2,
        max=2.0,
        step=0.05,
        tier=ParameterTier.ADVANCED,
        group="seasonality",
        label="January Seasonality Factor",
        help="Join rate multiplier for January. Typically high due to 'new year' energy and hobby interest.",
        affects=[]
    ),

    "SEASONALITY_FEB": Parameter(
        name="SEASONALITY_FEB",
        type=ParameterType.FLOAT,
        default=1.05,
        min=0.2,
        max=2.0,
        step=0.05,
        tier=ParameterTier.ADVANCED,
        group="seasonality",
        label="February Seasonality Factor",
        help="Join rate multiplier for February. Usually steady, with some post-new-year energy remaining.",
        affects=[]
    ),

    "SEASONALITY_MAR": Parameter(
        name="SEASONALITY_MAR",
        type=ParameterType.FLOAT,
        default=1.10,
        min=0.2,
        max=2.0,
        step=0.05,
        tier=ParameterTier.ADVANCED,
        group="seasonality",
        label="March Seasonality Factor",
        help="Join rate multiplier for March. Often stronger due to improving weather and spring activity planning.",
        affects=[]
    ),

    "SEASONALITY_APR": Parameter(
        name="SEASONALITY_APR",
        type=ParameterType.FLOAT,
        default=1.08,
        min=0.2,
        max=2.0,
        step=0.05,
        tier=ParameterTier.ADVANCED,
        group="seasonality",
        label="April Seasonality Factor",
        help="Join rate multiplier for April. Spring increases hobby interest and recreational enrollment.",
        affects=[]
    ),

    "SEASONALITY_MAY": Parameter(
        name="SEASONALITY_MAY",
        type=ParameterType.FLOAT,
        default=0.95,
        min=0.2,
        max=2.0,
        step=0.05,
        tier=ParameterTier.ADVANCED,
        group="seasonality",
        label="May Seasonality Factor",
        help="Join rate multiplier for May. Often dips slightly as people shift to outdoor activities.",
        affects=[]
    ),

    "SEASONALITY_JUN": Parameter(
        name="SEASONALITY_JUN",
        type=ParameterType.FLOAT,
        default=0.85,
        min=0.2,
        max=2.0,
        step=0.05,
        tier=ParameterTier.ADVANCED,
        group="seasonality",
        label="June Seasonality Factor",
        help="Join rate multiplier for June. Summer drop-off begins as members travel or engage in outdoor hobbies.",
        affects=[]
    ),

    "SEASONALITY_JUL": Parameter(
        name="SEASONALITY_JUL",
        type=ParameterType.FLOAT,
        default=0.80,
        min=0.2,
        max=2.0,
        step=0.05,
        tier=ParameterTier.ADVANCED,
        group="seasonality",
        label="July Seasonality Factor",
        help="Join rate multiplier for July. Typically lowest joining month due to travel and outdoor activity preferences.",
        affects=[]
    ),

    "SEASONALITY_AUG": Parameter(
        name="SEASONALITY_AUG",
        type=ParameterType.FLOAT,
        default=0.90,
        min=0.2,
        max=2.0,
        step=0.05,
        tier=ParameterTier.ADVANCED,
        group="seasonality",
        label="August Seasonality Factor",
        help="Join rate multiplier for August. Slight rebound as people return from summer trips.",
        affects=[]
    ),

    "SEASONALITY_SEP": Parameter(
        name="SEASONALITY_SEP",
        type=ParameterType.FLOAT,
        default=1.20,
        min=0.2,
        max=2.0,
        step=0.05,
        tier=ParameterTier.ADVANCED,
        group="seasonality",
        label="September Seasonality Factor",
        help="Join rate multiplier for September. Strong back-to-routine effect and fall class enrollment.",
        affects=[]
    ),

    "SEASONALITY_OCT": Parameter(
        name="SEASONALITY_OCT",
        type=ParameterType.FLOAT,
        default=1.10,
        min=0.2,
        max=2.0,
        step=0.05,
        tier=ParameterTier.ADVANCED,
        group="seasonality",
        label="October Seasonality Factor",
        help="Join rate multiplier for October. Generally strong month for creative and indoor activities.",
        affects=[]
    ),

    "SEASONALITY_NOV": Parameter(
        name="SEASONALITY_NOV",
        type=ParameterType.FLOAT,
        default=0.98,
        min=0.2,
        max=2.0,
        step=0.05,
        tier=ParameterTier.ADVANCED,
        group="seasonality",
        label="November Seasonality Factor",
        help="Join rate multiplier for November. Slight slowing as holidays approach.",
        affects=[]
    ),

    "SEASONALITY_DEC": Parameter(
        name="SEASONALITY_DEC",
        type=ParameterType.FLOAT,
        default=0.75,
        min=0.2,
        max=2.0,
        step=0.05,
        tier=ParameterTier.ADVANCED,
        group="seasonality",
        label="December Seasonality Factor",
        help="Join rate multiplier for December. Significant slowdown due to holidays and reduced discretionary time.",
        affects=[]
    ),

    "RETAIL_CLAY_PRICE_PER_BAG": Parameter(
        name="RETAIL_CLAY_PRICE_PER_BAG",
        type=ParameterType.FLOAT,
        default=25.0,
        min=15.0,
        max=50.0,
        step=1.0,
        tier=ParameterTier.ADVANCED,
        group="clay_firing_revenue",
        label="Retail Clay Price ($/bag)",
        help="Price charged to members per 25lb clay bag. Key add-on revenue stream. Typically marked up 40-60% over wholesale cost.",
        affects=[]
    ),

    "WHOLESALE_CLAY_COST_PER_BAG": Parameter(
        name="WHOLESALE_CLAY_COST_PER_BAG",
        type=ParameterType.FLOAT,
        default=16.75,
        min=8.0,
        max=30.0,
        step=0.25,
        tier=ParameterTier.ADVANCED,
        group="clay_firing_revenue",
        label="Wholesale Clay Cost ($/bag)",
        help="Cost of clay per 25lb bag from supplier. Direct cost of goods sold. Affects profit margin on clay sales to members.",
        affects=[]
    ),

    "HOBBYIST_CLAY_LOW": Parameter(
        name="HOBBYIST_CLAY_LOW",
        type=ParameterType.FLOAT,
        default=0.25,
        min=0.1,
        max=2.0,
        step=0.1,
        tier=ParameterTier.ADVANCED,
        group="clay_firing_revenue",
        label="Hobbyist Clay Usage - Low (bags/month)",
        help="Minimum monthly clay consumption for hobbyist members. Part of triangular distribution modeling usage variation.",
        affects=[]
    ),

    "HOBBYIST_CLAY_TYPICAL": Parameter(
        name="HOBBYIST_CLAY_TYPICAL",
        type=ParameterType.FLOAT,
        default=0.5,
        min=0.1,
        max=3.0,
        step=0.1,
        tier=ParameterTier.ADVANCED,
        group="clay_firing_revenue",
        label="Hobbyist Clay Usage - Typical (bags/month)",
        help="Most common monthly clay consumption for hobbyist members. Peak of triangular distribution.",
        affects=[]
    ),

    "HOBBYIST_CLAY_HIGH": Parameter(
        name="HOBBYIST_CLAY_HIGH",
        type=ParameterType.FLOAT,
        default=1.0,
        min=0.5,
        max=5.0,
        step=0.1,
        tier=ParameterTier.ADVANCED,
        group="clay_firing_revenue",
        label="Hobbyist Clay Usage - High (bags/month)",
        help="Maximum monthly clay consumption for hobbyist members. Upper bound of triangular distribution.",
        affects=[]
    ),

    "COMMITTED_ARTIST_CLAY_LOW": Parameter(
        name="COMMITTED_ARTIST_CLAY_LOW",
        type=ParameterType.FLOAT,
        default=1.0,
        min=0.5,
        max=3.0,
        step=0.1,
        tier=ParameterTier.ADVANCED,
        group="clay_firing_revenue",
        label="Committed Artist Clay Usage - Low (bags/month)",
        help="Minimum monthly clay consumption for committed artist members.",
        affects=[]
    ),

    "COMMITTED_ARTIST_CLAY_TYPICAL": Parameter(
        name="COMMITTED_ARTIST_CLAY_TYPICAL",
        type=ParameterType.FLOAT,
        default=1.5,
        min=0.5,
        max=4.0,
        step=0.1,
        tier=ParameterTier.ADVANCED,
        group="clay_firing_revenue",
        label="Committed Artist Clay Usage - Typical (bags/month)",
        help="Most common monthly clay consumption for committed artist members.",
        affects=[]
    ),

    "COMMITTED_ARTIST_CLAY_HIGH": Parameter(
        name="COMMITTED_ARTIST_CLAY_HIGH",
        type=ParameterType.FLOAT,
        default=2.0,
        min=1.0,
        max=6.0,
        step=0.1,
        tier=ParameterTier.ADVANCED,
        group="clay_firing_revenue",
        label="Committed Artist Clay Usage - High (bags/month)",
        help="Maximum monthly clay consumption for committed artist members.",
        affects=[]
    ),

    "PRODUCTION_POTTER_CLAY_LOW": Parameter(
        name="PRODUCTION_POTTER_CLAY_LOW",
        type=ParameterType.FLOAT,
        default=2.0,
        min=1.0,
        max=5.0,
        step=0.1,
        tier=ParameterTier.ADVANCED,
        group="clay_firing_revenue",
        label="Production Potter Clay Usage - Low (bags/month)",
        help="Minimum monthly clay consumption for production potter members.",
        affects=[]
    ),

    "PRODUCTION_POTTER_CLAY_TYPICAL": Parameter(
        name="PRODUCTION_POTTER_CLAY_TYPICAL",
        type=ParameterType.FLOAT,
        default=2.5,
        min=1.5,
        max=6.0,
        step=0.1,
        tier=ParameterTier.ADVANCED,
        group="clay_firing_revenue",
        label="Production Potter Clay Usage - Typical (bags/month)",
        help="Most common monthly clay consumption for production potter members.",
        affects=[]
    ),

    "PRODUCTION_POTTER_CLAY_HIGH": Parameter(
        name="PRODUCTION_POTTER_CLAY_HIGH",
        type=ParameterType.FLOAT,
        default=3.0,
        min=2.0,
        max=10.0,
        step=0.1,
        tier=ParameterTier.ADVANCED,
        group="clay_firing_revenue",
        label="Production Potter Clay Usage - High (bags/month)",
        help="Maximum monthly clay consumption for production potter members.",
        affects=[]
    ),

    "SEASONAL_USER_CLAY_LOW": Parameter(
        name="SEASONAL_USER_CLAY_LOW",
        type=ParameterType.FLOAT,
        default=0.25,
        min=0.1,
        max=2.0,
        step=0.1,
        tier=ParameterTier.ADVANCED,
        group="clay_firing_revenue",
        label="Seasonal User Clay Usage - Low (bags/month)",
        help="Minimum monthly clay consumption for seasonal user members.",
        affects=[]
    ),

    "SEASONAL_USER_CLAY_TYPICAL": Parameter(
        name="SEASONAL_USER_CLAY_TYPICAL",
        type=ParameterType.FLOAT,
        default=0.5,
        min=0.1,
        max=3.0,
        step=0.1,
        tier=ParameterTier.ADVANCED,
        group="clay_firing_revenue",
        label="Seasonal User Clay Usage - Typical (bags/month)",
        help="Most common monthly clay consumption for seasonal user members.",
        affects=[]
    ),

    "SEASONAL_USER_CLAY_HIGH": Parameter(
        name="SEASONAL_USER_CLAY_HIGH",
        type=ParameterType.FLOAT,
        default=1.0,
        min=0.5,
        max=5.0,
        step=0.1,
        tier=ParameterTier.ADVANCED,
        group="clay_firing_revenue",
        label="Seasonal User Clay Usage - High (bags/month)",
        help="Maximum monthly clay consumption for seasonal user members.",
        affects=[]
    ),

    # =============================================================================
    # REVENUE: WORKSHOPS
    # =============================================================================
    "WORKSHOPS_ENABLED": Parameter(
        name="WORKSHOPS_ENABLED",
        type=ParameterType.BOOL,
        default=True,
        tier=ParameterTier.IMPORTANT,
        group="workshops",
        label="Enable Workshop Revenue Stream",
        help="Whether studio offers short pottery workshops for beginners. Key revenue and member acquisition channel for many studios.",
        affects=[]
    ),

    "WORKSHOPS_PER_MONTH": Parameter(
        name="WORKSHOPS_PER_MONTH",
        type=ParameterType.FLOAT,
        default=2.0,
        min=0.0,
        max=20.0,
        step=0.5,
        tier=ParameterTier.ADVANCED,
        group="workshops",
        label="Workshops per Month",
        help="Average number of workshops offered monthly. More workshops = more revenue but requires instructor time and capacity.",
        affects=[]
    ),

    "WORKSHOP_AVG_ATTENDANCE": Parameter(
        name="WORKSHOP_AVG_ATTENDANCE",
        type=ParameterType.INT,
        default=10,
        min=1,
        max=30,
        step=1,
        tier=ParameterTier.ADVANCED,
        group="workshops",
        label="Average Workshop Attendance",
        help="Typical number of participants per workshop. Limited by space and instructor capacity.",
        affects=[]
    ),

    "WORKSHOP_FEE": Parameter(
        name="WORKSHOP_FEE",
        type=ParameterType.FLOAT,
        default=75.0,
        min=20.0,
        max=150.0,
        step=5.0,
        tier=ParameterTier.ADVANCED,
        group="workshops",
        label="Workshop Fee per Person ($)",
        help="Price charged per workshop participant. Key revenue driver - should cover materials, instructor time, and profit margin.",
        affects=[]
    ),

    "WORKSHOP_COST_PER_EVENT": Parameter(
        name="WORKSHOP_COST_PER_EVENT",
        type=ParameterType.FLOAT,
        default=50.0,
        min=0.0,
        max=500.0,
        step=10.0,
        tier=ParameterTier.ADVANCED,
        group="workshops",
        label="Workshop Variable Cost per Event ($)",
        help="Direct costs per workshop: instructor pay, materials, cleanup. Subtracted from gross revenue to get net contribution.",
        affects=[]
    ),

    "WORKSHOP_CONV_RATE": Parameter(
        name="WORKSHOP_CONV_RATE",
        type=ParameterType.FLOAT,
        default=0.12,
        min=0.0,
        max=0.5,
        step=0.01,
        tier=ParameterTier.ADVANCED,
        group="workshops",
        label="Workshop to Member Conversion Rate",
        help="Fraction of workshop participants who become members. Key metric - workshops as member acquisition funnel.",
        affects=[]
    ),

    "WORKSHOP_CONV_LAG_MO": Parameter(
        name="WORKSHOP_CONV_LAG_MO",
        type=ParameterType.INT,
        default=1,
        min=0,
        max=6,
        step=1,
        tier=ParameterTier.ADVANCED,
        group="workshops",
        label="Workshop Conversion Lag (months)",
        help="Months between workshop participation and membership signup. Accounts for decision time and class schedules.",
        affects=[]
    ),

    # =============================================================================
    # REVENUE: CLASSES
    # =============================================================================
    "CLASSES_ENABLED": Parameter(
        name="CLASSES_ENABLED",
        type=ParameterType.BOOL,
        default=True,
        tier=ParameterTier.IMPORTANT,
        group="classes",
        label="Enable Class Revenue Stream",
        help="Whether studio offers multi-week pottery courses. Higher revenue per participant but requires structured curriculum.",
        affects=[]
    ),

    "CLASSES_CALENDAR_MODE": Parameter(
        name="CLASSES_CALENDAR_MODE",
        type=ParameterType.SELECT,
        default="semester",
        options=["monthly", "semester"],
        tier=ParameterTier.ADVANCED,
        group="classes",
        label="Class Schedule Type",
        help="Monthly = continuous rolling classes. Semester = structured terms with breaks. Affects cash flow timing and member acquisition patterns.",
        affects=[]
    ),

    "CLASS_COHORTS_PER_MONTH": Parameter(
        name="CLASS_COHORTS_PER_MONTH",
        type=ParameterType.INT,
        default=2,
        min=0,
        max=10,
        step=1,
        tier=ParameterTier.ADVANCED,
        group="classes",
        label="Class Cohorts per Month/Term",
        help="Number of class groups starting per period. More cohorts = more revenue but requires instructor capacity.",
        affects=[]
    ),

    "CLASS_CAP_PER_COHORT": Parameter(
        name="CLASS_CAP_PER_COHORT",
        type=ParameterType.INT,
        default=10,
        min=3,
        max=20,
        step=1,
        tier=ParameterTier.ADVANCED,
        group="classes",
        label="Students per Class",
        help="Maximum students per class cohort. Limited by instruction quality and workspace capacity.",
        affects=[]
    ),

    "CLASS_PRICE": Parameter(
        name="CLASS_PRICE",
        type=ParameterType.FLOAT,
        default=600.0,
        min=100.0,
        max=1000.0,
        step=25.0,
        tier=ParameterTier.ADVANCED,
        group="classes",
        label="Class Series Price ($)",
        help="Tuition for complete multi-week course. Major revenue stream - should cover instructor costs, materials, and profit.",
        affects=[]
    ),

    "CLASS_FILL_MEAN": Parameter(
        name="CLASS_FILL_MEAN",
        type=ParameterType.FLOAT,
        default=0.85,
        min=0.3,
        max=1.0,
        step=0.05,
        tier=ParameterTier.ADVANCED,
        group="classes",
        label="Average Class Fill Rate",
        help="Typical fraction of class capacity that actually enrolls. 0.85 = 85% average enrollment. Accounts for no-shows and cancellations.",
        affects=[]
    ),

    "CLASS_COST_PER_STUDENT": Parameter(
        name="CLASS_COST_PER_STUDENT",
        type=ParameterType.FLOAT,
        default=40.0,
        min=10.0,
        max=100.0,
        step=5.0,
        tier=ParameterTier.ADVANCED,
        group="classes",
        label="Variable Cost per Student ($)",
        help="Materials and supplies cost per class student over full course. Clay, glazes, firing costs, handouts, etc.",
        affects=[]
    ),

    "CLASS_INSTR_RATE_PER_HR": Parameter(
        name="CLASS_INSTR_RATE_PER_HR",
        type=ParameterType.FLOAT,
        default=30.0,
        min=15.0,
        max=100.0,
        step=2.5,
        tier=ParameterTier.ADVANCED,
        group="classes",
        label="Instructor Hourly Rate ($)",
        help="Compensation for class instructor per hour. Major cost component for class programs.",
        affects=[]
    ),

    "CLASS_HOURS_PER_COHORT": Parameter(
        name="CLASS_HOURS_PER_COHORT",
        type=ParameterType.FLOAT,
        default=18.0,
        min=6.0,
        max=40.0,
        step=1.0,
        tier=ParameterTier.ADVANCED,
        group="classes",
        label="Total Hours per Class Series",
        help="Total instructor hours per complete class (e.g., 6 weeks Ã— 3 hours = 18). Affects instructor costs.",
        affects=[]
    ),

    "CLASS_CONV_RATE": Parameter(
        name="CLASS_CONV_RATE",
        type=ParameterType.FLOAT,
        default=0.12,
        min=0.0,
        max=0.5,
        step=0.01,
        tier=ParameterTier.ADVANCED,
        group="classes",
        label="Class to Member Conversion Rate",
        help="Fraction of class students who become members. Higher than workshop conversion due to deeper engagement.",
        affects=[]
    ),

    "CLASS_CONV_LAG_MO": Parameter(
        name="CLASS_CONV_LAG_MO",
        type=ParameterType.INT,
        default=1,
        min=0,
        max=6,
        step=1,
        tier=ParameterTier.ADVANCED,
        group="classes",
        label="Class Conversion Lag (months)",
        help="Months between class completion and membership signup. Often immediate as students are already engaged.",
        affects=[]
    ),

    "CLASS_EARLY_CHURN_MULT": Parameter(
        name="CLASS_EARLY_CHURN_MULT",
        type=ParameterType.FLOAT,
        default=0.8,
        min=0.1,
        max=1.5,
        step=0.05,
        tier=ParameterTier.ADVANCED,
        group="classes",
        label="Class Convert Early Churn Multiplier",
        help="Churn rate modifier for class converts in first 3-6 months. <1.0 = lower churn due to formal introduction to pottery.",
        affects=[]
    ),

    "CLASS_SEMESTER_LENGTH_MONTHS": Parameter(
        name="CLASS_SEMESTER_LENGTH_MONTHS",
        type=ParameterType.INT,
        default=3,
        min=1,
        max=6,
        step=1,
        tier=ParameterTier.ADVANCED,
        group="classes",
        label="Semester Length (months)",
        help="Duration of each semester in months. Only relevant if using semester scheduling mode.",
        affects=[]
    ),

    # =============================================================================
    # REVENUE: EVENTS
    # =============================================================================
    "EVENTS_ENABLED": Parameter(
        name="EVENTS_ENABLED",
        type=ParameterType.BOOL,
        default=True,
        tier=ParameterTier.IMPORTANT,
        group="events",
        label="Enable Event Revenue Stream",
        help="Whether the studio hosts public events such as paint-a-pot, parties, and group activities. High-margin revenue stream.",
        affects=[]
    ),

    "BASE_EVENTS_PER_MONTH_LAMBDA": Parameter(
        name="BASE_EVENTS_PER_MONTH_LAMBDA",
        type=ParameterType.FLOAT,
        default=3.0,
        min=0.0,
        max=20.0,
        step=0.5,
        tier=ParameterTier.ADVANCED,
        group="events",
        label="Base Events per Month (λ)",
        help="Average number of monthly events before applying seasonality and random variation. Modeled using a Poisson draw.",
        affects=[]
    ),

    "EVENTS_MAX_PER_MONTH": Parameter(
        name="EVENTS_MAX_PER_MONTH",
        type=ParameterType.INT,
        default=4,
        min=1,
        max=30,
        step=1,
        tier=ParameterTier.IMPORTANT,
        group="events",
        label="Maximum Events per Month",
        help="Hard limit on monthly events due to staffing and space constraints. Prevents unrealistic spikes.",
        affects=[]
    ),

    "TICKET_PRICE": Parameter(
        name="TICKET_PRICE",
        type=ParameterType.FLOAT,
        default=75.0,
        min=30.0,
        max=200.0,
        step=5.0,
        tier=ParameterTier.IMPORTANT,
        group="events",
        label="Event Ticket Price ($)",
        help="Price per event participant. Should cover bisque ware, glazes, staff time, and profitability.",
        affects=[]
    ),

    "ATTENDEES_PER_EVENT_RANGE": Parameter(
        name="ATTENDEES_PER_EVENT_RANGE",
        type=ParameterType.JSON,
        default="[8, 10, 12]",
        tier=ParameterTier.ADVANCED,
        group="events",
        label="Event Attendance Range",
        help="JSON list of possible attendance values. Each event randomly selects one. Format: [min, mid, max].",
        affects=[]
    ),

    "EVENT_MUG_COST_RANGE": Parameter(
        name="EVENT_MUG_COST_RANGE",
        type=ParameterType.JSON,
        default="[4.5, 7.5]",
        tier=ParameterTier.ADVANCED,
        group="events",
        label="Bisque Mug Cost Range",
        help="JSON list [min, max] cost of bisque mugs for events. Random draw per participant.",
        affects=[]
    ),

    "EVENT_CONSUMABLES_PER_PERSON": Parameter(
        name="EVENT_CONSUMABLES_PER_PERSON",
        type=ParameterType.FLOAT,
        default=2.5,
        min=1.0,
        max=20.0,
        step=0.5,
        tier=ParameterTier.ADVANCED,
        group="events",
        label="Consumables Cost per Person ($)",
        help="Glazes, brushes, cleanup materials, and packaging per event participant.",
        affects=[]
    ),

    "EVENT_STAFF_RATE_PER_HOUR": Parameter(
        name="EVENT_STAFF_RATE_PER_HOUR",
        type=ParameterType.FLOAT,
        default=22.0,
        min=0.0,
        max=50.0,
        step=1.0,
        tier=ParameterTier.ADVANCED,
        group="events",
        label="Event Staff Hourly Rate ($)",
        help="Hourly wage paid to staff for running events including setup and cleanup. Set to 0 if owner-operated.",
        affects=[]
    ),

    "EVENT_HOURS_PER_EVENT": Parameter(
        name="EVENT_HOURS_PER_EVENT",
        type=ParameterType.FLOAT,
        default=2.0,
        min=1.0,
        max=8.0,
        step=0.5,
        tier=ParameterTier.ADVANCED,
        group="events",
        label="Staff Hours per Event",
        help="Total staff time per event including setup, instruction, and cleaning.",
        affects=[]
    ),

    # =============================================================================
    # REVENUE: DESIGNATED STUDIOS
    # =============================================================================
    "DESIGNATED_STUDIO_COUNT": Parameter(
        name="DESIGNATED_STUDIO_COUNT",
        type=ParameterType.INT,
        default=2,
        min=0,
        max=10,
        step=1,
        tier=ParameterTier.IMPORTANT,
        group="designated_studios",
        label="Number of Designated Studios",
        help="Private workspaces for advanced ceramicists. Rentable monthly. Limited by physical space.",
        affects=[]
    ),

    "DESIGNATED_STUDIO_PRICE": Parameter(
        name="DESIGNATED_STUDIO_PRICE",
        type=ParameterType.FLOAT,
        default=300.0,
        min=100.0,
        max=1000.0,
        step=25.0,
        tier=ParameterTier.IMPORTANT,
        group="designated_studios",
        label="Designated Studio Monthly Price ($)",
        help="Monthly rent per designated studio. Key premium revenue stream.",
        affects=[]
    ),

    "DESIGNATED_STUDIO_BASE_OCCUPANCY": Parameter(
        name="DESIGNATED_STUDIO_BASE_OCCUPANCY",
        type=ParameterType.FLOAT,
        default=0.3,
        min=0.0,
        max=1.0,
        step=0.05,
        tier=ParameterTier.ADVANCED,
        group="designated_studios",
        label="Designated Studio Occupancy Rate",
        help="Expected fraction of designated studios rented on average. Affects revenue and cash flow volatility.",
        affects=[]
    ),
    # =============================================================================
    # OPERATING COSTS: FIXED
    # =============================================================================
    "INSURANCE_COST": Parameter(
        name="INSURANCE_COST",
        type=ParameterType.FLOAT,
        default=75.0,
        min=50.0,
        max=500.0,
        step=10.0,
        tier=ParameterTier.IMPORTANT,
        group="fixed_costs",
        label="Monthly Insurance Cost ($)",
        help="General liability and property insurance. Required for most leases and essential for pottery studio operations.",
        affects=[]
    ),

    "GLAZE_COST_PER_MONTH": Parameter(
        name="GLAZE_COST_PER_MONTH",
        type=ParameterType.FLOAT,
        default=833.33,
        min=200.0,
        max=2000.0,
        step=50.0,
        tier=ParameterTier.ADVANCED,
        group="fixed_costs",
        label="Monthly Glaze Cost ($)",
        help="Glazes, underglazes, and finishing materials. Fixed cost since members use unlimited glazes. Major expense item.",
        affects=[]
    ),

    "HEATING_COST_WINTER": Parameter(
        name="HEATING_COST_WINTER",
        type=ParameterType.FLOAT,
        default=450.0,
        min=100.0,
        max=1500.0,
        step=25.0,
        tier=ParameterTier.ADVANCED,
        group="fixed_costs",
        label="Winter Monthly Heating ($)",
        help="Heating costs during cold months (Oct–Mar). Higher for pottery studios due to large spaces and kiln heat loss.",
        affects=[]
    ),

    "HEATING_COST_SUMMER": Parameter(
        name="HEATING_COST_SUMMER",
        type=ParameterType.FLOAT,
        default=30.0,
        min=0.0,
        max=500.0,
        step=10.0,
        tier=ParameterTier.ADVANCED,
        group="fixed_costs",
        label="Summer Monthly Heating ($)",
        help="Minimal heating costs during warm months (Apr–Sep). May be just hot water heater and minimal space heating.",
        affects=[]
    ),

    # =============================================================================
    # OPERATING COSTS: VARIABLE
    # =============================================================================
    "COST_PER_KWH": Parameter(
        name="COST_PER_KWH",
        type=ParameterType.FLOAT,
        default=0.2182,
        min=0.08,
        max=0.50,
        step=0.01,
        tier=ParameterTier.ADVANCED,
        group="variable_costs",
        label="Electricity Rate ($/kWh)",
        help="Local electricity rate including all fees and taxes. Kilns are major electricity consumers.",
        affects=[]
    ),

    "WATER_COST_PER_GALLON": Parameter(
        name="WATER_COST_PER_GALLON",
        type=ParameterType.FLOAT,
        default=0.02,
        min=0.005,
        max=0.05,
        step=0.002,
        tier=ParameterTier.ADVANCED,
        group="variable_costs",
        label="Water Cost ($/gallon)",
        help="Water and sewer costs per gallon. Pottery uses significant water for clay prep and cleanup.",
        affects=[]
    ),

    "GALLONS_PER_BAG_CLAY": Parameter(
        name="GALLONS_PER_BAG_CLAY",
        type=ParameterType.FLOAT,
        default=1.0,
        min=0.5,
        max=3.0,
        step=0.1,
        tier=ParameterTier.ADVANCED,
        group="variable_costs",
        label="Water per Clay Bag (gallons)",
        help="Water consumption per 25lb clay bag for mixing and cleanup. Varies by clay type and studio practices.",
        affects=[]
    ),

    "KWH_PER_FIRING_KMT1027": Parameter(
        name="KWH_PER_FIRING_KMT1027",
        type=ParameterType.FLOAT,
        default=75.0,
        min=40.0,
        max=120.0,
        step=5.0,
        tier=ParameterTier.ADVANCED,
        group="variable_costs",
        label="kWh per Firing - Kiln 1 (KMT1027)",
        help="Electricity consumption per firing cycle for smaller kiln. Varies by firing temperature and duration.",
        affects=[]
    ),

    "KWH_PER_FIRING_KMT1427": Parameter(
        name="KWH_PER_FIRING_KMT1427",
        type=ParameterType.FLOAT,
        default=110.0,
        min=60.0,
        max=180.0,
        step=5.0,
        tier=ParameterTier.ADVANCED,
        group="variable_costs",
        label="kWh per Firing - Kiln 2 (KMT1427)",
        help="Electricity consumption per firing cycle for larger kiln. Higher capacity but more energy per firing.",
        affects=[]
    ),

    "DYNAMIC_FIRINGS": Parameter(
        name="DYNAMIC_FIRINGS",
        type=ParameterType.BOOL,
        default=True,
        tier=ParameterTier.ADVANCED,
        group="variable_costs",
        label="Dynamic Firing Schedule",
        help="Whether firing frequency adjusts based on member count. True = more members trigger more firings. False = fixed schedule.",
        affects=[]
    ),

    "BASE_FIRINGS_PER_MONTH": Parameter(
        name="BASE_FIRINGS_PER_MONTH",
        type=ParameterType.INT,
        default=10,
        min=2,
        max=30,
        step=1,
        tier=ParameterTier.ADVANCED,
        group="variable_costs",
        label="Base Firings per Month",
        help="Firing frequency at reference member count. Used for scaling if dynamic firings enabled, or as fixed rate if disabled.",
        affects=[]
    ),

    "REFERENCE_MEMBERS_FOR_BASE_FIRINGS": Parameter(
        name="REFERENCE_MEMBERS_FOR_BASE_FIRINGS",
        type=ParameterType.INT,
        default=12,
        min=5,
        max=50,
        step=1,
        tier=ParameterTier.ADVANCED,
        group="variable_costs",
        label="Reference Member Count for Firing Scale",
        help="Member count that triggers base firing frequency. More members = proportionally more firings if dynamic enabled.",
        affects=[]
    ),

    "MIN_FIRINGS_PER_MONTH": Parameter(
        name="MIN_FIRINGS_PER_MONTH",
        type=ParameterType.INT,
        default=4,
        min=1,
        max=15,
        step=1,
        tier=ParameterTier.ADVANCED,
        group="variable_costs",
        label="Minimum Firings per Month",
        help="Floor on monthly firings even with very few members. Ensures kiln maintenance and minimum service level.",
        affects=[]
    ),

    "MAX_FIRINGS_PER_MONTH": Parameter(
        name="MAX_FIRINGS_PER_MONTH",
        type=ParameterType.INT,
        default=12,
        min=8,
        max=50,
        step=1,
        tier=ParameterTier.ADVANCED,
        group="variable_costs",
        label="Maximum Firings per Month",
        help="Ceiling on monthly firings due to kiln capacity and staff time constraints. Prevents unrealistic firing schedules.",
        affects=[]
    ),
    # =============================================================================
    # OPERATIONAL COSTS: MAINTENANCE & MARKETING
    # =============================================================================
    "MAINTENANCE_BASE_COST": Parameter(
        name="MAINTENANCE_BASE_COST",
        type=ParameterType.FLOAT,
        default=200.0,
        min=50.0,
        max=1000.0,
        step=25.0,
        tier=ParameterTier.ADVANCED,
        group="operational_costs",
        label="Base Monthly Maintenance ($)",
        help="Predictable maintenance costs: kiln elements, wheel repairs, tool replacement. Core facility upkeep.",
        affects=[]
    ),

    "MAINTENANCE_RANDOM_STD": Parameter(
        name="MAINTENANCE_RANDOM_STD",
        type=ParameterType.FLOAT,
        default=150.0,
        min=0.0,
        max=500.0,
        step=25.0,
        tier=ParameterTier.ADVANCED,
        group="operational_costs",
        label="Random Maintenance Variation ($)",
        help="Standard deviation of unpredictable maintenance costs. Models equipment failures and emergency repairs.",
        affects=[]
    ),

    "MARKETING_COST_BASE": Parameter(
        name="MARKETING_COST_BASE",
        type=ParameterType.FLOAT,
        default=300.0,
        min=0.0,
        max=2000.0,
        step=50.0,
        tier=ParameterTier.ADVANCED,
        group="operational_costs",
        label="Base Monthly Marketing ($)",
        help="Ongoing marketing spend: social media ads, printed materials, website. Essential for member acquisition.",
        affects=[]
    ),

    "MARKETING_RAMP_MONTHS": Parameter(
        name="MARKETING_RAMP_MONTHS",
        type=ParameterType.INT,
        default=12,
        min=1,
        max=24,
        step=1,
        tier=ParameterTier.ADVANCED,
        group="operational_costs",
        label="Marketing Ramp Duration (months)",
        help="Months of elevated marketing spend during startup. Higher early spend builds initial awareness.",
        affects=[]
    ),

    "MARKETING_RAMP_MULTIPLIER": Parameter(
        name="MARKETING_RAMP_MULTIPLIER",
        type=ParameterType.FLOAT,
        default=2.0,
        min=1.0,
        max=5.0,
        step=0.25,
        tier=ParameterTier.ADVANCED,
        group="operational_costs",
        label="Marketing Ramp Multiplier",
        help="Multiplier on base marketing spend during ramp period. 2.0 = double spend for the first N months.",
        affects=[]
    ),

    # =============================================================================
    # STAFF COSTS
    # =============================================================================
    "STAFF_EXPANSION_THRESHOLD": Parameter(
        name="STAFF_EXPANSION_THRESHOLD",
        type=ParameterType.INT,
        default=50,
        min=20,
        max=200,
        step=5,
        tier=ParameterTier.ADVANCED,
        group="staff_costs",
        label="Staff Hiring Threshold (members)",
        help="Member count that triggers hiring the first employee. Represents owner capacity limit and service quality needs.",
        affects=[]
    ),

    "STAFF_COST_PER_MONTH": Parameter(
        name="STAFF_COST_PER_MONTH",
        type=ParameterType.FLOAT,
        default=2500.0,
        min=1500.0,
        max=8000.0,
        step=100.0,
        tier=ParameterTier.ADVANCED,
        group="staff_costs",
        label="Monthly Staff Cost ($)",
        help="Total monthly cost for the first employee including wages, payroll taxes, and benefits.",
        affects=[]
    ),

    # =============================================================================
    # ENTITY TYPE & TAXATION
    # =============================================================================
    "ENTITY_TYPE": Parameter(
        name="ENTITY_TYPE",
        type=ParameterType.SELECT,
        default="sole_prop",
        options=["sole_prop", "partnership", "s_corp", "c_corp"],
        tier=ParameterTier.ADVANCED,
        group="taxation",
        label="Business Entity Type",
        help="Legal structure affecting taxation and owner compensation. Sole prop = simplest, S-corp = payroll taxes, C-corp = double taxation.",
        affects=[]
    ),

    "MA_PERSONAL_INCOME_TAX_RATE": Parameter(
        name="MA_PERSONAL_INCOME_TAX_RATE",
        type=ParameterType.FLOAT,
        default=0.05,
        min=0.0,
        max=0.15,
        step=0.005,
        tier=ParameterTier.ADVANCED,
        group="taxation",
        label="MA Personal Income Tax Rate",
        help="Massachusetts personal income tax rate. Applies to pass-through income for sole proprietorships, partnerships, and S-corps.",
        affects=[]
    ),

    "SE_SOC_SEC_RATE": Parameter(
        name="SE_SOC_SEC_RATE",
        type=ParameterType.FLOAT,
        default=0.124,
        min=0.08,
        max=0.15,
        step=0.001,
        tier=ParameterTier.ADVANCED,
        group="taxation",
        label="Self-Employment Social Security Rate",
        help="Combined employer+employee Social Security rate for self-employed individuals. Applies up to wage base.",
        affects=[]
    ),

    "SE_MEDICARE_RATE": Parameter(
        name="SE_MEDICARE_RATE",
        type=ParameterType.FLOAT,
        default=0.029,
        min=0.02,
        max=0.05,
        step=0.001,
        tier=ParameterTier.ADVANCED,
        group="taxation",
        label="Self-Employment Medicare Rate",
        help="Combined employer+employee Medicare rate for self-employed income. Applies to all income with no wage cap.",
        affects=[]
    ),

    "SE_SOC_SEC_WAGE_BASE": Parameter(
        name="SE_SOC_SEC_WAGE_BASE",
        type=ParameterType.INT,
        default=168600,
        min=100000,
        max=200000,
        step=1000,
        tier=ParameterTier.ADVANCED,
        group="taxation",
        label="SE Social Security Wage Base ($)",
        help="Annual wage base limit for Social Security tax. SE income above this amount is exempt from SS tax.",
        affects=[]
    ),

    "SCORP_OWNER_SALARY_PER_MONTH": Parameter(
        name="SCORP_OWNER_SALARY_PER_MONTH",
        type=ParameterType.FLOAT,
        default=4000.0,
        min=0.0,
        max=10000.0,
        step=100.0,
        tier=ParameterTier.ADVANCED,
        group="taxation",
        label="S-Corp Owner Monthly Salary ($)",
        help="Reasonable salary requirement for S-Corp owners. Salary is subject to payroll taxes; profits above salary avoid SE tax.",
        affects=[]
    ),

    "FED_CORP_TAX_RATE": Parameter(
        name="FED_CORP_TAX_RATE",
        type=ParameterType.FLOAT,
        default=0.21,
        min=0.15,
        max=0.35,
        step=0.01,
        tier=ParameterTier.ADVANCED,
        group="taxation",
        label="Federal Corporate Tax Rate",
        help="Federal income tax rate applied to C-Corporation profits before dividends.",
        affects=[]
    ),

    "MA_CORP_TAX_RATE": Parameter(
        name="MA_CORP_TAX_RATE",
        type=ParameterType.FLOAT,
        default=0.08,
        min=0.05,
        max=0.12,
        step=0.005,
        tier=ParameterTier.ADVANCED,
        group="taxation",
        label="MA Corporate Tax Rate",
        help="Massachusetts corporate income tax rate for C-Corporations. Combined with federal rate for total tax burden.",
        affects=[]
    ),

    "MA_SALES_TAX_RATE": Parameter(
        name="MA_SALES_TAX_RATE",
        type=ParameterType.FLOAT,
        default=0.0625,
        min=0.0,
        max=0.15,
        step=0.005,
        tier=ParameterTier.ADVANCED,
        group="taxation",
        label="MA Sales Tax Rate",
        help="Massachusetts sales tax rate applied to clay and retail sales. Must be collected and remitted quarterly.",
        affects=[]
    ),

    # =============================================================================
    # FINANCING: SBA LOANS
    # =============================================================================
    "LOAN_504_AMOUNT_OVERRIDE": Parameter(
        name="LOAN_504_AMOUNT_OVERRIDE",
        type=ParameterType.FLOAT,
        default=0.0,
        min=0.0,
        max=500000.0,
        step=1000.0,
        tier=ParameterTier.ADVANCED,
        group="financing",
        label="SBA 504 Loan Amount Override ($, 0=Auto-calculate)",
        help="Manual override for SBA 504 loan amount. Leave at 0 to auto-calculate from CapEx equipment costs plus contingency.",
        affects=[]
    ),

    "LOAN_7A_AMOUNT_OVERRIDE": Parameter(
        name="LOAN_7A_AMOUNT_OVERRIDE",
        type=ParameterType.FLOAT,
        default=0.0,
        min=0.0,
        max=500000.0,
        step=1000.0,
        tier=ParameterTier.ADVANCED,
        group="financing",
        label="SBA 7(a) Loan Amount Override ($, 0=Auto-calculate)",
        help="Manual override for SBA 7(a) loan amount. Leave at 0 to auto-calculate from 8 months of OpEx (rent + owner draw + insurance).",
        affects=[]
    ),

    "LOAN_504_ANNUAL_RATE": Parameter(
        name="LOAN_504_ANNUAL_RATE",
        type=ParameterType.FLOAT,
        default=0.070,
        min=0.03,
        max=0.15,
        step=0.001,
        tier=ParameterTier.IMPORTANT,
        group="financing",
        label="SBA 504 Annual Rate",
        help="Blended interest rate for SBA 504 loan (equipment/real estate). Typically lower than conventional financing.",
        affects=[]
    ),

    "LOAN_504_TERM_YEARS": Parameter(
        name="LOAN_504_TERM_YEARS",
        type=ParameterType.INT,
        default=20,
        min=5,
        max=25,
        step=1,
        tier=ParameterTier.ESSENTIAL,
        group="financing",
        label="SBA 504 Term (years)",
        help="Repayment period for 504 loan. Longer terms available for real estate (20 years) vs equipment (10–15 years).",
        affects=[]
    ),

    "IO_MONTHS_504": Parameter(
        name="IO_MONTHS_504",
        type=ParameterType.INT,
        default=6,
        min=0,
        max=18,
        step=1,
        tier=ParameterTier.IMPORTANT,
        group="financing",
        label="504 Interest-Only Months",
        help="Initial months with interest-only payments on 504 loan. Helps cash flow during the build-out and startup phase.",
        affects=[]
    ),

    "LOAN_7A_ANNUAL_RATE": Parameter(
        name="LOAN_7A_ANNUAL_RATE",
        type=ParameterType.FLOAT,
        default=0.115,
        min=0.05,
        max=0.20,
        step=0.001,
        tier=ParameterTier.IMPORTANT,
        group="financing",
        label="SBA 7(a) Annual Rate",
        help="Interest rate for SBA 7(a) loan (working capital/general business). Typically higher than 504 but more flexible.",
        affects=[]
    ),

    "LOAN_7A_TERM_YEARS": Parameter(
        name="LOAN_7A_TERM_YEARS",
        type=ParameterType.INT,
        default=7,
        min=5,
        max=10,
        step=1,
        tier=ParameterTier.ESSENTIAL,
        group="financing",
        label="SBA 7(a) Term (years)",
        help="Repayment period for 7(a) loan. Generally shorter than 504, reflecting working capital vs fixed asset financing.",
        affects=[]
    ),

    "IO_MONTHS_7A": Parameter(
        name="IO_MONTHS_7A",
        type=ParameterType.INT,
        default=6,
        min=0,
        max=18,
        step=1,
        tier=ParameterTier.IMPORTANT,
        group="financing",
        label="7(a) Interest-Only Months",
        help="Initial months with interest-only payments on 7(a) loan. Preserves working capital during startup.",
        affects=[]
    ),

    "LOAN_CONTINGENCY_PCT": Parameter(
        name="LOAN_CONTINGENCY_PCT",
        type=ParameterType.FLOAT,
        default=0.08,
        min=0.0,
        max=0.30,
        step=0.01,
        tier=ParameterTier.ADVANCED,
        group="financing",
        label="CapEx Contingency %",
        help="Percentage buffer added to equipment and buildout costs when sizing the loan. Accounts for overruns and surprise expenses.",
        affects=[]
    ),

    "RUNWAY_MONTHS": Parameter(
        name="RUNWAY_MONTHS",
        type=ParameterType.INT,
        default=12,
        min=6,
        max=24,
        step=1,
        tier=ParameterTier.ESSENTIAL,
        group="financing",
        label="Operating Runway (months)",
        help="Months of operating expenses to include when sizing the 7(a) working-capital loan. Higher runway = more cushion but more debt service.",
        affects=[]
    ),

    "EXTRA_BUFFER": Parameter(
        name="EXTRA_BUFFER",
        type=ParameterType.FLOAT,
        default=10000.0,
        min=0.0,
        max=50000.0,
        step=1000.0,
        tier=ParameterTier.ADVANCED,
        group="financing",
        label="Extra Working Capital Buffer ($)",
        help="Additional cash buffer beyond calculated runway. Useful for uncertain markets, longer build-outs, or conservative planning.",
        affects=[]
    ),

    "RESERVE_FLOOR": Parameter(
        name="RESERVE_FLOOR",
        type=ParameterTier.FLOAT,
        default=5000.0,
        min=0.0,
        max=50000.0,
        step=1000.0,
        tier=ParameterTier.ADVANCED,
        group="financing",
        label="Minimum Cash Reserve ($)",
        help="Minimum cash balance to maintain. Used for line-of-credit sizing and survival analysis.",
        affects=[]
    ),

    "FEES_UPFRONT_PCT_7A": Parameter(
        name="FEES_UPFRONT_PCT_7A",
        type=ParameterType.FLOAT,
        default=0.03,
        min=0.0,
        max=0.05,
        step=0.0025,
        tier=ParameterTier.ADVANCED,
        group="financing",
        label="7(a) Upfront Fee %",
        help="SBA guarantee fee as a percentage of 7(a) loan amount. Typically 2–3.5% depending on loan size.",
        affects=[]
    ),

    "FEES_UPFRONT_PCT_504": Parameter(
        name="FEES_UPFRONT_PCT_504",
        type=ParameterType.FLOAT,
        default=0.02,
        min=0.0,
        max=0.05,
        step=0.0025,
        tier=ParameterTier.ADVANCED,
        group="financing",
        label="504 Upfront Fee %",
        help="SBA guarantee fee as a percentage of 504 loan amount. Generally lower than 7(a) fees.",
        affects=[]
    ),

    "FEES_PACKAGING": Parameter(
        name="FEES_PACKAGING",
        type=ParameterType.FLOAT,
        default=2500.0,
        min=0.0,
        max=10000.0,
        step=250.0,
        tier=ParameterTier.ADVANCED,
        group="financing",
        label="Loan Packaging Fee ($)",
        help="Professional fee for loan-application preparation and SBA packaging. Common when using consultants or packagers.",
        affects=[]
    ),

    "FEES_CLOSING": Parameter(
        name="FEES_CLOSING",
        type=ParameterType.FLOAT,
        default=1500.0,
        min=0.0,
        max=5000.0,
        step=100.0,
        tier=ParameterTier.ADVANCED,
        group="financing",
        label="Loan Closing Costs ($)",
        help="Legal, title, and closing costs incurred at loan funding. One-time expense.",
        affects=[]
    ),

    "FINANCE_FEES_7A": Parameter(
        name="FINANCE_FEES_7A",
        type=ParameterType.BOOL,
        default=True,
        tier=ParameterTier.ADVANCED,
        group="financing",
        label="Finance 7(a) Fees into Loan",
        help="Whether 7(a) fees are rolled into the loan principal (vs paid in cash). Financing fees preserves cash but raises total debt.",
        affects=[]
    ),

    "FINANCE_FEES_504": Parameter(
        name="FINANCE_FEES_504",
        type=ParameterType.BOOL,
        default=True,
        tier=ParameterTier.ADVANCED,
        group="financing",
        label="Finance 504 Fees into Loan",
        help="Whether 504 fees are rolled into the loan principal (vs paid in cash). Financing fees preserves cash but raises total debt.",
        affects=[]
    ),

    "EXTRA_504_BUFFER": Parameter(
        name="EXTRA_504_BUFFER",
        type=ParameterType.FLOAT,
        default=0.0,
        min=0.0,
        max=200000.0,
        step=500.0,
        tier=ParameterTier.ADVANCED,
        group="financing",
        label="SBA 504 Misc Buffer ($)",
        help="Extra amount added on top of 504-eligible equipment total plus contingency. Use for buildout odds-and-ends not fully itemized.",
        affects=[]
    ),
        # =============================================================================
    # GRANTS
    # =============================================================================
    "grant_amount": Parameter(
        name="grant_amount",
        type=ParameterType.FLOAT,
        default=0.0,
        min=0.0,
        max=100000.0,
        step=100.0,
        tier=ParameterTier.ADVANCED,
        group="grants",
        label="Grant Amount ($)",
        help="Non-dilutive grant funding received by the studio. Applied in the month specified by 'grant_month'.",
        affects=[]
    ),

    "grant_month": Parameter(
        name="grant_month",
        type=ParameterType.INT,
        default=-1,
        min=-1,
        max=60,
        step=1,
        tier=ParameterTier.ADVANCED,
        group="grants",
        label="Month Grant Arrives",
        help="Month in which grant funds are added to the cash balance. 0 means received at start.",
        affects=[]
    ),

    # =============================================================================
    # MEMBERSHIP TRAJECTORY MODE
    # =============================================================================
    "MEMBERSHIP_MODE": Parameter(
        name="MEMBERSHIP_MODE",
        type=ParameterType.SELECT,
        default="calculated",
        options=["calculated", "manual_table", "piecewise_trends"],
        tier=ParameterTier.ADVANCED,
        group="membership_trajectory",
        label="Membership Projection Method",
        help=(
            "How to determine membership over time: calculated from market dynamics, "
            "manual month-by-month input, or piecewise trend specification."
        ),
        affects=[]
    ),

    # =============================================================================
    # SIMULATION CONTROLS
    # =============================================================================
    "MONTHS": Parameter(
        name="MONTHS",
        type=ParameterType.INT,
        default=60,
        min=12,
        max=120,
        step=6,
        tier=ParameterTier.ESSENTIAL,
        group="simulation",
        label="Simulation Horizon (months)",
        help="Total months to simulate. Longer horizons show mature operations but increase runtime. 60 months (5 years) is typical.",
        affects=[]
    ),

    "N_SIMULATIONS": Parameter(
        name="N_SIMULATIONS",
        type=ParameterType.INT,
        default=100,
        min=10,
        max=300,
        step=10,
        tier=ParameterTier.ESSENTIAL,
        group="simulation",
        label="Number of Simulations",
        help="Monte Carlo simulations to run. More runs give better percentile estimates but take longer. 100+ recommended.",
        affects=[]
    ),

    "RANDOM_SEED": Parameter(
        name="RANDOM_SEED",
        type=ParameterType.INT,
        default=42,
        min=1,
        max=999999,
        step=1,
        tier=ParameterTier.ADVANCED,
        group="simulation",
        label="Random Seed",
        help="Random number generator seed for reproducible results. Change to explore different random worlds with same parameters.",
        affects=[]
    ),
}