import tkinter as tk
from tkinter import messagebox, simpledialog
from tkcalendar import Calendar
import os
import datetime
import subprocess
import webbrowser
from blog_icon import iconb64
from PIL import ImageTk
from base64 import b64decode
import shutil

running_processes = {}

def execute_script(script_name, script_path, file_name, button):
    global running_processes
    try:
        button.config(text="Terminate", bg="red", command=lambda: terminate_process(script_name, button))

        command = f"Set-Location '{script_path}'; .\\{file_name}"
        running_process = subprocess.Popen(["pwsh", "-NoLogo", "-Command", command])
        running_processes[script_name] = (running_process, button)

        if script_name == "local":
            show_open_button()

        root.after(100, lambda: check_process(script_name, button))
    except Exception as e:
        print(f"启动 PowerShell 时出错: {e}")

def check_process(script_name, button):
    if script_name in running_processes:
        process, button = running_processes[script_name]
        if process.poll() is None:
            root.after(100, lambda: check_process(script_name, button))
        else:
            restore_button(button, script_name)

def terminate_process(script_name, button):
    if script_name in running_processes:
        process, button = running_processes[script_name]
        os.system(f'taskkill /t /f /pid {process.pid}')
        print(f"{script_name} 已终止。")
        del running_processes[script_name]
    
    restore_button(button, script_name)

def restore_button(button, script_name):
    if button:
        button.config(text=script_name.capitalize(), bg="SystemButtonFace",
                      command=lambda: execute_script(script_name, r"E:\ChenHuaneng\Article\Blogs", f"{script_name}.ps1", button))
    
    if script_name == "local":
        hide_open_button()

def terminate_all_processes():
    global running_processes
    for script_name in list(running_processes.keys()):
        terminate_process(script_name, None)
    print("所有脚本已终止。")

def show_open_button():
    btn_open.pack(side=tk.LEFT, padx=5)

def hide_open_button():
    btn_open.pack_forget()

def open_localhost():
    webbrowser.open("http://localhost:8080")

def on_closing():
    terminate_all_processes()
    root.destroy()
def open_folder(year, month, day):
    # 构建文件夹路径
    folder_path = f"E:\\ChenHuaneng\\Article\\Blogs\\source\\_posts\\{year}\\{month:d}\\{day:d}"
    if os.path.exists(folder_path):
        os.startfile(folder_path)
    else:
        messagebox.showinfo("Info", f"{year}-{month:d}-{day:d} 没有对应的文件夹")

def create_hexo_post(post_name):
    if not post_name:
        print("文章名称为空，操作已取消。")
        return

    try:
        # 获取当前日期
        today = datetime.datetime.today()
        year = today.strftime("%Y")
        month = today.strftime("%m")
        day = today.strftime("%d")

        # 定义文件路径
        base_dir = r"E:\ChenHuaneng\Article\Blogs\source"
        post_dir = os.path.join(base_dir, "_posts", year, month, day)
        img_dir = os.path.join(base_dir, "imgs", "posts", year, month, day)

        # 创建日期文件夹（如果不存在）
        if not os.path.exists(post_dir):
            os.makedirs(post_dir)
            print(f"创建文章文件夹: {post_dir}")
        else:
            print(f"文章文件夹已存在: {post_dir}")

        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
            print(f"创建图片文件夹: {img_dir}")
        else:
            print(f"图片文件夹已存在: {img_dir}")

        # 检查同名文件是否存在
        while True:
            post_filename = f"{year}-{month}-{day}-{post_name}.md"
            new_post_path = os.path.join(post_dir, post_filename)
            new_post_folder_path = os.path.join(post_dir, f"{year}-{month}-{day}-{post_name}")

            if os.path.exists(new_post_path):
                print(f"文件 '{new_post_path}' 已存在，正在打开该文件。请重新输入新的文章名称。")
                open_file(new_post_path)  # 打开已有文件
                post_name = simpledialog.askstring("创建新文章", "文件已存在，请重新输入文章名称:")
                if not post_name:
                    print("操作已取消。")
                    return
            else:
                # 在 Hexo 项目的根目录执行命令
                hexo_root = r"E:\ChenHuaneng\Article\Blogs"
                command = f'cd /d "{hexo_root}" && hexo new post "{post_name}"'
                os.system(command)

                # 检查文件是否已成功创建，并移动文件
                post_path = os.path.join(base_dir, "_posts", post_filename)
                post_folder_path = os.path.join(base_dir, "_posts", f"{year}-{month}-{day}-{post_name}")

                if os.path.exists(post_path):
                    shutil.move(post_path, new_post_path)
                    print(f"文章已创建并移动到: {new_post_path}")
                    modify_markdown_file(new_post_path, post_filename, year, month, day)
                else:
                    print(f"未找到要移动的文章文件: {post_path}")

                # 移动同名文件夹
                if os.path.exists(post_folder_path):
                    shutil.move(post_folder_path, new_post_folder_path)
                    print(f"同名文件夹已移动到: {new_post_folder_path}")
                else:
                    print(f"未找到要移动的文件夹: {post_folder_path}")

                break

        # 自动打开新创建的文件
        open_file(new_post_path)

        # 打开图片和文章所在的文件夹
        open_folder_create(img_dir)
        open_folder_create(post_dir)

    except KeyboardInterrupt:
        print("\n程序已被用户中止。")

