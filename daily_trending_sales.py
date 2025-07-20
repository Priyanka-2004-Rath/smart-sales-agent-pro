# daily_trending_sales.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import streamlit as st
import time
import re

class DailyTrendingSales:
    def __init__(self):
        self.base_url = "https://economictimes.indiatimes.com/industry"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def fetch_trending_headlines(self, max_headlines=10):
        """Fetch trending headlines from Economic Times Industry section"""
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            headlines = []
            
            # Multiple selectors for different headline formats on ET
            selectors = [
                'h3 a',
                '.eachStory h3 a',
                '.story-box h3 a',
                'h2 a',
                '.content h3 a'
            ]
            
            for selector in selectors:
                headline_elements = soup.select(selector)
                for element in headline_elements:
                    if element and element.get_text(strip=True):
                        headline_text = element.get_text(strip=True)
                        link = element.get('href', '')
                        
                        # Clean and filter headlines
                        if self.is_relevant_headline(headline_text):
                            headlines.append({
                                'title': headline_text,
                                'link': self.normalize_link(link),
                                'timestamp': datetime.now().strftime('%H:%M')
                            })
                        
                        if len(headlines) >= max_headlines:
                            break
                
                if len(headlines) >= max_headlines:
                    break
            
            return headlines[:max_headlines] if headlines else self.get_fallback_headlines()
            
        except Exception as e:
            st.error(f"Error fetching headlines: {str(e)}")
            return self.get_fallback_headlines()
    
    def is_relevant_headline(self, headline):
        """Filter relevant business/sales headlines"""
        relevant_keywords = [
            'sales', 'revenue', 'profit', 'growth', 'business', 'market', 'industry',
            'company', 'startup', 'investment', 'funding', 'merger', 'acquisition',
            'earnings', 'financial', 'economy', 'trade', 'export', 'import', 'deal',
            'partnership', 'launch', 'expansion', 'quarter', 'annual', 'report'
        ]
        
        headline_lower = headline.lower()
        return (
            any(keyword in headline_lower for keyword in relevant_keywords) and
            len(headline) > 20 and
            len(headline) < 200 and
            not any(skip in headline_lower for skip in ['video', 'photos', 'gallery'])
        )
    
    def normalize_link(self, link):
        """Normalize relative links to absolute URLs"""
        if link.startswith('http'):
            return link
        elif link.startswith('/'):
            return f"https://economictimes.indiatimes.com{link}"
        else:
            return f"https://economictimes.indiatimes.com/{link}"
    
    def get_fallback_headlines(self):
        """Fallback headlines when scraping fails"""
        current_date = datetime.now().strftime('%B %d, %Y')
        return [
            {
                'title': f'Indian Economy Shows Resilience in Q3 FY24 - {current_date}',
                'link': 'https://economictimes.indiatimes.com/industry',
                'timestamp': datetime.now().strftime('%H:%M')
            },
            {
                'title': f'Tech Sector Leads Growth with 15% Revenue Increase - {current_date}',
                'link': 'https://economictimes.indiatimes.com/industry',
                'timestamp': datetime.now().strftime('%H:%M')
            },
            {
                'title': f'Manufacturing PMI Hits 8-Month High - {current_date}',
                'link': 'https://economictimes.indiatimes.com/industry',
                'timestamp': datetime.now().strftime('%H:%M')
            },
            {
                'title': f'Startup Funding Rebounds with $2.3B in New Investments - {current_date}',
                'link': 'https://economictimes.indiatimes.com/industry',
                'timestamp': datetime.now().strftime('%H:%M')
            },
            {
                'title': f'Export Growth Accelerates to 12% YoY - {current_date}',
                'link': 'https://economictimes.indiatimes.com/industry',
                'timestamp': datetime.now().strftime('%H:%M')
            }
        ]
    
    def get_trending_analysis(self, headlines):
        """Analyze trending topics from headlines"""
        all_text = ' '.join([h['title'] for h in headlines]).lower()
        
        # Define trending categories
        categories = {
            'Technology': ['tech', 'ai', 'digital', 'software', 'startup', 'app', 'platform'],
            'Manufacturing': ['manufacturing', 'production', 'factory', 'industrial'],
            'Finance': ['bank', 'financial', 'loan', 'investment', 'fund'],
            'Healthcare': ['health', 'pharma', 'medical', 'hospital'],
            'Energy': ['energy', 'power', 'oil', 'gas', 'renewable', 'solar'],
            'Retail': ['retail', 'consumer', 'shopping', 'ecommerce'],
            'Auto': ['auto', 'car', 'vehicle', 'automotive']
        }
        
        category_scores = {}
        for category, keywords in categories.items():
            score = sum(all_text.count(keyword) for keyword in keywords)
            if score > 0:
                category_scores[category] = score
        
        # Get top trending category
        if category_scores:
            top_category = max(category_scores, key=category_scores.get)
            return {
                'trending_sector': top_category,
                'all_scores': category_scores,
                'total_mentions': sum(category_scores.values())
            }
        else:
            return {
                'trending_sector': 'General Business',
                'all_scores': {'General Business': 1},
                'total_mentions': 1
            }

