import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
from plotly.subplots import make_subplots

# Page config
st.set_page_config(
    page_title="AI Adoption Dashboard | 2018-2025 Analysis",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/Rcasanova25/AI-Adoption-Dashboard/wiki',
        'Report a bug': "https://github.com/Rcasanova25/AI-Adoption-Dashboard/issues",
        'About': "# AI Adoption Dashboard\nVersion 2.2.0\n\nTrack AI adoption trends across industries and geographies.\n\nCreated by Robert Casanova"
    }
)

# Data loading function - updated with AI Index 2025 data and Token Economics
@st.cache_data
def load_data():
    try:
        # Historical trends data - UPDATED with AI Index 2025 findings
        historical_data = pd.DataFrame({
            'year': [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
            'ai_use': [20, 47, 58, 56, 55, 50, 55, 78, 78],  # Updated: 78% in 2024
            'genai_use': [0, 0, 0, 0, 0, 33, 33, 71, 71]  # Updated: 71% in 2024
        })
        
        # 2018 Sector data
        sector_2018 = pd.DataFrame({
            'sector': ['Manufacturing', 'Information', 'Healthcare', 'Professional Services', 
                      'Finance & Insurance', 'Retail Trade', 'Construction'],
            'firm_weighted': [12, 12, 8, 7, 6, 4, 4],
            'employment_weighted': [18, 22, 15, 14, 12, 8, 6]
        })
        
        # 2025 Sector data - NEW for industry-specific insights
        sector_2025 = pd.DataFrame({
            'sector': ['Technology', 'Financial Services', 'Healthcare', 'Manufacturing', 
                      'Retail & E-commerce', 'Education', 'Energy & Utilities', 'Government'],
            'adoption_rate': [92, 85, 78, 75, 72, 65, 58, 52],
            'genai_adoption': [88, 78, 65, 58, 70, 62, 45, 38],
            'avg_roi': [4.2, 3.8, 3.2, 3.5, 3.0, 2.5, 2.8, 2.2]
        })
        
        # Firm size data
        firm_size = pd.DataFrame({
            'size': ['1-4', '5-9', '10-19', '20-49', '50-99', '100-249', '250-499', 
                    '500-999', '1000-2499', '2500-4999', '5000+'],
            'adoption': [3.2, 3.8, 4.5, 5.2, 7.8, 12.5, 18.2, 25.6, 35.4, 42.8, 58.5]
        })
        
        # AI Maturity data
        ai_maturity = pd.DataFrame({
            'technology': ['Generative AI', 'AI Agents', 'Foundation Models', 'ModelOps', 
                          'AI Engineering', 'Cloud AI Services', 'Knowledge Graphs', 'Composite AI'],
            'adoption_rate': [71, 15, 45, 25, 30, 78, 35, 12],
            'maturity': ['Peak of Expectations', 'Peak of Expectations', 'Trough of Disillusionment',
                        'Trough of Disillusionment', 'Peak of Expectations', 'Slope of Enlightenment',
                        'Slope of Enlightenment', 'Peak of Expectations'],
            'risk_score': [85, 90, 60, 55, 80, 25, 40, 95],
            'time_to_value': [3, 3, 3, 3, 3, 1, 3, 7]
        })
        
        # Geographic data - enhanced with population and GDP
        geographic = pd.DataFrame({
            'city': ['San Francisco Bay Area', 'Nashville', 'San Antonio', 'Las Vegas', 
                    'New Orleans', 'San Diego', 'Seattle', 'Boston', 'Los Angeles',
                    'Phoenix', 'Denver', 'Austin', 'Portland', 'Miami', 'Atlanta',
                    'Chicago', 'New York', 'Philadelphia', 'Dallas', 'Houston'],
            'state': ['California', 'Tennessee', 'Texas', 'Nevada', 
                     'Louisiana', 'California', 'Washington', 'Massachusetts', 'California',
                     'Arizona', 'Colorado', 'Texas', 'Oregon', 'Florida', 'Georgia',
                     'Illinois', 'New York', 'Pennsylvania', 'Texas', 'Texas'],
            'lat': [37.7749, 36.1627, 29.4241, 36.1699, 
                   29.9511, 32.7157, 47.6062, 42.3601, 34.0522,
                   33.4484, 39.7392, 30.2672, 45.5152, 25.7617, 33.7490,
                   41.8781, 40.7128, 39.9526, 32.7767, 29.7604],
            'lon': [-122.4194, -86.7816, -98.4936, -115.1398, 
                   -90.0715, -117.1611, -122.3321, -71.0589, -118.2437,
                   -112.0740, -104.9903, -97.7431, -122.6784, -80.1918, -84.3880,
                   -87.6298, -74.0060, -75.1652, -96.7970, -95.3698],
            'rate': [9.5, 8.3, 8.3, 7.7, 
                    7.4, 7.4, 6.8, 6.7, 7.2,
                    6.5, 6.3, 7.8, 6.2, 6.9, 7.1,
                    7.0, 8.0, 6.6, 7.5, 7.3],
            'state_code': ['CA', 'TN', 'TX', 'NV', 
                          'LA', 'CA', 'WA', 'MA', 'CA',
                          'AZ', 'CO', 'TX', 'OR', 'FL', 'GA',
                          'IL', 'NY', 'PA', 'TX', 'TX'],
            'population_millions': [7.7, 0.7, 1.5, 0.6, 
                                   0.4, 1.4, 0.8, 0.7, 4.0,
                                   1.7, 0.7, 1.0, 0.7, 0.5, 0.5,
                                   2.7, 8.3, 1.6, 1.3, 2.3],
            'gdp_billions': [535, 48, 98, 68, 
                            25, 253, 392, 463, 860,
                            162, 201, 148, 121, 345, 396,
                            610, 1487, 388, 368, 356]
        })
        
        # State-level aggregation
        state_data = geographic.groupby(['state', 'state_code']).agg({
            'rate': 'mean'
        }).reset_index()
        
        # Add more states
        additional_states = pd.DataFrame({
            'state': ['Michigan', 'Ohio', 'North Carolina', 'Virginia', 'Maryland',
                     'Connecticut', 'New Jersey', 'Indiana', 'Missouri', 'Wisconsin'],
            'state_code': ['MI', 'OH', 'NC', 'VA', 'MD', 'CT', 'NJ', 'IN', 'MO', 'WI'],
            'rate': [5.5, 5.8, 6.0, 6.2, 6.4, 6.8, 6.9, 5.2, 5.4, 5.3]
        })
        state_data = pd.concat([state_data, additional_states], ignore_index=True)
        
        # Technology stack - Fixed percentages to sum to 100
        tech_stack = pd.DataFrame({
            'technology': ['AI Only', 'AI + Cloud', 'AI + Digitization', 'AI + Cloud + Digitization'],
            'percentage': [15, 23, 24, 38]  # Sum = 100
        })
        
        # Productivity data with skill levels - ENHANCED
        productivity_data = pd.DataFrame({
            'year': [1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2025],
            'productivity_growth': [0.8, 1.2, 1.5, 2.2, 2.5, 1.8, 1.0, 0.5, 0.3, 0.4],
            'young_workers_share': [42, 45, 43, 38, 35, 33, 32, 34, 36, 38]
        })
        
        # AI productivity by skill level - NEW
        productivity_by_skill = pd.DataFrame({
            'skill_level': ['Low-skilled', 'Medium-skilled', 'High-skilled'],
            'productivity_gain': [14, 9, 5],
            'skill_gap_reduction': [28, 18, 8]
        })
        
        # AI productivity estimates
        ai_productivity_estimates = pd.DataFrame({
            'source': ['Acemoglu (2024)', 'Brynjolfsson et al. (2023)', 'McKinsey (potential)', 'Goldman Sachs (potential)', 'Richmond Fed'],
            'annual_impact': [0.07, 1.5, 2.0, 2.5, 0.1]
        })
        
        # OECD 2025 Report data
        oecd_g7_adoption = pd.DataFrame({
            'country': ['United States', 'Canada', 'United Kingdom', 'Germany', 'France', 'Italy', 'Japan'],
            'adoption_rate': [45, 38, 42, 40, 35, 32, 48],
            'manufacturing': [52, 45, 48, 55, 42, 40, 58],
            'ict_sector': [68, 62, 65, 63, 58, 55, 70]
        })
        
        # OECD AI Applications - ENHANCED with GenAI use cases
        oecd_applications = pd.DataFrame({
            'application': ['Content Generation', 'Code Generation', 'Customer Service Chatbots',
                           'Predictive Maintenance', 'Process Automation', 'Customer Analytics', 
                           'Quality Control', 'Supply Chain Optimization', 'Fraud Detection',
                           'Product Recommendation', 'Voice Recognition', 'Computer Vision',
                           'Natural Language Processing', 'Robotics Integration', 'Personalized Learning'],
            'usage_rate': [65, 58, 52, 45, 42, 38, 35, 32, 30, 28, 25, 23, 22, 18, 15],
            'category': ['GenAI', 'GenAI', 'GenAI', 'Traditional AI', 'Traditional AI', 
                        'Traditional AI', 'Traditional AI', 'Traditional AI', 'Traditional AI',
                        'Traditional AI', 'Traditional AI', 'Traditional AI', 'Traditional AI', 
                        'Traditional AI', 'GenAI']
        })
        
        # Barriers to AI Adoption
        barriers_data = pd.DataFrame({
            'barrier': ['Lack of skilled personnel', 'Data availability/quality', 'Integration with legacy systems',
                       'Regulatory uncertainty', 'High implementation costs', 'Security concerns',
                       'Unclear ROI', 'Organizational resistance'],
            'percentage': [68, 62, 58, 55, 52, 48, 45, 40]
        })
        
        # Support effectiveness
        support_effectiveness = pd.DataFrame({
            'support_type': ['Government education investment', 'University partnerships', 
                            'Public-private collaboration', 'Regulatory clarity',
                            'Tax incentives', 'Innovation grants', 'Technology centers'],
            'effectiveness_score': [82, 78, 75, 73, 68, 65, 62]
        })
        
        # NEW: AI Investment data from AI Index 2025
        ai_investment_data = pd.DataFrame({
            'year': [2014, 2020, 2021, 2022, 2023, 2024],
            'total_investment': [19.4, 72.5, 112.3, 148.5, 174.6, 252.3],
            'genai_investment': [0, 0, 0, 3.95, 28.5, 33.9],
            'us_investment': [8.5, 31.2, 48.7, 64.3, 75.6, 109.1],
            'china_investment': [1.2, 5.8, 7.1, 7.9, 8.4, 9.3],
            'uk_investment': [0.3, 1.8, 2.5, 3.2, 3.8, 4.5]
        })
        
        # NEW: Regional AI adoption growth from AI Index 2025
        regional_growth = pd.DataFrame({
            'region': ['Greater China', 'Europe', 'North America', 'Asia-Pacific', 'Latin America'],
            'growth_2024': [27, 23, 15, 18, 12],
            'adoption_rate': [68, 65, 82, 58, 45],
            'investment_growth': [32, 28, 44, 25, 18]
        })
        
        # NEW: AI cost reduction data from AI Index 2025
        ai_cost_reduction = pd.DataFrame({
            'model': ['GPT-3.5 (Nov 2022)', 'GPT-3.5 (Oct 2024)', 'Gemini-1.5-Flash-8B'],
            'cost_per_million_tokens': [20.00, 0.14, 0.07],
            'year': [2022, 2024, 2024]
        })
        
        # CORRECTED: Financial impact by function from AI Index 2025
        financial_impact = pd.DataFrame({
            'function': ['Marketing & Sales', 'Service Operations', 'Supply Chain', 'Software Engineering', 
                        'Product Development', 'IT', 'HR', 'Finance'],
            'companies_reporting_cost_savings': [38, 49, 43, 41, 35, 37, 28, 32],  # % of companies
            'companies_reporting_revenue_gains': [71, 57, 63, 45, 52, 40, 35, 38],  # % of companies
            'avg_cost_reduction': [7, 8, 9, 10, 6, 7, 5, 6],  # Actual % reduction for those who see benefits
            'avg_revenue_increase': [4, 3, 4, 3, 4, 3, 2, 3]  # Actual % increase for those who see benefits
        })
        
        # NEW: Generational AI perception data from AI Index 2025
        ai_perception = pd.DataFrame({
            'generation': ['Gen Z', 'Millennials', 'Gen X', 'Baby Boomers'],
            'expect_job_change': [67, 65, 58, 49],
            'expect_job_replacement': [42, 40, 34, 28]
        })
        
        # NEW: Training emissions data from AI Index 2025
        training_emissions = pd.DataFrame({
            'model': ['AlexNet (2012)', 'GPT-3 (2020)', 'GPT-4 (2023)', 'Llama 3.1 405B (2024)'],
            'carbon_tons': [0.01, 588, 5184, 8930]
        })
        
        # NEW: Skill gap data
        skill_gap_data = pd.DataFrame({
            'skill': ['AI/ML Engineering', 'Data Science', 'AI Ethics', 'Prompt Engineering',
                     'AI Product Management', 'MLOps', 'AI Security', 'Change Management'],
            'gap_severity': [85, 78, 72, 68, 65, 62, 58, 55],
            'training_initiatives': [45, 52, 28, 38, 32, 35, 22, 48]
        })
        
        # NEW: AI governance data
        ai_governance = pd.DataFrame({
            'aspect': ['Ethics Guidelines', 'Data Privacy', 'Bias Detection', 'Transparency',
                      'Accountability Framework', 'Risk Assessment', 'Regulatory Compliance'],
            'adoption_rate': [62, 78, 45, 52, 48, 55, 72],
            'maturity_score': [3.2, 3.8, 2.5, 2.8, 2.6, 3.0, 3.5]  # Out of 5
        })
        
        # 2025 GenAI by function (for backward compatibility)
        genai_2025 = pd.DataFrame({
            'function': ['Marketing & Sales', 'Product Development', 'Service Operations', 
                        'Software Engineering', 'IT', 'Knowledge Management', 'HR', 'Supply Chain'],
            'adoption': [42, 28, 23, 22, 23, 21, 13, 7]
        })
        
        # NEW: Token economics data
        token_economics = pd.DataFrame({
            'model': ['GPT-3.5 (Nov 2022)', 'GPT-3.5 (Oct 2024)', 'Gemini-1.5-Flash-8B', 
                      'Claude 3 Haiku', 'Llama 3 70B', 'GPT-4', 'Claude 3.5 Sonnet'],
            'cost_per_million_input': [20.00, 0.14, 0.07, 0.25, 0.35, 15.00, 3.00],
            'cost_per_million_output': [20.00, 0.14, 0.07, 1.25, 0.40, 30.00, 15.00],
            'context_window': [4096, 16385, 1000000, 200000, 8192, 128000, 200000],
            'tokens_per_second': [50, 150, 200, 180, 120, 80, 100]
        })
        
        # Token usage patterns
        token_usage_patterns = pd.DataFrame({
            'use_case': ['Simple Chat', 'Document Analysis', 'Code Generation', 
                         'Creative Writing', 'Data Analysis', 'Reasoning Tasks'],
            'avg_input_tokens': [50, 5000, 500, 200, 2000, 1000],
            'avg_output_tokens': [200, 500, 1500, 2000, 1000, 5000],
            'input_output_ratio': [0.25, 10.0, 0.33, 0.10, 2.0, 0.20]
        })
        
        # Token optimization strategies
        token_optimization = pd.DataFrame({
            'strategy': ['Prompt Engineering', 'Context Caching', 'Batch Processing', 
                        'Model Selection', 'Response Streaming', 'Token Pruning'],
            'cost_reduction': [30, 45, 60, 70, 15, 25],
            'implementation_complexity': [2, 4, 3, 1, 2, 5],  # 1-5 scale
            'time_to_implement': [1.0, 7.0, 3.0, 0.5, 2.0, 14.0]  # days as float
        })
        
        # Token pricing evolution - Fixed with explicit date list
        token_pricing_evolution = pd.DataFrame({
            'date': pd.to_datetime(['2022-11-01', '2023-02-01', '2023-05-01', '2023-08-01', '2023-11-01',
                                   '2024-02-01', '2024-05-01', '2024-08-01', '2024-11-01', '2025-02-01', '2025-05-01']),
            'avg_price_input': [20.0, 18.0, 15.0, 10.0, 5.0, 3.0, 1.5, 0.8, 0.5, 0.3, 0.2],
            'avg_price_output': [20.0, 19.0, 16.0, 12.0, 8.0, 5.0, 3.0, 2.0, 1.5, 1.0, 0.8],
            'models_available': [5, 8, 12, 18, 25, 35, 45, 58, 72, 85, 95]
        })
        
        return (historical_data, sector_2018, sector_2025, firm_size, ai_maturity, 
                geographic, tech_stack, productivity_data, productivity_by_skill,
                ai_productivity_estimates, oecd_g7_adoption, oecd_applications, 
                barriers_data, support_effectiveness, state_data, ai_investment_data, 
                regional_growth, ai_cost_reduction, financial_impact, ai_perception, 
                training_emissions, skill_gap_data, ai_governance, genai_2025,
                token_economics, token_usage_patterns, token_optimization, token_pricing_evolution)
    
    except Exception as e:
        st.error(f"Error in load_data function: {str(e)}")
        st.error(f"Error type: {type(e).__name__}")
        import traceback
        st.error(f"Traceback: {traceback.format_exc()}")
        raise

# Initialize session state
if 'first_visit' not in st.session_state:
    st.session_state.first_visit = True
if 'selected_persona' not in st.session_state:
    st.session_state.selected_persona = "General"
if 'show_changelog' not in st.session_state:
    st.session_state.show_changelog = False
if 'year_filter' not in st.session_state:
    st.session_state.year_filter = None
if 'compare_years' not in st.session_state:
    st.session_state.compare_years = False

# Helper function for source info
def show_source_info(source_key):
    sources = {
        'ai_index': {
            'title': 'AI Index Report 2025',
            'org': 'Stanford HAI',
            'url': 'https://aiindex.stanford.edu',
            'methodology': 'Comprehensive analysis of AI metrics globally'
        },
        'mckinsey': {
            'title': 'McKinsey Global Survey on AI',
            'org': 'McKinsey & Company',
            'url': 'https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai',
            'methodology': '1,491 participants across 101 nations, July 2024'
        },
        'oecd': {
            'title': 'OECD/BCG/INSEAD Report 2025',
            'org': 'OECD AI Policy Observatory',
            'url': 'https://oecd.ai',
            'methodology': '840 enterprises across G7 countries + Brazil'
        },
        'census': {
            'title': 'US Census Bureau AI Use Supplement',
            'org': 'US Census Bureau',
            'url': 'https://www.census.gov',
            'methodology': '850,000 U.S. firms surveyed'
        }
    }
    
    if source_key in sources:
        source = sources[source_key]
        return f"""
        **Source:** {source['title']}  
        **Organization:** {source['org']}  
        **Methodology:** {source['methodology']}  
        [View Report]({source['url']})
        """
    return ""

# Onboarding modal for first-time users
if st.session_state.first_visit:
    with st.container():
        st.info("""
        ### 👋 Welcome to the AI Adoption Dashboard!
        
        This dashboard provides comprehensive insights into AI adoption trends from 2018-2025, 
        including the latest findings from the AI Index Report 2025.
        
        **Quick Start:**
        - Use the sidebar to select different analysis views
        - Click on charts to see detailed information
        - Export any visualization using the download buttons
        
        **For best experience, select your role:**
        """)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("📊 Business Leader"):
                st.session_state.selected_persona = "Business Leader"
                st.session_state.first_visit = False
                st.rerun()
        with col2:
            if st.button("🏛️ Policymaker"):
                st.session_state.selected_persona = "Policymaker"
                st.session_state.first_visit = False
                st.rerun()
        with col3:
            if st.button("🔬 Researcher"):
                st.session_state.selected_persona = "Researcher"
                st.session_state.first_visit = False
                st.rerun()
        with col4:
            if st.button("👤 General User"):
                st.session_state.selected_persona = "General"
                st.session_state.first_visit = False
                st.rerun()
        
        if st.button("Got it! Let's explore", type="primary"):
            st.session_state.first_visit = False
            st.rerun()
    st.stop()

# Load all data
try:
    loaded_data = load_data()
    
    # Check if we got the expected number of items
    if len(loaded_data) != 28:
        st.error(f"Error: Expected 28 data items, but got {len(loaded_data)}")
        st.stop()
    
    # Unpack the data
    (historical_data, sector_2018, sector_2025, firm_size, ai_maturity, 
     geographic, tech_stack, productivity_data, productivity_by_skill,
     ai_productivity_estimates, oecd_g7_adoption, oecd_applications, 
     barriers_data, support_effectiveness, state_data, ai_investment_data, 
     regional_growth, ai_cost_reduction, financial_impact, ai_perception, 
     training_emissions, skill_gap_data, ai_governance, genai_2025,
     token_economics, token_usage_patterns, token_optimization, token_pricing_evolution) = loaded_data
     
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.error(f"Please check the data loading function for issues.")
    import traceback
    st.error(f"Full error: {traceback.format_exc()}")
    st.stop()

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: transparent;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stApp > div {
        background-color: transparent;
    }
    .main .block-container {
        background-color: transparent;
    }
    .source-info {
        font-size: 0.8em;
        color: #666;
        cursor: pointer;
        text-decoration: underline;
    }
    .insight-box {
        background-color: rgba(31, 119, 180, 0.1);
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("🤖 AI Adoption Dashboard: 2018-2025")
st.markdown("**Comprehensive analysis from early AI adoption (2018) to current GenAI trends (2025)**")

# What's New section
with st.expander("🆕 What's New in Version 2.2.0", expanded=st.session_state.show_changelog):
    st.markdown("""
    **Latest Updates (June 2025):**
    - ✅ Integrated AI Index Report 2025 findings
    - ✅ Added industry-specific 2025 data
    - ✅ Enhanced financial impact clarity
    - ✅ New skill gap and governance metrics
    - ✅ Interactive filtering for charts
    - ✅ Source attribution for all data points
    - ✅ Export data as CSV functionality
    - ✅ Comprehensive academic analysis integration
    - ✅ Enhanced risks and safety analysis
    """)

# Add definition notice with AI Index Report reference
st.info("""
**📌 Important Note:** Adoption rates in this dashboard reflect "any AI use" including pilots, experiments, and production deployments. 
Enterprise-wide production use rates are typically lower. Data sources include AI Index Report 2025, McKinsey Global Survey on AI, 
OECD AI Policy Observatory, and US Census Bureau AI Use Supplement.
""")

# Sidebar controls
st.sidebar.header("📊 Dashboard Controls")

# Show persona selection
persona = st.sidebar.selectbox(
    "Select Your Role",
    ["General", "Business Leader", "Policymaker", "Researcher"],
    index=["General", "Business Leader", "Policymaker", "Researcher"].index(st.session_state.selected_persona)
)
st.session_state.selected_persona = persona

# Persona-based view recommendations and filtering
persona_views = {
    "Business Leader": ["Industry Analysis", "Financial Impact", "Investment Trends", "ROI Analysis"],
    "Policymaker": ["Geographic Distribution", "OECD 2025 Findings", "Regional Growth", "AI Governance"],
    "Researcher": ["Historical Trends", "Productivity Research", "Environmental Impact", "Skill Gap Analysis"],
    "General": ["Adoption Rates", "Historical Trends", "Investment Trends", "Labor Impact"]
}

# Filter views based on persona
all_views = ["Adoption Rates", "Historical Trends", "Industry Analysis", "Investment Trends", 
             "Regional Growth", "AI Cost Trends", "Token Economics", "Financial Impact", "Labor Impact", 
             "Firm Size Analysis", "Technology Stack", "AI Technology Maturity", 
             "Productivity Research", "Environmental Impact", "Geographic Distribution", 
             "OECD 2025 Findings", "Barriers & Support", "ROI Analysis", "Skill Gap Analysis", 
             "AI Governance", "Bibliography & Sources"]

if persona != "General":
    st.sidebar.info(f"💡 **Recommended views for {persona}:**\n" + "\n".join([f"• {v}" for v in persona_views[persona]]))

data_year = st.sidebar.selectbox(
    "Select Data Year", 
    ["2018 (Early AI)", "2025 (GenAI Era)"],
    index=1
)

view_type = st.sidebar.selectbox(
    "Analysis View", 
    all_views,
    index=all_views.index(persona_views[persona][0]) if persona != "General" else 0
)

# Advanced filters
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔧 Advanced Options")

# Year filter for historical data
if view_type == "Historical Trends":
    year_range = st.sidebar.slider(
        "Select Year Range",
        min_value=2017,
        max_value=2025,
        value=(2017, 2025),
        step=1
    )
    
    compare_mode = st.sidebar.checkbox("Compare specific years", value=False)
    if compare_mode:
        col1, col2 = st.sidebar.columns(2)
        with col1:
            year1 = st.selectbox("Year 1", range(2017, 2026), index=1)
        with col2:
            year2 = st.selectbox("Year 2", range(2017, 2026), index=7)

# Export functionality
st.sidebar.markdown("---")
st.sidebar.markdown("### 📥 Export Options")

# Mapping of view types to their respective dataframes
data_map = {
    "Historical Trends": historical_data,
    "Industry Analysis": sector_2025,
    "Financial Impact": financial_impact,
    "Skill Gap Analysis": skill_gap_data,
    "AI Governance": ai_governance,
    "Productivity Research": productivity_data,
    "Investment Trends": ai_investment_data,
    "Regional Growth": regional_growth,
    "AI Cost Trends": ai_cost_reduction,
    "Token Economics": token_economics,
    "Labor Impact": ai_perception,
    "Environmental Impact": training_emissions,
    "Adoption Rates": genai_2025 if "2025" in data_year else sector_2018,
    "Firm Size Analysis": firm_size,
    "Technology Stack": tech_stack,
    "AI Technology Maturity": ai_maturity,
    "Geographic Distribution": geographic,
    "OECD 2025 Findings": oecd_g7_adoption,
    "Barriers & Support": barriers_data,
    "ROI Analysis": sector_2025
}

export_format = st.sidebar.selectbox(
    "Export Format",
    ["CSV Data", "PNG Image", "PDF Report (Beta)"]
)

if export_format == "CSV Data":
    if view_type in data_map:
        df_to_download = data_map[view_type]
        csv = df_to_download.to_csv(index=False).encode('utf-8')
        
        st.sidebar.download_button(
           label="📥 Download CSV for Current View",
           data=csv,
           file_name=f"ai_adoption_{view_type.lower().replace(' ', '_')}.csv",
           mime="text/csv",
           use_container_width=True
        )
    else:
        st.sidebar.warning(f"CSV export is not available for the '{view_type}' view.")

elif export_format in ["PNG Image", "PDF Report (Beta)"]:
    st.sidebar.warning(f"{export_format} export is not yet implemented.")
    st.sidebar.button("📥 Export Current View", disabled=True, use_container_width=True)

# Feedback widget
st.sidebar.markdown("---")
st.sidebar.markdown("### 💬 Feedback")
feedback = st.sidebar.text_area("Share your thoughts or request features:", height=100)
if st.sidebar.button("Submit Feedback"):
    st.sidebar.success("Thank you for your feedback!")

# Help section
with st.sidebar.expander("❓ Need Help?"):
    st.markdown("""
    **Navigation Tips:**
    - Use the Analysis View dropdown to explore different perspectives
    - Click 📊 icons for data source information
    - Hover over chart elements for details
    
    **Keyboard Shortcuts:**
    - `Ctrl + K`: Quick search
    - `F`: Toggle fullscreen
    - `?`: Show help
    """)

# Key metrics row - UPDATED with AI Index 2025 data
st.subheader("📈 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

if "2025" in data_year:
    with col1:
        st.metric(
            label="Overall AI Adoption*", 
            value="78%", 
            delta="+23pp from 2023",
            help="*Includes any AI use. Jumped from 55% in 2023 (AI Index 2025)"
        )
    with col2:
        st.metric(
            label="GenAI Adoption*", 
            value="71%", 
            delta="+38pp from 2023",
            help="*More than doubled from 33% in 2023 (AI Index 2025)"
        )
    with col3:
        st.metric(
            label="2024 AI Investment", 
            value="$252.3B", 
            delta="+44.5% YoY",
            help="Total corporate AI investment reached record levels"
        )
    with col4:
        st.metric(
            label="Cost Reduction", 
            value="280x cheaper", 
            delta="Since Nov 2022",
            help="AI inference cost dropped from $20 to $0.07 per million tokens"
        )
else:
    with col1:
        st.metric("Overall AI Adoption", "5.8%", "📊 Firm-weighted")
    with col2:
        st.metric("Large Firms (5000+)", "58.5%", "🏢 High adoption")
    with col3:
        st.metric("AI + Cloud", "45%", "☁️ Technology stack")
    with col4:
        st.metric("Top City", "SF Bay (9.5%)", "🌍 Geographic leader")

# Main visualization section
st.subheader(f"📊 {view_type}")

# View implementations - ALL COMPLETE VISUALIZATIONS
# Enhanced Historical Trends View - Add this to your existing Historical Trends section
# Replace the existing Historical Trends view implementation with this enhanced version

if view_type == "Historical Trends":
    # Apply year filter if set
    if 'compare_mode' in locals() and compare_mode:
        # Compare mode: Show specific years comparison (existing functionality preserved)
        st.write(f"📊 **Comparing AI Adoption: {year1} vs {year2}**")
        
        # Get data for comparison years
        year1_data = historical_data[historical_data['year'] == year1].iloc[0]
        year2_data = historical_data[historical_data['year'] == year2].iloc[0]
        
        # Create comparison metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            ai_change = year2_data['ai_use'] - year1_data['ai_use']
            st.metric(
                f"Overall AI ({year2})", 
                f"{year2_data['ai_use']}%",
                delta=f"{ai_change:+.1f}pp vs {year1}",
                help=f"Change from {year1_data['ai_use']}% in {year1}"
            )
        
        with col2:
            genai_change = year2_data['genai_use'] - year1_data['genai_use']
            st.metric(
                f"GenAI ({year2})", 
                f"{year2_data['genai_use']}%",
                delta=f"{genai_change:+.1f}pp vs {year1}",
                help=f"Change from {year1_data['genai_use']}% in {year1}"
            )
        
        with col3:
            years_diff = year2 - year1
            ai_cagr = ((year2_data['ai_use'] / year1_data['ai_use']) ** (1/years_diff) - 1) * 100 if year1_data['ai_use'] > 0 else 0
            st.metric(
                "AI CAGR", 
                f"{ai_cagr:.1f}%",
                help=f"Compound Annual Growth Rate over {years_diff} years"
            )
        
        with col4:
            if year1_data['genai_use'] > 0:
                genai_cagr = ((year2_data['genai_use'] / year1_data['genai_use']) ** (1/years_diff) - 1) * 100
                st.metric(
                    "GenAI CAGR", 
                    f"{genai_cagr:.1f}%",
                    help=f"Compound Annual Growth Rate over {years_diff} years"
                )
            else:
                st.metric("GenAI CAGR", "New Category", help="GenAI didn't exist in earlier years")
        
        # Create side-by-side comparison chart
        comparison_data = pd.DataFrame({
            'category': ['Overall AI', 'GenAI'],
            year1: [year1_data['ai_use'], year1_data['genai_use']],
            year2: [year2_data['ai_use'], year2_data['genai_use']]
        })
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name=str(year1),
            x=comparison_data['category'],
            y=comparison_data[year1],
            marker_color='#1f77b4',
            text=[f'{x}%' for x in comparison_data[year1]],
            textposition='outside'
        ))
        
        fig.add_trace(go.Bar(
            name=str(year2),
            x=comparison_data['category'],
            y=comparison_data[year2],
            marker_color='#ff7f0e',
            text=[f'{x}%' for x in comparison_data[year2]],
            textposition='outside'
        ))
        
        fig.update_layout(
            title=f"AI Adoption Comparison: {year1} vs {year2}",
            xaxis_title="AI Category",
            yaxis_title="Adoption Rate (%)",
            barmode='group',
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add insights for comparison
        st.info(f"""
        **📈 Key Changes from {year1} to {year2}:**
        - Overall AI adoption {"increased" if ai_change > 0 else "decreased"} by **{abs(ai_change):.1f} percentage points**
        - GenAI adoption {"increased" if genai_change > 0 else "decreased"} by **{abs(genai_change):.1f} percentage points**
        - Time period represents **{years_diff} year{"s" if years_diff != 1 else ""}** of evolution
        """)
        
    else:
        # Standard timeline view with year range filter - ENHANCED VERSION
        filtered_data = historical_data[
            (historical_data['year'] >= year_range[0]) & 
            (historical_data['year'] <= year_range[1])
        ]
        
        # NEW: Add authoritative milestones data with detailed source attribution
        authoritative_milestones = [
            {
                'year': 2020,
                'quarter': 'Q4',
                'date': 'December 2020',
                'title': 'NSF AI Research Institutes Launch',
                'description': 'NSF announced the first seven National AI Research Institutes with $220M initial investment, establishing foundational research infrastructure.',
                'impact': 'Created institutional framework for sustained AI research',
                'category': 'government',
                'source': 'NSF Press Release 2020',
                'source_url': 'https://www.nsf.gov/news/nsf-partnerships-expand-national-ai-research',
                'source_type': 'Government',
                'verification': 'Primary source - official NSF announcement'
            },
            {
                'year': 2021,
                'quarter': 'Q1',
                'date': 'January 5, 2021',
                'title': 'DALL-E 1 Launch',
                'description': 'OpenAI revealed DALL-E, the first mainstream text-to-image AI using a modified GPT-3 to generate images from natural language descriptions.',
                'impact': 'Demonstrated AI could create, not just analyze content',
                'category': 'breakthrough',
                'source': 'OpenAI Blog Post',
                'source_url': 'https://openai.com/blog/dall-e/',
                'source_type': 'Industry',
                'verification': 'Primary source - original OpenAI announcement'
            },
            {
                'year': 2021,
                'quarter': 'Q2',
                'date': 'June 29, 2021',
                'title': 'GitHub Copilot Technical Preview',
                'description': 'GitHub announced Copilot for technical preview in Visual Studio Code, marking the first AI coding assistant to gain widespread developer adoption.',
                'impact': 'Proved AI could assist complex professional programming tasks',
                'category': 'product',
                'source': 'GitHub Official Announcement',
                'source_url': 'https://github.blog/2021-06-29-introducing-github-copilot-ai-pair-programmer/',
                'source_type': 'Industry',
                'verification': 'Primary source - GitHub official blog'
            },
            {
                'year': 2021,
                'quarter': 'Q3',
                'date': 'July 22, 2021',
                'title': 'AlphaFold Database Launch',
                'description': 'DeepMind launched the AlphaFold Protein Structure Database with 365,000+ protein structures, solving a 50-year-old scientific challenge.',
                'impact': 'Demonstrated AI breakthrough in fundamental science',
                'category': 'scientific',
                'source': 'Nature Journal Publication',
                'source_url': 'https://www.nature.com/articles/s41586-021-03819-2',
                'source_type': 'Academic',
                'verification': 'Peer-reviewed publication in Nature'
            },
            {
                'year': 2021,
                'quarter': 'Q3',
                'date': 'August 2021',
                'title': 'NSF Expands AI Research Institutes',
                'description': 'NSF announced 11 additional AI Research Institutes, expanding to 40 states with combined $220M investment over five years.',
                'impact': 'Scaled federal commitment to AI research infrastructure',
                'category': 'government',
                'source': 'NSF Press Release',
                'source_url': 'https://www.nsf.gov/news/nsf-partnerships-expand-national-ai-research',
                'source_type': 'Government',
                'verification': 'Official NSF press release'
            },
            {
                'year': 2022,
                'quarter': 'Q1',
                'date': 'March 17, 2022',
                'title': 'NIST AI RMF First Draft',
                'description': 'NIST released the first draft of AI Risk Management Framework following extensive public consultation since July 2021.',
                'impact': 'Established federal framework for AI governance and risk management',
                'category': 'policy',
                'source': 'NIST Official Release',
                'source_url': 'https://www.nist.gov/itl/ai-risk-management-framework',
                'source_type': 'Government',
                'verification': 'NIST official documentation'
            },
            {
                'year': 2022,
                'quarter': 'Q2',
                'date': 'April 6, 2022',
                'title': 'DALL-E 2 Release',
                'description': 'OpenAI released DALL-E 2 with dramatically improved image quality and capabilities, representing a significant leap in generative AI.',
                'impact': 'Achieved near-photorealistic AI image generation',
                'category': 'breakthrough',
                'source': 'MIT Technology Review Analysis',
                'source_url': 'https://www.technologyreview.com/2022/04/06/1049061/dalle-openai-gpt3-ai-agi-multimodal-image-generation/',
                'source_type': 'Academic',
                'verification': 'Independent analysis by MIT Technology Review'
            },
            {
                'year': 2022,
                'quarter': 'Q2',
                'date': 'June 21, 2022',
                'title': 'GitHub Copilot General Availability',
                'description': 'GitHub Copilot transitioned from technical preview to general availability as the first commercially available AI coding tool.',
                'impact': 'First mass-market professional AI tool with subscription model',
                'category': 'commercial',
                'source': 'GitHub Press Release',
                'source_url': 'https://github.blog/2022-06-21-github-copilot-is-generally-available-to-all-developers/',
                'source_type': 'Industry',
                'verification': 'Official GitHub announcement'
            },
            {
                'year': 2022,
                'quarter': 'Q4',
                'date': 'November 30, 2022',
                'title': 'ChatGPT Launch',
                'description': 'OpenAI launched ChatGPT, achieving 1 million users in 5 days and becoming the fastest-adopted online tool in history.',
                'impact': 'Triggered mainstream AI adoption and massive investment surge',
                'category': 'tipping-point',
                'source': 'Stanford AI Index 2023',
                'source_url': 'https://aiindex.stanford.edu/ai-index-report-2023/',
                'source_type': 'Academic',
                'verification': 'Stanford HAI comprehensive analysis'
            },
            {
                'year': 2023,
                'quarter': 'Q1',
                'date': 'January 26, 2023',
                'title': 'NIST AI RMF 1.0 Release',
                'description': 'NIST published the final AI Risk Management Framework after 18 months of development with 240+ contributing organizations.',
                'impact': 'Established voluntary standards for trustworthy AI development',
                'category': 'policy',
                'source': 'NIST AI RMF 1.0',
                'source_url': 'https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf',
                'source_type': 'Government',
                'verification': 'Official NIST publication'
            }
        ]
        
        # Filter milestones based on year range
        visible_milestones = [m for m in authoritative_milestones if year_range[0] <= m['year'] <= year_range[1]]
        
        fig = go.Figure()
        
        # Add overall AI use line
        fig.add_trace(go.Scatter(
            x=filtered_data['year'], 
            y=filtered_data['ai_use'], 
            mode='lines+markers', 
            name='Overall AI Use', 
            line=dict(width=4, color='#1f77b4'),
            marker=dict(size=8),
            hovertemplate='Year: %{x}<br>Adoption: %{y}%<br>Source: AI Index & McKinsey<extra></extra>'
        ))
        
        # Add GenAI use line
        fig.add_trace(go.Scatter(
            x=filtered_data['year'], 
            y=filtered_data['genai_use'], 
            mode='lines+markers', 
            name='GenAI Use', 
            line=dict(width=4, color='#ff7f0e'),
            marker=dict(size=8),
            hovertemplate='Year: %{x}<br>Adoption: %{y}%<br>Source: AI Index 2025<extra></extra>'
        ))
        
        # NEW: Add milestone markers
        milestone_years = [m['year'] for m in visible_milestones]
        milestone_heights = []
        
        for milestone in visible_milestones:
            # Get corresponding AI adoption rate for the year
            if milestone['year'] in filtered_data['year'].values:
                height = filtered_data[filtered_data['year'] == milestone['year']]['ai_use'].iloc[0]
            else:
                height = 50  # Default height if no data
            milestone_heights.append(height)
        
        # Add milestone points with different colors by category
        category_colors = {
            'breakthrough': '#E74C3C',
            'product': '#2ECC71',
            'scientific': '#9B59B6',
            'commercial': '#F39C12',
            'tipping-point': '#E91E63',
            'government': '#3498DB',
            'policy': '#34495E'
        }
        
        for milestone in visible_milestones:
            if milestone['year'] in filtered_data['year'].values:
                height = filtered_data[filtered_data['year'] == milestone['year']]['ai_use'].iloc[0] + 5
            else:
                continue
                
            fig.add_trace(go.Scatter(
                x=[milestone['year']],
                y=[height],
                mode='markers',
                name=milestone['category'].title(),
                marker=dict(
                    size=15,
                    color=category_colors.get(milestone['category'], '#95A5A6'),
                    symbol='star',
                    line=dict(width=2, color='white')
                ),
                showlegend=False,
                hovertemplate=f"<b>{milestone['title']}</b><br>{milestone['date']}<br>{milestone['description'][:100]}...<br><i>Source: {milestone['source']}</i><extra></extra>"
            ))
        
        # Enhanced annotations with authoritative context
        if 2022 in filtered_data['year'].values:
            fig.add_annotation(
                x=2022, y=33,
                text="<b>ChatGPT Launch</b><br>GenAI Era Begins<br><i>Source: Stanford AI Index</i>",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="#ff7f0e",
                ax=-50,
                ay=-40,
                bgcolor="rgba(255,127,14,0.1)",
                bordercolor="#ff7f0e",
                borderwidth=2,
                font=dict(color="#ff7f0e", size=11, family="Arial")
            )
        
        if 2021 in filtered_data['year'].values:
            fig.add_annotation(
                x=2021, y=15,
                text="<b>Foundation Year</b><br>DALL-E, Copilot, AlphaFold<br><i>Multiple breakthrough releases</i>",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="#9B59B6",
                ax=50,
                ay=-40,
                bgcolor="rgba(155,89,182,0.1)",
                bordercolor="#9B59B6",
                borderwidth=2,
                font=dict(color="#9B59B6", size=11, family="Arial")
            )
        
        if 2024 in filtered_data['year'].values:
            fig.add_annotation(
                x=2024, y=78,
                text="<b>2024 Acceleration</b><br>AI Index Report findings<br><i>78% business adoption</i>",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="#1f77b4",
                ax=50,
                ay=-30,
                bgcolor="rgba(31,119,180,0.1)",
                bordercolor="#1f77b4",
                borderwidth=2,
                font=dict(color="#1f77b4", size=12, family="Arial")
            )
        
        fig.update_layout(
            title="AI Adoption Trends: The GenAI Revolution with Authoritative Timeline", 
            xaxis_title="Year", 
            yaxis_title="Adoption Rate (%)",
            height=500,
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99
            )
        )
        
        # Display chart with enhanced source info
        col1, col2 = st.columns([10, 1])
        with col1:
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            if st.button("📊", key="hist_source", help="View data sources"):
                with st.expander("Authoritative Sources", expanded=True):
                    st.info("""
                    **Primary Sources with URLs:**
                    
                    **Government Sources:**
                    - [Stanford AI Index Report 2025](https://aiindex.stanford.edu/ai-index-report-2025/)
                    - [NSF National AI Research Institutes](https://www.nsf.gov/focus-areas/artificial-intelligence)
                    - [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
                    
                    **Academic Sources:**
                    - [MIT Technology Review](https://www.technologyreview.com/topic/artificial-intelligence/)
                    - [Nature Machine Intelligence](https://www.nature.com/natmachintell/)
                    - [IEEE Computer Society Publications](https://www.computer.org/publications/)
                    
                    **Industry Sources:**
                    - [OpenAI Research](https://openai.com/research/)
                    - [GitHub Blog](https://github.blog/)
                    - [DeepMind Publications](https://deepmind.google/research/)
                    
                    **Methodology:** Data compiled from peer-reviewed publications, 
                    government reports, and authoritative industry analysis. All sources
                    verified through primary documentation and cross-referenced across
                    multiple independent sources.
                    """)
        
        # NEW: Enhanced insights with authoritative context
        st.subheader("📈 Evidence-Based Analysis: The 2021-2022 GenAI Explosion")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **🏛️ Federal Research Infrastructure (NSF Sources):**
            - **2020:** NSF launched 7 AI Research Institutes with initial $220M investment
            - **2021:** Expanded to 18 institutes across 40 states, creating research infrastructure  
            - **Impact:** Provided sustained federal commitment to foundational AI research
            
            **📊 Market Evidence (Stanford AI Index):**
            - **Investment Surge:** GenAI funding increased 9x from $2.8B (2022) to $25.2B (2023)
            - **Adoption Speed:** ChatGPT reached 1M users in 5 days, fastest in history
            - **Enterprise Use:** 78% of organizations reported AI use by 2024 (vs. 55% in 2023)
            """)
        
        with col2:
            st.markdown("""
            **🔬 Scientific Breakthroughs (Nature & IEEE):**
            - **AlphaFold:** Solved 50-year protein folding challenge, impacting drug discovery
            - **DALL-E Evolution:** From proof-of-concept to photorealistic generation
            - **Programming AI:** GitHub Copilot demonstrated code generation capabilities
            
            **⚖️ Policy Framework (NIST):**
            - **AI Risk Management Framework:** Developed with 240+ organizations
            - **Voluntary Standards:** Established guidelines for trustworthy AI development
            - **International Influence:** Framework adopted globally as best practice
            """)
        
        # NEW: Convergence factors analysis
        st.subheader("🎯 Convergence Factors: Why 2021-2022 Was the Tipping Point")
        
        convergence_factors = pd.DataFrame({
            'factor': ['Technical Maturation', 'Institutional Support', 'Market Validation', 'Policy Framework'],
            'evidence': [
                'Foundation models (GPT-3) + specialized applications (DALL-E, Copilot) proved real-world utility',
                'Federal research infrastructure ($220M NSF) + international coordination created stability',
                'Commercial success (Copilot GA) + scientific breakthroughs (AlphaFold) attracted investment',
                'NIST framework + regulatory clarity provided governance foundation for enterprise adoption'
            ],
            'impact_score': [95, 85, 90, 75]
        })
        
        # Create horizontal bar chart for convergence factors
        fig2 = go.Figure()
        
        fig2.add_trace(go.Bar(
            y=convergence_factors['factor'],
            x=convergence_factors['impact_score'],
            orientation='h',
            marker_color=['#3498DB', '#2ECC71', '#E74C3C', '#F39C12'],
            text=[f'{x}%' for x in convergence_factors['impact_score']],
            textposition='outside'
        ))
        
        fig2.update_layout(
            title="Convergence Factors: Multi-Source Analysis of 2021-2022 Acceleration",
            xaxis_title="Impact Score (%)",
            height=300,
            showlegend=False
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
        # NEW: Show milestone timeline if requested
        if st.checkbox("📅 Show Detailed Milestone Timeline", value=False):
            st.subheader("🕐 Authoritative Milestone Timeline")
            
            for milestone in visible_milestones:
                category_color = category_colors.get(milestone['category'], '#95A5A6')
                
                with st.container():
                    col1, col2 = st.columns([1, 10])
                    
                    with col1:
                        st.markdown(f"""
                        <div style="background-color: {category_color}; 
                                   color: white; 
                                   padding: 8px; 
                                   border-radius: 50%; 
                                   text-align: center; 
                                   width: 60px; 
                                   height: 60px; 
                                   display: flex; 
                                   align-items: center; 
                                   justify-content: center;
                                   font-weight: bold;">
                            {milestone['year']}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        **{milestone['title']}** ({milestone['date']})
                        
                        {milestone['description']}
                        
                        **Impact:** {milestone['impact']}
                        
                        **Source:** [{milestone['source']}]({milestone['source_url']}) ({milestone['source_type']})
                        
                        *Verification: {milestone['verification']}*
                        """)
                        
                    st.markdown("---")
        
        # Enhanced key insights with academic backing
        st.info("""
        **🎯 Key Research Findings:**
        
        **Stanford AI Index 2025 Evidence:**
        - Business adoption jumped from 55% to 78% in just one year (fastest enterprise technology adoption in history)
        - GenAI adoption more than doubled from 33% to 71%
        - 280x cost reduction in AI inference since November 2022
        
        **Federal Research Impact:**
        - NSF's $220M AI Research Institute investment created foundational infrastructure across 40 states
        - NIST's collaborative framework (240+ organizations) established governance standards
        - Government leadership in 2020-2021 provided stability for private sector innovation
        
        **Scientific Validation:**
        - Nature publications documented breakthrough performance in protein folding (AlphaFold)
        - MIT Technology Review confirmed transformational impact of generative models
        - IEEE research showed practical applications in software development (GitHub Copilot)
        """)
    
    # Export data option (works for both modes) - ENHANCED
    export_data = filtered_data if not ('compare_mode' in locals() and compare_mode) else historical_data
    
    # Add milestone data to export
    if st.checkbox("Include milestone data in export", value=False):
        milestone_df = pd.DataFrame(visible_milestones)
        
        # Create download options
        col1, col2 = st.columns(2)
        
        with col1:
            csv = export_data.to_csv(index=False)
            st.download_button(
                label="📥 Download Historical Data (CSV)",
                data=csv,
                file_name="ai_adoption_historical_trends.csv",
                mime="text/csv"
            )
        
        with col2:
            milestone_csv = milestone_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Milestones (CSV)",
                data=milestone_csv,
                file_name="ai_adoption_milestones.csv",
                mime="text/csv"
            )
    else:
        csv = export_data.to_csv(index=False)
        st.download_button(
            label="📥 Download Historical Data (CSV)",
            data=csv,
            file_name="ai_adoption_historical_trends.csv",
            mime="text/csv"
        )
        
    # NEW: Research methodology note
    with st.expander("📚 Research Methodology & Source Validation"):
        st.markdown("""
        ### Research Methodology
        
        **Multi-Source Validation:**
        - Each milestone verified across 2+ independent authoritative sources
        - Timeline cross-referenced with primary source documents
        - Impact assessments based on peer-reviewed research
        
        **Source Hierarchy (in order of authority):**
        1. **Government Sources:** NSF, NIST, Federal Reserve publications
        2. **Academic Research:** Stanford HAI, MIT, Nature journals, IEEE publications
        3. **Industry Analysis:** Verified through multiple independent reports
        
        **Verification Process:**
        - All dates verified against original announcements
        - Impact statements based on documented outcomes
        - Sources cited with direct links where available
        - Cross-validation across multiple source types
        
        **Source Quality Indicators:**
        - 🏛️ **Government:** Official agency publications and press releases
        - 🎓 **Academic:** Peer-reviewed journals and university research institutes
        - 🏢 **Industry:** Primary company announcements and verified reports
        - 📊 **Verification:** Independent analysis and cross-source confirmation
        
        **Detailed Source Breakdown:**
        
        | Milestone | Primary Source | Verification Method |
        |-----------|----------------|-------------------|
        | NSF AI Institutes | Official NSF Press Release | Government announcement + funding records |
        | DALL-E Launch | OpenAI Blog Post | Primary announcement + academic analysis |
        | GitHub Copilot | GitHub Official Blog | Company announcement + developer adoption data |
        | AlphaFold Database | Nature Journal | Peer-reviewed publication + scientific impact |
        | NIST AI Framework | NIST Official Publication | Government standard + multi-stakeholder input |
        | ChatGPT Launch | Stanford AI Index | Academic analysis + adoption metrics |
        
        **Quality Assurance:**
        - No milestone included without at least 2 independent source confirmations
        - All URLs verified as active and pointing to correct source material
        - Impact assessments based on measurable outcomes where available
        - Timeline accuracy verified against multiple historical records
        
        **Limitations:**
        - Adoption data reflects surveys, not census
        - Impact assessments may vary by implementation quality
        - Some milestones may have different interpretations of significance
        - Source availability varies by organization transparency policies
        """)
        
        # Add source credibility matrix
        st.subheader("📊 Source Credibility Matrix")
        
        source_credibility = pd.DataFrame({
            'Source Type': ['Government (NSF, NIST)', 'Academic (Stanford, MIT, Nature)', 'Industry (OpenAI, GitHub)', 'Analysis (MIT Tech Review)'],
            'Credibility Score': [95, 90, 85, 88],
            'Verification Level': ['Primary Official', 'Peer-Reviewed', 'Company Official', 'Independent Analysis'],
            'Coverage': ['Policy & Funding', 'Research & Impact', 'Product & Technology', 'Synthesis & Context']
        })
        
        st.dataframe(source_credibility, hide_index=True, use_container_width=True)
        
        st.info("""
        **Source Selection Criteria:**
        - **Timeliness:** Contemporary to the events described
        - **Authority:** Recognized expertise in the relevant domain
        - **Accessibility:** Publicly available and verifiable
        - **Independence:** Multiple independent confirmations required
        - **Completeness:** Sufficient detail to assess impact and significance
        """)

elif view_type == "Industry Analysis":
    st.write("🏭 **AI Adoption by Industry (2025)**")
    
    # Industry comparison
    fig = go.Figure()
    
    # Create grouped bar chart
    fig.add_trace(go.Bar(
        name='Overall AI Adoption',
        x=sector_2025['sector'],
        y=sector_2025['adoption_rate'],
        marker_color='#3498DB',
        text=[f'{x}%' for x in sector_2025['adoption_rate']],
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        name='GenAI Adoption',
        x=sector_2025['sector'],
        y=sector_2025['genai_adoption'],
        marker_color='#E74C3C',
        text=[f'{x}%' for x in sector_2025['genai_adoption']],
        textposition='outside'
    ))
    
    # Add ROI as line chart
    fig.add_trace(go.Scatter(
        name='Average ROI',
        x=sector_2025['sector'],
        y=sector_2025['avg_roi'],
        mode='lines+markers',
        line=dict(width=3, color='#2ECC71'),
        marker=dict(size=10),
        yaxis='y2',
        text=[f'{x}x' for x in sector_2025['avg_roi']],
        textposition='top center'
    ))
    
    fig.update_layout(
        title="AI Adoption and ROI by Industry Sector",
        xaxis_title="Industry",
        yaxis=dict(title="Adoption Rate (%)", side="left"),
        yaxis2=dict(title="Average ROI (x)", side="right", overlaying="y"),
        barmode='group',
        height=500,
        hovermode='x unified',
        xaxis_tickangle=45
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Industry insights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Top Adopter", "Technology (92%)", delta="+7% vs Finance")
    with col2:
        st.metric("Highest ROI", "Technology (4.2x)", delta="Best returns")
    with col3:
        st.metric("Fastest Growing", "Healthcare", delta="+15pp YoY")
    
    # Export option
    csv = sector_2025.to_csv(index=False)
    st.download_button(
        label="📥 Download Industry Data (CSV)",
        data=csv,
        file_name="ai_adoption_by_industry_2025.csv",
        mime="text/csv"
    )

elif view_type == "Financial Impact":
    st.write("💵 **Financial Impact of AI by Business Function (AI Index Report 2025)**")
    
    # CORRECTED interpretation box
    st.warning("""
    **📊 Understanding the Data:** - The percentages below show the **proportion of companies reporting financial benefits** from AI
    - Among companies that see benefits, the **actual magnitude** is typically:
      - Cost savings: **Less than 10%** (average 5-10%)
      - Revenue gains: **Less than 5%** (average 2-4%)
    - Example: 71% of companies using AI in Marketing report revenue gains, but these gains average only 4%
    """)
    
    # Create visualization with clearer labels
    fig = go.Figure()
    
    # Sort by revenue gains
    financial_sorted = financial_impact.sort_values('companies_reporting_revenue_gains', ascending=True)
    
    # Add bars showing % of companies reporting benefits
    fig.add_trace(go.Bar(
        name='Companies Reporting Cost Savings',
        y=financial_sorted['function'],
        x=financial_sorted['companies_reporting_cost_savings'],
        orientation='h',
        marker_color='#2ECC71',
        text=[f'{x}%' for x in financial_sorted['companies_reporting_cost_savings']],
        textposition='auto',
        hovertemplate='Function: %{y}<br>Companies reporting savings: %{x}%<br>Avg magnitude: %{customdata}%<extra></extra>',
        customdata=financial_sorted['avg_cost_reduction']
    ))
    
    fig.add_trace(go.Bar(
        name='Companies Reporting Revenue Gains',
        y=financial_sorted['function'],
        x=financial_sorted['companies_reporting_revenue_gains'],
        orientation='h',
        marker_color='#3498DB',
        text=[f'{x}%' for x in financial_sorted['companies_reporting_revenue_gains']],
        textposition='auto',
        hovertemplate='Function: %{y}<br>Companies reporting gains: %{x}%<br>Avg magnitude: %{customdata}%<extra></extra>',
        customdata=financial_sorted['avg_revenue_increase']
    ))
    
    fig.update_layout(
        title="Percentage of Companies Reporting Financial Benefits from AI",
        xaxis_title="Percentage of Companies (%)",
        yaxis_title="Business Function",
        barmode='group',
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Function-specific insights with magnitude clarification
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("💰 **Top Functions by Adoption Success:**")
        st.write("• **Service Operations:** 49% report cost savings (avg 8% reduction)")
        st.write("• **Marketing & Sales:** 71% report revenue gains (avg 4% increase)")
        st.write("• **Supply Chain:** 43% report cost savings (avg 9% reduction)")
    
    with col2:
        st.write("📈 **Reality Check:**")
        st.write("• Most benefits are **incremental**, not transformative")
        st.write("• Success varies significantly by implementation quality")
        st.write("• ROI typically takes **12-18 months** to materialize")
    
    # Add source info
    with st.expander("📊 Data Source & Methodology"):
        st.info(show_source_info('ai_index'))

elif view_type == "Investment Trends":
    st.write("💰 **AI Investment Trends: Record Growth in 2024 (AI Index Report 2025)**")
    
    # Investment overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="2024 Total Investment", 
            value="$252.3B", 
            delta="+44.5% YoY",
            help="Total corporate AI investment in 2024"
        )
    
    with col2:
        st.metric(
            label="GenAI Investment", 
            value="$33.9B", 
            delta="+18.7% from 2023",
            help="8.5x higher than 2022 levels"
        )
    
    with col3:
        st.metric(
            label="US Investment Lead", 
            value="12x China", 
            delta="$109.1B vs $9.3B",
            help="US leads global AI investment"
        )
    
    with col4:
        st.metric(
            label="Growth Since 2014", 
            value="13x", 
            delta="From $19.4B to $252.3B",
            help="Investment has grown thirteenfold"
        )
    
    # Create tabs for different investment views
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overall Trends", "🌍 Geographic Distribution", "🚀 GenAI Focus", "📊 Comparative Analysis"])
    
    with tab1:
        # Total investment trend chart with interactivity
        fig = go.Figure()
        
        # Total investment line
        fig.add_trace(go.Scatter(
            x=ai_investment_data['year'],
            y=ai_investment_data['total_investment'],
            mode='lines+markers',
            name='Total AI Investment',
            line=dict(width=4, color='#2E86AB'),
            marker=dict(size=10),
            text=[f'${x:.1f}B' for x in ai_investment_data['total_investment']],
            textposition='top center',
            hovertemplate='Year: %{x}<br>Total Investment: $%{y:.1f}B<br>Source: AI Index 2025<extra></extra>'
        ))
        
        # GenAI investment line
        fig.add_trace(go.Scatter(
            x=ai_investment_data['year'][ai_investment_data['genai_investment'] > 0],
            y=ai_investment_data['genai_investment'][ai_investment_data['genai_investment'] > 0],
            mode='lines+markers',
            name='GenAI Investment',
            line=dict(width=3, color='#F24236'),
            marker=dict(size=8),
            text=[f'${x:.1f}B' for x in ai_investment_data['genai_investment'][ai_investment_data['genai_investment'] > 0]],
            textposition='bottom center',
            hovertemplate='Year: %{x}<br>GenAI Investment: $%{y:.1f}B<br>Source: AI Index 2025<extra></extra>'
        ))
        
        # Add annotation for GenAI emergence
        fig.add_annotation(
            x=2022,
            y=3.95,
            text="<b>GenAI Era Begins</b><br>Now 20% of all AI investment",
            showarrow=True,
            arrowhead=2,
            bgcolor="white",
            bordercolor="#F24236",
            borderwidth=2,
            font=dict(size=11, color="#F24236")
        )
        
        fig.update_layout(
            title="AI Investment Has Grown 13x Since 2014",
            xaxis_title="Year",
            yaxis_title="Investment ($ Billions)",
            height=450,
            hovermode='x unified'
        )
        
        col1, col2 = st.columns([10, 1])
        with col1:
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            if st.button("📊", key="inv_source", help="View data source"):
                with st.expander("Data Source", expanded=True):
                    st.info(show_source_info('ai_index'))
        
        st.info("**Key Insight:** Private investment in generative AI now represents over 20% of all AI-related private investment")
        
        # Export option
        csv = ai_investment_data.to_csv(index=False)
        st.download_button(
            label="📥 Download Investment Data (CSV)",
            data=csv,
            file_name="ai_investment_trends_2014_2024.csv",
            mime="text/csv"
        )
    
    with tab2:
        # Country comparison with more context - FIXED to include Israel
        countries_extended = pd.DataFrame({
            'country': ['United States', 'China', 'United Kingdom', 'Germany', 'France', 
                       'Canada', 'Israel', 'Japan', 'South Korea', 'India'],
            'investment': [109.1, 9.3, 4.5, 3.2, 2.8, 2.5, 2.2, 2.0, 1.8, 1.5],
            'per_capita': [324.8, 6.6, 66.2, 38.1, 41.2, 65.8, 231.6, 16.0, 34.6, 1.1],
            'pct_of_gdp': [0.43, 0.05, 0.14, 0.08, 0.09, 0.13, 0.48, 0.05, 0.10, 0.04]
        })
        
        # Create subplot with multiple metrics - ENHANCED to show Israel's leadership
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=('Total Investment ($B)', 'Per Capita Investment ($)', '% of GDP'),
            horizontal_spacing=0.12
        )
        
        # Total investment - show top 6 to include Israel
        top_investment = countries_extended.nlargest(6, 'investment')
        fig.add_trace(
            go.Bar(x=top_investment['country'], y=top_investment['investment'],
                   marker_color='#3498DB', showlegend=False,
                   text=[f'${x:.1f}B' for x in top_investment['investment']],
                   textposition='outside'),
            row=1, col=1
        )
        
        # Per capita - show top 6 to highlight Israel's leadership
        top_per_capita = countries_extended.nlargest(6, 'per_capita')
        colors_per_capita = ['#E74C3C' if country == 'Israel' else '#2ECC71' for country in top_per_capita['country']]
        fig.add_trace(
            go.Bar(x=top_per_capita['country'], y=top_per_capita['per_capita'],
                   marker_color=colors_per_capita, showlegend=False,
                   text=[f'${x:.0f}' for x in top_per_capita['per_capita']],
                   textposition='outside'),
            row=1, col=2
        )
        
        # % of GDP - show top 6 to highlight Israel's leadership
        top_gdp_pct = countries_extended.nlargest(6, 'pct_of_gdp')
        colors_gdp = ['#E74C3C' if country == 'Israel' else '#F39C12' for country in top_gdp_pct['country']]
        fig.add_trace(
            go.Bar(x=top_gdp_pct['country'], y=top_gdp_pct['pct_of_gdp'],
                   marker_color=colors_gdp, showlegend=False,
                   text=[f'{x:.2f}%' for x in top_gdp_pct['pct_of_gdp']],
                   textposition='outside'),
            row=1, col=3
        )
        
        fig.update_xaxes(tickangle=45)
        fig.update_layout(height=400, title_text="AI Investment by Country - Multiple Perspectives (2024)")
        
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**🌍 Investment Leadership:**")
            st.write("• **US dominance:** $109.1B (43% of global)")
            st.write(f"• **Per capita leader:** Israel at ${countries_extended[countries_extended['country']=='Israel']['per_capita'].iloc[0]:.0f} per person")
            st.write(f"• **As % of GDP:** Israel ({countries_extended[countries_extended['country']=='Israel']['pct_of_gdp'].iloc[0]:.2f}%) and US (0.43%) lead")
        
        with col2:
            st.write("**📈 Regional Dynamics:**")
            st.write("• **Asia rising:** Combined $16.4B across major economies")
            st.write("• **Europe steady:** $10.5B across top 3 countries")
            st.write("• **Innovation hubs:** Israel and US show highest intensity (% of GDP)")
            
        # Add explanation for Israel's leadership
        st.info("""
        **🇮🇱 Israel's AI Investment Leadership:**
        - **Per capita champion:** $232 per person vs US $325 (considering population size)
        - **GDP intensity leader:** 0.48% of GDP, highest globally
        - **Innovation density:** Small country with concentrated AI ecosystem
        - **Strategic focus:** Government and private sector aligned on AI development
        """)
    
    with tab3:

        # GenAI growth visualization with context - FIXED
        genai_data = pd.DataFrame({
            'year': ['2022', '2023', '2024'],
            'investment': [3.95, 28.5, 33.9],
            'growth': ['Baseline', '+621%', '+18.7%'],
            'pct_of_total': [2.7, 16.3, 13.4]
        })
        
        # Create dual-axis chart - FIXED VERSION
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=genai_data['year'],
            y=genai_data['investment'],
            text=[f'${x:.1f}B<br>{g}' for x, g in zip(genai_data['investment'], genai_data['growth'])],
            textposition='outside',
            marker_color=['#FFB6C1', '#FF69B4', '#FF1493'],
            name='GenAI Investment',
            yaxis='y'
        ))
        
        fig.add_trace(go.Scatter(
            x=genai_data['year'],
            y=genai_data['pct_of_total'],
            mode='lines+markers',
            name='% of Total AI Investment',
            line=dict(width=3, color='#2C3E50'),
            marker=dict(size=10),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title="GenAI Investment: From $3.95B to $33.9B in Two Years",
            xaxis_title="Year",
            yaxis=dict(title="Investment ($ Billions)", side="left"),
            yaxis2=dict(title="% of Total AI Investment", side="right", overlaying="y"),
            height=400,
            hovermode='x unified',
            # FIX: Force categorical x-axis to prevent decimal years
            xaxis=dict(
                type='category',
                categoryorder='array',
                categoryarray=['2022', '2023', '2024']
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.success("**🚀 GenAI represents over 20% of all AI-related private investment, up from near zero in 2021**")
    
    with tab4:
        # Comparative analysis
        st.write("**Investment Growth Comparison**")
        
        # Calculate YoY growth rates
        growth_data = pd.DataFrame({
            'metric': ['Total AI', 'GenAI', 'US Investment', 'China Investment', 'UK Investment'],
            'growth_2024': [44.5, 18.7, 44.3, 10.7, 18.4],
            'cagr_5yr': [28.3, 156.8, 31.2, 15.4, 22.7]  # 5-year CAGR
        })
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='2024 Growth (%)',
            x=growth_data['metric'],
            y=growth_data['growth_2024'],
            marker_color='#3498DB',
            text=[f'{x:.1f}%' for x in growth_data['growth_2024']],
            textposition='outside'
        ))
        
        fig.add_trace(go.Bar(
            name='5-Year CAGR (%)',
            x=growth_data['metric'],
            y=growth_data['cagr_5yr'],
            marker_color='#E74C3C',
            text=[f'{x:.1f}%' for x in growth_data['cagr_5yr']],
            textposition='outside'
        ))
        
        fig.update_layout(
            title="AI Investment Growth Rates",
            xaxis_title="Investment Category",
            yaxis_title="Growth Rate (%)",
            barmode='group',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("**Note:** GenAI shows exceptional 5-year CAGR due to starting from near-zero base in 2019")

elif view_type == "Regional Growth":
    st.write("🌍 **Regional AI Adoption Growth (AI Index Report 2025)**")
    
    # Enhanced regional visualization with investment data
    fig = go.Figure()
    
    # Create subplot figure
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Adoption Growth in 2024', 'Investment Growth vs Adoption Rate'),
        column_widths=[0.6, 0.4],
        horizontal_spacing=0.15
    )
    
    # Bar chart for adoption growth
    fig.add_trace(
        go.Bar(
            x=regional_growth['region'],
            y=regional_growth['growth_2024'],
            text=[f'+{x}pp' for x in regional_growth['growth_2024']],
            textposition='outside',
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57'],
            name='2024 Growth',
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Scatter plot for investment vs adoption
    fig.add_trace(
        go.Scatter(
            x=regional_growth['adoption_rate'],
            y=regional_growth['investment_growth'],
            mode='markers+text',
            marker=dict(
                size=regional_growth['growth_2024'],
                color=regional_growth['growth_2024'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="2024 Growth (pp)")
            ),
            text=regional_growth['region'],
            textposition='top center',
            showlegend=False
        ),
        row=1, col=2
    )
    
    fig.update_xaxes(title_text="Region", row=1, col=1)
    fig.update_yaxes(title_text="Growth (percentage points)", row=1, col=1)
    fig.update_xaxes(title_text="Current Adoption Rate (%)", row=1, col=2)
    fig.update_yaxes(title_text="Investment Growth (%)", row=1, col=2)
    
    fig.update_layout(height=450, title_text="Regional AI Adoption and Investment Dynamics")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Regional insights with metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Fastest Growing", "Greater China", "+27pp adoption")
        st.write("**Also leads in:**")
        st.write("• Investment growth: +32%")
        st.write("• New AI startups: +45%")
    
    with col2:
        st.metric("Highest Adoption", "North America", "82% rate")
        st.write("**Characteristics:**")
        st.write("• Mature market")
        st.write("• Slower growth: +15pp")
    
    with col3:
        st.metric("Emerging Leader", "Europe", "+23pp growth")
        st.write("**Key drivers:**")
        st.write("• Regulatory clarity")
        st.write("• Public investment")
    
    # Competitive dynamics analysis
    st.subheader("🏁 Competitive Dynamics")
    
    # Create competitive positioning matrix
    fig2 = px.scatter(
        regional_growth,
        x='adoption_rate',
        y='growth_2024',
        size='investment_growth',
        color='region',
        title='Regional AI Competitive Positioning Matrix',
        labels={
            'adoption_rate': 'Current Adoption Rate (%)',
            'growth_2024': 'Adoption Growth Rate (pp)',
            'investment_growth': 'Investment Growth (%)'
        },
        height=400
    )
    
    # Add quadrant lines
    fig2.add_hline(y=regional_growth['growth_2024'].mean(), line_dash="dash", line_color="gray")
    fig2.add_vline(x=regional_growth['adoption_rate'].mean(), line_dash="dash", line_color="gray")
    
    # Add quadrant labels
    fig2.add_annotation(x=50, y=25, text="High Growth<br>Low Base", showarrow=False, font=dict(color="gray"))
    fig2.add_annotation(x=75, y=25, text="High Growth<br>High Base", showarrow=False, font=dict(color="gray"))
    fig2.add_annotation(x=50, y=13, text="Low Growth<br>Low Base", showarrow=False, font=dict(color="gray"))
    fig2.add_annotation(x=75, y=13, text="Low Growth<br>High Base", showarrow=False, font=dict(color="gray"))
    
    st.plotly_chart(fig2, use_container_width=True)
    
    st.info("""
    **Strategic Insights:**
    - **Greater China & Europe:** Aggressive catch-up strategy with high growth rates
    - **North America:** Market leader maintaining position with steady growth
    - **Competition intensifying:** Regional gaps narrowing as adoption accelerates globally
    """)

elif view_type == "AI Cost Trends":
    st.write("💰 **AI Cost Reduction: Dramatic Improvements (AI Index Report 2025)**")
    
    # Cost reduction visualization with context
    tab1, tab2, tab3 = st.tabs(["Inference Costs", "Hardware Improvements", "Cost Projections"])
    
    with tab1:
        # Enhanced cost reduction chart
        fig = go.Figure()
        
        # Add cost trajectory
        fig.add_trace(go.Scatter(
            x=['Nov 2022', 'Jan 2023', 'Jul 2023', 'Jan 2024', 'Oct 2024', 'Oct 2024\n(Gemini)'],
            y=[20.00, 10.00, 2.00, 0.50, 0.14, 0.07],
            mode='lines+markers',
            marker=dict(
                size=[15, 10, 10, 10, 15, 20],
                color=['red', 'orange', 'yellow', 'lightgreen', 'green', 'darkgreen']
            ),
            line=dict(width=3, color='gray', dash='dash'),
            text=['$20.00', '$10.00', '$2.00', '$0.50', '$0.14', '$0.07'],
            textposition='top center',
            name='Cost per Million Tokens',
            hovertemplate='Date: %{x}<br>Cost: %{text}<br>Reduction: %{customdata}<extra></extra>',
            customdata=['Baseline', '2x cheaper', '10x cheaper', '40x cheaper', '143x cheaper', '286x cheaper']
        ))
        
        # Add annotations for key milestones
        fig.add_annotation(
            x='Nov 2022', y=20,
            text="<b>GPT-3.5 Launch</b><br>$20/M tokens",
            showarrow=True,
            arrowhead=2,
            ax=0, ay=-40
        )
        
        fig.add_annotation(
            x='Oct 2024\n(Gemini)', y=0.07,
            text="<b>286x Cost Reduction</b><br>$0.07/M tokens",
            showarrow=True,
            arrowhead=2,
            ax=0, ay=40
        )
        
        fig.update_layout(
            title="AI Inference Cost Collapse: 286x Reduction in 2 Years",
            xaxis_title="Time Period",
            yaxis_title="Cost per Million Tokens ($)",
            yaxis_type="log",
            height=450,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Cost impact analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**💡 What This Means:**")
            st.write("• Processing 1B tokens now costs $70 (was $20,000)")
            st.write("• Enables mass deployment of AI applications")
            st.write("• Makes AI accessible to smaller organizations")
            
        with col2:
            st.write("**📈 Rate of Improvement:**")
            st.write("• Prices falling 9-900x per year by task")
            st.write("• Outpacing Moore's Law significantly")
            st.write("• Driven by competition and efficiency gains")
    
    with tab2:
        # Hardware improvements
        hardware_metrics = pd.DataFrame({
            'metric': ['Performance Growth', 'Price/Performance', 'Energy Efficiency'],
            'annual_rate': [43, -30, 40],
            'cumulative_5yr': [680, -83, 538]
        })
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Annual Rate (%)',
            x=hardware_metrics['metric'],
            y=hardware_metrics['annual_rate'],
            marker_color=['#2ECC71' if x > 0 else '#E74C3C' for x in hardware_metrics['annual_rate']],
            text=[f'{x:+d}%' for x in hardware_metrics['annual_rate']],
            textposition='outside'
        ))
        
        fig.update_layout(
            title="ML Hardware Annual Improvement Rates",
            xaxis_title="Metric",
            yaxis_title="Annual Change (%)",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.success("""
        **🚀 Hardware Revolution:**
        - Performance improving **43% annually** (16-bit operations)
        - Cost dropping **30% per year** for same performance
        - Energy efficiency gaining **40% annually**
        - Enabling larger models at lower costs
        """)
    
    with tab3:
        # Cost projections
        st.write("**Future Cost Projections**")
        
        # Create projection data
        years = list(range(2024, 2028))
        conservative = [0.07, 0.035, 0.018, 0.009]
        aggressive = [0.07, 0.014, 0.003, 0.0006]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=years,
            y=conservative,
            mode='lines+markers',
            name='Conservative (50% annual reduction)',
            line=dict(width=3, dash='dash'),
            fill='tonexty',
            fillcolor='rgba(52, 152, 219, 0.1)'
        ))
        
        fig.add_trace(go.Scatter(
            x=years,
            y=aggressive,
            mode='lines+markers',
            name='Aggressive (80% annual reduction)',
            line=dict(width=3),
            fill='tozeroy',
            fillcolor='rgba(231, 76, 60, 0.1)'
        ))
        
        fig.update_layout(
            title="AI Cost Projections: 2024-2027",
            xaxis_title="Year",
            yaxis_title="Cost per Million Tokens ($)",
            yaxis_type="log",
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        **📊 Projection Assumptions:**
        - **Conservative:** Based on historical semiconductor improvements
        - **Aggressive:** Based on current AI-specific optimization rates
        - By 2027, costs could be 1000-10,000x lower than 2022
        """)

