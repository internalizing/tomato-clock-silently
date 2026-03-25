import tkinter as tk
from tkinter import font
import time
import threading

class 番茄钟悬浮窗:
    def __init__(self):
        self.窗口 = tk.Tk()
        self.状态 = "待机"  # 待机/专注/休息
        
        # 无边框、置顶、透明背景
        self.窗口.overrideredirect(True)
        self.窗口.attributes('-topmost', True)
        self.窗口.attributes('-transparentcolor', 'white')
        
        # 窗口位置和大小
        self.窗口.geometry("120x120+1500+100")  # 右下角附近
        
        # 番茄图案（先用emoji代替，后期换图片）
        self.标签 = tk.Label(
            self.窗口, 
            text="🍅", 
            font=("Segoe UI Emoji", 60),
            bg='white',
            cursor='hand2'
        )
        self.标签.pack(expand=True)
        
        # 点击事件
        self.标签.bind("<Button-1>", self.点击处理)
        
        # 可拖动
        self.标签.bind("<ButtonPress-1>", self.开始拖动)
        self.标签.bind("<B1-Motion>", self.拖动)
        
    def 点击处理(self, event):
        if self.状态 == "待机":
            self.开始专注()
    
    def 开始专注(self):
        self.状态 = "专注"
        self.标签.config(text="🍅💧")  # 横截面占位符
        # 启动计时线程
        threading.Thread(target=self.专注计时, daemon=True).start()
    
    def 专注计时(self):
        for i in range(25 * 60):
            if self.状态 != "专注":
                return
            time.sleep(1)
        # 25分钟结束
        self.窗口.after(0, self.专注结束)
    
    def 专注结束(self):
        print("专注完成！该弹鲜花动画了")
        self.状态 = "休息"
        # 这里接第2阶段：弹鲜花、变番茄小人
    
    def 开始拖动(self, event):
        self.拖动起始X = event.x
        self.拖动起始Y = event.y
    
    def 拖动(self, event):
        x = self.窗口.winfo_x() + event.x - self.拖动起始X
        y = self.窗口.winfo_y() + event.y - self.拖动起始Y
        self.窗口.geometry(f"+{x}+{y}")
    
    def 运行(self):
        self.窗口.mainloop()

if __name__ == "__main__":
    app = 番茄钟悬浮窗()
    app.运行()