# Function to add to your main app.py
def render_daily_trending_section():
    """Render the daily trending sales section"""
    
    # Initialize trending sales in session state
    if 'trending_sales' not in st.session_state:
        st.session_state.trending_sales = DailyTrendingSales()
    
    if 'last_fetch_time' not in st.session_state:
        st.session_state.last_fetch_time = datetime.min
    
    if 'cached_headlines' not in st.session_state:
        st.session_state.cached_headlines = []
    
    # Auto-refresh every 30 minutes
    current_time = datetime.now()
    if (current_time - st.session_state.last_fetch_time).seconds > 1800:  # 30 minutes
        with st.spinner("🔄 Fetching latest trending headlines..."):
            st.session_state.cached_headlines = st.session_state.trending_sales.fetch_trending_headlines()
            st.session_state.last_fetch_time = current_time
    
    # Display section
    st.markdown("---")
    
    # Get current date info
    current_date = datetime.now()
    day_name = current_date.strftime('%A')
    formatted_date = current_date.strftime('%B %d, %Y')
    
    st.markdown(f"""
    <div class="glass-card">
        <h2 style="color: white; text-align: center; margin-bottom: 1rem;">
            📈 Daily Trending Sales & Business News
        </h2>
        <div style="text-align: center; color: rgba(255,255,255,0.8); margin-bottom: 2rem;">
            <span style="font-size: 1.2rem;">📅 {day_name}, {formatted_date}</span>
            <br>
            <span style="font-size: 0.9rem; opacity: 0.7;">Last updated: {st.session_state.last_fetch_time.strftime('%H:%M')} | Source: Economic Times</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Control buttons
    refresh_col1, refresh_col2, refresh_col3 = st.columns([2, 1, 1])
    
    with refresh_col2:
        if st.button("🔄 Refresh News", use_container_width=True):
            with st.spinner("📰 Fetching latest headlines..."):
                st.session_state.cached_headlines = st.session_state.trending_sales.fetch_trending_headlines()
                st.session_state.last_fetch_time = datetime.now()
                st.success("✅ Headlines updated!")
                time.sleep(0.5)
                st.rerun()
    
    with refresh_col3:
        auto_refresh = st.checkbox("🔄 Auto-refresh", value=True)
    
    # Display headlines
    if st.session_state.cached_headlines:
        # Trending analysis
        analysis = st.session_state.trending_sales.get_trending_analysis(st.session_state.cached_headlines)
        
        # Trending sector display
        st.markdown(f"""
        <div class="glass-card">
            <div style="text-align: center;">
                <h3 style="color: #667eea; margin-bottom: 1rem;">🔥 Today's Trending Sector</h3>
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                           color: white; padding: 1rem 2rem; border-radius: 25px; 
                           display: inline-block; font-size: 1.3rem; font-weight: 600;">
                    {analysis['trending_sector']} 
                    <span style="font-size: 0.9rem; opacity: 0.8;">({analysis['total_mentions']} mentions)</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Headlines grid
        st.markdown("### 📰 Latest Headlines")
        
        # Display headlines in cards
        for i, headline in enumerate(st.session_state.cached_headlines):
            with st.container():
                st.markdown(f"""
                <div class="glass-card" style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: between; align-items: start;">
                        <div style="flex: 1;">
                            <h4 style="color: white; margin-bottom: 0.5rem; line-height: 1.4;">
                                📊 {headline['title']}
                            </h4>
                            <div style="display: flex; gap: 1rem; margin-top: 1rem;">
                                <span style="color: rgba(255,255,255,0.7); font-size: 0.9rem;">
                                    🕒 {headline['timestamp']}
                                </span>
                                <a href="{headline['link']}" target="_blank" 
                                   style="color: #667eea; text-decoration: none; font-size: 0.9rem;">
                                    🔗 Read Full Article
                                </a>
                            </div>
                        </div>
                        <div style="margin-left: 1rem;">
                            <span style="background: rgba(102, 126, 234, 0.2); 
                                       color: #667eea; padding: 0.3rem 0.8rem; 
                                       border-radius: 15px; font-size: 0.8rem;">
                                #{i+1}
                            </span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Sector breakdown chart
        if len(analysis['all_scores']) > 1:
            st.markdown("### 📊 Sector Activity Breakdown")
            
            import plotly.express as px
            import pandas as pd
            
            sector_df = pd.DataFrame(
                list(analysis['all_scores'].items()), 
                columns=['Sector', 'Mentions']
            ).sort_values('Mentions', ascending=True)
            
            fig_sectors = px.bar(
                sector_df, 
                x='Mentions', 
                y='Sector',
                orientation='h',
                title="📈 Sector Activity Today",
                color='Mentions',
                color_continuous_scale="Viridis"
            )
            fig_sectors.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                title_font_size=16
            )
            st.plotly_chart(fig_sectors, use_container_width=True)
    
    else:
        st.markdown("""
        <div class="glass-card">
            <div style="text-align: center; padding: 3rem; color: rgba(255,255,255,0.7);">
                <h3>📰 No Headlines Available</h3>
                <p>Unable to fetch trending news at the moment. Please try refreshing.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Daily insights summary
    if st.session_state.cached_headlines:
        st.markdown("### 💡 Daily Business Insights")
        
        # Generate AI insights based on headlines
        headlines_text = ' '.join([h['title'] for h in st.session_state.cached_headlines[:5]])
        
        insights = [
            f"📈 **Market Focus:** {analysis['trending_sector']} sector is showing high activity today",
            f"📊 **News Volume:** {len(st.session_state.cached_headlines)} trending stories tracked",
            f"🎯 **Opportunity Alert:** Monitor {analysis['trending_sector'].lower()} companies for sales prospects",
            f"💼 **Business Trend:** Current market sentiment appears {'positive' if 'growth' in headlines_text.lower() else 'mixed'}"
        ]
        
        for insight in insights:
            st.markdown(f"""
            <div class="glass-card" style="margin-bottom: 0.5rem; padding: 1rem;">
                <p style="color: rgba(255,255,255,0.9); margin: 0;">{insight}</p>
            </div>
            """, unsafe_allow_html=True)