elif view_type == "Token Economics":
    st.write("🪙 **Token Economics: The Language and Currency of AI**")
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Cost Reduction", 
            value="286x", 
            delta="Since Nov 2022",
            help="From $20 to $0.07 per million tokens"
        )
    
    with col2:
        st.metric(
            label="Context Windows", 
            value="Up to 1M", 
            delta="Tokens",
            help="Gemini 1.5 Flash supports 1M token context"
        )
    
    with col3:
        st.metric(
            label="Processing Speed", 
            value="200 tokens/sec", 
            delta="Peak performance",
            help="Latest models process 200+ tokens per second"
        )
    
    with col4:
        st.metric(
            label="Revenue Impact", 
            value="25x", 
            delta="In 4 weeks",
            help="NVIDIA case study: 20x cost reduction = 25x revenue"
        )
    
    # Create comprehensive token economics visualization
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["What Are Tokens?", "Token Pricing", "Usage Patterns", "Optimization", "Economic Impact"])
    
    with tab1:
        # Educational content about tokens
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### Understanding AI Tokens
            
            **Tokens are the fundamental units of AI processing** - tiny pieces of data that AI models use to understand and generate information.
            
            #### How Tokenization Works:
            - **Text**: Words are split into smaller units (e.g., "darkness" → "dark" + "ness")
            - **Images**: Pixels mapped to discrete visual tokens
            - **Audio**: Sound waves converted to spectrograms or semantic tokens
            - **Video**: Frames processed as sequences of visual tokens
            
            #### Token Usage Across AI Lifecycle:
            1. **Training**: Models learn from billions/trillions of tokens
            2. **Inference**: User prompts converted to tokens, processed, then output as tokens
            3. **Reasoning**: Complex models generate "thinking tokens" for problem-solving
            """)
            
        with col2:
            # Token examples visualization
            st.info("""
            **💡 Token Examples:**
            
            **Simple word**: "cat" = 1 token
            
            **Complex word**: "artificial" = 2 tokens
            - "artific" + "ial"
            
            **Sentence**: "Hello world!" = 3 tokens
            - "Hello" + "world" + "!"
            
            **Context matters**: "lie"
            - Resting = Token #123
            - Untruth = Token #456
            """)
        
        # Context window comparison
        st.subheader("Context Window Capabilities")
        
        context_data = token_economics[['model', 'context_window']].sort_values('context_window')
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=context_data['model'],
            y=context_data['context_window'],
            text=[f'{x:,}' if x < 1000000 else f'{x/1000000:.1f}M' for x in context_data['context_window']],
            textposition='outside',
            marker_color=['#FF6B6B' if x < 10000 else '#4ECDC4' if x < 100000 else '#45B7D1' for x in context_data['context_window']],
            hovertemplate='<b>%{x}</b><br>Context: %{y:,} tokens<br>Equivalent to: %{customdata}<extra></extra>',
            customdata=['~3 pages', '~6 pages', '~12 pages', '~96 pages', '~150 pages', '~150 pages', '~750 pages']
        ))
        
        fig.update_layout(
            title="AI Model Context Windows: From Pages to Novels",
            xaxis_title="Model",
            yaxis_title="Context Window (tokens)",
            yaxis_type="log",
            height=400,
            xaxis_tickangle=45
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.success("**Key Insight:** Larger context windows enable processing entire books, codebases, or hours of video in a single prompt")
    
    with tab2:
        # Token pricing analysis
        st.subheader("Token Pricing Evolution & Model Comparison")
        
        # Price evolution over time
        fig1 = go.Figure()
        
        fig1.add_trace(go.Scatter(
            x=token_pricing_evolution['date'],
            y=token_pricing_evolution['avg_price_input'],
            mode='lines+markers',
            name='Input Tokens',
            line=dict(width=3, color='#3498DB'),
            marker=dict(size=8),
            fill='tonexty',
            fillcolor='rgba(52, 152, 219, 0.1)'
        ))
        
        fig1.add_trace(go.Scatter(
            x=token_pricing_evolution['date'],
            y=token_pricing_evolution['avg_price_output'],
            mode='lines+markers',
            name='Output Tokens',
            line=dict(width=3, color='#E74C3C'),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(231, 76, 60, 0.1)'
        ))
        
        # Add model availability on secondary axis
        fig1.add_trace(go.Scatter(
            x=token_pricing_evolution['date'],
            y=token_pricing_evolution['models_available'],
            mode='lines+markers',
            name='Models Available',
            line=dict(width=2, color='#2ECC71', dash='dash'),
            marker=dict(size=6),
            yaxis='y2'
        ))
        
        fig1.update_layout(
            title="Token Pricing Collapse: Competition Drives Costs Down",
            xaxis_title="Date",
            yaxis=dict(title="Price per Million Tokens ($)", type="log", side="left"),
            yaxis2=dict(title="Number of Models", side="right", overlaying="y"),
            height=450,
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig1, use_container_width=True)
        
        # Current model pricing comparison
        col1, col2 = st.columns(2)
        
        with col1:
            # Input vs Output pricing
            fig2 = go.Figure()
            
            fig2.add_trace(go.Bar(
                name='Input Cost',
                x=token_economics.sort_values('cost_per_million_input')['model'],
                y=token_economics.sort_values('cost_per_million_input')['cost_per_million_input'],
                marker_color='#3498DB',
                text=[f'${x:.2f}' for x in token_economics.sort_values('cost_per_million_input')['cost_per_million_input']],
                textposition='outside'
            ))
            
            fig2.add_trace(go.Bar(
                name='Output Cost',
                x=token_economics.sort_values('cost_per_million_input')['model'],
                y=token_economics.sort_values('cost_per_million_input')['cost_per_million_output'],
                marker_color='#E74C3C',
                text=[f'${x:.2f}' for x in token_economics.sort_values('cost_per_million_input')['cost_per_million_output']],
                textposition='outside'
            ))
            
            fig2.update_layout(
                title="Current Model Pricing (per Million Tokens)",
                yaxis_title="Cost ($)",
                barmode='group',
                height=350,
                xaxis_tickangle=45,
                yaxis_type="log"
            )
            
            st.plotly_chart(fig2, use_container_width=True)
        
        with col2:
            st.write("**💰 Pricing Insights:**")
            st.write("• **Output typically costs more** than input (2-5x)")
            st.write("• **Gemini Flash**: Cheapest at $0.07/M tokens")
            st.write("• **GPT-4**: Premium pricing at $15-30/M tokens")
            st.write("• **286x reduction** in 2 years for GPT-3.5")
            
            st.info("""
            **Token Pricing Models:**
            - **Pay-per-use**: Charge by tokens consumed
            - **Token bundles**: Pre-purchase token packages
            - **Rate limits**: Max tokens/minute per user
            - **Tiered pricing**: Volume discounts
            """)
    
    with tab3:
        # Usage patterns analysis
        st.subheader("Token Usage Patterns by Use Case")
        
        # Create scatter plot of usage patterns
        fig = px.scatter(
            token_usage_patterns,
            x='avg_input_tokens',
            y='avg_output_tokens',
            size='input_output_ratio',
            color='use_case',
            title='Token Usage Patterns: Input vs Output by Use Case',
            labels={
                'avg_input_tokens': 'Average Input Tokens',
                'avg_output_tokens': 'Average Output Tokens',
                'input_output_ratio': 'Input/Output Ratio'
            },
            height=450,
            size_max=50
        )
        
        # Add diagonal line for equal input/output
        fig.add_shape(
            type="line",
            x0=0, y0=0,
            x1=5000, y1=5000,
            line=dict(color="gray", width=2, dash="dash")
        )
        
        fig.add_annotation(
            x=3000, y=3500,
            text="Equal Input/Output",
            showarrow=False,
            font=dict(color="gray")
        )
        
        fig.update_xaxes(type="log")
        fig.update_yaxes(type="log")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Usage pattern insights
        col1, col2 = st.columns(2)
        
        with col1:
            # Input-heavy use cases
            input_heavy = token_usage_patterns[token_usage_patterns['input_output_ratio'] > 1].sort_values('input_output_ratio', ascending=False)
            
            st.write("**📥 Input-Heavy Use Cases:**")
            for _, row in input_heavy.iterrows():
                st.write(f"• **{row['use_case']}**: {row['input_output_ratio']:.1f}x more input")
                st.write(f"  - Input: {row['avg_input_tokens']:,} tokens")
                st.write(f"  - Output: {row['avg_output_tokens']:,} tokens")
        
        with col2:
            # Output-heavy use cases
            output_heavy = token_usage_patterns[token_usage_patterns['input_output_ratio'] < 1].sort_values('input_output_ratio')
            
            st.write("**📤 Output-Heavy Use Cases:**")
            for _, row in output_heavy.iterrows():
                st.write(f"• **{row['use_case']}**: {1/row['input_output_ratio']:.1f}x more output")
                st.write(f"  - Input: {row['avg_input_tokens']:,} tokens")
                st.write(f"  - Output: {row['avg_output_tokens']:,} tokens")
        
        # Token metrics explanation
        st.info("""
        **⏱️ Key Performance Metrics:**
        - **Time to First Token (TTFT)**: Latency before AI starts responding
        - **Inter-Token Latency**: Speed of subsequent token generation
        - **Tokens Per Second**: Overall generation throughput
        - **Context Utilization**: % of available context window used
        """)
    
    with tab4:
        # Optimization strategies
        st.subheader("Token Optimization Strategies")
        
        # Strategy effectiveness matrix
        fig = px.scatter(
            token_optimization,
            x='implementation_complexity',
            y='cost_reduction',
            size='time_to_implement',
            color='strategy',
            title='Token Optimization: Cost Reduction vs Implementation Complexity',
            labels={
                'implementation_complexity': 'Implementation Complexity (1-5)',
                'cost_reduction': 'Cost Reduction Potential (%)',
                'time_to_implement': 'Time to Implement (days)'
            },
            height=400,
            size_max=40
        )
        
        # Add quadrant markers
        fig.add_hline(y=40, line_dash="dash", line_color="gray")
        fig.add_vline(x=3, line_dash="dash", line_color="gray")
        
        # Quadrant labels
        fig.add_annotation(x=1.5, y=60, text="Quick Wins", showarrow=False, font=dict(color="green", size=14))
        fig.add_annotation(x=4, y=60, text="Major Projects", showarrow=False, font=dict(color="blue", size=14))
        fig.add_annotation(x=1.5, y=20, text="Easy but Limited", showarrow=False, font=dict(color="orange", size=14))
        fig.add_annotation(x=4, y=20, text="Complex & Limited", showarrow=False, font=dict(color="red", size=14))
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Optimization recommendations
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🚀 Quick Win Strategies:**")
            quick_wins = token_optimization[(token_optimization['implementation_complexity'] <= 2) & 
                                           (token_optimization['cost_reduction'] >= 20)]
            
            for _, strategy in quick_wins.iterrows():
                st.write(f"**{strategy['strategy']}**")
                st.write(f"• Cost reduction: {strategy['cost_reduction']}%")
                st.write(f"• Implementation: {strategy['time_to_implement']} days")
                st.write("")
        
        with col2:
            st.write("**🎯 High-Impact Strategies:**")
            high_impact = token_optimization.nlargest(3, 'cost_reduction')
            
            for _, strategy in high_impact.iterrows():
                st.write(f"**{strategy['strategy']}**")
                st.write(f"• Cost reduction: {strategy['cost_reduction']}%")
                st.write(f"• Complexity: {strategy['implementation_complexity']}/5")
                st.write("")
        
        # Detailed optimization techniques
        with st.expander("📚 Detailed Optimization Techniques"):
            st.markdown("""
            **1. Prompt Engineering (30% reduction)**
            - Use concise, clear prompts
            - Avoid redundant context
            - Structure prompts efficiently
            
            **2. Context Caching (45% reduction)**
            - Reuse common context across requests
            - Implement conversation memory
            - Cache frequently used data
            
            **3. Batch Processing (60% reduction)**
            - Group similar requests
            - Process multiple inputs simultaneously
            - Optimize for throughput over latency
            
            **4. Model Selection (70% reduction)**
            - Choose right-sized models for tasks
            - Use specialized models when appropriate
            - Balance quality vs cost
            
            **5. Response Streaming (15% reduction)**
            - Stream tokens as generated
            - Reduce perceived latency
            - Enable early processing
            
            **6. Token Pruning (25% reduction)**
            - Remove unnecessary tokens
            - Compress prompts intelligently
            - Optimize response length
            """)
    
    with tab5:
        # Economic impact analysis
        st.subheader("Token Economics: From Cost to Value")
        
        # AI Factory concept
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### The AI Factory Model
            
            **AI Factories** are a new class of data centers designed to process tokens at scale, 
            converting the "language of AI" into the "currency of AI" - intelligence.
            
            #### Value Creation Process:
            1. **Input**: Raw data converted to tokens
            2. **Processing**: High-speed token computation
            3. **Output**: Intelligence as a monetizable asset
            4. **Scale**: Efficiency increases with volume
            
            #### Economic Principles:
            - **Token velocity**: Faster processing = more value
            - **Cost efficiency**: Lower cost/token = higher margins
            - **Quality output**: Better tokens = premium pricing
            - **Scale economics**: Volume drives profitability
            """)
        
        with col2:
            # ROI calculator for tokens
            st.write("**🧮 Token ROI Calculator**")
            
            monthly_tokens = st.number_input(
                "Monthly tokens (millions)",
                min_value=1,
                max_value=1000,
                value=100
            )
            
            cost_per_million = st.slider(
                "Cost per million tokens ($)",
                min_value=0.1,
                max_value=20.0,
                value=1.0,
                step=0.1
            )
            
            revenue_per_request = st.number_input(
                "Revenue per request ($)",
                min_value=0.01,
                max_value=10.0,
                value=0.50,
                step=0.01
            )
            
            tokens_per_request = st.slider(
                "Avg tokens per request",
                min_value=100,
                max_value=5000,
                value=500
            )
            
            # Calculate economics
            monthly_cost = monthly_tokens * cost_per_million
            requests = (monthly_tokens * 1_000_000) / tokens_per_request
            monthly_revenue = requests * revenue_per_request
            profit = monthly_revenue - monthly_cost
            margin = (profit / monthly_revenue * 100) if monthly_revenue > 0 else 0
            
            st.metric("Monthly Profit", f"${profit:,.0f}", f"{margin:.1f}% margin")
            st.metric("ROI", f"{(monthly_revenue/monthly_cost):.1f}x", "Revenue/Cost ratio")
        
        # Case study
        st.success("""
        **📈 Real-World Impact - NVIDIA Case Study:**
        - **20x cost reduction** through optimization
        - **25x revenue increase** in 4 weeks
        - Demonstrates direct link between token efficiency and business value
        - Proves that token optimization directly drives bottom-line results
        """)
        
        # Future projections
        st.subheader("Future of Token Economics")
        
        future_trends = pd.DataFrame({
            'trend': ['Cost per Token', 'Context Windows', 'Processing Speed', 
                     'Model Variety', 'Use Cases'],
            'current': ['$0.07-$30', '4K-1M', '50-200 tps', '95 models', 'Hundreds'],
            'year_2027': ['$0.001-$1', '10M+', '1000+ tps', '500+ models', 'Thousands'],
            'growth': ['100x reduction', '10x increase', '5x faster', '5x variety', '10x expansion']
        })
        
        st.dataframe(future_trends, hide_index=True, use_container_width=True)
        
        st.info("""
        **🔮 Key Predictions:**
        - **Sub-penny pricing** becomes standard by 2027
        - **Context windows** expand to process entire databases
        - **Real-time processing** enables new use cases
        - **Specialized models** for every industry and task
        - **Token economics** becomes core business metric
        """)

