import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ==============================================================================
# 办公室复印纸采购优化大作业 - 第二阶段：可视化
# 学号：20250001 (请自行修改)
# 姓名：张三 (请自行修改)
# 脚本说明：基于Matplotlib和Seaborn的图表绘制
# ==============================================================================

# 设置中文字体支持（适配Mac和Windows系统）
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False # 解决负号显示问题

def visualize_data(input_file="20250001_result.csv"):
    if not os.path.exists(input_file):
        print(f"[错误] 找不到数据文件: {input_file}，请先运行预处理脚本。")
        return

    df = pd.read_csv(input_file)
    df['日期'] = pd.to_datetime(df['日期'])
    
    print("开始生成数据可视化图表...")
    
    # 图表1：不同品牌A4纸价格时间趋势折线图
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x='日期', y='真实平台价格', hue='品牌', alpha=0.7)
    plt.title('过去一年各品牌A4纸价格走势')
    plt.xlabel('日期')
    plt.ylabel('价格 (元/箱)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('chart1_price_trend.png', dpi=300)
    print("已生成: chart1_price_trend.png (价格趋势图)")
    
    # 图表2：各品牌平均价格对比柱状图
    plt.figure(figsize=(10, 6))
    avg_price = df.groupby('品牌')['真实平台价格'].mean().sort_values(ascending=False).reset_index()
    sns.barplot(data=avg_price, x='品牌', y='真实平台价格', palette='viridis')
    plt.title('各品牌A4复印纸平均价格对比')
    plt.xlabel('品牌')
    plt.ylabel('平均价格 (元/箱)')
    # 在柱子上显示具体数值
    for i, v in enumerate(avg_price['真实平台价格']):
        plt.text(i, v + 1, f'{v:.2f}', ha='center', va='bottom')
    plt.tight_layout()
    plt.savefig('chart2_brand_avg_price.png', dpi=300)
    print("已生成: chart2_brand_avg_price.png (平均价格柱状图)")
    
    # 图表3：价格分布箱线图（发现离群点与价格带）
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x='品牌', y='真实平台价格', palette='Set2')
    plt.title('各品牌A4纸价格分布特征(箱线图)')
    plt.xlabel('品牌')
    plt.ylabel('价格 (元/箱)')
    plt.tight_layout()
    plt.savefig('chart3_price_boxplot.png', dpi=300)
    print("已生成: chart3_price_boxplot.png (价格箱线图)")
    
    # 图表4：月份-价格热力图（用于寻找采购淡旺季）
    df['月份'] = df['日期'].dt.month
    monthly_price = df.pivot_table(index='品牌', columns='月份', values='真实平台价格', aggfunc='mean')
    plt.figure(figsize=(12, 6))
    sns.heatmap(monthly_price, annot=True, fmt=".1f", cmap="YlGnBu")
    plt.title('各品牌每月平均价格热力图')
    plt.tight_layout()
    plt.savefig('chart4_monthly_heatmap.png', dpi=300)
    print("已生成: chart4_monthly_heatmap.png (月度价格热力图)")
    
    print("所有可视化图表已生成完毕。")

if __name__ == "__main__":
    visualize_data()
