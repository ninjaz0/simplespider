import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error
from datetime import datetime, timedelta
import os

# ==============================================================================
# 办公室复印纸采购优化大作业 - 第二阶段：科学建模
# 学号：20250001 (请自行修改)
# 姓名：张三 (请自行修改)
# 脚本说明：基于Scikit-learn构建时间序列趋势预测模型
# ==============================================================================

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

def build_and_evaluate_model(input_file="20250001_result.csv"):
    if not os.path.exists(input_file):
        print(f"[错误] 找不到数据文件: {input_file}，请先运行预处理脚本。")
        return

    df = pd.read_csv(input_file)
    df['日期'] = pd.to_datetime(df['日期'])
    
    # 我们以"得力"品牌为例进行建模训练展示
    target_brand = "得力"
    brand_df = df[df['品牌'] == target_brand].copy()
    brand_df = brand_df.sort_values('日期')
    
    # 特征工程：将日期转换为数字特征（例如距离起始日期的天数），并提取月份作为周期特征
    min_date = brand_df['日期'].min()
    brand_df['days_since_start'] = (brand_df['日期'] - min_date).dt.days
    brand_df['month'] = brand_df['日期'].dt.month
    
    # 按照时间顺序划分训练集（前80%）和测试集（后20%）
    train_size = int(len(brand_df) * 0.8)
    train_df = brand_df.iloc[:train_size]
    test_df = brand_df.iloc[train_size:]
    
    X_train = train_df[['days_since_start', 'month']]
    y_train = train_df['真实平台价格']
    X_test = test_df[['days_since_start', 'month']]
    y_test = test_df['真实平台价格']
    
    # 构建并训练线性回归模型
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # 预测
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    # 评估模型
    rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    mae = mean_absolute_error(y_test, y_pred_test)
    
    print("\n" + "="*40)
    print(f"【{target_brand}】品牌价格预测模型评估结果")
    print(f"测试集 RMSE: {rmse:.2f}")
    print(f"测试集 MAE: {mae:.2f}")
    print("="*40 + "\n")
    
    # 可视化真实价格与预测价格的拟合效果
    plt.figure(figsize=(12, 6))
    plt.plot(train_df['日期'], y_train, label='训练集真实价格', alpha=0.6)
    plt.plot(test_df['日期'], y_test, label='测试集真实价格', color='blue', alpha=0.6)
    plt.plot(test_df['日期'], y_pred_test, label='测试集预测价格', color='red', linestyle='--')
    plt.title(f'{target_brand}品牌复印纸价格预测拟合图')
    plt.xlabel('日期')
    plt.ylabel('价格')
    plt.legend()
    plt.tight_layout()
    plt.savefig('chart5_model_fitting.png', dpi=300)
    print("已生成: chart5_model_fitting.png (模型拟合效果图)")
    
    return model, min_date

def generate_pk_predictions(model, min_date, df):
    """
    为限时PK赛生成未来一段时间内所有商品的预测结果文件。
    要求格式：商品ID、日期、预测价格、价格趋势（+涨/-跌）、品牌、型号、数据获取时间
    """
    print("正在生成PK赛要求的结果文件...")
    
    predictions = []
    
    # 获取唯一的商品信息组合
    unique_items = df[['商品ID', '品牌', '型号']].drop_duplicates()
    
    # 预测未来30天（5月）
    future_start = datetime(2026, 5, 1)
    for i in range(30):
        target_date = future_start + timedelta(days=i)
        days_since_start = (target_date - min_date).days
        month = target_date.month
        
        for _, item in unique_items.iterrows():
            # 使用训练好的模型预测
            pred_price = model.predict([[days_since_start, month]])[0]
            
            # 添加一点基于品牌的偏移（因为模型是用“得力”训练的，作为简单基准扩展到其他品牌）
            # 真实场景中，应当为每个品牌独立训练模型。这里为了演示PK输出格式进行了简化处理。
            if item['品牌'] == '齐心': pred_price -= 10
            if item['品牌'] == '天章': pred_price -= 15
            if item['品牌'] == '誉品': pred_price -= 18
            if item['品牌'] == '晨光': pred_price -= 5
            
            # 简单判断趋势（比如判断该月是否是传统涨价月，或基于前一天价格预测对比）
            trend = "+涨" if month in [2, 9] else "-跌"
            
            predictions.append({
                "商品ID": item['商品ID'],
                "日期": target_date.strftime('%Y-%m-%d'),
                "预测价格": round(pred_price, 2),
                "价格趋势": trend,
                "品牌": item['品牌'],
                "型号": item['型号'],
                "数据获取时间": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
    pred_df = pd.DataFrame(predictions)
    pred_df.to_csv("20250001_predict.csv", index=False, encoding='utf-8-sig')
    print("[成功] 预测结果已保存至 20250001_predict.csv")

if __name__ == "__main__":
    df = pd.read_csv("20250001_result.csv")
    df['日期'] = pd.to_datetime(df['日期'])
    
    trained_model, base_date = build_and_evaluate_model()
    if trained_model:
        generate_pk_predictions(trained_model, base_date, df)
