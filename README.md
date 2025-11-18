# Pottery Studio Financial Simulator v2.0

A comprehensive Monte Carlo financial modeling tool for pottery studio owners.

## Features

- **Monte Carlo Simulation**: Realistic scenario planning with probabilistic outcomes
- **Multi-Revenue Streams**: Model memberships, classes, workshops, events
- **SBA Loan Analysis**: Detailed 504 and 7(a) loan calculations with DSCR
- **Capacity Planning**: Station-based utilization modeling
- **Member Dynamics**: Archetype-based churn and acquisition
- **Risk Assessment**: Percentile-based cash flow analysis

## Installation
```bash
# Clone repository
git clone [your-repo-url]
cd pottery_studio_v2

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

## Project Structure
```text
pottery_studio_v2/
├── config/          # Parameter definitions and presets
├── simulation/      # Core Monte Carlo engine
├── validation/      # Business rules and validation
├── ui/              # Smart UI components
├── analysis/        # Visualization and exports
├── utils/           # Scenario management
├── pages/           # Multi-page Streamlit interface
├── tests/           # Unit and integration tests
└── scenarios/       # Saved user scenarios
```

## Quick Start

Run:
```bash
streamlit run app.py
```

Then navigate to **🚀 Quick Start** and answer 8 questions about your studio to view instant financial projections.

## Documentation

See `docs/` directory for:

- Architecture overview  
- Parameter reference  
- API documentation  

## Testing

```bash
pytest tests/
```

## License

[Your License]

## Version

2.0.0 — Complete refactor with modular architecture
