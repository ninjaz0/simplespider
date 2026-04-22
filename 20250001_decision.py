import sys
from datetime import datetime

# ==============================================================================
# 办公室复印纸采购优化大作业 - 第三阶段：模拟实战PK
# 学号：20250001 (请自行修改)
# 姓名：张三 (请自行修改)
# 脚本说明：遵循所有业务约束的交互式采购决策程序
# ==============================================================================

class PurchaseDecisionSystem:
    def __init__(self):
        self.budget = 20000.0
        self.storage = 40
        self.max_storage = 150
        # 初始时间定为当年的4月30日
        self.current_date = datetime.strptime("4.30", "%m.%d")
        self.year = 2025 # 假设起始年份
        
        # 消耗规则
        self.consumption_rules = {
            1: 10, 2: 10, 3: 20, 4: 20, 5: 20, 6: 20,
            7: 10, 8: 10, 9: 20, 10: 20, 11: 20, 12: 20
        }
        
        # 计算全年总需求量(从5月到次年4月)
        # 以及次年4.30要求的20箱库存，预留出总的安全库存下限
        
        # 启动时，需要直接扣除5月1日的消耗，并输出
        self._advance_time_to(datetime.strptime("5.1", "%m.%d"))
        print(f"5.1,{self.storage}")

    def _get_consumption_for_month(self, month):
        return self.consumption_rules.get(month, 20)

    def _advance_time_to(self, target_date):
        """将时间推进到目标日期，并扣除期间每个月1号的消耗"""
        # 如果是跨年，我们需要处理年份
        if target_date.month < self.current_date.month and target_date.month < 5:
            target_year = self.year + 1
        else:
            target_year = self.year
            
        target_full_date = datetime(target_year, target_date.month, target_date.day)
        current_full_date = datetime(self.year, self.current_date.month, self.current_date.day)
        
        # 逐月推进，检查每个月的1号是否在时间区间内
        # 例如从 4.30 推进到 6.20，需要触发 5.1 和 6.1 的扣减
        check_date = current_full_date
        while True:
            # 找到下一个月的1号
            if check_date.month == 12:
                next_month_1st = datetime(check_date.year + 1, 1, 1)
            else:
                next_month_1st = datetime(check_date.year, check_date.month + 1, 1)
                
            if next_month_1st <= target_full_date:
                # 触发扣减
                consume = self._get_consumption_for_month(next_month_1st.month)
                self.storage -= consume
                if self.storage < 0:
                    print(f"[致命错误] {next_month_1st.month}月1日库存核减后为负数({self.storage})！断货！")
                check_date = next_month_1st
            else:
                break
                
        self.current_date = target_date
        self.year = target_year

    def _calculate_future_needs(self):
        """计算为了熬到次年5月（含最后的20箱保底），还需要多少箱"""
        needs = 0
        current_month = self.current_date.month
        current_year = self.year
        
        end_date = datetime(2025 + 1, 5, 1) # 我们必须熬过次年4月，并余留20箱给5月
        
        check_date = datetime(current_year, current_month, 1)
        if self.current_date.day == 1:
            # 如果当天是1号，说明当月已经扣过了，从下个月开始算未来的纯新增需求
            pass
        
        # 逐月累加未来还要扣除的量
        temp_date = check_date
        while True:
            if temp_date.month == 12:
                next_month = datetime(temp_date.year + 1, 1, 1)
            else:
                next_month = datetime(temp_date.year, temp_date.month + 1, 1)
                
            if next_month < end_date:
                needs += self._get_consumption_for_month(next_month.month)
                temp_date = next_month
            else:
                break
                
        # 加上明年5月的保底20箱
        needs += 20
        
        # 减去当前库存，就是纯粹还需要购买的箱数
        required_purchases = max(0, needs - self.storage)
        return required_purchases

    def make_decision(self, month_day_str, price, brand):
        try:
            target_date = datetime.strptime(month_day_str, "%m.%d")
        except ValueError:
            print("日期格式错误，应为 m.d，例如 6.20")
            return
            
        # 1. 推进时间并核减库存
        self._advance_time_to(target_date)
        
        # 2. 策略计算购买量
        # 我们需要保留足够的钱来支付未来的必须消耗。假设未来极高价格为100元。
        future_boxes_needed = self._calculate_future_needs()
        
        buy_num = 0
        
        # 可用空间
        available_space = self.max_storage - self.storage
        
        if available_space > 0:
            if price <= 80:
                # 极佳价格，买爆！只要预算够
                affordable = int(self.budget // price)
                buy_num = min(available_space, affordable)
            elif price <= 85:
                # 好价格，买一部分，但也看看预算
                affordable = int(self.budget // price)
                # 留点钱防身
                safe_buy = min(available_space, affordable, 80) 
                buy_num = safe_buy
            elif price <= 92:
                # 一般价格，看库存是否告急。如果库存熬不过未来2个月，买一点
                months_to_look = 2
                look_needs = 0
                temp_m = self.current_date.month
                for _ in range(months_to_look):
                    temp_m = temp_m + 1 if temp_m < 12 else 1
                    look_needs += self._get_consumption_for_month(temp_m)
                
                if self.storage < look_needs:
                    buy_num = min(available_space, look_needs - self.storage + 20)
            else:
                # 价格太贵，除非马上要断货，否则不买
                if self.storage < 20: # 危险水位
                    buy_num = min(available_space, 20)
                    
        # 最终安全校验：不能超过预算
        if buy_num * price > self.budget:
            buy_num = int(self.budget // price)
            
        # 3. 结算
        if buy_num > 0:
            cost = buy_num * price
            self.budget -= cost
            self.storage += buy_num
            
        # 4. 格式化输出: month.day,price,PurchaseNum,StorageNum,BudgeLeft
        output = f"{month_day_str},{price},{buy_num},{self.storage},{round(self.budget, 2)}"
        print(output)


def main():
    print("=====================================================")
    print("进入模拟实战PK阶段 - 请依次输入问卷调查的数据")
    print("输入格式：month.day,price,brand (例如: 6.20,82,齐心白云海)")
    print("输入 'exit' 或 'quit' 退出程序")
    print("=====================================================")
    
    system = PurchaseDecisionSystem()
    
    while True:
        try:
            user_input = input("请输入: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['exit', 'quit']:
                break
                
            parts = user_input.split(',')
            if len(parts) != 3:
                print("输入格式错误，请严格按照 month.day,price,brand 输入")
                continue
                
            month_day = parts[0].strip()
            price = float(parts[1].strip())
            brand = parts[2].strip()
            
            system.make_decision(month_day, price, brand)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"发生错误: {e}")

if __name__ == "__main__":
    main()
