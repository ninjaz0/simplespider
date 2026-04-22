import pandas as pd
import numpy as np
import os

# ==============================================================================
# 办公室复印纸采购优化大作业 - 第一阶段：数据预处理
# 学号：20250001 (请自行修改)
# 姓名：张三 (请自行修改)
# 脚本说明：清洗爬取的原始数据，处理缺失值、异常值，并计算基础统计量
# ==============================================================================

def clean_and_preprocess(input_file="raw_scraped_data.csv", output_file="20250001_result.csv"):
    if not os.path.exists(input_file):
        print(f"[错误] 找不到输入文件: {input_file}")
        return None
        
    print(f"正在加载原始数据: {input_file}")
    df = pd.read_csv(input_file)
    
    print(f"原始数据总行数: {len(df)}")
    
    # 1. 处理缺失值：价格列为空的行直接丢弃
    missing_count = df['真实平台价格'].isnull().sum()
    print(f"发现缺失价格数据: {missing_count} 条，正在清除...")
    df = df.dropna(subset=['真实平台价格'])
    
    # 2. 格式统一与转换：确保价格是浮点数
    # 有时候爬虫爬下来带有人民币符号如 '¥99.0'
    if df['真实平台价格'].dtype == object:
        df['真实平台价格'] = df['真实平台价格'].astype(str).str.replace('¥', '').str.replace(',', '').astype(float)
    else:
        df['真实平台价格'] = df['真实平台价格'].astype(float)
        
    # 3. 处理异常值：价格为0或极高的视为异常
    # 假设正常的A4 70g一箱（5包）价格在 10 到 200 之间
    abnormal_mask = (df['真实平台价格'] < 10) | (df['真实平台价格'] > 200)
    abnormal_count = abnormal_mask.sum()
    print(f"发现异常价格数据(低于10或高于200): {abnormal_count} 条，正在过滤...")
    df = df[~abnormal_mask]
    
    # 4. 时间格式标准化
    df['日期'] = pd.to_datetime(df['日期']).dt.strftime('%Y-%m-%d')
    
    print(f"清洗后数据总行数: {len(df)}")
    
    # 保存清洗后的数据，这就是PK赛需要提交的结果
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"[成功] 清洗完成，已保存至 {output_file}")
    
    return df

def basic_statistics(df):
    """进行基础的统计分析并打印"""
    print("\n" + "="*40)
    print("基础统计分析报告")
    print("="*40)
    
    # 计算各品牌的平均价格、最高价、最低价
    stats = df.groupby('品牌')['真实平台价格'].agg(['mean', 'max', 'min', 'std', 'count']).round(2)
    stats.columns = ['平均价格', '最高价', '最低价', '价格标准差', '样本数量']
    
    print("\n【各品牌价格统计】")
    print(stats)
    
    # 找出整体最便宜的Top 5记录
    print("\n【最便宜的5条购买记录】")
    cheapest = df.nsmallest(5, '真实平台价格')[['日期', '品牌', '真实平台价格', '商品来源网站']]
    print(cheapest)

if __name__ == "__main__":
    cleaned_df = clean_and_preprocess()
    if cleaned_df is not None:
        basic_statistics(cleaned_df)
