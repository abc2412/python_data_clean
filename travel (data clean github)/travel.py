import pandas as pd
import numpy as np
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

# ==================== 1. 读取数据 ====================
# 假设你的文件名为 "tourism_data.xlsx"，请根据实际修改文件名字
df = pd.read_excel("travel_dataset.xlsx")

# 保存原始行数
original_rows = len(df)

print("原始数据形状:", df.shape)
print("原始列名:", df.columns)

# ==================== 2. 查看基本信息 ====================
print("\n数据类型预览")
print(df.dtypes)
print("\n前5行数据")
print(df.head())

# ==================== 3. 删除完全重复的行 ====================
before_dedup = len(df)
df = df.drop_duplicates()
after_dedup = len(df)
duplicate_removed = before_dedup - after_dedup
print(f"\n删除重复行: {duplicate_removed} 行")

# ==================== 4. 处理缺失值 ====================
# 4.1 数值型字段用中位数填充，类别型字段用众数填充
# 游客年龄: 用中位数填充
if "游客年龄" in df.columns:
    median_age = df["游客年龄"].median()
    df["游客年龄"] = df["游客年龄"].fillna(median_age)

# 消费金额: 用中位数填充
if "消费金额" in df.columns:
    median_amount = df["消费金额"].median()
    df["消费金额"] = df["消费金额"].fillna(median_amount)

# 景点门票: 用中位数填充（如果是数值）
if "景点门票" in df.columns:
    # 先尝试转为数值，无法转换的变成NaN
    df["景点门票"] = pd.to_numeric(df["景点门票"], errors="coerce")
    median_ticket = df["景点门票"].median()
    df["景点门票"] = df["景点门票"].fillna(median_ticket)

# 景点类型: 用众数填充
if "景点类型" in df.columns:
    modes=df["景点类型"].mode()
    if not modes.empty:
        mode_type=modes[0]
    else:
        mode_type="未知"
    df["景点类型"] = df["景点类型"].fillna(mode_type)

# 游玩日期: 如果为空，删除该行（日期太重要，不随意填充）
if "游玩日期" in df.columns:
    before_date = len(df)
    df = df.dropna(subset=["游玩日期"])
    date_removed = before_date - len(df)
    print(f"删除游玩日期为空的行: {date_removed} 行")

# 年份、月份: 如果能从游玩日期提取，就填充；否则用众数
if "游玩日期" in df.columns:
    # 确保游玩日期是datetime类型
    df["游玩日期"] = pd.to_datetime(df["游玩日期"], errors="coerce")
    # 如果年份或月份缺失，尝试从日期提取
    if "年份" in df.columns:
        df["年份"] = df["年份"].fillna(df["游玩日期"].dt.year)
        # 还剩下的缺失值用众数填充
        if df["年份"].isna().any():
            mode_year = df["年份"].mode()[0] if not df["年份"].mode().empty else 2023
            df["年份"] = df["年份"].fillna(mode_year)
    if "月份" in df.columns:
        df["月份"] = df["月份"].fillna(df["游玩日期"].dt.month)
        if df["月份"].isna().any():
            mode_month = df["月份"].mode()[0] if not df["月份"].mode().empty else 6
            df["月份"] = df["月份"].fillna(mode_month)

# ==================== 5. 数据类型转换与格式统一 ====================
# 游客年龄: 转为整数，并限制在0-120之间
if "游客年龄" in df.columns:
    df["游客年龄"] = pd.to_numeric(df["游客年龄"], errors="coerce")
    # 异常值: 年龄<0 或 >120 设为中位数
    median_age = df["游客年龄"].median()
    # 逻辑：保留 0<=年龄<=120 的数据，其他的（不满足条件的）全部变成 median_age
    df["游客年龄"] = df["游客年龄"].where(
        (df["游客年龄"] >= 0) & (df["游客年龄"] <= 120),
        median_age
    )
    df["游客年龄"] = df["游客年龄"].astype(int)

# 消费金额: 转为浮点数，负数设为0
if "消费金额" in df.columns:
    df["消费金额"] = pd.to_numeric(df["消费金额"], errors="coerce")
    df.loc[df["消费金额"] < 0, "消费金额"] = 0.0
    df["消费金额"] = df["消费金额"].fillna(0.0)

# 景点门票: 转为浮点数，负数设为0
if "景点门票" in df.columns:
    df["景点门票"] = pd.to_numeric(df["景点门票"], errors="coerce")
    df.loc[df["景点门票"] < 0, "景点门票"] = 0.0
    df["景点门票"] = df["景点门票"].fillna(0.0)

