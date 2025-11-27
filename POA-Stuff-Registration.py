import tkinter as tk
from tkinter import messagebox
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageTk, ImageGrab
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("警告：未安装PIL库，保存图片功能将不可用")
    print("请运行: pip install pillow")

class AttributeAllocator:
    def __init__(self, root):
        self.root = root
        self.root.title("P.O.A.职员能力登记")
        self.root.geometry("800x800")  # 增加窗口大小以容纳子数值
        self.root.resizable(False, False)
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 初始状态
        self.parent_confirmed = False
        
        # 初始值设置
        self.total_points = 27
        self.attributes = {
            "力量": {
                "value": 10, 
                "deficit_history": [],
                "sub_attributes": {
                    "攻击": {"value": 0, "deficit_history": []},
                    "防御": {"value": 0, "deficit_history": []},
                    "负重": {"value": 0, "deficit_history": []},
                    "突围": {"value": 0, "deficit_history": []}
                }
            },
            "体质": {
                "value": 10, 
                "deficit_history": [],
                "sub_attributes": {
                    "生命值": {"value": 0, "deficit_history": []},
                    "恢复力": {"value": 0, "deficit_history": []},
                    "毒抗": {"value": 0, "deficit_history": []},
                    "法抗": {"value": 0, "deficit_history": []}
                }
            },
            "魅力": {
                "value": 10, 
                "deficit_history": [],
                "sub_attributes": {
                    "领导": {"value": 0, "deficit_history": []},
                    "游说": {"value": 0, "deficit_history": []},
                    "欺瞒": {"value": 0, "deficit_history": []},
                    "恫吓": {"value": 0, "deficit_history": []}
                }
            },
            "敏捷": {
                "value": 10, 
                "deficit_history": [],
                "sub_attributes": {
                    "精准": {"value": 0, "deficit_history": []},
                    "闪避": {"value": 0, "deficit_history": []},
                    "巧手": {"value": 0, "deficit_history": []},
                    "潜行": {"value": 0, "deficit_history": []}
                }
            },
            "智力": {
                "value": 10, 
                "deficit_history": [],
                "sub_attributes": {
                    "魔法": {"value": 0, "deficit_history": []},
                    "调查": {"value": 0, "deficit_history": []},
                    "战略": {"value": 0, "deficit_history": []},
                    "分析": {"value": 0, "deficit_history": []}
                }
            },
            "感知": {
                "value": 10, 
                "deficit_history": [],
                "sub_attributes": {
                    "洞察": {"value": 0, "deficit_history": []},
                    "医药": {"value": 0, "deficit_history": []},
                    "直觉": {"value": 0, "deficit_history": []},
                    "警觉": {"value": 0, "deficit_history": []}
                }
            }
        }
        
        # 创建界面
        self.create_widgets()
        self.update_display()
    
    def create_widgets(self):
        # 标题
        title_label = tk.Label(self.root, text="属性分配系统", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 总点数显示
        points_frame = tk.Frame(self.root)
        points_frame.pack(pady=10)
        
        tk.Label(points_frame, text="剩余点数:", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        self.points_label = tk.Label(points_frame, text=str(self.total_points), 
                                   font=("Arial", 14, "bold"), fg="blue")
        self.points_label.pack(side=tk.LEFT, padx=5)
        
        # 状态显示
        self.status_label = tk.Label(self.root, text="当前分配母属性", font=("Arial", 10), fg="green")
        self.status_label.pack(pady=5)
        
        # 创建两列属性框架
        columns_frame = tk.Frame(self.root)
        columns_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # 左列
        left_frame = tk.Frame(columns_frame)
        left_frame.pack(side=tk.LEFT, padx=20, fill=tk.BOTH, expand=True)
        
        # 右列
        right_frame = tk.Frame(columns_frame)
        right_frame.pack(side=tk.RIGHT, padx=20, fill=tk.BOTH, expand=True)
        
        # 为每个属性创建控件
        self.attribute_widgets = {}
        attribute_names = list(self.attributes.keys())
        
        for i, attr_name in enumerate(attribute_names):
            # 决定放在左列还是右列
            if i < 3:
                parent = left_frame
            else:
                parent = right_frame
                
            self.create_attribute_widget(parent, attr_name)
        
        # 按钮框架
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=15)
        
        # 确认按钮
        self.confirm_btn = tk.Button(button_frame, text="确认母属性分配", command=self.confirm_parent_allocation,
                                   bg="orange", fg="white", font=("Arial", 12), width=15)
        self.confirm_btn.pack(side=tk.LEFT, padx=10)
        
        # 重置按钮 (初始隐藏)
        self.reset_btn = tk.Button(button_frame, text="重置所有属性", command=self.reset_allocation,
                                 bg="red", fg="white", font=("Arial", 12), width=15)
        # 初始隐藏重置按钮
        self.reset_btn.pack_forget()
        
        # 保存按钮（只在有PIL时启用）
        self.save_btn = tk.Button(button_frame, text="保存为图片", command=self.save_as_image,
                                bg="green", fg="white", font=("Arial", 12), width=15)
        self.save_btn.pack(side=tk.LEFT, padx=10)
        
        if not HAS_PIL:
            self.save_btn.config(state=tk.DISABLED, text="保存 (需Pillow)")
        
        # 退出按钮
        quit_btn = tk.Button(button_frame, text="退出程序", command=self.on_closing,
                           bg="gray", fg="white", font=("Arial", 10), width=10)
        quit_btn.pack(side=tk.LEFT, padx=10)
    
    def create_attribute_widget(self, parent, attr_name):
        # 主属性框架
        main_frame = tk.Frame(parent, relief="groove", bd=2, padx=5, pady=5)
        main_frame.pack(pady=8, fill=tk.X)
        
        # 属性名称和值框架
        header_frame = tk.Frame(main_frame)
        header_frame.pack(fill=tk.X)
        
        # 属性名称
        name_label = tk.Label(header_frame, text=attr_name, width=8, font=("Arial", 11, "bold"))
        name_label.pack(side=tk.LEFT)
        
        # 属性值显示
        value_var = tk.StringVar()
        value_label = tk.Label(header_frame, textvariable=value_var, width=4, 
                             font=("Arial", 11, "bold"), relief="sunken", bg="lightgray")
        value_label.pack(side=tk.LEFT, padx=5)
        
        # 按钮框架
        btn_frame = tk.Frame(header_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        # 减号按钮
        minus_btn = tk.Button(btn_frame, text="-", width=3, height=1,
                            command=lambda: self.decrement_attribute(attr_name))
        minus_btn.pack(side=tk.LEFT, padx=2)
        
        # 加号按钮
        plus_btn = tk.Button(btn_frame, text="+", width=3, height=1,
                           command=lambda: self.increment_attribute(attr_name))
        plus_btn.pack(side=tk.LEFT, padx=2)
        
        # 子属性框架 (初始隐藏)
        sub_frame = tk.Frame(main_frame)
        # 初始时不显示子属性
        sub_frame.pack_forget()
        
        # 为每个子属性创建控件
        sub_widgets = {}
        for sub_name in self.attributes[attr_name]["sub_attributes"].keys():
            sub_frame_row = tk.Frame(sub_frame)
            sub_frame_row.pack(fill=tk.X, pady=2)
            
            # 子属性名称
            sub_name_label = tk.Label(sub_frame_row, text=sub_name, width=8, font=("Arial", 9))
            sub_name_label.pack(side=tk.LEFT)
            
            # 子属性值显示
            sub_value_var = tk.StringVar()
            sub_value_label = tk.Label(sub_frame_row, textvariable=sub_value_var, width=4, 
                                     font=("Arial", 9), relief="sunken")
            sub_value_label.pack(side=tk.LEFT, padx=5)
            
            # 子属性按钮框架
            sub_btn_frame = tk.Frame(sub_frame_row)
            sub_btn_frame.pack(side=tk.RIGHT)
            
            # 子属性减号按钮 (初始隐藏)
            sub_minus_btn = tk.Button(sub_btn_frame, text="-", width=3, height=1,
                                    command=lambda an=attr_name, sn=sub_name: self.decrement_sub_attribute(an, sn))
            sub_minus_btn.pack(side=tk.LEFT, padx=1)
            sub_minus_btn.pack_forget()  # 初始隐藏
            
            # 子属性加号按钮 (初始隐藏)
            sub_plus_btn = tk.Button(sub_btn_frame, text="+", width=3, height=1,
                                   command=lambda an=attr_name, sn=sub_name: self.increment_sub_attribute(an, sn))
            sub_plus_btn.pack(side=tk.LEFT, padx=1)
            sub_plus_btn.pack_forget()  # 初始隐藏
            
            sub_widgets[sub_name] = {
                "value_var": sub_value_var,
                "minus_btn": sub_minus_btn,
                "plus_btn": sub_plus_btn,
                "frame": sub_frame_row
            }
        
        # 存储控件引用
        self.attribute_widgets[attr_name] = {
            "value_var": value_var,
            "minus_btn": minus_btn,
            "plus_btn": plus_btn,
            "sub_frame": sub_frame,
            "sub_widgets": sub_widgets
        }
    
    def increment_attribute(self, attr_name):
        if self.parent_confirmed:
            return
            
        if self.total_points <= 0:
            return
            
        attr = self.attributes[attr_name]
        current_value = attr["value"]
        
        # 如果当前值小于10且有失衡调换记录
        if current_value < 10 and attr["deficit_history"]:
            # 获取最近一次的减少量
            last_deficit = attr["deficit_history"][-1]
            # 计算实际恢复量（不超过10）
            actual_restore = min(last_deficit, 10 - current_value)
            
            # 恢复数值
            attr["value"] += actual_restore
            
            # 更新失衡记录
            if actual_restore == last_deficit:
                # 完全恢复了这次减少
                attr["deficit_history"].pop()
            else:
                # 部分恢复，更新记录
                attr["deficit_history"][-1] = last_deficit - actual_restore
            
            # 消耗1点
            self.total_points -= 1
        else:
            # 正常加点
            attr["value"] += 1
            self.total_points -= 1
        
        self.update_display()
    
    def decrement_attribute(self, attr_name):
        if self.parent_confirmed:
            return
            
        attr = self.attributes[attr_name]
        current_value = attr["value"]
        
        if current_value <= 10:
            # 特殊递减规则
            decrement_amount = 2 + len(attr["deficit_history"])
                
            if current_value > decrement_amount:
                attr["value"] -= decrement_amount
                # 记录这次失衡减少的量到历史列表
                attr["deficit_history"].append(decrement_amount)
                self.total_points += 1
            else:
                messagebox.showwarning("警告", f"{attr_name} 无法再减少了！")
                return
        else:
            # 正常递减
            attr["value"] -= 1
            self.total_points += 1
        
        self.update_display()
    
    def increment_sub_attribute(self, attr_name, sub_name):
        if not self.parent_confirmed:
            return
            
        attr = self.attributes[attr_name]
        sub_attr = attr["sub_attributes"][sub_name]
        
        # 计算母属性可分配的总点数 (基础的10 + 分配的点数)
        parent_total = attr["value"]
        
        # 计算已分配的子属性点数总和
        allocated_points = sum(sub["value"] for sub in attr["sub_attributes"].values())
        
        # 检查是否还有可分配的点数
        if allocated_points < parent_total:
            # 正常加点
            sub_attr["value"] += 1
        else:
            messagebox.showwarning("警告", f"{attr_name} 的子属性已分配完所有可用点数！")
            return
        
        self.update_display()
    
    def decrement_sub_attribute(self, attr_name, sub_name):
        if not self.parent_confirmed:
            return
            
        attr = self.attributes[attr_name]
        sub_attr = attr["sub_attributes"][sub_name]
        current_value = sub_attr["value"]
        
        if current_value > 0:
            # 正常递减
            sub_attr["value"] -= 1
        else:
            messagebox.showwarning("警告", f"{attr_name}的{sub_name} 无法再减少了！")
            return
        
        self.update_display()
    
    def confirm_parent_allocation(self):
        if self.total_points > 0:
            result = messagebox.askyesno("确认", f"还有{self.total_points}点未分配，确定要确认母属性分配吗？")
            if not result:
                return
        
        self.parent_confirmed = True
        self.status_label.config(text="当前分配子属性", fg="blue")
        
        # 隐藏母属性的加减按钮
        for attr_name, widgets in self.attribute_widgets.items():
            widgets["minus_btn"].pack_forget()
            widgets["plus_btn"].pack_forget()
            
            # 显示子属性框架
            widgets["sub_frame"].pack(fill=tk.X)
            
            # 显示子属性的加减按钮
            for sub_widgets in widgets["sub_widgets"].values():
                sub_widgets["minus_btn"].pack(side=tk.LEFT, padx=1)
                sub_widgets["plus_btn"].pack(side=tk.LEFT, padx=1)
        
        # 隐藏确认按钮，显示重置按钮
        self.confirm_btn.pack_forget()
        self.reset_btn.pack(side=tk.LEFT, padx=10)
        
        self.update_display()
    
    def reset_allocation(self):
        result = messagebox.askyesno("重置", "确定要重置所有属性吗？这将清除所有分配。")
        if not result:
            return
        
        # 重置状态
        self.parent_confirmed = False
        self.total_points = 27
        
        # 重置所有属性
        for attr_name, attr_data in self.attributes.items():
            attr_data["value"] = 10
            attr_data["deficit_history"] = []
            
            # 重置子属性
            for sub_attr in attr_data["sub_attributes"].values():
                sub_attr["value"] = 0
                sub_attr["deficit_history"] = []
        
        # 更新界面状态
        self.status_label.config(text="当前分配母属性", fg="green")
        
        # 显示母属性的加减按钮
        for attr_name, widgets in self.attribute_widgets.items():
            widgets["minus_btn"].pack(side=tk.LEFT, padx=2)
            widgets["plus_btn"].pack(side=tk.LEFT, padx=2)
            
            # 隐藏子属性框架
            widgets["sub_frame"].pack_forget()
            
            # 隐藏子属性的加减按钮
            for sub_widgets in widgets["sub_widgets"].values():
                sub_widgets["minus_btn"].pack_forget()
                sub_widgets["plus_btn"].pack_forget()
        
        # 显示确认按钮，隐藏重置按钮
        self.reset_btn.pack_forget()
        self.confirm_btn.pack(side=tk.LEFT, padx=10)
        
        self.update_display()
    
    def update_display(self):
        # 更新总点数显示
        self.points_label.config(text=str(self.total_points))
        
        # 更新每个属性的显示和按钮状态
        for attr_name, widgets in self.attribute_widgets.items():
            attr_data = self.attributes[attr_name]
            current_value = attr_data["value"]
            
            # 更新母属性数值显示
            widgets["value_var"].set(str(current_value))
            
            # 更新母属性加号按钮状态
            if self.parent_confirmed:
                widgets["plus_btn"].pack_forget()
            else:
                if self.total_points <= 0:
                    widgets["plus_btn"].pack_forget()
                else:
                    widgets["plus_btn"].pack(side=tk.LEFT, padx=2)
            
            # 更新母属性减号按钮状态
            if self.parent_confirmed:
                widgets["minus_btn"].pack_forget()
            else:
                if current_value <= 10:
                    decrement_amount = 2 + len(attr_data["deficit_history"])
                    if current_value <= decrement_amount:
                        widgets["minus_btn"].config(state=tk.DISABLED)
                    else:
                        widgets["minus_btn"].config(state=tk.NORMAL)
                else:
                    widgets["minus_btn"].config(state=tk.NORMAL)
            
            # 更新子属性显示
            if self.parent_confirmed:
                parent_total = attr_data["value"]
                allocated_points = 0
                
                for sub_name, sub_data in attr_data["sub_attributes"].items():
                    sub_widgets = widgets["sub_widgets"][sub_name]
                    sub_value = sub_data["value"]
                    
                    # 更新子属性数值显示
                    sub_widgets["value_var"].set(str(sub_value))
                    
                    # 累计已分配点数
                    allocated_points += sub_value
                    
                    # 更新子属性按钮状态
                    if sub_value <= 0:
                        sub_widgets["minus_btn"].config(state=tk.DISABLED)
                    else:
                        sub_widgets["minus_btn"].config(state=tk.NORMAL)
                    
                    # 检查是否还能分配子属性点数
                    if allocated_points >= parent_total:
                        sub_widgets["plus_btn"].config(state=tk.DISABLED)
                    else:
                        sub_widgets["plus_btn"].config(state=tk.NORMAL)
    
    def save_as_image(self):
        """将当前界面保存为PNG图片"""
        if not HAS_PIL:
            messagebox.showerror("错误", "请先安装Pillow库：pip install pillow")
            return
        
        try:
            self.root.update()
        
            # 简化截图：直接截取整个屏幕区域
            x = self.root.winfo_rootx()
            y = self.root.winfo_rooty()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
        
            image = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            filename = os.path.join(desktop_path, "attribute_allocation.png")
        
            image.save(filename, "PNG")
            messagebox.showinfo("成功", f"图片已保存到桌面: attribute_allocation.png")
    
        except Exception as e:
            messagebox.showerror("错误", f"保存图片时出错: {str(e)}")
    
    def on_closing(self):
        """处理窗口关闭事件"""
        if messagebox.askokcancel("退出", "确定要退出程序吗？"):
            self.root.destroy()
            sys.exit()

def main():
    try:
        root = tk.Tk()
        app = AttributeAllocator(root)
        root.mainloop()
    except Exception as e:
        print(f"程序运行出错: {e}")
        input("按Enter键退出...")

if __name__ == "__main__":
    main()

    
