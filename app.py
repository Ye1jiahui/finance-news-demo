import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
import akshare as ak
from datetime import datetime, timedelta

# ==========================================
# 1. 页面基础配置
# ==========================================
st.set_page_config(
    page_title="FinTech Pro | 金融市场看板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. 侧边栏配置
# ==========================================
st.sidebar.title("🎛️ 控制台")

st.sidebar.subheader("1. 市场行情配置")
asset_map = {
    "Apple Inc. (AAPL)": "AAPL",
    "Tesla, Inc. (TSLA)": "TSLA",
    "黄金期货 (Gold)": "GC=F",
    "原油期货 (Crude Oil)": "CL=F",
    "上证指数 (SSEC)": "000001.SS"
}
selected_asset_label = st.sidebar.selectbox("选择关注标的", list(asset_map.keys()))
selected_symbol = asset_map[selected_asset_label]

time_period = st.sidebar.select_slider(
    "时间跨度",
    options=['1mo', '3mo', '6mo', '1y', 'ytd'],
    value='3mo'
)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 刷新全站数据", use_container_width=True):
    st.cache_data.clear()

st.sidebar.info("💡 提示：图表支持鼠标悬停、缩放和拖拽交互。")

# ==========================================
# 3. 核心功能函数
# ==========================================

# --- A. 获取新闻 ---
@st.cache_data(ttl=600)
def get_news_data():
    try:
        # 尝试获取东方财富7x24
        df = ak.stock_telegraph_em()
        return df.rename(columns={'发布时间': 'time', '标题': 'title', '内容': 'content'}), "Real API"
    except:
        # 模拟数据兜底
        mock_data = {
            'time': [datetime.now().strftime("%H:%M"), "10:30", "09:15"],
            'title': ["【模拟】美联储暗示维持利率不变", "【模拟】新能源板块早盘活跃", "【模拟】国际金价小幅回落"],
            'content': ["由于接口访问受限，当前展示为模拟数据。请关注左侧图表功能的实现逻辑。", "...", "..."]
        }
        return pd.DataFrame(mock_data), "Mock Data"

# --- B. 获取/生成行情数据 ---
@st.cache_data(ttl=3600)
def get_chart_data(symbol, period):
    # 1. 尝试真实请求
    try:
        df = yf.download(symbol, period=period, progress=False)
        
        # 【关键修复】处理 yfinance 可能返回 MultiIndex 的问题
        # 如果列是多层级的 (例如: ('Close', 'AAPL'))，只取 'Close' 这一层
        if isinstance(df.columns, pd.MultiIndex):
            df = df.xs(symbol, level=1, axis=1)
            
        if not df.empty:
            return df, "真实市场数据 (Yahoo Finance)"
    except Exception as e:
        print(f"API Error: {e}")
        pass
    
    # 2. 失败则生成模拟数据
    dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(100)) 
    
    mock_df = pd.DataFrame(index=dates)
    mock_df['Close'] = prices
    mock_df['Open'] = prices + np.random.randn(100) * 0.5
    mock_df['High'] = mock_df[['Open', 'Close']].max(axis=1) + np.random.rand(100)
    mock_df['Low'] = mock_df[['Open', 'Close']].min(axis=1) - np.random.rand(100)
    
    return mock_df, "模拟演示数据 (API限流保护模式)"

# ==========================================
# 4. 页面主布局
# ==========================================

st.title("🚀 FinTech 全球市场看板")
st.markdown("Designed by **产品经理求职者** | Python Streamlit Demo")

tab1, tab2, tab3 = st.tabs(["📊 市场行情 (Charts)", "📰 7x24 快讯 (News)", "ℹ️ 关于项目"])

# --- Tab 1: 交互式图表 ---
with tab1:
    st.subheader(f"{selected_asset_label} - 走势分析")
    
    with st.spinner('正在量化分析引擎计算中...'):
        chart_df, data_source = get_chart_data(selected_symbol, time_period)
    
    # 【关键修复】数据清洗与类型转换
    try:
        # 1. 获取 Close 列
        close_series = chart_df['Close']
        
        # 2. 确保它是简单的 Series，不是 DataFrame
        if isinstance(close_series, pd.DataFrame):
            close_series = close_series.iloc[:, 0]
            
        # 3. 强制转换为纯 Python float (解决 TypeError 核心步骤)
        last_close = float(close_series.iloc[-1])
        prev_close = float(close_series.iloc[-2])
        
        change = last_close - prev_close
        pct_change = (change / prev_close) * 100
        
    except Exception as e:
        # 如果数据异常，显示默认值防止报错
        st.error(f"数据解析异常: {e}")
        last_close, change, pct_change = 0.0, 0.0, 0.0

    # 展示指标
    col1, col2, col3 = st.columns(3)
    col1.metric("最新收盘价", f"${last_close:.2f}", f"{change:.2f} ({pct_change:.2f}%)")
    col2.metric("数据来源", data_source, delta_color="off")
    col3.metric("当前周期", time_period)

    # 绘制 K线图
    fig = go.Figure(data=[go.Candlestick(x=chart_df.index,
                open=chart_df['Open'],
                high=chart_df['High'],
                low=chart_df['Low'],
                close=chart_df['Close'],
                name='K线')])

    fig.update_layout(
        title=f'{selected_symbol} 价格走势',
        xaxis_title='日期',
        yaxis_title='价格',
        height=500,
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 2: 新闻快讯 ---
with tab2:
    st.header("全球金融快讯流")
    news_df, news_source = get_news_data()
    
    if "Mock" in news_source:
        st.warning("⚠️ 实时接口繁忙，已切换至历史/模拟数据演示。")
        
    for index, row in news_df.head(15).iterrows():
        with st.container():
            col_time, col_content = st.columns([1, 5])
            with col_time:
                st.markdown(f"**{row.get('time', '刚刚')}**")
            with col_content:
                st.markdown(f"##### {row.get('title', '快讯')}")
                st.markdown(f"{row.get('content', '')}")
            st.divider()

# --- Tab 3: 关于 ---
with tab3:
    st.markdown("""
    ### 📌 项目设计思路 (STAR法则应用)
    *   **Situation (背景):** 面试中不仅要展示原型图，更需要展示**技术落地能力**与**MVP思维**。
    *   **Task (任务):** 搭建一个集成了**数据获取(API)、数据清洗(Pandas)、可视化(Plotly)**的综合看板。
    *   **Action (行动):** 
        1. 使用 `yfinance` 构建多源数据层，并处理了**MultiIndex数据结构清洗**问题。
        2. 设计**降级熔断机制**：当API不稳定时，自动生成模拟数据。
        3. 采用**模块化布局**，将高频(看行情)与低频(看新闻)需求分离。
    *   **Result (结果):** 0成本上线，具备完整的用户交互体验。
    """)