def modify_markdown_file(file_path, post_filename, year, month, day):
    """修改生成的 Markdown 文件，更新图片路径和 typora-root-url"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    date_str = f"{year}/{month}/{day}"
    content = content.replace("/imgs/posts/year/month/day/banner.", f"/imgs/posts/{date_str}/banner.")
    file_name_without_extension = post_filename[:-3]
    content = content.replace("[[filename]]", file_name_without_extension)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"已更新 Markdown 文件中的图片路径和 typora-root-url.")

def open_file(file_path):
    """打开指定文件"""
    if os.path.exists(file_path):
        os.startfile(file_path)
        print(f"已打开文件: {file_path}")
    else:
        print(f"文件不存在: {file_path}")

def open_folder_create(folder_path):
    """打开指定文件夹"""
    if os.path.exists(folder_path):
        os.startfile(folder_path)
        print(f"已打开文件夹: {folder_path}")
    else:
        print(f"文件夹不存在: {folder_path}")

def check_dates():
    # 获取当前显示的年份和月份
    month, year = calendar.get_displayed_month()

    # 遍历当月的每一天
    for day in range(1, 32):  # 最多31天
        try:
        # 检查是否为有效日期
            date = datetime.date(year, month, day)
            folder_path = f"E:\\ChenHuaneng\\Article\\Blogs\\source\\_posts\\{year}\\{month:d}\\{day:d}"
            if os.path.exists(folder_path):
                calendar.calevent_create(date, "有文件夹", "exists")  # 添加事件标记
                calendar.tag_config("exists", background="lightgreen")
        except ValueError:
            # 跳过无效日期
            # print("error")
            continue

def on_click(event):
    selected_date = calendar.get_date()
    if selected_date:  # 确保有选中的日期
        year, month, day = map(int, selected_date.split("-"))
        open_folder(year, month, day)

# 窗口居中
def center_window(root, width, height):
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    size = "%dx%d+%d+%d" % (
        width,
        height,
        (screenwidth - width) / 2,
        (screenheight - height) / 2,
    )
    root.geometry(size)
    root.update()

# 创建主窗口
root = tk.Tk()
root.title("Blog Manager")

# 设置窗口大小不能改变
root.resizable(False, False)

# 设置窗口居中
center_window(root, 400, 300)

# 硬编码图标
icon_img = iconb64()
icon_img = b64decode(icon_img)
icon_img = ImageTk.PhotoImage(data=icon_img)
root.tk.call('wm', 'iconphoto', root._w, icon_img)

# 设置图标
root.iconbitmap("icon.ico")

# 修改任务栏图标
root.wm_iconbitmap("icon.ico")

# 创建日历
calendar = Calendar(
    root,
    selectmode="day",
    year=datetime.datetime.now().year,
    month=datetime.datetime.now().month,
    date_pattern="yyyy-mm-dd",
    firstweekday="sunday", # 设置每周的第一天为周日
)
calendar.pack(pady=20)

# 绑定日期选择事件
calendar.bind("<<CalendarSelected>>", on_click)

# 每次更新月份时检查文件夹是否存在
calendar.bind("<<CalendarMonthChanged>>", lambda e: check_dates())

# 检查当前月份的文件夹
check_dates()

root.protocol("WM_DELETE_WINDOW", on_closing)

# 创建按钮框架
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# 创建按钮
btn_deploy = tk.Button(button_frame, text="Deploy", command=lambda: execute_script("deploy", r"E:\ChenHuaneng\Article\Blogs", "deploy.ps1", btn_deploy))
btn_local = tk.Button(button_frame, text="Local", command=lambda: execute_script("local", r"E:\ChenHuaneng\Article\Blogs", "local.ps1", btn_local))
btn_create = tk.Button(button_frame, text="Create", command=lambda: create_hexo_post(simpledialog.askstring("创建新文章", "请输入文章名称:")))
btn_open = tk.Button(button_frame, text="Open", command=open_localhost)

# 初始时隐藏 "Open" 按钮
hide_open_button()

# 横向排布按钮
btn_deploy.pack(side=tk.LEFT, padx=5)
btn_local.pack(side=tk.LEFT, padx=5)
btn_create.pack(side=tk.LEFT, padx=5)

root.mainloop()
