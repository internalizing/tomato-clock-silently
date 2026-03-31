import tkinter as tk
from PIL import Image, ImageTk
import time
import threading
import os

# ============================================
专注时长分钟 = 25  # 测试时改成 5
# ============================================

代码目录 = os.path.dirname(os.path.abspath(__file__))

class 番茄钟悬浮窗:
    def __init__(self):
        self.窗口 = tk.Tk()
        self.状态 = "待机"
        self.剩余秒数 = 专注时长分钟 * 60
        self.计时器线程 = None
        self.拖动起始X = 0
        self.拖动起始Y = 0
        self.正在拖动 = False
        self.单击时间 = 0
        
        self.窗口.overrideredirect(True)
        self.窗口.attributes('-topmost', True)
        
        # 获取屏幕尺寸
        self.屏幕宽 = self.窗口.winfo_screenwidth()
        self.屏幕高 = self.窗口.winfo_screenheight()
        任务栏高度 = 40
        边距 = 20
        
        # 待机状态：右下角，完全可见
        初始x = self.屏幕宽 - 100 - 边距
        初始y = self.屏幕高 - 100 - 任务栏高度 - 边距
        self.窗口.geometry(f"100x100+{初始x}+{初始y}")
        
        self.图片路径 = {
            "待机": os.path.join(代码目录, "tomato_idle.png"),
            "专注": os.path.join(代码目录, "tomato_cut.png"),
        }
        self.当前图片 = None
        
        self.主框架 = tk.Frame(self.窗口, bg='white')
        self.主框架.pack(fill='both', expand=True)
        
        self.左面板 = tk.Frame(self.主框架, bg='white', width=100, height=100)
        self.左面板.pack(side='left')
        self.左面板.pack_propagate(False)
        
        self.画布 = tk.Canvas(self.左面板, width=100, height=100, 
                              highlightthickness=0, bg='white')
        self.画布.pack()
        
        self.右面板 = tk.Frame(self.主框架, bg='white', width=80, height=100)
        
        self.窗口.attributes('-transparentcolor', 'white')
        
        self.画布.bind("<ButtonPress-1>", self.鼠标按下)
        self.画布.bind("<B1-Motion>", self.鼠标移动)
        self.画布.bind("<ButtonRelease-1>", self.鼠标释放)
        self.画布.bind("<Double-Button-1>", self.双击开始)
        self.画布.bind("<Button-3>", self.右键关闭)
        
        self.时间标签 = tk.Label(self.右面板, text=f"{专注时长分钟}:00", 
                                font=("Arial", 16, "bold"),
                                bg='white', fg='#FF6B6B')
        
        # 暂停按钮 - 两条竖线
        self.暂停画布 = tk.Canvas(self.右面板, width=20, height=20,
                                  highlightthickness=0, bg='white')
        self.暂停画布.create_rectangle(6, 4, 10, 16, fill='#FF6B6B', outline='')
        self.暂停画布.create_rectangle(12, 4, 16, 16, fill='#FF6B6B', outline='')
        self.暂停画布.bind("<Button-1>", lambda e: self.点击暂停())
        
        # 继续按钮 - 等边三角形比例
        self.继续画布 = tk.Canvas(self.右面板, width=20, height=20,
                                  highlightthickness=0, bg='white')
        # 等边三角形：底边20，高度约17，比例协调
        self.继续画布.create_polygon([(2, 2), (2, 18), (18, 10)], 
                                       fill='#4ECDC4', outline='')
        self.继续画布.bind("<Button-1>", lambda e: self.点击继续())
        
        self.结束按钮 = tk.Label(self.右面板, text="end", 
                                font=("Brush Script MT", 12, "bold"),
                                bg='white', fg='#4ECDC4',
                                cursor='hand2')
        self.结束按钮.bind("<Button-1>", lambda e: self.点击结束())
        
        self.加载图片("待机")
    
    def 加载图片(self, 状态):
        路径 = self.图片路径.get(状态)
        try:
            if os.path.exists(路径):
                图片 = Image.open(路径)
                if 图片.mode != 'RGBA':
                    图片 = 图片.convert('RGBA')
                图片 = 图片.resize((80, 80), Image.Resampling.LANCZOS)
                self.当前图片 = ImageTk.PhotoImage(图片)
                self.画布.delete("all")
                self.画布.create_image(50, 50, image=self.当前图片, anchor='center')
            else:
                raise FileNotFoundError()
        except Exception as e:
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
        
        # 边界检测：确保窗口不完全移出屏幕
        窗口宽 = self.窗口.winfo_width()
        窗口高 = self.窗口.winfo_height()
        
        # 左边界：至少保留20px在屏幕内
        if x < -窗口宽 + 20:
            x = -窗口宽 + 20
        # 右边界
        if x > self.屏幕宽 - 20:
            x = self.屏幕宽 - 20
        # 上边界
        if y < -窗口高 + 20:
            y = -窗口高 + 20
        # 下边界（考虑任务栏）
        if y > self.屏幕高 - 20:
            y = self.屏幕高 - 20
        
        self.窗口.geometry(f"+{x}+{y}")
    
    def 鼠标释放(self, event):
        pass
    
    def 双击开始(self, event):
        if self.正在拖动 or self.状态 != "待机":
            return
        self.状态 = "专注"
        self.剩余秒数 = 专注时长分钟 * 60
        self.加载图片("专注")
        self.展开专注界面()
        self.计时器线程 = threading.Thread(target=self.计时循环, daemon=True)
        self.计时器线程.start()
    
    def 展开专注界面(self):
        """展开界面，自动调整位置确保不超出屏幕"""
        当前x = self.窗口.winfo_x()
        当前y = self.窗口.winfo_y()
        
        # 窗口变宽为180
        新宽度 = 180
        新高度 = 100
        
        # 检测右侧是否超出屏幕
        if 当前x + 新宽度 > self.屏幕宽 - 20:
            # 如果靠右，向左展开
            新x = self.屏幕宽 - 新宽度 - 20
        else:
            新x = 当前x
        
        # 检测底部是否超出
        if 当前y + 新高度 > self.屏幕高 - 20:
            新y = self.屏幕高 - 新高度 - 20
        else:
            新y = 当前y
        
        self.窗口.geometry(f"{新宽度}x{新高度}+{新x}+{新y}")
        self.右面板.pack(side='left')
        self.时间标签.config(text=f"{专注时长分钟}:00")
        self.时间标签.place(relx=0.5, rely=0.35, anchor='center')
        self.暂停画布.place(relx=0.5, rely=0.65, anchor='center')
        self.继续画布.place_forget()
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
        self.暂停画布.place_forget()
        self.继续画布.place(relx=0.3, rely=0.65, anchor='center')
        self.结束按钮.place(relx=0.7, rely=0.65, anchor='center')
    
    def 点击继续(self):
        if self.状态 != "暂停":
            return
        self.状态 = "专注"
        self.继续画布.place_forget()
        self.结束按钮.place_forget()
        self.暂停画布.place(relx=0.5, rely=0.65, anchor='center')
    
    def 点击结束(self):
        self.状态 = "待机"
        self.剩余秒数 = 专注时长分钟 * 60
        self.右面板.pack_forget()
        self.时间标签.place_forget()
        self.暂停画布.place_forget()
        self.继续画布.place_forget()
        self.结束按钮.place_forget()
        
        当前x = self.窗口.winfo_x()
        当前y = self.窗口.winfo_y()
        
        # 结束计时后，确保番茄完全可见
        if 当前x + 100 > self.屏幕宽 - 20:
            当前x = self.屏幕宽 - 100 - 20
        if 当前y + 100 > self.屏幕高 - 20:
            当前y = self.屏幕高 - 100 - 20
        
        self.窗口.geometry(f"100x100+{当前x}+{当前y}")
        self.画布.coords("all", 50, 50)
        self.加载图片("待机")
    
    def 计时完成(self):
        self.状态 = "完成"
        self.暂停画布.place_forget()
        self.时间标签.config(text="完成！", fg='#4ECDC4')
    
    def 右键关闭(self, event):
        self.窗口.destroy()
    
    def 运行(self):
        self.窗口.mainloop()

if __name__ == "__main__":
    app = 番茄钟悬浮窗()
    app.运行()