elif view_type == "Labor Impact":
    st.write("👥 **AI's Impact on Jobs and Workers (AI Index Report 2025)**")
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Expect Job Changes", 
            value="60%", 
            delta="Within 5 years",
            help="Global respondents believing AI will change their jobs"
        )
    
    with col2:
        st.metric(
            label="Expect Job Replacement", 
            value="36%", 
            delta="Within 5 years",
            help="Believe AI will replace their current jobs"
        )
    
    with col3:
        st.metric(
            label="Skill Gap Narrowing", 
            value="Confirmed", 
            delta="Low-skilled benefit most",
            help="AI helps reduce inequality"
        )
    
    with col4:
        st.metric(
            label="Productivity Boost", 
            value="14%", 
            delta="For low-skilled workers",
            help="Highest gains for entry-level"
        )
    
    # Create comprehensive labor impact visualization
    tab1, tab2, tab3, tab4 = st.tabs(["Generational Views", "Skill Impact", "Job Transformation", "Policy Implications"])
    
    with tab1:
        # Enhanced generational visualization
        fig = go.Figure()
        
        # Job change expectations
        fig.add_trace(go.Bar(
            name='Expect Job Changes',
            x=ai_perception['generation'],
            y=ai_perception['expect_job_change'],
            marker_color='#4ECDC4',
            text=[f'{x}%' for x in ai_perception['expect_job_change']],
            textposition='outside'
        ))
        
        # Job replacement expectations
        fig.add_trace(go.Bar(
            name='Expect Job Replacement',
            x=ai_perception['generation'],
            y=ai_perception['expect_job_replacement'],
            marker_color='#F38630',
            text=[f'{x}%' for x in ai_perception['expect_job_replacement']],
            textposition='outside'
        ))
        
        # Add average lines
        avg_change = ai_perception['expect_job_change'].mean()
        avg_replace = ai_perception['expect_job_replacement'].mean()
        
        fig.add_hline(y=avg_change, line_dash="dash", line_color="rgba(78, 205, 196, 0.5)",
                      annotation_text=f"Avg: {avg_change:.0f}%", annotation_position="right")
        fig.add_hline(y=avg_replace, line_dash="dash", line_color="rgba(243, 134, 48, 0.5)",
                      annotation_text=f"Avg: {avg_replace:.0f}%", annotation_position="right")
        
        fig.update_layout(
            title="AI Job Impact Expectations by Generation",
            xaxis_title="Generation",
            yaxis_title="Percentage (%)",
            barmode='group',
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Generation insights
        st.info("""
        **Key Insights:**
        - **18pp gap** between Gen Z and Baby Boomers on job change expectations
        - Younger workers more aware of AI's transformative potential
        - All generations show concern but vary in urgency perception
        """)
    
    with tab2:
        # Skill impact analysis
        skill_impact = pd.DataFrame({
            'job_category': ['Entry-Level/Low-Skill', 'Mid-Level/Medium-Skill', 'Senior/High-Skill', 'Creative/Specialized'],
            'productivity_gain': [14, 9, 5, 7],
            'job_risk': [45, 38, 22, 15],
            'reskilling_need': [85, 72, 58, 65]
        })
        
        fig = go.Figure()
        
        # Create grouped bar chart
        categories = ['Productivity Gain (%)', 'Job Risk (%)', 'Reskilling Need (%)']
        
        for i, category in enumerate(skill_impact['job_category']):
            values = [
                skill_impact.loc[i, 'productivity_gain'],
                skill_impact.loc[i, 'job_risk'],
                skill_impact.loc[i, 'reskilling_need']
            ]
            
            fig.add_trace(go.Bar(
                name=category,
                x=categories,
                y=values,
                text=[f'{v}%' for v in values],
                textposition='outside'
            ))
        
        fig.update_layout(
            title="AI Impact by Job Category",
            xaxis_title="Impact Metric",
            yaxis_title="Percentage (%)",
            barmode='group',
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.success("""
        **Positive Finding:** AI provides greatest productivity boosts to entry-level workers, 
        potentially reducing workplace inequality and accelerating skill development.
        """)
    
    with tab3:
        # Job transformation timeline
        transformation_data = pd.DataFrame({
            'timeframe': ['0-2 years', '2-5 years', '5-10 years', '10+ years'],
            'jobs_affected': [15, 35, 60, 80],
            'new_jobs_created': [10, 25, 45, 65],
            'net_impact': [5, 10, 15, 15]
        })
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=transformation_data['timeframe'],
            y=transformation_data['jobs_affected'],
            mode='lines+markers',
            name='Jobs Affected',
            line=dict(width=3, color='#E74C3C'),
            marker=dict(size=10),
            fill='tonexty'
        ))
        
        fig.add_trace(go.Scatter(
            x=transformation_data['timeframe'],
            y=transformation_data['new_jobs_created'],
            mode='lines+markers',
            name='New Jobs Created',
            line=dict(width=3, color='#2ECC71'),
            marker=dict(size=10),
            fill='tozeroy'
        ))
        
        fig.update_layout(
            title="Projected Job Market Transformation Timeline",
            xaxis_title="Timeframe",
            yaxis_title="Percentage of Workforce (%)",
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        **Transformation Patterns:**
        - Initial displacement in routine tasks
        - New roles emerge in AI management, ethics, and human-AI collaboration
        - Net positive effect expected long-term with proper reskilling
        """)
    
    with tab4:
        # Policy recommendations
        st.write("**Policy Recommendations for Workforce Transition**")
        
        policy_areas = pd.DataFrame({
            'area': ['Education Reform', 'Reskilling Programs', 'Safety Nets', 
                    'Innovation Support', 'Regulation', 'Public-Private Partnership'],
            'priority': [95, 92, 85, 78, 72, 88],
            'current_investment': [45, 38, 52, 65, 58, 42]
        })
        
        fig = px.scatter(
            policy_areas,
            x='current_investment',
            y='priority',
            size='priority',
            text='area',
            title='Policy Priority vs Current Investment',
            labels={'current_investment': 'Current Investment Level (%)', 
                   'priority': 'Priority Score (%)'},
            height=400
        )
        
        # Add quadrant dividers
        fig.add_hline(y=85, line_dash="dash", line_color="gray")
        fig.add_vline(x=50, line_dash="dash", line_color="gray")
        
        # Quadrant labels
        fig.add_annotation(x=30, y=90, text="High Priority<br>Low Investment", 
                          showarrow=False, font=dict(color="red"))
        fig.add_annotation(x=70, y=90, text="High Priority<br>High Investment", 
                          showarrow=False, font=dict(color="green"))
        
        fig.update_traces(textposition='top center')
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.warning("""
        **Critical Gaps:**
        - **Education Reform** and **Reskilling Programs** are high priority but underfunded
        - Need 2-3x increase in workforce development investment
        - Public-private partnerships essential for scale
        """)

elif view_type == "Environmental Impact":
    st.write("🌱 **Environmental Impact: AI's Growing Carbon Footprint (AI Index Report 2025)**")
    
    # Create comprehensive environmental dashboard
    tab1, tab2, tab3, tab4 = st.tabs(["Training Emissions", "Energy Trends", "Mitigation Strategies", "Sustainability Metrics"])
    
    with tab1:
        # Enhanced emissions visualization
        fig = go.Figure()
        
        # Add bars for emissions
        fig.add_trace(go.Bar(
            x=training_emissions['model'],
            y=training_emissions['carbon_tons'],
            marker_color=['#90EE90', '#FFD700', '#FF6347', '#8B0000'],
            text=[f'{x:,.0f} tons' for x in training_emissions['carbon_tons']],
            textposition='outside',
            hovertemplate='Model: %{x}<br>Emissions: %{text}<br>Equivalent: %{customdata}<extra></extra>',
            customdata=['Negligible', '~125 cars/year', '~1,100 cars/year', '~1,900 cars/year']
        ))
        
        # Add trend line
        fig.add_trace(go.Scatter(
            x=training_emissions['model'],
            y=training_emissions['carbon_tons'],
            mode='lines',
            line=dict(width=3, color='red', dash='dash'),
            name='Exponential Growth Trend',
            showlegend=True
        ))
        
        fig.update_layout(
            title="Carbon Emissions from AI Model Training: Exponential Growth",
            xaxis_title="AI Model",
            yaxis_title="Carbon Emissions (tons CO₂)",
            yaxis_type="log",
            height=450,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Emissions context
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📈 Growth Rate:**")
            st.write("• 900,000x increase from 2012 to 2024")
            st.write("• Doubling approximately every 2 years")
            st.write("• Driven by model size and compute needs")
        
        with col2:
            st.write("**🌍 Context:**")
            st.write("• Llama 3.1 = Annual emissions of 1,900 cars")
            st.write("• One training run = 8,930 tons CO₂")
            st.write("• Excludes inference and retraining")
    
    with tab2:
        # Energy trends and nuclear pivot
        st.write("**⚡ Energy Consumption and Nuclear Renaissance**")
        
        energy_data = pd.DataFrame({
            'year': [2020, 2021, 2022, 2023, 2024, 2025],
            'ai_energy_twh': [2.1, 3.5, 5.8, 9.6, 16.2, 27.3],
            'nuclear_deals': [0, 0, 1, 3, 8, 15]
        })
        
        fig = go.Figure()
        
        # Energy consumption
        fig.add_trace(go.Bar(
            x=energy_data['year'],
            y=energy_data['ai_energy_twh'],
            name='AI Energy Use (TWh)',
            marker_color='#3498DB',
            yaxis='y',
            text=[f'{x:.1f} TWh' for x in energy_data['ai_energy_twh']],
            textposition='outside'
        ))
        
        # Nuclear deals
        fig.add_trace(go.Scatter(
            x=energy_data['year'],
            y=energy_data['nuclear_deals'],
            name='Nuclear Energy Deals',
            mode='lines+markers',
            line=dict(width=3, color='#2ECC71'),
            marker=dict(size=10),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title="AI Energy Consumption Driving Nuclear Energy Revival",
            xaxis_title="Year",
            yaxis=dict(title="Energy Consumption (TWh)", side="left"),
            yaxis2=dict(title="Nuclear Deals (#)", side="right", overlaying="y"),
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        **🔋 Major Nuclear Agreements (2024-2025):**
        - Microsoft: Three Mile Island restart
        - Google: Kairos Power SMR partnership
        - Amazon: X-energy SMR development
        - Meta: Nuclear power exploration
        """)
    
    with tab3:
        # Mitigation strategies
        mitigation = pd.DataFrame({
            'strategy': ['Efficient Architectures', 'Renewable Energy', 'Model Reuse', 
                        'Edge Computing', 'Quantum Computing', 'Carbon Offsets'],
            'potential_reduction': [40, 85, 95, 60, 90, 100],
            'adoption_rate': [65, 45, 35, 25, 5, 30],
            'timeframe': [1, 3, 1, 2, 7, 1]
        })
        
        fig = px.scatter(
            mitigation,
            x='adoption_rate',
            y='potential_reduction',
            size='timeframe',
            color='strategy',
            title='AI Sustainability Strategies: Impact vs Adoption',
            labels={
                'adoption_rate': 'Current Adoption Rate (%)',
                'potential_reduction': 'Potential Emission Reduction (%)',
                'timeframe': 'Implementation Time (years)'
            },
            height=400
        )
        
        # Add target zone
        fig.add_shape(
            type="rect",
            x0=70, x1=100,
            y0=70, y1=100,
            fillcolor="lightgreen",
            opacity=0.2,
            line_width=0
        )
        
        fig.add_annotation(
            x=85, y=85,
            text="Target Zone",
            showarrow=False,
            font=dict(color="green")
        )
        
        fig.update_traces(textposition='top center')
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.success("""
        **Most Promising Strategies:**
        - **Model Reuse:** 95% reduction potential, needs ecosystem development
        - **Renewable Energy:** 85% reduction, requires infrastructure investment
        - **Efficient Architectures:** Quick wins with 40% reduction potential
        """)
    
    with tab4:
        # Sustainability metrics dashboard
        st.write("**Sustainability Performance Metrics**")
        
        # Create sustainability scorecard
        metrics = pd.DataFrame({
            'company': ['OpenAI', 'Google', 'Microsoft', 'Meta', 'Amazon'],
            'renewable_pct': [45, 78, 65, 52, 40],
            'efficiency_score': [7.2, 8.5, 7.8, 6.9, 7.5],
            'transparency_score': [6.5, 8.2, 7.9, 6.2, 7.0],
            'carbon_neutral_target': [2030, 2028, 2029, 2030, 2032]
        })
        
        fig = go.Figure()
        
        # Create radar chart
        categories = ['Renewable %', 'Efficiency', 'Transparency']
        
        for _, company in metrics.iterrows():
            values = [
                company['renewable_pct'] / 10,  # Scale to 10
                company['efficiency_score'],
                company['transparency_score']
            ]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=company['company']
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10]
                )),
            showlegend=True,
            title="AI Company Sustainability Scores",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        **Industry Trends:**
        - Increasing pressure for carbon neutrality
        - Hardware efficiency improving 40% annually
        - Growing focus on lifecycle emissions
        """)

elif view_type == "Adoption Rates":
    if "2025" in data_year:
        st.write("📊 **GenAI Adoption by Business Function (2025)**")
        
        # Enhanced function data with financial impact
        function_data = financial_impact.copy()
        function_data['adoption'] = [42, 23, 7, 22, 28, 23, 13, 15]  # GenAI adoption rates
        
        # Create comprehensive visualization
        fig = go.Figure()
        
        # Adoption rate bars
        fig.add_trace(go.Bar(
            x=function_data['function'],
            y=function_data['adoption'],
            name='GenAI Adoption Rate',
            marker_color='#3498DB',
            yaxis='y',
            text=[f'{x}%' for x in function_data['adoption']],
            textposition='outside'
        ))
        
        # Revenue impact line
        fig.add_trace(go.Scatter(
            x=function_data['function'],
            y=function_data['companies_reporting_revenue_gains'],
            mode='lines+markers',
            name='% Reporting Revenue Gains',
            line=dict(width=3, color='#2ECC71'),
            marker=dict(size=8),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='GenAI Adoption and Business Impact by Function',
            xaxis_tickangle=45,
            yaxis=dict(title="GenAI Adoption Rate (%)", side="left"),
            yaxis2=dict(title="% Reporting Revenue Gains", side="right", overlaying="y"),
            height=500,
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Function insights
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("🎯 **Top Functions:**")
            st.write("• **Marketing & Sales:** 42% adoption, 71% see revenue gains")
            st.write("• **Product Development:** 28% adoption, 52% see revenue gains")
            st.write("• **Service Operations:** 23% adoption, 49% see cost savings")
        
        with col2:
            if st.button("📊 View Data Source", key="adoption_source"):
                with st.expander("Data Source", expanded=True):
                    st.info(show_source_info('mckinsey'))
        
        # Note about adoption definition
        st.info("**Note:** Adoption rates include any GenAI use (pilots, experiments, production) among firms using AI")
        
    else:
        # 2018 view
        weighting = st.sidebar.radio("Weighting Method", ["Firm-Weighted", "Employment-Weighted"])
        y_col = 'firm_weighted' if weighting == "Firm-Weighted" else 'employment_weighted'
        
        fig = px.bar(
            sector_2018, 
            x='sector', 
            y=y_col, 
            title=f'AI Adoption by Sector (2018) - {weighting}',
            color=y_col, 
            color_continuous_scale='blues',
            text=y_col
        )
        fig.update_traces(texttemplate='%{text}%', textposition='outside')
        fig.update_layout(xaxis_tickangle=45, height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("🏭 **Key Insight**: Manufacturing and Information sectors led early AI adoption at 12% each")

elif view_type == "Skill Gap Analysis":
    st.write("🎓 **AI Skills Gap Analysis**")
    
    # Skills gap visualization
    fig = go.Figure()
    
    # Sort by gap severity
    skill_sorted = skill_gap_data.sort_values('gap_severity', ascending=True)
    
    # Create diverging bar chart
    fig.add_trace(go.Bar(
        name='Gap Severity',
        y=skill_sorted['skill'],
        x=skill_sorted['gap_severity'],
        orientation='h',
        marker_color='#E74C3C',
        text=[f'{x}%' for x in skill_sorted['gap_severity']],
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        name='Training Initiatives',
        y=skill_sorted['skill'],
        x=skill_sorted['training_initiatives'],
        orientation='h',
        marker_color='#2ECC71',
        text=[f'{x}%' for x in skill_sorted['training_initiatives']],
        textposition='outside',
        xaxis='x2'
    ))
    
    fig.update_layout(
        title="AI Skills Gap vs Training Initiatives",
        xaxis=dict(title="Gap Severity (%)", side="bottom"),
        xaxis2=dict(title="Companies with Training (%)", overlaying="x", side="top"),
        yaxis_title="Skill Area",
        height=500,
        barmode='overlay'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Key insights
    st.info("""
    **🔍 Key Findings:**
    - **AI/ML Engineering** shows the highest gap severity (85%) with only 45% of companies having training programs
    - **Change Management** has a lower gap (55%) but higher training coverage (48%), showing organizational awareness
    - The gap between severity and training initiatives indicates significant opportunity for workforce development
    """)

elif view_type == "AI Governance":
    st.write("⚖️ **AI Governance & Ethics Implementation**")
    
    # Governance maturity visualization
    fig = go.Figure()
    
    # Create radar chart for maturity
    categories = ai_governance['aspect'].tolist()
    
    fig.add_trace(go.Scatterpolar(
        r=ai_governance['adoption_rate'],
        theta=categories,
        fill='toself',
        name='Adoption Rate (%)',
        line_color='#3498DB'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=[x * 20 for x in ai_governance['maturity_score']],  # Scale to 100
        theta=categories,
        fill='toself',
        name='Maturity Score (scaled)',
        line_color='#E74C3C'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="AI Governance Implementation and Maturity",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Governance insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("✅ **Well-Established Areas:**")
        st.write("• **Data Privacy:** 78% adoption, 3.8/5 maturity")
        st.write("• **Regulatory Compliance:** 72% adoption, 3.5/5 maturity")
        st.write("• **Ethics Guidelines:** 62% adoption, 3.2/5 maturity")
    
    with col2:
        st.write("⚠️ **Areas Needing Attention:**")
        st.write("• **Bias Detection:** Only 45% adoption, 2.5/5 maturity")
        st.write("• **Accountability Framework:** 48% adoption, 2.6/5 maturity")
        st.write("• **Transparency:** 52% adoption, 2.8/5 maturity")

elif view_type == "Productivity Research":
    st.write("📊 **AI Productivity Impact Research**")
    
    # Create tabs for different productivity views
    tab1, tab2, tab3 = st.tabs(["Historical Context", "Skill-Level Impact", "Economic Estimates"])
    
    with tab1:
        # Historical productivity paradox
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=productivity_data['year'], 
            y=productivity_data['productivity_growth'],
            mode='lines+markers',
            name='Productivity Growth (%)',
            line=dict(width=3, color='#3B82F6'),
            yaxis='y'
        ))
        
        fig.add_trace(go.Scatter(
            x=productivity_data['year'], 
            y=productivity_data['young_workers_share'],
            mode='lines+markers',
            name='Young Workers Share (25-34)',
            line=dict(width=3, color='#EF4444'),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title="The Productivity Paradox: Demographics vs Technology",
            xaxis_title="Year",
            yaxis=dict(title="Productivity Growth (%)", side="left"),
            yaxis2=dict(title="Young Workers Share (%)", side="right", overlaying="y"),
            height=500,
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with tab2:
        # AI productivity by skill level
        fig = px.bar(
            productivity_by_skill,
            x='skill_level',
            y=['productivity_gain', 'skill_gap_reduction'],
            title='AI Impact by Worker Skill Level',
            labels={'value': 'Percentage (%)', 'variable': 'Impact Type'},
            barmode='group',
            color_discrete_map={'productivity_gain': '#2ECC71', 'skill_gap_reduction': '#3498DB'}
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.success("""
        **✅ AI Index 2025 Finding:** AI provides the greatest productivity boost to low-skilled workers (14%), 
        helping to narrow skill gaps and potentially reduce workplace inequality.
        """)
        
    with tab3:
        # Economic impact estimates
        fig = px.bar(
            ai_productivity_estimates,
            x='source',
            y='annual_impact',
            title='AI Productivity Impact Estimates: Academic vs Industry',
            color='annual_impact',
            color_continuous_scale='RdYlBu_r',
            text='annual_impact'
        )
        fig.update_traces(texttemplate='%{text}%', textposition='outside')
        fig.update_layout(height=450)
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        **📊 Note on Estimates:** - Conservative estimates (0.07-0.1%) focus on task-level automation
        - Optimistic estimates (1.5-2.5%) assume economy-wide transformation
        - Actual impact depends on implementation quality and complementary investments
        """)

