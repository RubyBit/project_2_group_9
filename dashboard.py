import json
import pandas as pd
import plotly
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests
import numpy as np

# Add animation to the dashboard header
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Load the JSON data
@st.cache_data
def load_data():
    with open("analysis_results/all_results.json", "r") as f:
        data = json.load(f)
    # Flatten nested JSON for easier analysis
    return pd.json_normalize(data)

# Set page configuration
st.set_page_config(layout="wide", page_title="Repository Analysis Dashboard", page_icon="📊")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4CAF50;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .metric-container {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .tab-subheader {
        font-size: 1.5rem;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

# Load data
df = load_data()

# Load animation
#lottie_data = load_lottie_url("https://assets2.lottiefiles.com/packages/lf20_uwWgICVMrw.json")

# Dashboard Header with Animation
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    #st_lottie(lottie_data, height=200, key="coding_animation")
    st.markdown("<h1 class='main-header'>Code Repository Analysis Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("This dashboard analyzes multiple aspects of your repositories including **code quality**, **complexity**, **dependencies**, **testing coverage**, **commit history**, and **sustainability scores**.")

# Sidebar: Enhanced filters
st.sidebar.header("Filter Options")
countries = sorted(df['metadata.country'].unique().tolist())
selected_country = st.sidebar.selectbox("Select Country", ["All"] + countries)

# Add org filter if country is selected
if selected_country != "All":
    df_filtered = df[df['metadata.country'] == selected_country]
    orgs = sorted(df_filtered['metadata.org'].unique().tolist())
    selected_org = st.sidebar.selectbox("Select Organization", ["All"] + orgs)
    if selected_org != "All":
        df_filtered = df_filtered[df_filtered['metadata.org'] == selected_org]
else:
    df_filtered = df.copy()

# Dashboard main content with tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📈 Overview", "🧹 Code Quality", "🔄 Commits & Testing", "🛡️ Security & Structure", "💡 Insights", "🔍 Repository Search"])

# Tab 1: Overview
with tab1:
    # Key metrics with improved styling
    st.markdown("## Key Metrics")
    
    # First row of metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        avg_lines = df_filtered['code_analysis.total_lines'].mean()
        st.metric("Avg Total Lines", f"{avg_lines:.0f}")
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        avg_files = df_filtered['code_analysis.file_count'].mean()
        st.metric("Avg File Count", f"{avg_files:.0f}")
        st.markdown("</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        avg_commits = df_filtered['commit_history.total_commits'].mean()
        st.metric("Avg Commits", f"{avg_commits:.0f}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Second row of metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        avg_contrib = df_filtered['commit_history.contributors'].mean()
        st.metric("Avg Contributors", f"{avg_contrib:.1f}")
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        avg_sustain = df_filtered['gemini_scores.overall_sustainability'].mean()
        st.metric("Avg Sustainability Score", f"{avg_sustain:.1f}/100")
        st.markdown("</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        has_tests = df_filtered['test_coverage.has_tests'].mean() * 100
        st.metric("Repos with Tests (%)", f"{has_tests:.1f}%")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Gemini Scores as Radar Chart
    st.markdown("## Sustainability Scorecard")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        gemini_cols = [
            'gemini_scores.documentation_quality',
            'gemini_scores.testing_robustness',
            'gemini_scores.modularity_and_design',
            'gemini_scores.error_handling',
            'gemini_scores.security_best_practices',
            'gemini_scores.scalability_potential',
            'gemini_scores.environmental_efficiency',
            'gemini_scores.social_inclusiveness'
        ]
        
        categories = [col.split('.')[-1].replace('_', ' ').title() for col in gemini_cols]
        values = [df_filtered[col].mean() for col in gemini_cols]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],  # Close the hexagon by repeating the first value
            theta=categories + [categories[0]],  # Close the hexagon by repeating the first category
            fill='toself',
            name='Average Score',
            line_color='rgba(0, 128, 0, 0.8)',  # Green line color
            fillcolor='rgba(0, 128, 0, 0.3)'  # Green fill color
        ))
        
        fig.update_layout(
            polar=dict(
            angularaxis=dict(
                tickfont=dict(size=12, color='rgba(255, 255, 255, 0.8)'),  # White text for categories
                gridcolor='rgba(255, 255, 255, 0.2)'  # Light white grid lines
            ),
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10, color='rgba(255, 255, 255, 0.8)'),  # White text for radial ticks
                gridcolor='rgba(255, 255, 255, 0.2)'  # Light white grid lines
            ),
            bgcolor='rgba(0, 0, 0, 0.8)'  # Dark background for the polar chart
            ),
            showlegend=False,
            title=dict(
            text="Sustainability Dimension Scores",
            font=dict(size=16, color='rgba(255, 255, 255, 0.9)')  # White title text
            ),
            template="plotly_dark",  # Use a dark theme
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Score Interpretation")
        st.markdown("""
        - **Documentation Quality**: Code comments, API docs, README
        - **Testing Robustness**: Test coverage, test types, CI integration
        - **Modularity**: Code organization, separation of concerns
        - **Error Handling**: Exception management, logging
        - **Security**: Auth practices, input validation, dependency management
        - **Scalability**: Performance under load, architecture
        - **Environmental**: Computation efficiency, resource usage
        - **Social**: Accessibility, inclusivity, ethics
        """)
    
    # File Type Distribution
    st.markdown("## Repository Composition")
    col1, col2 = st.columns(2)
    
    with col1:
        # Extract file types data
        file_types = {}
        for repo_idx, row in df_filtered.iterrows():
            file_types_str = row.get('code_analysis.file_types', '{}')
            if isinstance(file_types_str, str):
                types_dict = json.loads(file_types_str)
            else:
                types_dict = file_types_str
            
            for file_type, count in types_dict.items():
                if file_type in file_types:
                    file_types[file_type] += count
                else:
                    file_types[file_type] = count
        
        # Create a dataframe for visualization
        if file_types:
            file_type_df = pd.DataFrame({
                'Extension': list(file_types.keys()),
                'Count': list(file_types.values())
            })
            
            fig = px.treemap(
                file_type_df,
                path=['Extension'],
                values='Count',
                title="File Type Distribution",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No file type data available")
    
    with col2:
        # Commit History Trend with Animation
        st.markdown("#### Commit Activity")
        # This is a placeholder - in a real implementation, we'd need time series data
        # Here we simulate a commit timeline from the data
        
        # Create a placeholder timeline using contributors and commits
        commits = df_filtered['commit_history.total_commits'].tolist()
        contribs = df_filtered['commit_history.contributors'].tolist()
        
        if commits and contribs:
            # Simulate a timeline
            n_points = 30
            dates = pd.date_range(end=pd.Timestamp.now(), periods=n_points)
            
            # Generate some simulated commit data
            commit_data = []
            for i, (c, cont) in enumerate(zip(commits, contribs)):
                # Skip if we're out of repos
                if i >= len(commits):
                    break
                    
                # Scale the commits across time periods
                daily_commits = np.random.poisson(c/n_points, n_points)
                for j, date in enumerate(dates):
                    commit_data.append({
                        'date': date,
                        'commits': daily_commits[j],
                        'repo_idx': i
                    })
            
            commit_df = pd.DataFrame(commit_data)
            commit_timeline = commit_df.groupby('date')['commits'].sum().reset_index()
            
            fig = px.line(
                commit_timeline, 
                x='date', 
                y='commits',
                markers=True,
                title="Commit Timeline (Simulated)",
                template="plotly_white"
            )
            
            # Add animation effect
            fig.update_traces(mode="lines+markers")
            fig.update_layout(
                hovermode="x unified",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No commit data available")

# Tab 2: Code Quality
with tab2:
    st.markdown("## Code Quality Analysis")
    
    # Sustainable vs. Unsustainable metrics
    col1, col2 = st.columns(2)
    
    with col1:
        # Sustainable metrics
        st.markdown("### Sustainable Code Practices")
        sustainable_cols = [col for col in df_filtered.columns if col.startswith('code_analysis.sustainable.')]
        
        if sustainable_cols:
            sustainable_data = pd.DataFrame({
                'Metric': [col.split('.')[-1].replace('_', ' ').title() for col in sustainable_cols],
                'Average': [df_filtered[col].mean() for col in sustainable_cols]
            })
            
            fig = px.bar(
                sustainable_data,
                x='Metric',
                y='Average',
                color='Average',
                color_continuous_scale='Viridis',
                title="Sustainable Code Metrics",
                template="plotly_white"
            )
            # set the y-axis range to 0-400
            fig.update_yaxes(range=[0, 400])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sustainable code metrics available")
    
    with col2:
        # Unsustainable metrics
        st.markdown("### Code Smells & Issues")
        unsustainable_cols = [col for col in df_filtered.columns if col.startswith('code_analysis.unsustainable.')]
        
        if unsustainable_cols:
            unsustainable_data = pd.DataFrame({
                'Metric': [col.split('.')[-1].replace('_', ' ').title() for col in unsustainable_cols],
                'Average': [df_filtered[col].mean() for col in unsustainable_cols]
            })
            
            fig = px.bar(
                unsustainable_data,
                x='Metric',
                y='Average',
                color='Average',
                color_continuous_scale='Reds',
                title="Code Smells & Issues",
                template="plotly_white"
            )
            # set the y-axis range to 0-100
            fig.update_yaxes(range=[0, 100])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No code smell metrics available")
    
    # Complexity metrics
    st.markdown("### Code Complexity Analysis")
    complexity_cols = [
        'complexity_analysis.average',
        'complexity_analysis.max',
        'complexity_analysis.complex_functions',
        'complexity_analysis.maintainability_index'
    ]
    
    complexity_data = df_filtered[complexity_cols].mean().reset_index()
    complexity_data.columns = ['Metric', 'Value']
    
    fig = px.bar(
        complexity_data,
        x='Metric',
        y='Value',
        color='Metric',
        title="Code Complexity Metrics",
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Environmental & Social Impact
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Environmental Impact")
        environmental_cols = [col for col in df_filtered.columns if col.startswith('code_analysis.environmental.')]
        
        if environmental_cols:
            env_data = pd.DataFrame({
                'Metric': [col.split('.')[-1].replace('_', ' ').title() for col in environmental_cols],
                'Average': [df_filtered[col].mean() for col in environmental_cols]
            })
            
            fig = px.bar(
                env_data,
                x='Metric',
                y='Average',
                color='Metric',
                color_discrete_sequence=px.colors.sequential.Greens,
                title="Environmental Impact Metrics",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No environmental metrics available")
    
    with col2:
        st.markdown("### Social Impact")
        social_cols = [col for col in df_filtered.columns if col.startswith('code_analysis.social.')]
        
        if social_cols:
            social_data = pd.DataFrame({
                'Metric': [col.split('.')[-1].replace('_', ' ').title() for col in social_cols],
                'Average': [df_filtered[col].mean() for col in social_cols]
            })
            
            fig = px.bar(
                social_data,
                x='Metric',
                y='Average',
                color='Metric',
                color_discrete_sequence=px.colors.sequential.Purples,
                title="Social Impact Metrics",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No social impact metrics available")

# Tab 3: Commits & Testing
with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Commit History Analysis")
        
        # Commit metrics visualization
        commit_cols = [
            'commit_history.total_commits',
            'commit_history.commit_frequency',
            'commit_history.active_days',
            'commit_history.contributors',
            'commit_history.commit_message_quality',
            'commit_history.test_driven_commits'
        ]
        
        commit_data = df_filtered[commit_cols].mean().reset_index()
        commit_data.columns = ['Metric', 'Value']
        
        # Clean up metric names
        commit_data['Metric'] = commit_data['Metric'].apply(
            lambda x: x.split('.')[-1].replace('_', ' ').title()
        )
        
        fig = px.bar(
            commit_data,
            x='Metric',
            y='Value',
            color='Metric',
            title="Commit History Metrics",
            template="plotly_white"
        )
        # set the y-axis range to 0-150
        fig.update_yaxes(range=[0, 150])
        st.plotly_chart(fig, use_container_width=True)
        
        # Commits by Country
        st.markdown("### Commits by Country")
        commits_by_country = df.groupby("metadata.country")["commit_history.total_commits"].sum().reset_index()
        
        fig = px.pie(
            commits_by_country,
            names="metadata.country",
            values="commit_history.total_commits",
            title="Total Commits by Country",
            template="plotly_white",
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Testing Coverage Analysis")
        
        # Test metrics visualization
        test_cols = [
            'test_coverage.has_tests',
            'test_coverage.test_files',
            'test_coverage.test_to_code_ratio',
            'test_coverage.test_lines'
        ]
        
        test_data = df_filtered[test_cols].mean().reset_index()
        test_data.columns = ['Metric', 'Value']
        
        # Clean up metric names
        test_data['Metric'] = test_data['Metric'].apply(
            lambda x: x.split('.')[-1].replace('_', ' ').title()
        )
        
        fig = px.bar(
            test_data,
            x='Metric',
            y='Value',
            color='Metric',
            title="Testing Metrics",
            template="plotly_white"
        )
        # set the y-axis range to 0-100
        fig.update_yaxes(range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)
        
        # Test Frameworks Used
        st.markdown("### Testing Frameworks")
        
        # Extract test frameworks
        test_frameworks = {}
        for _, row in df_filtered.iterrows():
            frameworks = row.get('test_coverage.test_frameworks', [])
            if frameworks:
                if isinstance(frameworks, str):
                    frameworks = json.loads(frameworks)
                
                for framework in frameworks:
                    if framework in test_frameworks:
                        test_frameworks[framework] += 1
                    else:
                        test_frameworks[framework] = 1
        
        if test_frameworks:
            framework_df = pd.DataFrame({
                'Framework': list(test_frameworks.keys()),
                'Count': list(test_frameworks.values())
            })
            
            fig = px.pie(
                framework_df,
                names='Framework',
                values='Count',
                title="Testing Frameworks Used",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No testing framework data available")

# Tab 4: Security & Structure
with tab4:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Repository Structure Analysis")
        
        # Structure metrics
        structure_cols = [
            'repo_structure.has_readme',
            'repo_structure.has_license',
            'repo_structure.has_gitignore',
            'repo_structure.has_ci_config',
            'repo_structure.has_dependency_manager',
            'repo_structure.has_docker',
            'repo_structure.has_contribution_guide',
            'repo_structure.has_code_of_conduct',
            'repo_structure.has_security_policy'
        ]
        
        structure_data = df_filtered[structure_cols].mean().reset_index()
        structure_data.columns = ['Feature', 'Adoption Rate']
        
        # Multiply by 100 to get percentage
        structure_data['Adoption Rate'] = structure_data['Adoption Rate'] * 100
        
        # Clean up feature names
        structure_data['Feature'] = structure_data['Feature'].apply(
            lambda x: x.split('.')[-1].replace('has_', '').replace('_', ' ').title()
        )
        
        fig = px.bar(
            structure_data,
            x='Feature',
            y='Adoption Rate',
            color='Adoption Rate',
            color_continuous_scale='Blues',
            title="Repository Feature Adoption (%)",
            template="plotly_white"
        )
        
        fig.update_layout(yaxis_title="Adoption Rate (%)")
        st.plotly_chart(fig, use_container_width=True)
        
        # Folder Depth & Architecture
        folder_cols = [
            'repo_structure.folder_depth',
            'repo_structure.dependency_count',
            'repo_structure.architecture_score'
        ]
        
        folder_data = df_filtered[folder_cols].mean().reset_index()
        folder_data.columns = ['Metric', 'Value']
        
        # Clean up metric names
        folder_data['Metric'] = folder_data['Metric'].apply(
            lambda x: x.split('.')[-1].replace('_', ' ').title()
        )
        
        fig = px.bar(
            folder_data,
            x='Metric',
            y='Value',
            color='Metric',
            title="Repository Architecture Metrics",
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Dependency Analysis")
        
        # Dependency metrics
        dependency_cols = [
            'dependency_analysis.total_dependencies',
            'dependency_analysis.direct_dependencies',
            'dependency_analysis.dev_dependencies',
            'dependency_analysis.outdated_dependencies'
        ]
        
        dependency_data = df_filtered[dependency_cols].mean().reset_index()
        dependency_data.columns = ['Metric', 'Value']
        
        # Clean up metric names
        dependency_data['Metric'] = dependency_data['Metric'].apply(
            lambda x: x.split('.')[-1].replace('_', ' ').title()
        )
        
        fig = px.bar(
            dependency_data,
            x='Metric',
            y='Value',
            color='Metric',
            title="Dependency Metrics",
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Security Metrics
        st.markdown("### Security Analysis")
        
        # Security aspects from various sections
        security_metrics = {
            'Security Best Practices': df_filtered['gemini_scores.security_best_practices'].mean(),
            'Error Handling': df_filtered['gemini_scores.error_handling'].mean(),
            'Has Security Policy': df_filtered['repo_structure.has_security_policy'].mean() * 100,
            'Code Smells': df_filtered['code_analysis.unsustainable.code_smells'].mean() if 'code_analysis.unsustainable.code_smells' in df_filtered.columns else 0
        }
        
        security_df = pd.DataFrame({
            'Aspect': list(security_metrics.keys()),
            'Value': list(security_metrics.values())
        })
        
        fig = px.bar(
            security_df,
            x='Aspect',
            y='Value',
            color='Aspect',
            title="Security Aspects",
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

# Tab 5: Insights
with tab5:
    st.markdown("## Critical Issues & Improvement Suggestions")
    
    # Find repositories with critical issues
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Common Critical Issues")
        
        # Extract and count critical issues
        all_issues = []
        for _, row in df_filtered.iterrows():
            issues = row.get('gemini_scores.critical_issues', [])
            if issues:
                if isinstance(issues, str):
                    issues = json.loads(issues)
                all_issues.extend(issues)
        
        if all_issues:
            # Group similar issues (simplified approach)
            issue_counts = {}
            for issue in all_issues:
                # Use just the first 50 chars as a key to group similar issues
                key = issue[:50]
                if key in issue_counts:
                    issue_counts[key] += 1
                else:
                    issue_counts[key] = 1
            
            # Display top issues
            top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            issue_df = pd.DataFrame({
                'Issue': [f"{issue}..." for issue, _ in top_issues],
                'Count': [count for _, count in top_issues]
            })
            
            fig = px.bar(
                issue_df,
                x='Count',
                y='Issue',
                orientation='h',
                color='Count',
                color_continuous_scale='Reds',
                title="Top Critical Issues",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No critical issues data available")
    
    with col2:
        st.markdown("### Common Improvement Suggestions")
        
        # Extract and count improvement suggestions
        all_suggestions = []
        for _, row in df_filtered.iterrows():
            suggestions = row.get('gemini_scores.improvement_suggestions', [])
            if suggestions:
                if isinstance(suggestions, str):
                    suggestions = json.loads(suggestions)
                all_suggestions.extend(suggestions)
        
        if all_suggestions:
            # Group similar suggestions (simplified approach)
            suggestion_counts = {}
            for suggestion in all_suggestions:
                # Use just the first 50 chars as a key to group similar suggestions
                key = suggestion[:50]
                if key in suggestion_counts:
                    suggestion_counts[key] += 1
                else:
                    suggestion_counts[key] = 1
            
            # Display top suggestions
            top_suggestions = sorted(suggestion_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            suggestion_df = pd.DataFrame({
                'Suggestion': [f"{suggestion}..." for suggestion, _ in top_suggestions],
                'Count': [count for _, count in top_suggestions]
            })
            
            fig = px.bar(
                suggestion_df,
                x='Count',
                y='Suggestion',
                orientation='h',
                color='Count',
                color_continuous_scale='Greens',
                title="Top Improvement Suggestions",
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No improvement suggestions data available")
    
    st.markdown("## Repository Details")
    detail_columns = [
        'metadata.org', 
        'metadata.repo_link', 
        'metadata.country',
        'code_analysis.total_lines', 
        'code_analysis.file_count',
        'commit_history.total_commits',
        'gemini_scores.overall_sustainability'
    ]
    
    # Sort by sustainability score
    df_details = df_filtered[detail_columns].sort_values(
        by='gemini_scores.overall_sustainability', 
        ascending=False
    ).reset_index(drop=True)
    
    # Rename columns for display
    df_details.columns = [
        'Organization', 
        'Repository Link', 
        'Country',
        'Total Lines', 
        'File Count',
        'Total Commits',
        'Sustainability Score'
    ]
    
    st.dataframe(df_details, use_container_width=True)

    with tab6:
        st.markdown("## Repository Search")
        
        # Create a list of repositories with org and country for better context
        repo_list = []
        for _, row in df.iterrows():
            repo_list.append(f"{row['metadata.org']} / {row['metadata.repo_link'].split('/')[-1]} ({row['metadata.country']})")
        
        # Search box with autocomplete
        search_term = st.text_input("Search repositories by name, organization, or country:", "")
        
        # Filter repositories based on search term
        filtered_repos = [repo for repo in repo_list if search_term.lower() in repo.lower()]
        
        if search_term and not filtered_repos:
            st.warning(f"No repositories found matching '{search_term}'")
        
        # Select repository from filtered list
        if filtered_repos:
            selected_repo = st.selectbox("Select a repository:", filtered_repos)
            
            # Extract org, repo name and country from the selected option
            selected_parts = selected_repo.split(" / ")
            selected_org = selected_parts[0]
            selected_repo_name = selected_parts[1].split(" (")[0]
            
            # Find the repository in the dataframe
            repo_mask = (df['metadata.org'] == selected_org) & (df['metadata.repo_link'].str.endswith(selected_repo_name))
            if repo_mask.any():
                repo_data = df[repo_mask].iloc[0]
                
                # Repository Overview
                st.markdown("### Repository Overview")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"**Organization:** {repo_data['metadata.org']}")
                    st.markdown(f"**Country:** {repo_data['metadata.country']}")
                    st.markdown(f"**Repository Link:** [GitHub]({repo_data['metadata.repo_link']})")
                
                with col2:
                    st.markdown(f"**Total Lines:** {int(repo_data['code_analysis.total_lines'])}")
                    st.markdown(f"**File Count:** {int(repo_data['code_analysis.file_count'])}")
                    st.markdown(f"**Total Commits:** {int(repo_data['commit_history.total_commits'])}")
                
                with col3:
                    st.markdown(f"**Contributors:** {int(repo_data['commit_history.contributors'])}")
                    st.markdown(f"**Has Tests:** {'Yes' if repo_data['test_coverage.has_tests'] else 'No'}")
                    st.markdown(f"**Overall Sustainability:** {repo_data['gemini_scores.overall_sustainability']:.1f}/100")
                
                # Sustainability Scores
                st.markdown("### Sustainability Scores")
                
                # Create two columns for a more compact display
                col1, col2 = st.columns(2)
                
                with col1:
                    # Sustainability radar chart
                    gemini_cols = [
                        'gemini_scores.documentation_quality',
                        'gemini_scores.testing_robustness',
                        'gemini_scores.modularity_and_design',
                        'gemini_scores.error_handling',
                        'gemini_scores.security_best_practices',
                        'gemini_scores.scalability_potential',
                        'gemini_scores.environmental_efficiency',
                        'gemini_scores.social_inclusiveness'
                    ]
                    
                    categories = [col.split('.')[-1].replace('_', ' ').title() for col in gemini_cols]
                    values = [repo_data[col] for col in gemini_cols]
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=values + [values[0]],
                        theta=categories + [categories[0]],
                        fill='toself',
                        line_color='rgba(0, 128, 0, 0.8)',
                        fillcolor='rgba(0, 128, 0, 0.3)'
                    ))
                    
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(visible=True, range=[0, 100]),
                            bgcolor='rgba(0, 0, 0, 0.8)'
                        ),
                        showlegend=False,
                        title="Sustainability Dimension Scores",
                        template="plotly_dark",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Display individual scores in a table
                    score_data = []
                    for col in gemini_cols:
                        score_data.append({
                            "Dimension": col.split('.')[-1].replace('_', ' ').title(),
                            "Score": repo_data[col]
                        })
                    
                    score_df = pd.DataFrame(score_data)
                    
                    # Add a color coding based on score
                    def color_code(val):
                        if val >= 80:
                            return 'background-color: #c6efce; color: #006100'  # Green
                        elif val >= 60:
                            return 'background-color: #ffeb9c; color: #9c5700'  # Yellow
                        else:
                            return 'background-color: #ffc7ce; color: #9c0006'  # Red
                    
                    st.dataframe(score_df.style.applymap(color_code, subset=['Score']), use_container_width=True)
                    
                    # Critical Issues and Improvement Suggestions
                    if 'gemini_scores.critical_issues' in repo_data and repo_data['gemini_scores.critical_issues']:
                        issues = repo_data['gemini_scores.critical_issues']
                        if isinstance(issues, str):
                            issues = json.loads(issues)
                        
                        if issues:
                            st.markdown("#### Top Critical Issues")
                            for issue in issues[:3]:  # Show top 3 issues
                                st.markdown(f"- {issue}")
                    
                    if 'gemini_scores.improvement_suggestions' in repo_data and repo_data['gemini_scores.improvement_suggestions']:
                        suggestions = repo_data['gemini_scores.improvement_suggestions']
                        if isinstance(suggestions, str):
                            suggestions = json.loads(suggestions)
                        
                        if suggestions:
                            st.markdown("#### Top Improvement Suggestions")
                            for suggestion in suggestions[:3]:  # Show top 3 suggestions
                                st.markdown(f"- {suggestion}")
                
                # Code Metrics Details
                st.markdown("### Code Metrics Details")
                
                # Create tabs for different metric categories
                code_tabs = st.tabs(["Quality", "Complexity", "Testing", "Structure"])
                
                with code_tabs[0]:  # Quality
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Sustainable practices
                        st.markdown("#### Sustainable Code Practices")
                        sustainable_cols = [col for col in repo_data.index if col.startswith('code_analysis.sustainable.')]
                        
                        if sustainable_cols:
                            sustainable_data = pd.DataFrame({
                                'Metric': [col.split('.')[-1].replace('_', ' ').title() for col in sustainable_cols],
                                'Value': [repo_data[col] for col in sustainable_cols]
                            })
                            st.dataframe(sustainable_data, use_container_width=True)
                        else:
                            st.info("No sustainable code metrics available")
                    
                    with col2:
                        # Code smells and issues
                        st.markdown("#### Code Smells & Issues")
                        unsustainable_cols = [col for col in repo_data.index if col.startswith('code_analysis.unsustainable.')]
                        
                        if unsustainable_cols:
                            unsustainable_data = pd.DataFrame({
                                'Metric': [col.split('.')[-1].replace('_', ' ').title() for col in unsustainable_cols],
                                'Value': [repo_data[col] for col in unsustainable_cols]
                            })
                            st.dataframe(unsustainable_data, use_container_width=True)
                        else:
                            st.info("No code smell metrics available")
                
                with code_tabs[1]:  # Complexity
                    # Complexity metrics
                    complexity_cols = [
                        'complexity_analysis.average',
                        'complexity_analysis.max',
                        'complexity_analysis.complex_functions',
                        'complexity_analysis.maintainability_index'
                    ]
                    
                    complexity_data = pd.DataFrame({
                        'Metric': [col.split('.')[-1].replace('_', ' ').title() for col in complexity_cols],
                        'Value': [repo_data.get(col, 0) for col in complexity_cols]
                    })
                    
                    fig = px.bar(
                        complexity_data,
                        x='Metric',
                        y='Value',
                        color='Metric',
                        title="Code Complexity Metrics",
                        template="plotly_white"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with code_tabs[2]:  # Testing
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Test metrics
                        st.markdown("#### Testing Metrics")
                        test_cols = [
                            'test_coverage.has_tests',
                            'test_coverage.test_files',
                            'test_coverage.test_to_code_ratio',
                            'test_coverage.test_lines'
                        ]
                        
                        test_data = pd.DataFrame({
                            'Metric': [col.split('.')[-1].replace('_', ' ').title() for col in test_cols],
                            'Value': [repo_data.get(col, 0) for col in test_cols]
                        })
                        st.dataframe(test_data, use_container_width=True)
                    
                    with col2:
                        # Test frameworks
                        st.markdown("#### Testing Frameworks")
                        frameworks = repo_data.get('test_coverage.test_frameworks', [])
                        
                        if frameworks:
                            if isinstance(frameworks, str):
                                frameworks = json.loads(frameworks)
                            
                            if frameworks:
                                st.write(", ".join(frameworks))
                            else:
                                st.info("No testing frameworks detected")
                        else:
                            st.info("No testing framework data available")
                
                with code_tabs[3]:  # Structure
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Repository structure features
                        st.markdown("#### Repository Structure")
                        structure_cols = [
                            'repo_structure.has_readme',
                            'repo_structure.has_license',
                            'repo_structure.has_gitignore',
                            'repo_structure.has_ci_config',
                            'repo_structure.has_dependency_manager',
                            'repo_structure.has_docker',
                            'repo_structure.has_contribution_guide',
                            'repo_structure.has_code_of_conduct',
                            'repo_structure.has_security_policy'
                        ]
                        
                        structure_data = pd.DataFrame({
                            'Feature': [col.split('.')[-1].replace('has_', '').replace('_', ' ').title() for col in structure_cols],
                            'Present': ['✅' if repo_data.get(col, False) else '❌' for col in structure_cols]
                        })
                        st.dataframe(structure_data, use_container_width=True)
                    
                    with col2:
                        # Architectural metrics
                        st.markdown("#### Architecture Metrics")
                        arch_cols = [
                            'repo_structure.folder_depth',
                            'repo_structure.dependency_count',
                            'repo_structure.architecture_score'
                        ]
                        
                        arch_data = pd.DataFrame({
                            'Metric': [col.split('.')[-1].replace('_', ' ').title() for col in arch_cols],
                            'Value': [repo_data.get(col, 0) for col in arch_cols]
                        })
                        st.dataframe(arch_data, use_container_width=True)
            else:
                st.error("Repository details not found. Please select another repository.")
        else:
            st.info("Enter a search term to find repositories")

st.markdown("---")
st.markdown("### End of Dashboard")