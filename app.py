import streamlit as st
import akshare as ak
import pandas as pd
from datetime import datetime

# 1. 页面配置 (PM思维：注重体验，设置标题和宽屏模式)
st.set_page_config(
    page_title="金融市场要闻 | 产品Demo",
    page_icon="📈",
    layout="centered"
)

# 2. 标题区 (展示你的求职意向)
st.title("📈 全球金融市场 7x24h 快讯")
st.markdown("""
**产品经理求职 Demo** | 数据来源：AKShare (开源财经接口)  
*这是一个基于 Python Streamlit 搭建的 MVP，用于展示数据抓取与前端呈现能力。*
""")


# 3. 获取数据函数 (加缓存，防止频繁请求导致页面卡顿)
@st.cache_data(ttl=300)  # 缓存5分钟，模拟真实产品的数据刷新策略
def get_news():
    try:
        # 使用 AKShare 获取新浪财经 7x24 小时直播新闻
        # 接口文档参考：https://akshare.xyz/
        news_df = ak.stock_info_global_futu()
        # 这里为了演示，我们使用富途/新浪的全球快讯接口，或者用 js_news_cctv 等
        # 注意：AKShare接口更新较快，如果报错，可以用备用接口
        # 备用方案：抓取东方财富 7x24
        news_df = ak.stock_telegraph_em()
        return news_df
    except Exception as e:
        return None


# 4. 侧边栏 (模拟产品功能的筛选)
st.sidebar.header("🔍 筛选配置")
display_count = st.sidebar.slider("展示条数", 10, 100, 20)
auto_refresh = st.sidebar.button("🔄 刷新数据")

# 5. 数据展示逻辑
if auto_refresh:
    st.cache_data.clear()

with st.spinner('正在从云端拉取最新财经数据...'):
    df = get_news()

if df is not None and not df.empty:
    # 简单的清洗：通常保留 时间、标题、内容
    # 东方财富接口返回字段通常包含：发布时间, 标题, 内容

    # 遍历展示前 N 条数据
    for index, row in df.head(display_count).iterrows():
        # 样式美化
        with st.container():
            # 这里的字段名需要根据实际接口返回调整，通常是 '发布时间', '标题', '内容'
            # 假设返回字段是 standard 的
            time_str = row.get('发布时间') or row.get('time')
            content = row.get('内容') or row.get('content') or row.get('title')

            st.markdown(f"### 🕒 {time_str}")
            st.info(content)
            st.divider()
else:
    st.error("数据接口暂时繁忙，请稍后刷新。")

# 6. 页脚 (Call to Action - 引导面试官联系你)
st.markdown("---")
st.markdown("Designed by **[你的名字]** | [查看我的在线简历](你的简历链接) | 电话: 138xxxx")