# 景点类型: 去除首尾空格，统一为首字母大写
if "景点类型" in df.columns:
    df["景点类型"] = df["景点类型"].astype(str).str.strip()
    df["景点类型"] = df["景点类型"].str.title()
    # 将空字符串或"nan"替换为"未知"
    df["景点类型"] = df["景点类型"].replace(["", "nan", "None"], "未知")

# 游玩日期: 已经是datetime，只保留有效日期
if "游玩日期" in df.columns:
    df = df.dropna(subset=["游玩日期"])
    # 将日期格式统一为 YYYY-MM-DD
    df["游玩日期"] = df["游玩日期"].dt.strftime("%Y-%m-%d")

# 年份、月份: 转为整数
if "年份" in df.columns:
    df["年份"] = pd.to_numeric(df["年份"], errors="coerce").fillna(2023).astype(int)
if "月份" in df.columns:
    df["月份"] = pd.to_numeric(df["月份"], errors="coerce").fillna(6).astype(int)
    # 逻辑：保留 1<=月份<=12 的数据，其他的（不满足条件的）全部变成 6
    df["月份"] = df["月份"].where(
        (df["月份"] >= 1) & (df["月份"] <= 12),
        6
    )


# ==================== 6. 再次删除因清洗产生的重复行 ====================
before_dedup2 = len(df)
df = df.drop_duplicates()
duplicate_removed2 = before_dedup2 - len(df)
if duplicate_removed2 > 0:
    print(f"清洗后再次删除重复行: {duplicate_removed2} 行")

# ==================== 7. 生成清洗报告 ====================
final_rows = len(df)
print("\n========== 清洗报告 ==========")
print(f"原始总行数: {original_rows}")
print(f"删除重复行(第一次): {duplicate_removed}")
print(f"删除游玩日期为空的行: {date_removed if 'date_removed' in dir() else 0}")
print(f"清洗后再次删除重复行: {duplicate_removed2 if duplicate_removed2 else 0}")
print(f"最终有效行数: {final_rows}")
print(f"总共删除行数: {original_rows - final_rows}")

# 统计各列缺失值（清洗后）
print("\n--- 清洗后各列缺失值统计 ---")
print(df.isnull().sum())

# 数值列的基本统计
numeric_cols = ["游客年龄", "消费金额", "景点门票"]
existing_numeric = [col for col in numeric_cols if col in df.columns]
if existing_numeric:
    print("\n--- 数值列描述性统计 ---")
    print(df[existing_numeric].describe())

# ==================== 8. 输出清洗后的数据 ====================
output_file = "cleaned_tourism_data.csv"
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print(f"\n清洗完成！已保存至: {output_file}")

# 1. 读取清洗后的数据文件
df = pd.read_csv("cleaned_tourism_data.csv")

# 2. 将“游玩日期”这一列转换成真正的日期类型（原来可能是字符串）
df["游玩日期"] = pd.to_datetime(df["游玩日期"])

# 3. 从日期中提取“年份-月份”，例如“2023-01”
#    这样我们可以按月份进行分组
df["年月"] = df["游玩日期"].dt.to_period("M")

# 4. 按“年月”分组，计算每个月的消费金额总和
monthly_amount = df.groupby("年月")["人均日消费"].sum()

# 5. 准备画图：创建画布，设置大小（宽度10英寸，高度5英寸）
plt.figure(figsize=(10, 5))

# 6. 绘制折线图
#    monthly_amount.index 是每个月份（如2023-01），转换成字符串是为了显示更清晰
#    monthly_amount.values 是每个月的消费总额
# 7. 绘制折线图（修改部分）
# 这里我们直接传入日期对象，而不是字符串，这样 Matplotlib 才能智能识别时间
plt.plot(monthly_amount.index.to_timestamp(), monthly_amount.values,
         marker="o", linestyle="-", color="b")

# 8. 设置 X 轴刻度间隔（核心修改）
ax = plt.gca()  # 获取当前坐标轴

# 设置每隔 3 个月显示一个刻度（你可以把 3 改成 6 或 12 来调整疏密）
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))

# 设置日期的显示格式为 "年-月"
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

# 自动旋转日期标签，防止重叠
plt.gcf().autofmt_xdate()

# 9. 添加标题和坐标轴标签（保持原样或微调）
plt.title("每月人均日消费趋势", fontsize=14)
plt.xlabel("日期", fontsize=12)
plt.ylabel("人均日消费 (元)", fontsize=12)

# 10. 显示网格
plt.grid(True, linestyle="--", alpha=0.6)
plt.show()