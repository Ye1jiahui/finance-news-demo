import streamlit as st
import akshare as ak
import pandas as pd
from datetime import datetime
import random

# 1. 页面配置
st.set_page_config(page_title="金融市场要闻 | 产品Demo", page_icon="📈", layout="centered")

# 2. 标题区
st.title("📈 全球金融市场 7x24h 快讯")
st.markdown("""
**产品经理面试 Demo** | 数据来源：AKShare / 模拟数据流  
*注：因云端服务器IP限制，若实时接口超时，将自动切换为模拟数据演示UI布局。*
""")

# 3. 获取数据函数 (带降级策略)
@st.cache_data(ttl=600)
def get_news():
    # --- 方案 A: 尝试东方财富接口 (通常最稳定) ---
    try:
        df = ak.stock_telegraph_em()
        # 统一字段名，方便后面展示
        df = df.rename(columns={'发布时间': 'time', '标题': 'title', '内容': 'content'})
        return df, "API (东方财富)"
    except:
        pass # 如果失败，静默进入方案 B

    # --- 方案 B: 尝试新浪财经接口 ---
    try:
        df = ak.stock_info_global_futu()
        df = df.rename(columns={'发布时间': 'time', '内容': 'content'})
        # 新浪接口有时没有标题，用内容截取
        df['title'] = df['content'].apply(lambda x: x[:30] + '...' if x else '快讯')
        return df, "API (新浪/富途)"
    except:
        pass # 如果还失败，进入方案 C

    # --- 方案 C: 模拟数据 (保底策略 - 只有PM才会想到的兜底方案) ---
    # 这是为了给面试官展示 UI 效果，防止页面白屏
    mock_data = {
        'time': [datetime.now().strftime("%H:%M:%S"), "10:30:00", "09:45:15", "09:15:00"],
        'title': [
            "【模拟数据】美联储暗示暂停加息，纳指期货盘前走高",
            "【模拟数据】A股三大指数集体高开，新能源板块领涨",
            "【模拟数据】国际金价突破2000美元关口，创近期新高",
            "【模拟数据】某知名科技巨头发布新款AI芯片，算力提升30%"
        ],
        'content': [
            "这是为了在接口被封锁时，依然能向面试官展示产品UI布局而设计的模拟数据。",
            "展示数据字段：标题高亮，内容详细展开，时间戳清晰可见。",
            "作为PM，考虑到边缘情况（Edge Case）是必须的职业素养。",
            "点击刷新按钮，可以尝试重新请求真实接口。"
        ]
    }
    return pd.DataFrame(mock_data), "模拟演示模式 (Mock Data)"

# 4. 侧边栏
st.sidebar.header("🔍 配置")
if st.sidebar.button("🔄 强制刷新"):
    st.cache_data.clear()

# 5. 数据展示
with st.spinner('正在连接金融数据中心...'):
    df, source_type = get_news()

# 展示当前数据源状态
if "模拟" in source_type:
    st.warning(f"当前数据源：{source_type} —— 真实接口暂时拥堵，已自动切换为演示模式。")
else:
    st.success(f"当前数据源：{source_type} —— 数据实时更新中。")

# 渲染列表
if df is not None and not df.empty:
    for index, row in df.head(20).iterrows():
        time_str = str(row.get('time', '刚刚'))
        title = str(row.get('title', '快讯'))
        content = str(row.get('content', title))
        
        with st.container():
            st.markdown(f"### 🕒 {time_str} | {title}")
            st.info(content)
            st.divider()

# 6. 页脚
st.markdown("---")
st.markdown("Designed by **[叶佳辉]**")