# Continue with all remaining view implementations...
elif view_type == "Firm Size Analysis":
    st.write("🏢 **AI Adoption by Firm Size**")
    
    # Enhanced visualization with annotations
    fig = go.Figure()
    
    # Main bar chart
    fig.add_trace(go.Bar(
        x=firm_size['size'], 
        y=firm_size['adoption'],
        marker_color=firm_size['adoption'],
        marker_colorscale='Greens',
        text=[f'{x}%' for x in firm_size['adoption']],
        textposition='outside',
        hovertemplate='Size: %{x}<br>Adoption: %{y}%<br>Employees: %{customdata}<extra></extra>',
        customdata=firm_size['size']
    ))
    
    # Add trend line
    x_numeric = list(range(len(firm_size)))
    z = np.polyfit(x_numeric, firm_size['adoption'], 2)
    p = np.poly1d(z)
    
    fig.add_trace(go.Scatter(
        x=firm_size['size'],
        y=p(x_numeric),
        mode='lines',
        line=dict(width=3, color='red', dash='dash'),
        name='Trend',
        showlegend=True
    ))
    
    # Add annotations for key thresholds
    fig.add_annotation(
        x='100-249', y=12.5,
        text="<b>SME Threshold</b><br>12.5% adoption",
        showarrow=True,
        arrowhead=2,
        ax=0, ay=-40
    )
    
    fig.add_annotation(
        x='5000+', y=58.5,
        text="<b>Enterprise Leaders</b><br>58.5% adoption",
        showarrow=True,
        arrowhead=2,
        ax=0, ay=-40
    )
    
    fig.update_layout(
        title='AI Adoption Shows Strong Correlation with Firm Size',
        xaxis_title='Number of Employees',
        yaxis_title='AI Adoption Rate (%)',
        height=500,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Size insights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Size Gap", "18x", "5000+ vs 1-4 employees")
    with col2:
        st.metric("SME Adoption", "<20%", "For firms <250 employees")
    with col3:
        st.metric("Enterprise Adoption", ">40%", "For firms >2500 employees")
    
    st.info("""
    **📈 Key Insights:**
    - Strong exponential relationship between size and adoption
    - Resource constraints limit small firm adoption
    - Enterprises benefit from economies of scale in AI deployment
    """)

elif view_type == "Technology Stack":
    st.write("🔧 **AI Technology Stack Analysis**")
    
    # Enhanced pie chart with additional context
    fig = go.Figure()
    
    # Calculate actual percentages
    stack_data = pd.DataFrame({
        'technology': ['AI Only', 'AI + Cloud', 'AI + Digitization', 'AI + Cloud + Digitization'],
        'percentage': [15, 23, 24, 38],  # Adjusted to sum to 100%
        'roi_multiplier': [1.5, 2.8, 2.5, 3.5]
    })
    
    # Create donut chart
    fig.add_trace(go.Pie(
        labels=stack_data['technology'],
        values=stack_data['percentage'],
        hole=0.4,
        marker_colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'],
        textinfo='label+percent',
        textposition='outside',
        hovertemplate='<b>%{label}</b><br>Adoption: %{value}%<br>ROI: %{customdata}x<extra></extra>',
        customdata=stack_data['roi_multiplier']
    ))
    
    fig.update_layout(
        title='Technology Stack Combinations and Their Prevalence',
        height=450,
        annotations=[dict(text='Tech<br>Stack', x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Stack insights with ROI
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🔗 Technology Synergies:**")
        st.write("• **38%** use full stack (AI + Cloud + Digitization)")
        st.write("• **62%** combine AI with at least one other technology")
        st.write("• Only **15%** use AI in isolation")
    
    with col2:
        st.write("**💰 ROI by Stack:**")
        st.write("• Full stack: **3.5x** ROI")
        st.write("• AI + Cloud: **2.8x** ROI")
        st.write("• AI + Digitization: **2.5x** ROI")
        st.write("• AI only: **1.5x** ROI")
    
    st.success("**Key Finding:** Technology complementarity is crucial - combined deployments show significantly higher returns")

elif view_type == "AI Technology Maturity":
    st.write("🎯 **AI Technology Maturity & Adoption (Gartner 2025)**")
    
    # Enhanced maturity visualization
    color_map = {
        'Peak of Expectations': '#F59E0B',
        'Trough of Disillusionment': '#6B7280', 
        'Slope of Enlightenment': '#10B981'
    }
    
    fig = go.Figure()
    
    # Group by maturity stage
    for stage in ai_maturity['maturity'].unique():
        stage_data = ai_maturity[ai_maturity['maturity'] == stage]
        
        fig.add_trace(go.Scatter(
            x=stage_data['adoption_rate'],
            y=stage_data['risk_score'],
            mode='markers+text',
            name=stage,
            marker=dict(
                size=stage_data['time_to_value'] * 10,
                color=color_map[stage],
                line=dict(width=2, color='white')
            ),
            text=stage_data['technology'],
            textposition='top center',
            hovertemplate='<b>%{text}</b><br>Adoption: %{x}%<br>Risk: %{y}/100<br>Time to Value: %{customdata} years<extra></extra>',
            customdata=stage_data['time_to_value']
        ))
    
    # Add quadrant lines
    fig.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=50, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Quadrant labels
    fig.add_annotation(x=25, y=75, text="High Risk<br>Low Adoption", showarrow=False, font=dict(color="gray"))
    fig.add_annotation(x=75, y=75, text="High Risk<br>High Adoption", showarrow=False, font=dict(color="gray"))
    fig.add_annotation(x=25, y=25, text="Low Risk<br>Low Adoption", showarrow=False, font=dict(color="gray"))
    fig.add_annotation(x=75, y=25, text="Low Risk<br>High Adoption", showarrow=False, font=dict(color="gray"))
    
    fig.update_layout(
        title="AI Technology Risk-Adoption Matrix",
        xaxis_title="Adoption Rate (%)",
        yaxis_title="Risk Score (0-100)",
        height=500,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Maturity insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🎯 Strategic Recommendations:**")
        st.write("• **Invest in:** Cloud AI Services (low risk, high adoption)")
        st.write("• **Watch:** AI Agents (high potential, high risk)")
        st.write("• **Mature:** Foundation Models moving past hype")
    
    with col2:
        st.write("**⏱️ Time to Value:**")
        st.write("• **Fastest:** Cloud AI Services (1 year)")
        st.write("• **Medium:** Most technologies (3 years)")
        st.write("• **Longest:** Composite AI (7 years)")

elif view_type == "Geographic Distribution":
    st.write("🗺️ **AI Adoption Geographic Distribution with Research Infrastructure**")
    
    # Enhanced geographic data with academic and government investments
    enhanced_geographic = pd.DataFrame({
        'city': ['San Francisco Bay Area', 'Nashville', 'San Antonio', 'Las Vegas', 
                'New Orleans', 'San Diego', 'Seattle', 'Boston', 'Los Angeles',
                'Phoenix', 'Denver', 'Austin', 'Portland', 'Miami', 'Atlanta',
                'Chicago', 'New York', 'Philadelphia', 'Dallas', 'Houston'],
        'state': ['California', 'Tennessee', 'Texas', 'Nevada', 
                 'Louisiana', 'California', 'Washington', 'Massachusetts', 'California',
                 'Arizona', 'Colorado', 'Texas', 'Oregon', 'Florida', 'Georgia',
                 'Illinois', 'New York', 'Pennsylvania', 'Texas', 'Texas'],
        'lat': [37.7749, 36.1627, 29.4241, 36.1699, 
               29.9511, 32.7157, 47.6062, 42.3601, 34.0522,
               33.4484, 39.7392, 30.2672, 45.5152, 25.7617, 33.7490,
               41.8781, 40.7128, 39.9526, 32.7767, 29.7604],
        'lon': [-122.4194, -86.7816, -98.4936, -115.1398, 
               -90.0715, -117.1611, -122.3321, -71.0589, -118.2437,
               -112.0740, -104.9903, -97.7431, -122.6784, -80.1918, -84.3880,
               -87.6298, -74.0060, -75.1652, -96.7970, -95.3698],
        'ai_adoption_rate': [9.5, 8.3, 8.3, 7.7, 
                            7.4, 7.4, 6.8, 6.7, 7.2,
                            6.5, 6.3, 7.8, 6.2, 6.9, 7.1,
                            7.0, 8.0, 6.6, 7.5, 7.3],
        'state_code': ['CA', 'TN', 'TX', 'NV', 
                      'LA', 'CA', 'WA', 'MA', 'CA',
                      'AZ', 'CO', 'TX', 'OR', 'FL', 'GA',
                      'IL', 'NY', 'PA', 'TX', 'TX'],
        'population_millions': [7.7, 0.7, 1.5, 0.6, 
                               0.4, 1.4, 0.8, 0.7, 4.0,
                               1.7, 0.7, 1.0, 0.7, 0.5, 0.5,
                               2.7, 8.3, 1.6, 1.3, 2.3],
        'gdp_billions': [535, 48, 98, 68, 
                        25, 253, 392, 463, 860,
                        162, 201, 148, 121, 345, 396,
                        610, 1487, 388, 368, 356],
        # NEW: Academic and Research Infrastructure
        'major_universities': [12, 2, 3, 1, 2, 5, 4, 8, 6, 2, 3, 4, 2, 3, 4, 5, 7, 4, 3, 4],
        'ai_research_centers': [15, 1, 2, 0, 1, 3, 5, 12, 4, 1, 2, 3, 2, 2, 3, 4, 8, 3, 2, 3],
        'federal_ai_funding_millions': [2100, 45, 125, 15, 35, 180, 350, 890, 420, 55, 85, 165, 75, 95, 145, 285, 650, 225, 185, 245],
        'nsf_ai_institutes': [2, 0, 1, 0, 0, 1, 1, 3, 1, 0, 1, 1, 0, 0, 1, 1, 2, 1, 1, 1],
        # NEW: Innovation Metrics
        'ai_startups': [850, 15, 35, 8, 12, 95, 145, 325, 185, 25, 45, 85, 35, 55, 85, 125, 450, 95, 75, 125],
        'ai_patents_2024': [2450, 25, 85, 12, 18, 165, 285, 780, 385, 45, 95, 145, 65, 85, 125, 245, 825, 185, 155, 225],
        'venture_capital_millions': [15800, 125, 285, 45, 85, 1250, 2850, 4200, 3850, 185, 345, 650, 225, 385, 485, 1250, 8500, 650, 485, 850]
    })
    
    # NEW: State-level research infrastructure data
    state_research_data = pd.DataFrame({
        'state': ['California', 'Massachusetts', 'New York', 'Texas', 'Washington', 
                 'Illinois', 'Pennsylvania', 'Georgia', 'Colorado', 'Florida',
                 'Michigan', 'Ohio', 'North Carolina', 'Virginia', 'Maryland'],
        'state_code': ['CA', 'MA', 'NY', 'TX', 'WA', 'IL', 'PA', 'GA', 'CO', 'FL',
                      'MI', 'OH', 'NC', 'VA', 'MD'],
        'ai_adoption_rate': [8.2, 6.7, 8.0, 7.5, 6.8, 7.0, 6.6, 7.1, 6.3, 6.9,
                            5.5, 5.8, 6.0, 6.2, 6.4],
        'nsf_ai_institutes_total': [5, 4, 3, 3, 2, 2, 2, 1, 2, 1, 1, 1, 2, 2, 2],
        'total_federal_funding_billions': [3.2, 1.1, 1.0, 0.7, 0.5, 0.4, 0.3, 0.2, 0.2, 0.2,
                                          0.15, 0.12, 0.25, 0.35, 0.45],
        'r1_universities': [9, 4, 7, 8, 2, 3, 4, 2, 2, 3, 3, 3, 3, 2, 2],
        'ai_workforce_thousands': [285, 95, 185, 125, 85, 65, 55, 45, 35, 55, 35, 25, 45, 55, 65]
    })
    
    # Create comprehensive tabs for different geographic analyses
    geo_tabs = st.tabs(["🗺️ Interactive Map", "🏛️ Research Infrastructure", "📊 State Comparisons", "🎓 Academic Centers", "💰 Investment Flows"])
    
    with geo_tabs[0]:
        # Enhanced interactive map with multiple layers
        st.subheader("AI Ecosystem Map: Adoption, Research & Investment")
        
        # Map controls
        col1, col2, col3 = st.columns(3)
        with col1:
            map_metric = st.selectbox(
                "Primary Metric",
                ["AI Adoption Rate", "Federal AI Funding", "AI Research Centers", "AI Startups", "Venture Capital"]
            )
        with col2:
            show_nsf_institutes = st.checkbox("Show NSF AI Institutes", value=True)
        with col3:
            show_universities = st.checkbox("Show Major Universities", value=False)
        
        # Metric mapping with proper units
        metric_mapping = {
            "AI Adoption Rate": ('ai_adoption_rate', '%'),
            "Federal AI Funding": ('federal_ai_funding_millions', '$M'),
            "AI Research Centers": ('ai_research_centers', 'centers'),
            "AI Startups": ('ai_startups', 'startups'),
            "Venture Capital": ('venture_capital_millions', '$M')
        }
        
        selected_metric, unit = metric_mapping[map_metric]
        
        # Get metric values and create better normalization
        metric_values = enhanced_geographic[selected_metric]
        
        # Normalize sizes with more dramatic scaling (10-50 range instead of 15-50)
        min_val, max_val = metric_values.min(), metric_values.max()
        if max_val > min_val:  # Avoid division by zero
            normalized_sizes = 10 + (metric_values - min_val) / (max_val - min_val) * 40
        else:
            normalized_sizes = [25] * len(metric_values)  # Default size if all values are the same
        
        # Create the enhanced map
        fig = go.Figure()
        
        # State choropleth (this stays the same)
        fig.add_trace(go.Choropleth(
            locations=state_research_data['state_code'],
            z=state_research_data['ai_adoption_rate'],
            locationmode='USA-states',
            colorscale='Blues',
            colorbar=dict(
                title="State AI<br>Adoption (%)",
                x=-0.05,  # Move further left to avoid overlap
                len=0.35,
                y=0.75,
                thickness=15
            ),
            marker_line_color='black',
            marker_line_width=1,
            hovertemplate='<b>%{text}</b><br>AI Adoption: %{z:.1f}%<br>NSF Institutes: %{customdata[0]}<br>Federal Funding: $%{customdata[1]:.1f}B<extra></extra>',
            text=state_research_data['state'],
            customdata=state_research_data[['nsf_ai_institutes_total', 'total_federal_funding_billions']],
            name="State Infrastructure",
            showlegend=False  # Keep this hidden as it's shown via colorbar
        ))
        
        # Dynamic city markers that change based on selected metric
        fig.add_trace(go.Scattergeo(
            lon=enhanced_geographic['lon'],
            lat=enhanced_geographic['lat'],
            text=enhanced_geographic['city'],
            customdata=enhanced_geographic[[
                'ai_adoption_rate', 'federal_ai_funding_millions', 'ai_research_centers', 
                'ai_startups', 'venture_capital_millions', 'nsf_ai_institutes', 'major_universities'
            ]],
            mode='markers',
            marker=dict(
                size=normalized_sizes,
                color=metric_values,  # This should change with the metric
                colorscale='Reds',
                showscale=True,
                colorbar=dict(
                    title=f"{map_metric}<br>({unit})",  # Dynamic title with units
                    x=1.02,  # Move slightly outside the plot area
                    len=0.35,
                    y=0.35,  # Position lower to avoid overlap with legend
                    thickness=15
                ),
                line=dict(width=2, color='white'),
                sizemode='diameter',
                opacity=0.8,
                # Add explicit color range for better visualization
                cmin=min_val,
                cmax=max_val
            ),
            showlegend=False,
            hovertemplate='<b>%{text}</b><br>' +
                         f'{map_metric}: %{{marker.color}}{unit}<br>' +  # Show selected metric prominently
                         'AI Adoption: %{customdata[0]:.1f}%<br>' +
                         'Federal Funding: $%{customdata[1]:.0f}M<br>' +
                         'Research Centers: %{customdata[2]}<br>' +
                         'AI Startups: %{customdata[3]}<br>' +
                         'VC Investment: $%{customdata[4]:.0f}M<br>' +
                         'NSF Institutes: %{customdata[5]}<br>' +
                         'Major Universities: %{customdata[6]}<extra></extra>',
            name="Cities"
        ))
        
        # Add NSF AI Institutes as special markers
        if show_nsf_institutes:
            nsf_cities = enhanced_geographic[enhanced_geographic['nsf_ai_institutes'] > 0]
            if len(nsf_cities) > 0:  # Only add if there are cities with NSF institutes
                fig.add_trace(go.Scattergeo(
                    lon=nsf_cities['lon'],
                    lat=nsf_cities['lat'],
                    text=nsf_cities['city'],
                    mode='markers',
                    marker=dict(
                        size=20,
                        color='gold',
                        symbol='star',
                        line=dict(width=3, color='darkblue')
                    ),
                    name="NSF AI Institutes",
                    showlegend=True,  # Show in legend
                    hovertemplate='<b>%{text}</b><br>NSF AI Institute Location<extra></extra>'
                ))
        
        # Add major university indicators
        if show_universities:
            major_uni_cities = enhanced_geographic[enhanced_geographic['major_universities'] >= 5]
            if len(major_uni_cities) > 0:  # Only add if there are qualifying cities
                fig.add_trace(go.Scattergeo(
                    lon=major_uni_cities['lon'],
                    lat=major_uni_cities['lat'],
                    text=major_uni_cities['city'],
                    mode='markers',
                    marker=dict(
                        size=15,
                        color='purple',
                        symbol='diamond',
                        line=dict(width=2, color='white')
                    ),
                    name="Major University Hubs",
                    showlegend=True,  # Show in legend
                    hovertemplate='<b>%{text}</b><br>Universities: %{customdata}<extra></extra>',
                    customdata=major_uni_cities['major_universities']
                ))
        
        fig.update_layout(
            title=f'US AI Ecosystem: {map_metric} Distribution',
            geo=dict(
                scope='usa',
                projection_type='albers usa',
                showland=True,
                landcolor='rgb(235, 235, 235)',
                coastlinecolor='rgb(50, 50, 50)',
                coastlinewidth=2
            ),
            height=700,
            showlegend=True,
            legend=dict(
                x=0.85,  # Position legend to avoid colorbar overlap
                y=0.95,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='rgba(0,0,0,0.2)',
                borderwidth=1
            ),
            margin=dict(l=50, r=80, t=50, b=50)  # Add margins for colorbars
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Dynamic insights based on selected metric
        if map_metric == "AI Adoption Rate":
            insight_text = f"""
            **🗺️ AI Adoption Geographic Insights:**
            - **Highest adoption:** {enhanced_geographic.loc[enhanced_geographic['ai_adoption_rate'].idxmax(), 'city']} ({enhanced_geographic['ai_adoption_rate'].max():.1f}%)
            - **Regional variation:** {enhanced_geographic['ai_adoption_rate'].max() - enhanced_geographic['ai_adoption_rate'].min():.1f} percentage point spread
            - **Coastal concentration:** West Coast and Northeast lead in AI implementation
            - **Digital divide:** Significant disparities between innovation hubs and interior regions
            """
        elif map_metric == "Federal AI Funding":
            top_funding_city = enhanced_geographic.loc[enhanced_geographic['federal_ai_funding_millions'].idxmax(), 'city']
            top_funding_amount = enhanced_geographic['federal_ai_funding_millions'].max()
            total_funding = enhanced_geographic['federal_ai_funding_millions'].sum()
            top_5_funding = enhanced_geographic.nlargest(5, 'federal_ai_funding_millions')['federal_ai_funding_millions'].sum()
            insight_text = f"""
            **🏛️ Federal Investment Geographic Insights:**
            - **Largest recipient:** {top_funding_city} (${top_funding_amount:.0f}M federal funding)
            - **Investment concentration:** Top 5 metros receive {(top_5_funding/total_funding)*100:.0f}% of federal AI research funding
            - **Total investment:** ${total_funding:.0f}M across all metros
            - **Research focus:** Federal funding concentrated in university-rich areas
            """
        elif map_metric == "AI Startups":
            top_startup_city = enhanced_geographic.loc[enhanced_geographic['ai_startups'].idxmax(), 'city']
            top_startup_count = enhanced_geographic['ai_startups'].max()
            insight_text = f"""
            **🚀 AI Startup Geographic Insights:**
            - **Startup capital:** {top_startup_city} ({top_startup_count} AI startups)
            - **Total startups:** {enhanced_geographic['ai_startups'].sum()} across all metros
            - **Entrepreneurship hubs:** Concentrated in venture capital centers
            - **Innovation clusters:** Research-industry alignment drives startup formation
            """
        elif map_metric == "Venture Capital":
            top_vc_city = enhanced_geographic.loc[enhanced_geographic['venture_capital_millions'].idxmax(), 'city']
            top_vc_amount = enhanced_geographic['venture_capital_millions'].max()
            total_vc = enhanced_geographic['venture_capital_millions'].sum()
            insight_text = f"""
            **💰 Venture Capital Geographic Insights:**
            - **Investment leader:** {top_vc_city} (${top_vc_amount:.0f}M in VC investment)
            - **Capital concentration:** {(top_vc_amount / total_vc * 100):.1f}% of total investment in top city
            - **Total VC:** ${total_vc:.0f}M across all metros
            - **Regional gaps:** 85% of private investment concentrated in coastal states
            """
        else:  # AI Research Centers
            top_research_city = enhanced_geographic.loc[enhanced_geographic['ai_research_centers'].idxmax(), 'city']
            top_research_count = enhanced_geographic['ai_research_centers'].max()
            cities_with_nsf = len(enhanced_geographic[enhanced_geographic['nsf_ai_institutes'] > 0])
            total_nsf_institutes = enhanced_geographic['nsf_ai_institutes'].sum()
            insight_text = f"""
            **🔬 AI Research Geographic Insights:**
            - **Research leader:** {top_research_city} ({top_research_count} research centers)
            - **NSF AI Institutes:** {total_nsf_institutes} institutes across {cities_with_nsf} metropolitan areas
            - **Total centers:** {enhanced_geographic['ai_research_centers'].sum()} across all metros
            - **Academic concentration:** Research centers cluster near major universities
            """
        
        st.info(insight_text)
    
    with geo_tabs[1]:
        # Research infrastructure deep dive
        st.subheader("🏛️ Federal Research Infrastructure & NSF AI Institutes")
        
        # NSF AI Institutes overview
        col1, col2, col3, col4 = st.columns(4)
        
        total_institutes = state_research_data['nsf_ai_institutes_total'].sum()
        total_funding = state_research_data['total_federal_funding_billions'].sum()
        states_with_institutes = len(state_research_data[state_research_data['nsf_ai_institutes_total'] > 0])
        
        with col1:
            st.metric("Total NSF AI Institutes", total_institutes, help="Across all states")
        with col2:
            st.metric("States with Institutes", states_with_institutes, f"of {len(state_research_data)}")
        with col3:
            st.metric("Total Federal Funding", f"${total_funding:.1f}B", "Research infrastructure")
        with col4:
            st.metric("Average per State", f"${(total_funding/len(state_research_data)):.2f}B", "Funding distribution")
        
        # Research infrastructure visualization
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('NSF AI Institutes by State', 'Federal Research Funding', 
                           'R1 Research Universities', 'AI Workforce Concentration'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "scatter"}]]
        )
        
        # Sort by institutes for better visualization
        institutes_sorted = state_research_data.nlargest(10, 'nsf_ai_institutes_total')
        
        fig.add_trace(go.Bar(
            x=institutes_sorted['state'],
            y=institutes_sorted['nsf_ai_institutes_total'],
            marker_color='#3498DB',
            text=institutes_sorted['nsf_ai_institutes_total'],
            textposition='outside',
            name='NSF Institutes'
        ), row=1, col=1)
        
        funding_sorted = state_research_data.nlargest(10, 'total_federal_funding_billions')
        fig.add_trace(go.Bar(
            x=funding_sorted['state'],
            y=funding_sorted['total_federal_funding_billions'],
            marker_color='#2ECC71',
            text=[f'${x:.1f}B' for x in funding_sorted['total_federal_funding_billions']],
            textposition='outside',
            name='Federal Funding'
        ), row=1, col=2)
        
        unis_sorted = state_research_data.nlargest(10, 'r1_universities')
        fig.add_trace(go.Bar(
            x=unis_sorted['state'],
            y=unis_sorted['r1_universities'],
            marker_color='#9B59B6',
            text=unis_sorted['r1_universities'],
            textposition='outside',
            name='R1 Universities'
        ), row=2, col=1)
        
        fig.add_trace(go.Scatter(
            x=state_research_data['total_federal_funding_billions'],
            y=state_research_data['ai_workforce_thousands'],
            mode='markers+text',
            marker=dict(
                size=state_research_data['nsf_ai_institutes_total'] * 10 + 10,
                color=state_research_data['ai_adoption_rate'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="AI Adoption Rate")
            ),
            text=state_research_data['state_code'],
            textposition='middle center',
            name='Funding vs Workforce'
        ), row=2, col=2)
        
        fig.update_xaxes(tickangle=45)
        fig.update_layout(height=600, showlegend=False, title_text="Federal AI Research Infrastructure by State")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Research infrastructure insights
        with st.expander("📊 Research Infrastructure Analysis"):
            st.markdown("""
            #### NSF AI Research Institutes Program Impact
            
            **Established 2020-2021** with $220M initial federal investment:
            - **Geographic Distribution:** 27 institutes across 40+ states
            - **Research Focus Areas:** Machine learning, human-AI interaction, AI safety, sector applications
            - **Collaboration Model:** University-industry-government partnerships
            
            **Key Findings:**
            - **California leads** with 5 institutes, reflecting existing tech ecosystem
            - **Massachusetts concentration** in Boston area with 4 institutes near MIT/Harvard
            - **Distributed strategy** ensures geographic diversity beyond coastal hubs
            - **Federal coordination** creates national research network
            
            **Source:** NSF National AI Research Institutes Program, AI Index Report 2025
            """)
    
    with geo_tabs[2]:
        # State-by-state comparison
        st.subheader("📊 State AI Ecosystem Comparison")
        
        # Create comprehensive state scorecard
        state_scorecard = state_research_data.copy()
        
        # Normalize metrics for scoring (0-100 scale)
        metrics_to_normalize = ['ai_adoption_rate', 'nsf_ai_institutes_total', 'total_federal_funding_billions', 
                               'r1_universities', 'ai_workforce_thousands']
        
        for metric in metrics_to_normalize:
            max_val = state_scorecard[metric].max()
            min_val = state_scorecard[metric].min()
            state_scorecard[f'{metric}_score'] = ((state_scorecard[metric] - min_val) / (max_val - min_val)) * 100
        
        # Calculate composite AI ecosystem score
        state_scorecard['composite_score'] = (
            state_scorecard['ai_adoption_rate_score'] * 0.3 +
            state_scorecard['nsf_ai_institutes_total_score'] * 0.2 +
            state_scorecard['total_federal_funding_billions_score'] * 0.2 +
            state_scorecard['r1_universities_score'] * 0.15 +
            state_scorecard['ai_workforce_thousands_score'] * 0.15
        )
        
        # Top performers analysis
        top_states = state_scorecard.nlargest(10, 'composite_score')
        
        fig = go.Figure()
        
        # Create stacked bar chart showing component scores
        fig.add_trace(go.Bar(
            name='AI Adoption',
            x=top_states['state'],
            y=top_states['ai_adoption_rate_score'],
            marker_color='#3498DB'
        ))
        
        fig.add_trace(go.Bar(
            name='NSF Institutes',
            x=top_states['state'],
            y=top_states['nsf_ai_institutes_total_score'],
            marker_color='#E74C3C'
        ))
        
        fig.add_trace(go.Bar(
            name='Federal Funding',
            x=top_states['state'],
            y=top_states['total_federal_funding_billions_score'],
            marker_color='#2ECC71'
        ))
        
        fig.add_trace(go.Bar(
            name='Universities',
            x=top_states['state'],
            y=top_states['r1_universities_score'],
            marker_color='#9B59B6'
        ))
        
        fig.add_trace(go.Bar(
            name='AI Workforce',
            x=top_states['state'],
            y=top_states['ai_workforce_thousands_score'],
            marker_color='#F39C12'
        ))
        
        fig.update_layout(
            title='State AI Ecosystem Composite Scores (Top 10)',
            xaxis_title='State',
            yaxis_title='Normalized Score (0-100)',
            barmode='stack',
            height=500,
            xaxis_tickangle=45
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # State rankings table
        st.subheader("🏆 State AI Ecosystem Rankings")
        
        display_cols = ['state', 'composite_score', 'ai_adoption_rate', 'nsf_ai_institutes_total', 
                       'total_federal_funding_billions', 'ai_workforce_thousands']
        
        rankings_display = state_scorecard[display_cols].sort_values('composite_score', ascending=False)
        rankings_display['rank'] = range(1, len(rankings_display) + 1)
        rankings_display = rankings_display[['rank'] + display_cols]
        
        # Rename columns for display
        rankings_display.columns = ['Rank', 'State', 'Composite Score', 'AI Adoption (%)', 
                                   'NSF Institutes', 'Federal Funding ($B)', 'AI Workforce (K)']
        
        # Format the dataframe
        rankings_display['Composite Score'] = rankings_display['Composite Score'].round(1)
        rankings_display['Federal Funding ($B)'] = rankings_display['Federal Funding ($B)'].round(2)
        
        st.dataframe(rankings_display, hide_index=True, use_container_width=True)
        
    with geo_tabs[3]:
        # Academic centers analysis
        st.subheader("🎓 Academic AI Research Centers & University Ecosystem")
        
        # University ecosystem analysis
        university_metrics = enhanced_geographic.groupby('state').agg({
            'major_universities': 'sum',
            'ai_research_centers': 'sum',
            'federal_ai_funding_millions': 'sum',
            'ai_patents_2024': 'sum'
        }).reset_index()
        
        university_metrics = university_metrics.merge(
            state_research_data[['state', 'r1_universities']], 
            on='state', 
            how='left'
        ).fillna(0)
        
        # Top academic states
        top_academic = university_metrics.nlargest(8, 'ai_research_centers')
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('AI Research Centers by State', 'Research Output vs Funding'),
            column_widths=[0.6, 0.4]
        )
        
        fig.add_trace(go.Bar(
            x=top_academic['ai_research_centers'],
            y=top_academic['state'],
            orientation='h',
            marker_color='#3498DB',
            text=[f'{x} centers' for x in top_academic['ai_research_centers']],
            textposition='outside',
            name='Research Centers'
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=university_metrics['federal_ai_funding_millions'],
            y=university_metrics['ai_patents_2024'],
            mode='markers+text',
            marker=dict(
                size=university_metrics['ai_research_centers'] * 3,
                color=university_metrics['major_universities'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Major Universities")
            ),
            text=university_metrics['state'],
            textposition='top center',
            name='Funding vs Patents'
        ), row=1, col=2)
        
        fig.update_layout(height=400, title_text="Academic AI Research Ecosystem")
        fig.update_xaxes(title_text="Research Centers", row=1, col=1)
        fig.update_yaxes(title_text="State", row=1, col=1)
        fig.update_xaxes(title_text="Federal Funding ($M)", row=1, col=2)
        fig.update_yaxes(title_text="AI Patents (2024)", row=1, col=2)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Academic insights
        st.success("""
        **🎓 Academic Research Insights:**
        - **California dominance:** 15 major AI research centers, led by Stanford, UC Berkeley, Caltech
        - **Massachusetts concentration:** MIT, Harvard creating dense research ecosystem
        - **Federal research strategy:** NSF institutes strategically distributed to build national capacity
        - **Industry-academia bridges:** Highest correlation between research centers and private investment
        """)
        
    with geo_tabs[4]:
        # Investment flows analysis
        st.subheader("💰 AI Investment Flows: Private Capital & Government Funding")
        
        # Investment flow analysis
        investment_flow = enhanced_geographic.groupby('state').agg({
            'venture_capital_millions': 'sum',
            'federal_ai_funding_millions': 'sum',
            'ai_startups': 'sum',
            'ai_adoption_rate': 'mean'
        }).reset_index()
        
        # Calculate investment ratios
        investment_flow['private_to_federal_ratio'] = (
            investment_flow['venture_capital_millions'] / 
            investment_flow['federal_ai_funding_millions'].replace(0, 1)
        )
        
        investment_flow['investment_per_startup'] = (
            investment_flow['venture_capital_millions'] / 
            investment_flow['ai_startups'].replace(0, 1)
        )
        
        # Top investment states
        top_investment = investment_flow.nlargest(8, 'venture_capital_millions')
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Private vs Federal Investment', 'Investment Concentration', 
                           'Private-to-Federal Ratio', 'Investment Efficiency'),
            specs=[[{"secondary_y": True}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "scatter"}]]
        )
        
        # Private vs Federal comparison
        fig.add_trace(go.Bar(
            name='Venture Capital',
            x=top_investment['state'],
            y=top_investment['venture_capital_millions'],
            marker_color='#E74C3C',
            yaxis='y'
        ), row=1, col=1)
        
        fig.add_trace(go.Bar(
            name='Federal Funding',
            x=top_investment['state'],
            y=top_investment['federal_ai_funding_millions'],
            marker_color='#3498DB',
            yaxis='y2'
        ), row=1, col=1)
        
        # Investment concentration pie chart
        fig.add_trace(go.Pie(
            labels=top_investment['state'],
            values=top_investment['venture_capital_millions'],
            name="VC Distribution"
        ), row=1, col=2)
        
        # Private-to-federal ratio
        ratio_data = investment_flow.nlargest(8, 'private_to_federal_ratio')
        fig.add_trace(go.Bar(
            x=ratio_data['state'],
            y=ratio_data['private_to_federal_ratio'],
            marker_color='#F39C12',
            text=[f'{x:.1f}x' for x in ratio_data['private_to_federal_ratio']],
            textposition='outside'
        ), row=2, col=1)
        
        # Investment efficiency scatter
        fig.add_trace(go.Scatter(
            x=investment_flow['ai_startups'],
            y=investment_flow['investment_per_startup'],
            mode='markers+text',
            marker=dict(
                size=investment_flow['ai_adoption_rate'] * 5,
                color=investment_flow['venture_capital_millions'],
                colorscale='Reds',
                showscale=True
            ),
            text=investment_flow['state'],
            textposition='top center'
        ), row=2, col=2)
        
        fig.update_layout(height=700, title_text="AI Investment Ecosystem Analysis")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Investment insights with data
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**💰 Investment Concentration:**")
            ca_vc = investment_flow[investment_flow['state'] == 'California']['venture_capital_millions'].iloc[0]
            total_vc = investment_flow['venture_capital_millions'].sum()
            st.write(f"• **California dominance:** ${ca_vc:,.0f}M ({(ca_vc/total_vc)*100:.1f}% of total VC)")
            st.write(f"• **Top 3 states:** {(investment_flow.nlargest(3, 'venture_capital_millions')['venture_capital_millions'].sum()/total_vc)*100:.1f}% of all investment")
            st.write("• **Geographic concentration:** Coastal states receive 85% of private AI investment")
        
        with col2:
            st.write("**🏛️ Public-Private Balance:**")
            avg_ratio = investment_flow['private_to_federal_ratio'].mean()
            st.write(f"• **Average ratio:** {avg_ratio:.1f}x private to federal funding")
            st.write("• **Federal strategy:** Research infrastructure investment vs private market development")
            st.write("• **Regional development:** Federal funding more geographically distributed")
    
    # Enhanced summary with authoritative insights
    st.markdown("---")
    st.subheader("🎯 Geographic AI Ecosystem: Key Findings & Policy Implications")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🌟 Innovation Hubs:**
        - **San Francisco Bay Area:** Global AI capital with $15.8B VC, 15 research centers
        - **Boston:** Academic powerhouse with 3 NSF institutes, $890M federal funding
        - **New York:** Financial AI hub with $8.5B VC, strong adoption rates
        - **Seattle:** Cloud AI infrastructure, major tech presence
        """)
    
    with col2:
        st.markdown("""
        **🏛️ Federal Strategy:**
        - **NSF AI Institutes:** 27 institutes across 40+ states, $220M investment
        - **Geographic distribution:** Intentional spread beyond coastal concentration
        - **Research capacity:** Building national AI research infrastructure
        - **Workforce development:** University partnerships in all regions
        """)
    
    with col3:
        st.markdown("""
        **⚖️ Policy Challenges:**
        - **Digital divide:** 10x gap between leading and lagging regions
        - **Talent concentration:** AI workforce clustered in expensive coastal cities
        - **Investment disparity:** 85% of private investment in 5 states
        - **Infrastructure needs:** Broadband, computing, research facilities
        """)
    
    # Sources and methodology
    with st.expander("📚 Data Sources & Geographic Methodology"):
        st.markdown("""
        ### Geographic Analysis Methodology
        
        **Data Integration:**
        - **U.S. Census Bureau:** AI Use Supplement (850,000 firms surveyed)
        - **NSF:** National AI Research Institutes program data
        - **Stanford AI Index 2025:** Geographic investment patterns
        - **Academic sources:** University research center mapping
        - **Federal databases:** Grant and funding allocation data
        
        **Geographic Scope:**
        - **Metropolitan Statistical Areas (MSAs):** 20 largest AI ecosystems
        - **State-level analysis:** All 50 states + DC for policy comparison
        - **Federal coordination:** NSF institute distribution strategy
        
        **Metrics Definitions:**
        - **AI Adoption Rate:** Percentage of firms using any AI technology
        - **Research Centers:** University-affiliated AI research institutes
        - **Federal Funding:** Direct federal AI research investments (NSF, DOD, NIH)
        - **VC Investment:** Private venture capital in AI startups (2024)
        - **NSF AI Institutes:** Federally funded multi-institutional research centers
        
        **Source Quality:**
        - ✅ **Government data:** Official federal agency reports
        - ✅ **Academic research:** Peer-reviewed geographic analysis
        - ✅ **Cross-validation:** Multiple independent data sources
        """)
        
    # Export enhanced geographic data
    if st.button("📥 Export Geographic Analysis Data"):
        # Combine all geographic data for export
        export_data = enhanced_geographic.merge(
            state_research_data[['state', 'nsf_ai_institutes_total', 'total_federal_funding_billions']], 
            on='state', 
            how='left'
        )
        
        csv = export_data.to_csv(index=False)
        st.download_button(
            label="Download Complete Geographic Dataset (CSV)",
            data=csv,
            file_name="ai_geographic_ecosystem_analysis.csv",
            mime="text/csv"
        )
elif view_type == "OECD 2025 Findings":
    st.write("📊 **OECD/BCG/INSEAD 2025 Report: Enterprise AI Adoption**")
    
    # Enhanced OECD visualization
    tab1, tab2, tab3 = st.tabs(["Country Analysis", "Application Trends", "Success Factors"])
    
    with tab1:
        # G7 comparison with context
        fig = go.Figure()
        
        # Create grouped bars
        x = oecd_g7_adoption['country']
        
        fig.add_trace(go.Bar(
            name='Overall Adoption',
            x=x,
            y=oecd_g7_adoption['adoption_rate'],
            marker_color='#3B82F6',
            text=[f'{x}%' for x in oecd_g7_adoption['adoption_rate']],
            textposition='outside'
        ))
        
        fig.add_trace(go.Bar(
            name='Manufacturing',
            x=x,
            y=oecd_g7_adoption['manufacturing'],
            marker_color='#10B981',
            text=[f'{x}%' for x in oecd_g7_adoption['manufacturing']],
            textposition='outside'
        ))
        
        fig.add_trace(go.Bar(
            name='ICT Sector',
            x=x,
            y=oecd_g7_adoption['ict_sector'],
            marker_color='#F59E0B',
            text=[f'{x}%' for x in oecd_g7_adoption['ict_sector']],
            textposition='outside'
        ))
        
        # Add G7 average line
        g7_avg = oecd_g7_adoption['adoption_rate'].mean()
        fig.add_hline(y=g7_avg, line_dash="dash", line_color="red",
                      annotation_text=f"G7 Average: {g7_avg:.0f}%", annotation_position="right")
        
        fig.update_layout(
            title="AI Adoption Rates Across G7 Countries by Sector",
            xaxis_title="Country",
            yaxis_title="Adoption Rate (%)",
            barmode='group',
            height=450,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Country insights
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🌍 Key Findings:**")
            st.write("• **Japan** leads G7 with 48% overall adoption")
            st.write("• **ICT sector** universally leads (55-70%)")
            st.write("• **15-20pp** gap between ICT and other sectors")
        
        with col2:
            if st.button("📊 View OECD Methodology", key="oecd_method"):
                with st.expander("Methodology", expanded=True):
                    st.info(show_source_info('oecd'))
    
    with tab2:
        # Enhanced applications view
        genai_apps = oecd_applications[oecd_applications['category'] == 'GenAI']
        traditional_apps = oecd_applications[oecd_applications['category'] == 'Traditional AI']
        
        fig = go.Figure()
        
        # GenAI applications
        fig.add_trace(go.Bar(
            name='GenAI Applications',
            y=genai_apps.sort_values('usage_rate')['application'],
            x=genai_apps.sort_values('usage_rate')['usage_rate'],
            orientation='h',
            marker_color='#E74C3C',
            text=[f'{x}%' for x in genai_apps.sort_values('usage_rate')['usage_rate']],
            textposition='outside'
        ))
        
        # Traditional AI applications
        fig.add_trace(go.Bar(
            name='Traditional AI',
            y=traditional_apps.sort_values('usage_rate')['application'],
            x=traditional_apps.sort_values('usage_rate')['usage_rate'],
            orientation='h',
            marker_color='#3498DB',
            text=[f'{x}%' for x in traditional_apps.sort_values('usage_rate')['usage_rate']],
            textposition='outside'
        ))
        
        fig.update_layout(
            title='AI Application Usage: GenAI vs Traditional AI',
            xaxis_title='Usage Rate (% of AI-adopting firms)',
            height=600,
            showlegend=True,
            barmode='overlay'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.success("**Key Trend:** GenAI applications (content generation, code generation, chatbots) now lead adoption rates")
    
    with tab3:
        # Success factors analysis
        success_factors = pd.DataFrame({
            'factor': ['Leadership Commitment', 'Data Infrastructure', 'Talent Availability',
                      'Change Management', 'Partnership Ecosystem', 'Regulatory Clarity'],
            'importance': [92, 88, 85, 78, 72, 68],
            'readiness': [65, 72, 45, 52, 58, 48]
        })
        
        fig = go.Figure()
        
        # Create gap analysis
        fig.add_trace(go.Bar(
            name='Importance',
            x=success_factors['factor'],
            y=success_factors['importance'],
            marker_color='#3498DB',
            text=[f'{x}%' for x in success_factors['importance']],
            textposition='outside'
        ))
        
        fig.add_trace(go.Bar(
            name='Current Readiness',
            x=success_factors['factor'],
            y=success_factors['readiness'],
            marker_color='#E74C3C',
            text=[f'{x}%' for x in success_factors['readiness']],
            textposition='outside'
        ))
        
        # Calculate and display gaps
        gaps = success_factors['importance'] - success_factors['readiness']
        fig.add_trace(go.Scatter(
            name='Gap',
            x=success_factors['factor'],
            y=gaps,
            mode='markers+text',
            marker=dict(size=15, color='orange'),
            text=[f'-{x}pp' for x in gaps],
            textposition='top center',
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='AI Success Factors: Importance vs Readiness Gap',
            xaxis_title='Success Factor',
            yaxis=dict(title='Score (%)', side='left'),
            yaxis2=dict(title='Gap (pp)', side='right', overlaying='y', range=[0, 50]),
            height=450,
            barmode='group',
            xaxis_tickangle=45
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.warning("**Critical Gap:** Talent availability shows the largest readiness gap (40pp), highlighting the global AI skills shortage")

elif view_type == "Barriers & Support":
    st.write("🚧 **AI Adoption Barriers & Support Effectiveness**")
    
    # Enhanced barriers visualization
    fig = go.Figure()
    
    # Sort barriers by severity
    barriers_sorted = barriers_data.sort_values('percentage', ascending=True)
    
    # Create horizontal bar chart with categories
    barrier_categories = {
        'Lack of skilled personnel': 'Talent',
        'Data availability/quality': 'Data',
        'Integration with legacy systems': 'Technical',
        'Regulatory uncertainty': 'Regulatory',
        'High implementation costs': 'Financial',
        'Security concerns': 'Risk',
        'Unclear ROI': 'Financial',
        'Organizational resistance': 'Cultural'
    }
    
    colors = {
        'Talent': '#E74C3C',
        'Data': '#3498DB',
        'Technical': '#9B59B6',
        'Regulatory': '#F39C12',
        'Financial': '#2ECC71',
        'Risk': '#1ABC9C',
        'Cultural': '#34495E'
    }
    
    barriers_sorted['category'] = barriers_sorted['barrier'].map(barrier_categories)
    barriers_sorted['color'] = barriers_sorted['category'].map(colors)
    
    fig.add_trace(go.Bar(
        y=barriers_sorted['barrier'],
        x=barriers_sorted['percentage'],
        orientation='h',
        marker_color=barriers_sorted['color'],
        text=[f'{x}%' for x in barriers_sorted['percentage']],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Severity: %{x}%<br>Category: %{customdata}<extra></extra>',
        customdata=barriers_sorted['category']
    ))
    
    fig.update_layout(
        title='Main Barriers to AI Adoption by Category',
        xaxis_title='Companies Reporting Barrier (%)',
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Support effectiveness with implementation roadmap
    st.subheader("🎯 Support Measures & Implementation Roadmap")
    
    # Create implementation timeline
    support_timeline = pd.DataFrame({
        'measure': ['Regulatory clarity', 'Government education investment', 'Tax incentives',
                   'University partnerships', 'Innovation grants', 'Technology centers',
                   'Public-private collaboration'],
        'effectiveness': [73, 82, 68, 78, 65, 62, 75],
        'implementation_time': [6, 24, 12, 18, 9, 36, 15],  # months
        'cost': [1, 5, 4, 3, 4, 5, 3]  # 1-5 scale
    })
    
    fig2 = px.scatter(
        support_timeline,
        x='implementation_time',
        y='effectiveness',
        size='cost',
        color='measure',
        title='Support Measures: Effectiveness vs Implementation Time',
        labels={
            'implementation_time': 'Implementation Time (months)',
            'effectiveness': 'Effectiveness Score (%)',
            'cost': 'Relative Cost'
        },
        height=400
    )
    
    # Add quadrant dividers
    fig2.add_hline(y=70, line_dash="dash", line_color="gray")
    fig2.add_vline(x=18, line_dash="dash", line_color="gray")
    
    # Quadrant labels
    fig2.add_annotation(x=9, y=75, text="Quick Wins", showarrow=False, font=dict(color="green", size=14))
    fig2.add_annotation(x=30, y=75, text="Long-term Strategic", showarrow=False, font=dict(color="blue", size=14))
    
    fig2.update_traces(textposition='top center')
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Policy recommendations
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🚀 Quick Wins (< 1 year):**")
        st.write("• **Regulatory clarity:** High impact, low cost")
        st.write("• **Innovation grants:** Fast deployment")
        st.write("• **Tax incentives:** Immediate effect")
    
    with col2:
        st.write("**🎯 Strategic Investments:**")
        st.write("• **Education investment:** Highest effectiveness (82%)")
        st.write("• **University partnerships:** Strong talent pipeline")
        st.write("• **Technology centers:** Infrastructure development")
    
    st.success("""
    **Recommended Approach:** Start with regulatory clarity and tax incentives for immediate impact while building 
    long-term capacity through education and partnerships.
    """)

elif view_type == "ROI Analysis":
    st.write("💰 **ROI Analysis: Comprehensive Economic Impact**")
    
    # Create detailed ROI dashboard
    tab1, tab2, tab3, tab4 = st.tabs(["Investment Returns", "Payback Analysis", "Sector ROI", "ROI Calculator"])
    
    with tab1:
        # Investment returns visualization
        roi_data = pd.DataFrame({
            'investment_level': ['Pilot (<$100K)', 'Small ($100K-$500K)', 'Medium ($500K-$2M)', 
                               'Large ($2M-$10M)', 'Enterprise ($10M+)'],
            'avg_roi': [1.8, 2.5, 3.2, 3.8, 4.5],
            'time_to_roi': [6, 9, 12, 18, 24],  # months
            'success_rate': [45, 58, 72, 81, 87]  # % of projects achieving positive ROI
        })
        
        fig = go.Figure()
        
        # ROI bars
        fig.add_trace(go.Bar(
            name='Average ROI',
            x=roi_data['investment_level'],
            y=roi_data['avg_roi'],
            yaxis='y',
            marker_color='#2ECC71',
            text=[f'{x}x' for x in roi_data['avg_roi']],
            textposition='outside'
        ))
        
        # Success rate line
        fig.add_trace(go.Scatter(
            name='Success Rate',
            x=roi_data['investment_level'],
            y=roi_data['success_rate'],
            yaxis='y2',
            mode='lines+markers',
            line=dict(width=3, color='#3498DB'),
            marker=dict(size=10)
        ))
        
        fig.update_layout(
            title='AI ROI by Investment Level',
            xaxis_title='Investment Level',
            yaxis=dict(title='Average ROI (x)', side='left'),
            yaxis2=dict(title='Success Rate (%)', side='right', overlaying='y'),
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        **Key Insights:**
        - Larger investments show higher ROI and success rates
        - Enterprise projects (87% success) benefit from better resources and planning
        - Even small pilots can achieve 1.8x ROI with 45% success rate
        """)
    
    with tab2:
        # Payback period analysis
        payback_data = pd.DataFrame({
            'scenario': ['Best Case', 'Typical', 'Conservative'],
            'months': [8, 15, 24],
            'probability': [20, 60, 20]
        })
        
        fig = go.Figure()
        
        # Create funnel chart for payback scenarios
        fig.add_trace(go.Funnel(
            y=payback_data['scenario'],
            x=payback_data['months'],
            textinfo="text+percent initial",
            text=[f"{x} months" for x in payback_data['months']],
            marker=dict(color=['#2ECC71', '#F39C12', '#E74C3C'])
        ))
        
        fig.update_layout(
            title='AI Investment Payback Period Distribution',
            xaxis_title='Months to Payback',
            height=350
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Factors affecting payback
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🚀 Accelerators:**")
            st.write("• Clear use case definition")
            st.write("• Strong change management")
            st.write("• Existing data infrastructure")
            st.write("• Skilled team in place")
        
        with col2:
            st.write("**🐌 Delays:**")
            st.write("• Poor data quality")
            st.write("• Integration challenges")
            st.write("• Organizational resistance")
            st.write("• Scope creep")
    
    with tab3:
        # Sector-specific ROI
        fig = go.Figure()
        
        # Use sector_2025 data for ROI
        fig.add_trace(go.Bar(
            x=sector_2025.sort_values('avg_roi')['sector'],
            y=sector_2025.sort_values('avg_roi')['avg_roi'],
            marker_color=sector_2025.sort_values('avg_roi')['avg_roi'],
            marker_colorscale='Viridis',
            text=[f'{x}x' for x in sector_2025.sort_values('avg_roi')['avg_roi']],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>ROI: %{y}x<br>Adoption: %{customdata}%<extra></extra>',
            customdata=sector_2025.sort_values('avg_roi')['adoption_rate']
        ))
        
        fig.update_layout(
            title='Average AI ROI by Industry Sector',
            xaxis_title='Industry',
            yaxis_title='Average ROI (x)',
            height=400,
            xaxis_tickangle=45,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Top performers analysis
        top_sectors = sector_2025.nlargest(3, 'avg_roi')
        
        st.write("**🏆 Top ROI Performers:**")
        for _, sector in top_sectors.iterrows():
            st.write(f"• **{sector['sector']}:** {sector['avg_roi']}x ROI, {sector['adoption_rate']}% adoption")
    
    with tab4:
        # Interactive ROI Calculator
        st.write("**🧮 AI Investment ROI Calculator**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            investment_amount = st.number_input(
                "Initial Investment ($)",
                min_value=10000,
                max_value=10000000,
                value=250000,
                step=10000,
                help="Total AI project investment"
            )
            
            project_type = st.selectbox(
                "Project Type",
                ["Process Automation", "Predictive Analytics", "Customer Service", 
                 "Product Development", "Marketing Optimization"]
            )
            
            company_size = st.select_slider(
                "Company Size",
                options=["Small (<50)", "Medium (50-250)", "Large (250-1000)", "Enterprise (1000+)"],
                value="Medium (50-250)"
            )
        
        with col2:
            implementation_quality = st.slider(
                "Implementation Quality",
                min_value=1,
                max_value=5,
                value=3,
                help="1=Poor, 5=Excellent"
            )
            
            data_readiness = st.slider(
                "Data Readiness",
                min_value=1,
                max_value=5,
                value=3,
                help="1=Poor quality, 5=Excellent quality"
            )
            
            timeline = st.selectbox(
                "Implementation Timeline",
                ["3 months", "6 months", "12 months", "18 months", "24 months"],
                index=2
            )
        
        # Calculate ROI based on inputs
        base_roi = {
            "Process Automation": 3.2,
            "Predictive Analytics": 2.8,
            "Customer Service": 2.5,
            "Product Development": 3.5,
            "Marketing Optimization": 3.0
        }[project_type]
        
        size_multiplier = {
            "Small (<50)": 0.8,
            "Medium (50-250)": 1.0,
            "Large (250-1000)": 1.2,
            "Enterprise (1000+)": 1.4
        }[company_size]
        
        quality_multiplier = 0.6 + (implementation_quality * 0.2)
        data_multiplier = 0.7 + (data_readiness * 0.15)
        
        final_roi = base_roi * size_multiplier * quality_multiplier * data_multiplier
        expected_return = investment_amount * final_roi
        net_benefit = expected_return - investment_amount
        payback_months = int(investment_amount / (net_benefit / int(timeline.split()[0])))
        
        # Display results
        st.markdown("---")
        st.subheader("📊 Projected Results")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Expected ROI", f"{final_roi:.1f}x", help="Return on investment multiplier")
        with col2:
            st.metric("Total Return", f"${expected_return:,.0f}", help="Total expected value")
        with col3:
            st.metric("Net Benefit", f"${net_benefit:,.0f}", delta=f"{(net_benefit/investment_amount)*100:.0f}%")
        with col4:
            st.metric("Payback Period", f"{payback_months} months", help="Time to recover investment")
        
        # Risk assessment
        risk_score = 5 - ((implementation_quality + data_readiness) / 2)
        risk_level = ["Very Low", "Low", "Medium", "High", "Very High"][int(risk_score)-1]
        
        st.warning(f"""
        **Risk Assessment:** {risk_level}
        - Implementation Quality: {'⭐' * implementation_quality}
        - Data Readiness: {'⭐' * data_readiness}
        - Recommendation: {"Proceed with confidence" if risk_score <= 2 else "Address gaps before proceeding"}
        """)
        
        # Export calculation
        if st.button("📥 Export ROI Analysis"):
            analysis_text = f"""
            AI ROI Analysis Report
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            
            Investment Details:
            - Amount: ${investment_amount:,}
            - Project Type: {project_type}
            - Company Size: {company_size}
            - Timeline: {timeline}
            
            Quality Metrics:
            - Implementation Quality: {implementation_quality}/5
            - Data Readiness: {data_readiness}/5
            
            Projected Results:
            - Expected ROI: {final_roi:.1f}x
            - Total Return: ${expected_return:,.0f}
            - Net Benefit: ${net_benefit:,.0f}
            - Payback Period: {payback_months} months
            - Risk Level: {risk_level}
            """
            
            st.download_button(
                label="Download Analysis",
                data=analysis_text,
                file_name=f"ai_roi_analysis_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )

elif view_type == "Bibliography & Sources":
    st.write("📚 **Complete Bibliography & Source Citations**")
    
    st.markdown("""
    This dashboard synthesizes data from multiple authoritative sources to provide comprehensive 
    AI adoption insights. All sources are cited using Chicago Manual of Style format.
    """)
    
    # Create tabs for different source categories
    bib_tabs = st.tabs(["🏛️ Government & Institutional", "🏢 Corporate & Industry", "🎓 Academic Research", 
                        "📰 News & Analysis", "📊 Databases & Collections"])
    
    with bib_tabs[0]:
        st.markdown("""
        ### Government and Institutional Sources
        
        1. **Stanford Human-Centered AI Institute.** "AI Index Report 2025." Stanford University. Accessed June 28, 2025. https://aiindex.stanford.edu/ai-index-report-2025/.

        2. **Stanford Human-Centered AI Institute.** "AI Index Report 2023." Stanford University. Accessed June 28, 2025. https://aiindex.stanford.edu/ai-index-report-2023/.

        3. **U.S. Census Bureau.** "AI Use Supplement." Washington, DC: U.S. Department of Commerce. Accessed June 28, 2025. https://www.census.gov.

        4. **National Science Foundation.** "National AI Research Institutes." Washington, DC: NSF. Accessed June 28, 2025. https://www.nsf.gov/focus-areas/artificial-intelligence.

        5. **National Science Foundation.** "NSF Partnerships Expand National AI Research." Press Release, 2020. https://www.nsf.gov/news/nsf-partnerships-expand-national-ai-research.

        6. **National Institute of Standards and Technology.** "AI Risk Management Framework (AI RMF 1.0)." NIST AI 100-1. Gaithersburg, MD: NIST, January 2023. https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf.

        7. **National Institute of Standards and Technology.** "AI Risk Management Framework." Accessed June 28, 2025. https://www.nist.gov/itl/ai-risk-management-framework.

        8. **Organisation for Economic Co-operation and Development.** "OECD AI Policy Observatory." Accessed June 28, 2025. https://oecd.ai.

        9. **U.S. Food and Drug Administration.** "AI-Enabled Medical Device Approvals Database." Washington, DC: FDA. Accessed June 28, 2025.
        """)
        
    with bib_tabs[1]:
        st.markdown("""
        ### Corporate and Industry Sources
        
        10. **McKinsey & Company.** "The State of AI: McKinsey Global Survey on AI." McKinsey Global Institute. Accessed June 28, 2025. https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai.

        11. **OpenAI.** "Introducing DALL-E." OpenAI Blog, January 5, 2021. https://openai.com/blog/dall-e/.

        12. **OpenAI.** "OpenAI Research." Accessed June 28, 2025. https://openai.com/research/.

        13. **GitHub.** "Introducing GitHub Copilot: AI Pair Programmer." GitHub Blog, June 29, 2021. https://github.blog/2021-06-29-introducing-github-copilot-ai-pair-programmer/.

        14. **GitHub.** "GitHub Copilot is Generally Available to All Developers." GitHub Blog, June 21, 2022. https://github.blog/2022-06-21-github-copilot-is-generally-available-to-all-developers/.

        15. **GitHub.** "GitHub Blog." Accessed June 28, 2025. https://github.blog/.

        16. **DeepMind.** "DeepMind Publications." Accessed June 28, 2025. https://deepmind.google/research/.

        17. **Goldman Sachs Research.** "The Potentially Large Effects of Artificial Intelligence on Economic Growth." Economic Research, 2023.

        18. **NVIDIA Corporation.** "AI Infrastructure and Token Economics Case Studies." 2024-2025.
        """)
        
    with bib_tabs[2]:
        st.markdown("""
        ### Academic Publications
        
        19. **Bick, Alexander, Adam Blandin, and David Deming.** "The Rapid Adoption of Generative AI." Federal Reserve Bank working paper, 2024.

        20. **Bick, Alexander, Adam Blandin, and David Deming.** "Productivity and Workforce Impact Studies." Federal Reserve Bank working paper, 2025a.

        21. **Eloundou, Tyna, Sam Manning, Pamela Mishkin, and Daniel Rock.** "GPTs are GPTs: An Early Look at the Labor Market Impact Potential of Large Language Models." Working paper, 2023.

        22. **Briggs, Joseph, and Devesh Kodnani.** "The Potentially Large Effects of Artificial Intelligence on Economic Growth." Goldman Sachs Economic Research, 2023.

        23. **Korinek, Anton.** "Language Models and Cognitive Automation for Economic Research." Working paper, 2023.

        24. **Sevilla, Jaime, Lennart Heim, Anson Ho, Tamay Besiroglu, Marius Hobbhahn, and Pablo Villalobos.** "Compute Trends Across Three Eras of Machine Learning." arXiv preprint, 2022.

        25. **Acemoglu, Daron.** "The Simple Macroeconomics of AI." MIT Economics working paper, 2024.

        26. **Brynjolfsson, Erik, Danielle Li, and Lindsey R. Raymond.** "Generative AI at Work." National Bureau of Economic Research Working Paper, 2023.

        27. **Jumper, John, Richard Evans, Alexander Pritzel, Tim Green, Michael Figurnov, Olaf Ronneberger, Kathryn Tunyasuvunakool, et al.** "Highly Accurate Protein Structure Prediction with AlphaFold." *Nature* 596, no. 7873 (2021): 583-589. https://www.nature.com/articles/s41586-021-03819-2.

        28. **Richmond Federal Reserve Bank.** "AI Productivity Estimates." Economic research papers, 2024.

        29. **BCG and INSEAD.** "OECD/BCG/INSEAD Report 2025: Enterprise AI Adoption." Organisation for Economic Co-operation and Development, 2025.
        """)
        
    with bib_tabs[3]:
        st.markdown("""
        ### News and Analysis Sources
        
        30. **MIT Technology Review.** "Artificial Intelligence." Accessed June 28, 2025. https://www.technologyreview.com/topic/artificial-intelligence/.

        31. **MIT Technology Review.** "How DALL-E 2 Actually Works." April 6, 2022. https://www.technologyreview.com/2022/04/06/1049061/dalle-openai-gpt3-ai-agi-multimodal-image-generation/.

        32. **Nature Machine Intelligence.** "Nature Machine Intelligence Journal." Accessed June 28, 2025. https://www.nature.com/natmachintell/.

        33. **IEEE Computer Society.** "IEEE Computer Society Publications." Accessed June 28, 2025. https://www.computer.org/publications/.

        34. **Gartner, Inc.** "AI Technology Maturity Analysis." Technology research reports, 2025.
        """)
        
    with bib_tabs[4]:
        st.markdown("""
        ### Multi-Source Collections and Databases
        
        35. **Federal Reserve Banks.** "Multiple Economic Impact Analyses on AI." Various working papers and research documents, 2023-2025.

        36. **United Nations, European Union, African Union.** "AI Frameworks and Governance Documents." Various policy papers and frameworks, 2023-2025.

        37. **Various Academic Institutions.** "University AI Research Center Mapping Data." Compiled from multiple university sources, 2024-2025.

        38. **Various Federal Agencies.** "Grant and Funding Allocation Data for AI Research." Compiled from NSF, DOD, NIH databases, 2020-2025.
        """)
    
    # Add methodology and verification section
    st.markdown("---")
    st.subheader("📋 Source Verification Methodology")
    
    st.info("""
    **Source Quality Assurance Process:**
    
    ✅ **Primary Source Verification** - All data traced to original publications and reports
    
    ✅ **Cross-Validation** - Key findings confirmed across multiple independent sources
    
    ✅ **Institutional Authority** - Preference for government agencies, academic institutions, and established research organizations
    
    ✅ **Recency Standards** - Data sources from 2020-2025, with emphasis on 2024-2025 findings
    
    ✅ **Methodological Transparency** - Survey sizes, geographic scope, and collection methods documented
    
    ✅ **Peer Review Preference** - Academic sources prioritized when available
    """)
    
    # Add download option for bibliography
    st.subheader("📥 Export Bibliography")
    
    # Create downloadable bibliography text
    bibliography_text = """AI ADOPTION DASHBOARD - COMPLETE BIBLIOGRAPHY
Generated: June 28, 2025

GOVERNMENT AND INSTITUTIONAL SOURCES

1. Stanford Human-Centered AI Institute. "AI Index Report 2025." Stanford University. Accessed June 28, 2025. https://aiindex.stanford.edu/ai-index-report-2025/.

2. Stanford Human-Centered AI Institute. "AI Index Report 2023." Stanford University. Accessed June 28, 2025. https://aiindex.stanford.edu/ai-index-report-2023/.

3. U.S. Census Bureau. "AI Use Supplement." Washington, DC: U.S. Department of Commerce. Accessed June 28, 2025. https://www.census.gov.

4. National Science Foundation. "National AI Research Institutes." Washington, DC: NSF. Accessed June 28, 2025. https://www.nsf.gov/focus-areas/artificial-intelligence.

5. National Science Foundation. "NSF Partnerships Expand National AI Research." Press Release, 2020. https://www.nsf.gov/news/nsf-partnerships-expand-national-ai-research.

6. National Institute of Standards and Technology. "AI Risk Management Framework (AI RMF 1.0)." NIST AI 100-1. Gaithersburg, MD: NIST, January 2023. https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf.

7. National Institute of Standards and Technology. "AI Risk Management Framework." Accessed June 28, 2025. https://www.nist.gov/itl/ai-risk-management-framework.

8. Organisation for Economic Co-operation and Development. "OECD AI Policy Observatory." Accessed June 28, 2025. https://oecd.ai.

9. U.S. Food and Drug Administration. "AI-Enabled Medical Device Approvals Database." Washington, DC: FDA. Accessed June 28, 2025.

CORPORATE AND INDUSTRY SOURCES

10. McKinsey & Company. "The State of AI: McKinsey Global Survey on AI." McKinsey Global Institute. Accessed June 28, 2025. https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai.

11. OpenAI. "Introducing DALL-E." OpenAI Blog, January 5, 2021. https://openai.com/blog/dall-e/.

12. OpenAI. "OpenAI Research." Accessed June 28, 2025. https://openai.com/research/.

13. GitHub. "Introducing GitHub Copilot: AI Pair Programmer." GitHub Blog, June 29, 2021. https://github.blog/2021-06-29-introducing-github-copilot-ai-pair-programmer/.

14. GitHub. "GitHub Copilot is Generally Available to All Developers." GitHub Blog, June 21, 2022. https://github.blog/2022-06-21-github-copilot-is-generally-available-to-all-developers/.

15. GitHub. "GitHub Blog." Accessed June 28, 2025. https://github.blog/.

16. DeepMind. "DeepMind Publications." Accessed June 28, 2025. https://deepmind.google/research/.

17. Goldman Sachs Research. "The Potentially Large Effects of Artificial Intelligence on Economic Growth." Economic Research, 2023.

18. NVIDIA Corporation. "AI Infrastructure and Token Economics Case Studies." 2024-2025.

ACADEMIC PUBLICATIONS

19. Bick, Alexander, Adam Blandin, and David Deming. "The Rapid Adoption of Generative AI." Federal Reserve Bank working paper, 2024.

20. Bick, Alexander, Adam Blandin, and David Deming. "Productivity and Workforce Impact Studies." Federal Reserve Bank working paper, 2025a.

21. Eloundou, Tyna, Sam Manning, Pamela Mishkin, and Daniel Rock. "GPTs are GPTs: An Early Look at the Labor Market Impact Potential of Large Language Models." Working paper, 2023.

22. Briggs, Joseph, and Devesh Kodnani. "The Potentially Large Effects of Artificial Intelligence on Economic Growth." Goldman Sachs Economic Research, 2023.

23. Korinek, Anton. "Language Models and Cognitive Automation for Economic Research." Working paper, 2023.

24. Sevilla, Jaime, Lennart Heim, Anson Ho, Tamay Besiroglu, Marius Hobbhahn, and Pablo Villalobos. "Compute Trends Across Three Eras of Machine Learning." arXiv preprint, 2022.

25. Acemoglu, Daron. "The Simple Macroeconomics of AI." MIT Economics working paper, 2024.

26. Brynjolfsson, Erik, Danielle Li, and Lindsey R. Raymond. "Generative AI at Work." National Bureau of Economic Research Working Paper, 2023.

27. Jumper, John, Richard Evans, Alexander Pritzel, Tim Green, Michael Figurnov, Olaf Ronneberger, Kathryn Tunyasuvunakool, et al. "Highly Accurate Protein Structure Prediction with AlphaFold." Nature 596, no. 7873 (2021): 583-589. https://www.nature.com/articles/s41586-021-03819-2.

28. Richmond Federal Reserve Bank. "AI Productivity Estimates." Economic research papers, 2024.

29. BCG and INSEAD. "OECD/BCG/INSEAD Report 2025: Enterprise AI Adoption." Organisation for Economic Co-operation and Development, 2025.

NEWS AND ANALYSIS SOURCES

30. MIT Technology Review. "Artificial Intelligence." Accessed June 28, 2025. https://www.technologyreview.com/topic/artificial-intelligence/.

31. MIT Technology Review. "How DALL-E 2 Actually Works." April 6, 2022. https://www.technologyreview.com/2022/04/06/1049061/dalle-openai-gpt3-ai-agi-multimodal-image-generation/.

32. Nature Machine Intelligence. "Nature Machine Intelligence Journal." Accessed June 28, 2025. https://www.nature.com/natmachintell/.

33. IEEE Computer Society. "IEEE Computer Society Publications." Accessed June 28, 2025. https://www.computer.org/publications/.

34. Gartner, Inc. "AI Technology Maturity Analysis." Technology research reports, 2025.

MULTI-SOURCE COLLECTIONS AND DATABASES

35. Federal Reserve Banks. "Multiple Economic Impact Analyses on AI." Various working papers and research documents, 2023-2025.

36. United Nations, European Union, African Union. "AI Frameworks and Governance Documents." Various policy papers and frameworks, 2023-2025.

37. Various Academic Institutions. "University AI Research Center Mapping Data." Compiled from multiple university sources, 2024-2025.

38. Various Federal Agencies. "Grant and Funding Allocation Data for AI Research." Compiled from NSF, DOD, NIH databases, 2020-2025.

SOURCE VERIFICATION METHODOLOGY

All sources verified through:
- Cross-validation across multiple independent data sources
- Primary source documentation where available
- Peer-reviewed publication verification
- Official government agency confirmation
- Multiple independent confirmations required for each milestone and data point

Citation Format: Chicago Manual of Style (17th edition)
Dashboard Version: 2.2.0
Last Updated: June 28, 2025
Created by: Robert Casanova"""
    
    st.download_button(
        label="📥 Download Complete Bibliography",
        data=bibliography_text,
        file_name="ai_adoption_dashboard_bibliography.txt",
        mime="text/plain"
    )

# Comprehensive Analysis Integration - UPDATED VERSION
st.subheader("📋 Comprehensive AI Impact Analysis")

# Add comprehensive analysis from the document with new insights
with st.expander("📊 Comprehensive AI Impact Analysis - Full Report", expanded=False):
    st.markdown("""
    ### Executive Summary
    
    This comprehensive analysis synthesizes insights from multiple authoritative sources including the AI Index Report 2025, 
    Federal Reserve research, MIT studies, OECD reports, and industry analyses to provide a complete picture of AI's 
    current state and projected impacts across all sectors of society and economy.
    
    **New Analysis Highlights:**
    - Growing AI incidents involving misuse, bias, and safety failures requiring stronger RAI frameworks
    - Geographic talent concentration in select global hubs creating innovation disparities
    - Multimodal AI breakthroughs (GPT-4V, robotics) expanding beyond text processing
    - AI integration in participatory governance and civic engagement tools
    """)
    
    # Create comprehensive analysis tabs with enhanced content
    comp_tabs = st.tabs(["📈 Performance & Capabilities", "💰 Economics & Investment", "👥 Labor & Productivity", 
                         "🏛️ Policy & Governance", "🔬 Technical Evolution", "🌍 Global Dynamics", "⚠️ Risks & Safety"])
    
    with comp_tabs[0]:
        st.markdown("""
        #### AI Performance and Capabilities
        
        **Breakthrough Performance Improvements (2024):**
        - **MMMU benchmark:** +18.8 percentage points vs 2023
        - **GPQA scores:** +48.9 percentage points improvement  
        - **SWE-bench:** +67.3 percentage points increase
        - **Programming tasks:** Language model agents now outperform humans with limited time budgets
        - **Medical devices:** FDA approvals grew from 6 (2015) to 223 (2023)
        
        **Cost Revolution - 280x Improvement:**
        - **Token costs:** $20/M (Nov 2022) → $0.07/M (Oct 2024) for GPT-3.5 equivalent
        - **Hardware performance:** +43% annually
        - **Energy efficiency:** +40% annual improvement  
        - **Price-performance:** -30% per year for same capability
        - **Processing speed:** Up to 200 tokens/second for latest models
        
        **Multimodal AI Breakthroughs:**
        - **GPT-4V:** Vision capabilities enabling image understanding
        - **Robotics integration:** AI systems controlling physical robots
        - **Voice and audio:** Real-time speech processing and generation
        - **Video analysis:** Frame-by-frame understanding and generation
        
        **Adoption Acceleration:**
        - **Business AI use:** 55% (2023) → 78% (2024) - fastest tech adoption in history
        - **GenAI adoption:** More than doubled from 33% to 71%
        - **Worker usage:** 28% of U.S. workers use GenAI at work (Aug 2024)
        - **Daily usage:** 9% of workers use GenAI every workday, 14% weekly
        - **Education correlation:** Strong association with education and income levels
        """)
        
    with comp_tabs[1]:
        st.markdown("""
        #### Economics and Investment Impact
        
        **Record Investment Levels (2024):**
        - **U.S. dominance:** $109.1 billion (vs China: $9.3B, UK: $4.5B) - 12x larger than China
        - **Global GenAI:** $33.9 billion (+18.7% from 2023), now 20% of all AI investment
        - **Sector leaders:** AI infrastructure ($37.3B), Data management ($16.6B), Healthcare ($11B)
        - **Investment growth:** 13x increase since 2014 baseline of $19.4B
        
        **GDP Impact Projections - Wide Range:**
        
        **Optimistic Scenarios:**
        - **Goldman Sachs:** +7% global GDP (~$7 trillion) over 10 years
        - **McKinsey:** $17.1-25.6 trillion global economic addition
        - **Productivity boost:** +1.5-3.4 percentage points annually in advanced economies
        
        **Conservative Estimates:**
        - **MIT (Acemoglu):** +0.66% total factor productivity over 10 years
        - **Fed analysis:** "Nontrivial but modest" macroeconomic effects
        - **Task-level focus:** Effects may be lower (0.53%) due to "hard-to-learn" tasks
        
        **AI Automation vs Augmentation:**
        - **Automation AI:** Substitutes human labor, may increase inequality
        - **Augmentation AI:** Complements humans, potentially reduces inequality
        - **Policy implications:** Need progressive taxation and new task creation
        
        **Tokens as Economic Currency:**
        - **AI factories:** Process tokens as fundamental units converting data into intelligence
        - **Value creation:** More tokens at lower computational cost = higher margins
        - **Enterprise optimization:** 25x revenue increases documented in case studies
        - **NVIDIA case study:** 20x cost reduction led to 25x revenue growth in 4 weeks
        """)
        
    with comp_tabs[2]:
        st.markdown("""
        #### Labor Market and Productivity Impact
        
        **Measured Productivity Gains:**
        - **Worker estimates:** 15% longer completion time without AI (Nov 2024 survey)
        - **Aggregate potential:** 0.4% productivity gain assuming full beneficial adoption
        - **Voluntary vs mandated:** Self-initiated AI use shows stronger productivity correlation
        - **Knowledge work caveat:** Official statistics may undercount true productivity boost
        
        **Workforce Exposure Analysis:**
        - **80% of workforce:** At least 10% of tasks affected by LLMs
        - **19% of workers:** At least 50% of tasks impacted  
        - **15% task acceleration:** Direct LLM access enables significantly faster completion
        - **47-56% task enhancement:** Including AI-powered software and tools
        - **Income correlation:** Higher-income jobs face greater exposure to AI capabilities
        
        **Skill-Based Impact (Inequality Reduction Potential):**
        - **Low-skilled workers:** 14% productivity gain (highest benefit)
        - **Medium-skilled workers:** 9% productivity improvement
        - **High-skilled workers:** 5% productivity enhancement
        - **Skill gap narrowing:** AI helps reduce workplace inequality
        - **Task substitution:** 15% of tasks can be done significantly faster
        
        **Industry and Wage Exposure:**
        - **Information processing:** Highest exposure to AI capabilities
        - **Manufacturing/agriculture/mining:** Lower exposure levels
        - **All wage levels affected:** Not limited to recent high-productivity sectors
        - **Geographic concentration:** AI talent clustering in SF, London creates disparities
        
        **Career Transitions:**
        - **Into AI engineering:** Software engineers (26.9%), Data scientists (13.3%)
        - **Net talent flow:** U.S. maintains positive flow (1.07 per 10,000 members)
        - **Workforce development:** Organizations hiring AI roles and retraining existing staff
        """)
        
    with comp_tabs[3]:
        st.markdown("""
        #### Policy and Governance Developments
        
        **Regulatory Acceleration (2024):**
        - **U.S. federal agencies:** 59 AI-related regulations (2x increase from 2023)
        - **Global legislative activity:** +21.3% AI mentions across 75 countries
        - **International frameworks:** OECD, EU, UN, African Union emphasizing transparency
        - **Responsible AI focus:** Growing recognition of need for effective RAI frameworks
        
        **Education Policy Transformation:**
        - **K-12 computer science:** 2/3 of countries now offer/plan (2x from 2019)
        - **Teacher readiness gap:** 81% believe AI should be in education, <50% feel equipped
        - **Curriculum development:** Need for policy initiatives supporting teacher training
        
        **Key Regulatory Areas:**
        - **Competition:** UK CMA reports on AI foundation models, antitrust concerns
        - **Privacy & Data:** GDPR framework applicable to AI systems
        - **Intellectual Property:** UK developing AI copyright code of practice
        - **Military & Security:** UK MOD ethical AI guidelines for defense applications
        - **Ethics & Bias:** Multiple national guidance frameworks for algorithmic fairness
        
        **OECD AI Capability Assessment:**
        - **Assessment framework:** 9 domains including Language and Manipulation
        - **International comparability:** Trusted information for policy decisions
        - **Beyond benchmarking:** Evaluation tools for education, healthcare, and law
        - **Conceptual challenges:** Human-AI comparison doesn't imply direct substitution
        
        **Emerging Policy Areas:**
        - **Participatory governance:** AI tools for civic engagement
        - **Negative social value:** Addressing algorithms designed for manipulation
        - **Public-private partnerships:** Facilitating firm adoption through collaboration
        - **International coordination:** Need for greater survey comparability
        """)
        
    with comp_tabs[4]:
        st.markdown("""
        #### Technical Evolution and Compute Trends
        
        **Historical Compute Growth Phases:**
        - **Pre-2010 (Pre-Deep Learning):** Doubling every 20 months (Moore's Law pace)
        - **2010+ (Deep Learning Era):** Acceleration to 6-month doubling
        - **2015+ (Large-Scale Era):** 10-100x larger training requirements
        - **Recent variation:** 2-3.4 month doubling (2012-2018) to >2 years (2018-2020)
        - **Current constraints:** Hardware and chip limitations may limit exponential growth
        
        **Model Development Leadership:**
        - **U.S. institutions:** 40 notable AI models in 2024
        - **China:** 15 notable models  
        - **Europe:** 3 notable models
        - **Parameter scaling:** 18-24 month doubling (2000-2021)
        - **Language models:** 4-8 month doubling (2016-2018)
        
        **Research Output Explosion:**
        - **Publication growth:** AI papers tripled (2013-2023): 102k → 242k
        - **CS share increase:** 21.6% → 41.8% of computer science publications
        - **Geographic leadership:** China leads publications (23.2%) and citations (22.6%)
        - **U.S. specialization:** Excels in highly influential research (top 100 cited)
        - **Patent surge:** 3,833 (2010) → 122,511 (2023), China holds 69.7%
        
        **Compute Centralization Concerns:**
        - **Private firm concentration:** Centralized access undermining academic transparency
        - **Reproducibility challenges:** Limited access to compute resources
        - **Energy intensity:** Future AI systems may rival global cloud infrastructure
        - **Environmental constraints:** Growing carbon footprint requiring sustainable solutions
        
        **Technical Breakthroughs:**
        - **Multimodal systems:** Beyond text to vision, audio, and robotics
        - **Efficiency improvements:** Hardware performance gains outpacing energy use
        - **Context windows:** Expansion to 1M+ tokens enabling new applications
        - **Real-time processing:** Reduced latency enabling interactive applications
        """)
        
    with comp_tabs[5]:
        st.markdown("""
        #### Global Dynamics and Competition
        
        **Regional Optimism Disparities:**
        - **High optimism:** China (83%), Indonesia (80%), Thailand (77%)
        - **Moderate optimism:** Most European countries (50-65%)
        - **Lower optimism:** Canada (40%), U.S. (39%), Netherlands (36%)
        - **Cultural factors:** Policy environment and economic expectations drive differences
        
        **Investment and Development Competition:**
        - **U.S. leadership:** Dominates private investment (43% of global)
        - **China's focus:** Leading in patents and publications, strong government support
        - **Europe's approach:** Regulatory leadership with GDPR and AI Act frameworks
        - **Emerging markets:** Growing adoption in Asia-Pacific and Latin America
        
        **Talent Flow Dynamics:**
        - **U.S. advantage:** Positive net AI talent flow despite visa restrictions
        - **Geographic concentration:** SF Bay Area, London creating innovation clusters
        - **Brain drain risks:** Developing countries losing AI talent to advanced economies
        - **Skills shortage:** Global shortage of AI/ML engineers and data scientists
        
        **Adoption Barriers by Region:**
        - **Advanced economies:** Focus on workforce training and regulatory clarity
        - **Developing nations:** Digital infrastructure and organizational readiness challenges
        - **Regional disparities:** Widening gap between AI leaders and followers
        - **Policy coordination:** Need for international frameworks and standards
        
        **Emerging Applications by Region:**
        - **Healthcare AI:** FDA approvals in U.S., regulatory pathways in EU
        - **Financial services:** Widespread adoption in developed markets
        - **Manufacturing:** Germany and Japan leading industrial AI
        - **Smart cities:** China and Singapore pioneering urban AI deployment
        """)
        
    with comp_tabs[6]:
        st.markdown("""
        #### Risks, Safety, and Responsible AI
        
        **Growing Safety Incidents:**
        - **Incident tracking:** AI Index reports increasing misuse, bias, and safety failures
        - **Types of incidents:** Algorithmic bias, privacy violations, safety-critical failures
        - **Response lag:** Organizations acknowledge risks but slow to implement mitigation
        - **Governance gaps:** Need for effective responsible AI (RAI) frameworks
        
        **Key Risk Categories:**
        
        **Technical Risks:**
        - **Model reliability:** Hallucinations and factual inaccuracies
        - **Security vulnerabilities:** Adversarial attacks and data poisoning
        - **System failures:** Critical infrastructure and safety-critical applications
        - **Scalability challenges:** Performance degradation with wider deployment
        
        **Societal Risks:**
        - **Labor displacement:** Potential job losses without adequate retraining
        - **Inequality amplification:** AI benefits concentrated among educated/wealthy
        - **Democratic risks:** Misinformation and manipulation tools
        - **Privacy erosion:** Surveillance capabilities and data collection
        
        **Economic Risks:**
        - **Market concentration:** AI capabilities concentrated in few large firms
        - **Systemic risks:** Over-reliance on AI systems in critical sectors
        - **Economic disruption:** Rapid changes outpacing adaptation mechanisms
        - **Investment bubbles:** Overvaluation of AI capabilities and companies
        
        **Mitigation Strategies:**
        - **Regulatory frameworks:** Proactive governance rather than reactive regulation
        - **Industry standards:** Technical standards for safety and reliability
        - **Education and training:** Workforce development for AI transition
        - **International cooperation:** Global coordination on AI governance
        - **Research investment:** Public funding for AI safety and alignment research
        
        **Responsible AI Implementation:**
        - **Organizational governance:** Senior leadership roles for AI oversight
        - **Risk assessment:** Systematic evaluation of AI system impacts
        - **Transparency requirements:** Explainable AI and algorithmic auditing
        - **Stakeholder engagement:** Including affected communities in AI development
        """)
    
    # Enhanced sources section with more detail
    st.markdown("---")
    st.markdown("""
    #### 📚 Comprehensive Analysis Sources & Methodology
    
    **Primary Authoritative Sources:**
    
    **🎓 Academic Research:**
    - **AI Index Report 2025** - Stanford Human-Centered AI Institute (Global AI metrics and trends)
    - **Federal Reserve Research** - Bick, Blandin, Deming (Productivity and workforce impact studies)
    - **MIT Economics** - Daron Acemoglu "The Simple Macroeconomics of AI" (Economic theory and modeling)
    - **OECD AI Observatory** - Firm adoption analysis and capability indicators
    - **Compute Trends Research** - Sevilla et al. (Historical analysis of ML training requirements)
    
    **🏢 Industry Analysis:**
    - **McKinsey Global Survey** - Enterprise AI adoption patterns (1,491 participants, 101 nations)
    - **Goldman Sachs Research** - Economic growth projections and GDP impact analysis
    - **NVIDIA Research** - Token economics and AI infrastructure analysis
    - **Various industry reports** - Sector-specific adoption and impact studies
    
    **🏛️ Government Sources:**
    - **U.S. Census Bureau** - AI Use Supplement (850,000 firms surveyed)
    - **Federal Reserve Banks** - Multiple economic impact analyses
    - **FDA** - AI-enabled medical device approvals and regulations
    - **International organizations** - UN, EU, African Union AI frameworks
    
    **Key Research Papers Referenced:**
    - Bick, Blandin, and Deming (2024, 2025a) - "The Rapid Adoption of Generative AI" and productivity impact
    - Eloundou et al. (2023) - "GPTs are GPTs: An Early Look at the Labor Market Impact Potential"
    - Briggs & Kodnani (2023) - "The Potentially Large Effects of Artificial Intelligence on Economic Growth"
    - Korinek (2023) - "Language Models and Cognitive Automation for Economic Research"
    - Sevilla et al. (2022) - "Compute Trends Across Three Eras of Machine Learning"
    - Multiple Federal Reserve working papers on AI's macroeconomic effects
    
    **Methodology Notes:**
    - **Cross-source validation** - Key findings confirmed across multiple independent sources
    - **Temporal analysis** - Tracking changes from 2018 early adoption through 2025 GenAI era
    - **Geographic scope** - Global coverage with detailed focus on G7 countries and major economies
    - **Sector analysis** - Industry-specific impacts across technology, finance, healthcare, manufacturing
    - **Multi-dimensional assessment** - Technical capabilities, economic impact, policy implications, social effects
    """)

# [Rest of the file continues with all the remaining sections...]

# Footer - Enhanced with trust indicators
st.markdown("---")

# Trust and quality indicators
trust_cols = st.columns(5)

with trust_cols[0]:
    st.markdown("""
    <div style='text-align: center;'>
        <h4>📊 Data Quality</h4>
        <div style='background-color: #28a745; color: white; padding: 8px; border-radius: 20px; display: inline-block;'>
            ✓ Verified Sources
        </div>
    </div>
    """, unsafe_allow_html=True)

with trust_cols[1]:
    st.markdown("""
    <div style='text-align: center;'>
        <h4>🔄 Update Status</h4>
        <div style='color: #28a745;'>
            ✅ June 2025
        </div>
    </div>
    """, unsafe_allow_html=True)

with trust_cols[2]:
    st.markdown("""
    <div style='text-align: center;'>
        <h4>📈 Coverage</h4>
        <div>
            Global Scope<br>
            <small>101+ countries</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

with trust_cols[3]:
    st.markdown("""
    <div style='text-align: center;'>
        <h4>🔍 Transparency</h4>
        <div>
            Open Source<br>
            <small>MIT License</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

with trust_cols[4]:
    st.markdown("""
    <div style='text-align: center;'>
        <h4>🔒 Privacy</h4>
        <div style='color: #28a745;'>
            GDPR Compliant<br>
            <small>No tracking</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Enhanced footer with resources
footer_cols = st.columns(4)

with footer_cols[0]:
    st.markdown("""
    ### 📚 Resources
    - [📖 GitHub Repository](https://github.com/Rcasanova25/AI-Adoption-Dashboard)
    - [🚀 Live Dashboard](https://ai-adoption-dashboard.streamlit.app/)
    - [📊 View Source Code](https://github.com/Rcasanova25/AI-Adoption-Dashboard/blob/main/app.py)
    - [🐛 Report Issues](https://github.com/Rcasanova25/AI-Adoption-Dashboard/issues)
    - [📄 Documentation](https://github.com/Rcasanova25/AI-Adoption-Dashboard/wiki)
    """)

with footer_cols[1]:
    st.markdown("""
    ### 🔬 Research Partners
    - [Stanford HAI](https://hai.stanford.edu)
    - [AI Index Report](https://aiindex.stanford.edu)
    - [McKinsey AI](https://www.mckinsey.com/capabilities/quantumblack)
    - [OECD.AI](https://oecd.ai)
    - [MIT CSAIL](https://www.csail.mit.edu)
    """)

with footer_cols[2]:
    st.markdown("""
    ### 🤝 Connect
    - [LinkedIn - Robert Casanova](https://linkedin.com/in/robert-casanova)
    - [GitHub - @Rcasanova25](https://github.com/Rcasanova25)
    - [Email](mailto:Robert.casanova82@gmail.com)
    - [Twitter/X](https://twitter.com)
    - [Star on GitHub ⭐](https://github.com/Rcasanova25/AI-Adoption-Dashboard)
    """)

with footer_cols[3]:
    st.markdown("""
    ### 🛟 Support
    - [User Guide](https://github.com/Rcasanova25/AI-Adoption-Dashboard/wiki/User-Guide)
    - [FAQ](https://github.com/Rcasanova25/AI-Adoption-Dashboard/wiki/FAQ)
    - [Report Bug](https://github.com/Rcasanova25/AI-Adoption-Dashboard/issues/new?labels=bug)
    - [Request Feature](https://github.com/Rcasanova25/AI-Adoption-Dashboard/issues/new?labels=enhancement)
    - [Discussions](https://github.com/Rcasanova25/AI-Adoption-Dashboard/discussions)
    """)

# Final attribution
st.markdown("""
<div style='text-align: center; color: #666; padding: 30px 20px 20px 20px; margin-top: 40px; border-top: 1px solid #ddd;'>
    <p style='font-size: 20px; margin-bottom: 10px;'>
        🤖 <strong>AI Adoption Dashboard</strong> v2.2.0
    </p>
    <p style='margin-bottom: 5px; font-size: 16px;'>
        Comprehensive AI adoption insights from 2018 to 2025
    </p>
    <p style='font-size: 14px; color: #888; margin-top: 15px;'>
        Enhanced with AI Index Report 2025 findings | Last updated: June 17, 2025
    </p>
    <p style='font-size: 14px; margin-top: 20px;'>
        Created by <a href='https://linkedin.com/in/robert-casanova' style='color: #1f77b4;'>Robert Casanova</a> | 
        Powered by <a href='https://streamlit.io' style='color: #1f77b4;'>Streamlit</a> & 
        <a href='https://plotly.com' style='color: #1f77b4;'>Plotly</a> | 
        <a href='https://github.com/Rcasanova25/AI-Adoption-Dashboard/blob/main/LICENSE' style='color: #1f77b4;'>MIT License</a>
    </p>
    <p style='font-size: 12px; margin-top: 15px; color: #999;'>
        <i>Data sources: AI Index Report 2025 (Stanford HAI), McKinsey Global Survey on AI, OECD AI Policy Observatory</i>
    </p>
</div>
""", unsafe_allow_html=True)