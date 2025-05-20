from pynput import mouse
import time
import tkinter as tk
from tkinter import ttk
from collections import deque

# 全局变量
last_time = None
polling_rates = deque(maxlen=10)  # 存储最近10次测量
accumulated_rates = []  # 在计算平均值前累积测量数据
max_polling_rate = 0
is_measuring = False
is_dynamic = False
listener = None
last_polling_rate = None  # 用于比较轮询率的变化

# 鼠标移动时触发的函数
def on_move(x, y):
    global last_time, polling_rates, accumulated_rates, max_polling_rate, is_dynamic, last_polling_rate

    current_time = time.perf_counter()

    if last_time is not None:
        delta_time = current_time - last_time

        if delta_time > 0.001:  # 忽略时间间隔小于1毫秒的事件
            polling_rate = 1 / delta_time
            polling_rate = min(polling_rate, 8000)  # 现代鼠标上限设为8000Hz

            # 累积测量值
            accumulated_rates.append(polling_rate)

            # 每累积10次测量值进行一次平均计算
            if len(accumulated_rates) >= 10:
                avg_polling_rate = sum(accumulated_rates) / len(accumulated_rates)
                accumulated_rates.clear()  # 清空累积数据

                polling_rates.append(avg_polling_rate)

                # 更新界面
                if avg_polling_rate > max_polling_rate:
                    max_polling_rate = avg_polling_rate
                    max_polling_label.config(text=f"最高记录：{max_polling_rate:.2f} Hz")

                polling_rate_label.config(text=f"平均轮询率：{avg_polling_rate:.2f} Hz")

                # 检测是否为动态轮询率
                if len(set([round(rate) for rate in polling_rates])) > 2:
                    is_dynamic = True
                else:
                    is_dynamic = False
                dynamic_label.config(text=f"动态轮询率：{'是' if is_dynamic else '否'}")

                # 更新轮询率列表
                update_polling_rate_list()

    last_time = current_time

# 更新轮询率列表的函数
def update_polling_rate_list():
    rate_list_text = "\n".join([f"{rate:.2f} Hz" for rate in polling_rates])
    polling_rate_list_text.delete(1.0, tk.END)  # 更新前清空文本框内容
    polling_rate_list_text.insert(tk.END, f"最近测量值：\n{rate_list_text}")

# 启动/停止测量的函数
def toggle_measurement():
    global listener, is_measuring, max_polling_rate, polling_rates, accumulated_rates, is_dynamic

    if not is_measuring:
        is_measuring = True
        start_button.config(text="停止测量")
        polling_rate_label.config(text="移动鼠标中...")
        max_polling_label.config(text="最高记录：0.00 Hz")
        dynamic_label.config(text="动态轮询率：未检测到")
        max_polling_rate = 0
        polling_rates.clear()
        accumulated_rates.clear()
        is_dynamic = False

        listener = mouse.Listener(on_move=on_move)
        listener.start()
    else:
        is_measuring = False
        start_button.config(text="开始测量")
        polling_rate_label.config(text="测量已停止")

        if listener:
            listener.stop()
            listener = None

# 优雅关闭应用程序的函数
def close_app():
    global listener
    if listener:
        listener.stop()
    root.destroy()

# 配置图形界面
root = tk.Tk()
root.title("鼠标轮询率测试器")
root.geometry("300x400")
 
# 修改以下值可调整颜色
background_color = "#1E1E1E"  # 窗口背景色
text_color = "#ffffff"  # 文本颜色
title_color = "#00ff00"  # 标题颜色
button_color = "#4C566A"  # 按钮颜色
button_text_color = "#2E3440"  # 按钮文字颜色

root.configure(bg=background_color)

# 应用程序标题
title_label = ttk.Label(
    root, text="LH - 鼠标轮询率测试器",
    font=("Arial", 14, "bold"), background=background_color, foreground=title_color
)
title_label.pack(pady=10)

polling_rate_label = ttk.Label(
    root, text="点击'开始测量'以启动",
    font=("Arial", 12), background=background_color, foreground=text_color
)
polling_rate_label.pack(pady=10)

max_polling_label = ttk.Label(
    root, text="最高记录：0.00 Hz",
    font=("Arial", 12), background=background_color, foreground=text_color
)
max_polling_label.pack(pady=10)

dynamic_label = ttk.Label(
    root, text="动态轮询率：未检测到",
    font=("Arial", 12), background=background_color, foreground=text_color
)
dynamic_label.pack(pady=10)

# 测量结果框架
frame_list = ttk.Frame(root, padding="10")
frame_list.pack(pady=10, fill=tk.X)

# 显示测量结果的文本框
polling_rate_list_text = tk.Text(frame_list, height=6, width=30, wrap=tk.WORD, bg=background_color, fg=text_color, font=("Arial", 10))
polling_rate_list_text.pack(fill=tk.BOTH, expand=True)

# 自定义按钮样式
style = ttk.Style()
style.configure(
    "Custom.TButton",
    font=("Arial", 12),
    padding=6,
    background=button_color,
    foreground=button_text_color
)
style.map(
    "Custom.TButton",
    background=[("active", "#5E81AC")],
    relief=[("pressed", "sunken"), ("!pressed", "raised")]
)

# 按钮框架
button_frame = tk.Frame(root, bg=background_color)
button_frame.pack(pady=10)

# 水平排列的按钮组
start_button = ttk.Button(button_frame, text="开始测量", command=toggle_measurement, style="Custom.TButton")
start_button.pack(side=tk.LEFT, padx=5)

exit_button = ttk.Button(button_frame, text="退出", command=close_app, style="Custom.TButton")
exit_button.pack(side=tk.LEFT, padx=5)

root.protocol("WM_DELETE_WINDOW", close_app)
root.mainloop()