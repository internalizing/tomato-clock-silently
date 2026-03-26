import tkinter as tk
from PIL import Image, ImageTk
import time
import threading
import os

# 调试信息
代码目录 = os.path.dirname(os.path.abspath(__file__))
print("=" * 50)
print("代码所在目录:", 代码目录)
print("=" * 50)

class 番茄钟悬浮窗:
    def __init__(self):
        self.窗口 = tk.Tk()
        self.状态 = "待机"
        self.剩余秒数 = 25 * 60
        self.计时器线程 = None
        self.拖动起始X = 0
        self.拖动起始Y = 0
        self.正在拖动 = False
        self.单击时间 = 0
        
        # 窗口设置
        self.窗口.overrideredirect(True)
        self.窗口.attributes('-topmost', True)
        
        # 屏幕尺寸计算位置
        屏幕宽 = self.窗口.winfo_screenwidth()
        屏幕高 = self.窗口.winfo_screenheight()
        任务栏高度 = 40
        边距 = 20
        
        初始x = 屏幕宽 - 100 - 边距
        初始y = 屏幕高 - 100 - 任务栏高度 - 边距
        self.窗口.geometry(f"100x100+{初始x}+{初始y}")
        
        # 图片路径
        self.图片路径 = {
            "待机": os.path.join(代码目录, "tomato_idle.png"),
            "专注": os.path.join(代码目录, "tomato_cut.png"),
        }
        self.当前图片 = None
        
        # 画布
        self.画布 = tk.Canvas(self.窗口, width=100, height=100, 
                              highlightthickness=0, bg='white')
        self.画布.pack()
        self.窗口.attributes('-transparentcolor', 'white')
        
        # 绑定事件
        self.画布.bind("<ButtonPress-1>", self.鼠标按下)
        self.画布.bind("<B1-Motion>", self.鼠标移动)
        self.画布.bind("<ButtonRelease-1>", self.鼠标释放)
        self.画布.bind("<Double-Button-1>", self.双击开始)
        self.画布.bind("<Button-3>", self.右键关闭)
        
        # UI元素
        self.时间标签 = tk.Label(self.窗口, text="25:00", 
                                font=("Arial", 12, "bold"),
                                bg='white', fg='#FF6B6B')
        
        self.暂停按钮 = tk.Button(self.窗口, text="⏸", font=("Arial", 10),
                                 bg='white', relief='flat',
                                 command=self.点击暂停)
        
        self.继续按钮 = tk.Button(self.窗口, text="▶", font=("Arial", 10),
                                 bg='#4ECDC4', fg='white', relief='flat',
                                 command=self.点击继续)
        
        self.结束按钮 = tk.Button(self.窗口, text="■", font=("Arial", 15),
                                 bg='#FF6B6B', fg='white', relief='flat',
                                 command=self.点击结束)
        
        # 加载初始图片
        self.加载图片("待机")
    
    def 加载图片(self, 状态):
        """加载PNG图片"""
        路径 = self.图片路径.get(状态)
        print(f"加载: {路径}")
        
        try:
            if os.path.exists(路径):
                图片 = Image.open(路径)
                if 图片.mode != 'RGBA':
                    图片 = 图片.convert('RGBA')
                图片 = 图片.resize((80, 80), Image.Resampling.LANCZOS)
                self.当前图片 = ImageTk.PhotoImage(图片)
                self.画布.delete("all")
                self.画布.create_image(50, 50, image=self.当前图片, anchor='center')
                print("  ✓ 图片加载成功")
            else:
                raise FileNotFoundError()
        except Exception as e:
            print(f"  ✗ 失败: {e}")
            self.画布.delete("all")
            emoji = "🍅" if 状态 == "待机" else "🍅💧"
            self.画布.create_text(50, 50, text=emoji, font=("Segoe UI Emoji", 40))
    
    def 鼠标按下(self, event):
        self.拖动起始X = event.x_root - self.窗口.winfo_x()
        self.拖动起始Y = event.y_root - self.窗口.winfo_y()
        self.正在拖动 = False
        self.单击时间 = time.time()
        self.窗口.lift()
        self.窗口.attributes('-topmost', True)
    
    def 鼠标移动(self, event):
        self.正在拖动 = True
        x = event.x_root - self.拖动起始X
        y = event.y_root - self.拖动起始Y
        self.窗口.geometry(f"+{x}+{y}")
    
    def 鼠标释放(self, event):
        pass
    
    def 双击开始(self, event):
        if self.正在拖动 or self.状态 != "待机":
            return
        self.状态 = "专注"
        self.剩余秒数 = 25 * 60
        self.加载图片("专注")
        self.展开专注界面()
        self.计时器线程 = threading.Thread(target=self.计时循环, daemon=True)
        self.计时器线程.start()
    
    def 展开专注界面(self):
        当前x = self.窗口.winfo_x()
        当前y = self.窗口.winfo_y()
        self.窗口.geometry(f"100x130+{当前x}+{当前y}")
        self.画布.coords("all", 50, 35)
        self.时间标签.config(text="25:00")
        self.时间标签.place(x=50, y=75, anchor='center')
        self.暂停按钮.place(x=50, y=105, anchor='center')
        self.继续按钮.place_forget()
        self.结束按钮.place_forget()
    
    def 计时循环(self):
        while self.剩余秒数 > 0 and self.状态 in ["专注", "暂停"]:
            if self.状态 == "专注":
                self.更新显示()
                self.剩余秒数 -= 1
                time.sleep(1)
            else:
                time.sleep(0.1)
        if self.剩余秒数 <= 0 and self.状态 == "专注":
            self.窗口.after(0, self.计时完成)
    
    def 更新显示(self):
        分 = self.剩余秒数 // 60
        秒 = self.剩余秒数 % 60
        self.窗口.after(0, lambda: self.时间标签.config(text=f"{分:02d}:{秒:02d}"))
    
    def 点击暂停(self):
        if self.状态 != "专注":
            return
        self.状态 = "暂停"
        self.暂停按钮.place_forget()
        self.继续按钮.place(x=35, y=105, anchor='center')
        self.结束按钮.place(x=65, y=105, anchor='center')
    
    def 点击继续(self):
        if self.状态 != "暂停":
            return
        self.状态 = "专注"
        self.继续按钮.place_forget()
        self.结束按钮.place_forget()
        self.暂停按钮.place(x=50, y=105, anchor='center')
    
    def 点击结束(self):
        """暂停时点击结束：放弃本次专注"""
        print("=== 点击结束被调用 ===")
        self.状态 = "待机"
        self.剩余秒数 = 25 * 60
        
        self.时间标签.place_forget()
        self.暂停按钮.place_forget()
        self.继续按钮.place_forget()
        self.结束按钮.place_forget()
        
        当前x = self.窗口.winfo_x()
        当前y = self.窗口.winfo_y()
        self.窗口.geometry(f"100x100+{当前x}+{当前y}")
        self.画布.coords("all", 50, 50)
        self.加载图片("待机")
        print("=== 结束完成，恢复待机 ===")
    
    def 计时完成(self):
        self.状态 = "完成"
        self.暂停按钮.place_forget()
        self.时间标签.config(text="完成！", fg='#4ECDC4')
    
    def 右键关闭(self, event):
        self.窗口.destroy()
    
    def 运行(self):
        self.窗口.mainloop()

if __name__ == "__main__":
    app = 番茄钟悬浮窗()
    app.运行()