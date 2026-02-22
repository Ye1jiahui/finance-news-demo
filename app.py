import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
import akshare as ak
from datetime import datetime, timedelta

# ==========================================
# 1. 页面基础配置 (Page Config)
# ==========================================
st.set_page_config(
    page_title="FinTech Pro | 金融市场看板",
    page_icon="📊",
    layout="wide", # 开启宽屏模式，图表更好看
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. 侧边栏配置 (Sidebar Configuration)
# ==========================================
st.sidebar.title("🎛️ 控制台")

# 功能 1: 市场标的选择
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

# 功能 2: 时间周期
time_period = st.sidebar.select_slider(
    "时间跨度",
    options=['1mo', '3mo', '6mo', '1y', 'ytd'],
    value='3mo'
)

# 功能 3: 刷新
st.sidebar.markdown("---")
if st.sidebar.button("🔄 刷新全站数据", use_container_width=True):
    st.cache_data.clear()

st.sidebar.info("💡 提示：图表支持鼠标悬停、缩放和拖拽交互。")

# ==========================================
# 3. 核心功能函数 (Data & Logic)
# ==========================================

# --- A. 获取新闻 (带降级策略) ---
@st.cache_data(ttl=600)
def get_news_data():
    try:
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

# --- B. 获取/生成行情数据 (核心亮点) ---
@st.cache_data(ttl=3600)
def get_chart_data(symbol, period):
    # 1. 尝试真实请求
    try:
        # 使用 yfinance 获取真实数据
        df = yf.download(symbol, period=period, progress=False)
        if not df.empty:
            return df, "真实市场数据 (Yahoo Finance)"
    except Exception:
        pass
    
    # 2. 失败则生成“高保真”模拟数据 (这是PM的Plan B)
    # 生成逼真的随机游走数据
    dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
    np.random.seed(42) # 固定种子，保证每次刷新图形一致
    # 模拟价格波动
    prices = 100 + np.cumsum(np.random.randn(100)) 
    
    # 构造OHLC数据 (开盘/最高/最低/收盘)
    mock_df = pd.DataFrame(index=dates)
    mock_df['Close'] = prices
    mock_df['Open'] = prices + np.random.randn(100) * 0.5
    mock_df['High'] = mock_df[['Open', 'Close']].max(axis=1) + np.random.rand(100)
    mock_df['Low'] = mock_df[['Open', 'Close']].min(axis=1) - np.random.rand(100)
    mock_df['Volume'] = np.random.randint(1000, 10000, size=100)
    
    return mock_df, "模拟演示数据 (API限流保护模式)"

# ==========================================
# 4. 页面主布局 (Main Layout)
# ==========================================

st.title("🚀 FinTech 全球市场看板")
st.markdown("Designed by **产品经理求职者** | Python Streamlit Demo")

# 使用 Tabs 分割不同业务模块
tab1, tab2, tab3 = st.tabs(["📊 市场行情 (Charts)", "📰 7x24 快讯 (News)", "ℹ️ 关于项目"])

# --- Tab 1: 交互式图表 (重头戏) ---
with tab1:
    st.subheader(f"{selected_asset_label} - 走势分析")
    
    # 获取数据
    with st.spinner('正在量化分析引擎计算中...'):
        chart_df, data_source = get_chart_data(selected_symbol, time_period)
    
    # 展示当前价格指标 (KPI Card)
    last_close = chart_df['Close'].iloc[-1]
    prev_close = chart_df['Close'].iloc[-2]
    change = last_close - prev_close
    pct_change = (change / prev_close) * 100
    
    # 使用列布局展示指标
    col1, col2, col3 = st.columns(3)
    col1.metric("最新收盘价", f"${last_close:.2f}", f"{change:.2f} ({pct_change:.2f}%)")
    col2.metric("数据来源", data_source, delta_color="off")
    col3.metric("当前周期", time_period)

    # 绘制 K线图 (使用 Plotly)
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
        template="plotly_white" # 简洁风格
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"注：当前展示数据源为 [{data_source}]。若为模拟数据，仅供UI交互演示。")

# --- Tab 2: 新闻快讯 ---
with tab2:
    st.header("全球金融快讯流")
    news_df, news_source = get_news_data()
    
    if "Mock" in news_source:
        st.warning("⚠️ 实时接口繁忙，已切换至历史/模拟数据演示。")
        
    for index, row in news_df.head(15).iterrows():
        # 简单的样式处理
        with st.container():
            col_time, col_content = st.columns([1, 5])
            with col_time:
                st.markdown(f"**{row.get('time', '刚刚')}**")
            with col_content:
                st.markdown(f"##### {row.get('title', '快讯')}")
                st.markdown(f"{row.get('content', '')}")
            st.divider()

# --- Tab 3: 关于 (展示产品思维) ---
with tab3:
    st.markdown("""
    ### 📌 项目设计思路 (STAR法则应用)
    
    *   **Situation (背景):** 面试中不仅要展示原型图，更需要展示**技术落地能力**与**MVP思维**。
    *   **Task (任务):** 搭建一个集成了**数据获取(API)、数据清洗(Pandas)、可视化(Plotly)与前端交互(Streamlit)**的综合看板。
    *   **Action (行动):** 
        1. 使用 `yfinance` 与 `akshare` 构建多源数据层。
        2. 设计**降级熔断机制**：当API不稳定时，自动生成符合正态分布的模拟数据，保证演示不挂。
        3. 采用**模块化布局**，将高频(看行情)与低频(看新闻)需求分离。
    *   **Result (结果):** 0成本上线，支持移动端访问，具备完整的用户交互体验。
    """)
