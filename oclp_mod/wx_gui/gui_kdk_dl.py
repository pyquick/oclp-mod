import wx
import requests
import threading
from wx.lib.agw.customtreectrl import CustomTreeCtrl
import time
from ..constants import Constants
from .. import constants

# KDK下载链接（全局变量，后续可用于存储用户选择的KDK下载地址）
kdkurl = ""
# KDK API代理与原始地址
KDK_API_LINK_PROXY:     str  = "https://oclpapi.simplehac.cn/KdkSupportPkg/manifest.json"  # 代理API，适合国内用户
KDK_API_LINK_ORIGIN:     str  = "https://dortania.github.io/KdkSupportPkg/manifest.json"    # 官方API，适合国际用户

class DownloadProgressFrame(wx.Frame):
    """
    下载进度窗口类
    用于显示KDK文件的下载进度、速度等信息，支持多线程下载，防止界面卡死。
    """
    def __init__(self, parent, title, url, file_path):
        super(DownloadProgressFrame, self).__init__(parent, title=title, size=(400, 150))
        panel = wx.Panel(self)
        # 标题标签
        self.title_label = wx.StaticText(panel, label="", pos=(10, 10))
        self.title_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        # 进度条控件
        self.progress_bar = wx.Gauge(panel, range=100, pos=(10, 40), size=(380, 25))
        self.progress_bar.SetValue(0)
        # 下载速度标签
        self.speed_label = wx.StaticText(panel, label="", pos=(10, 70))
        self.speed_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

        # 绑定窗口关闭事件，确保线程安全退出
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.url = url  # 下载链接
        self.file_path = file_path  # 保存路径
        self.downloading = True  # 下载状态标志

        # 启动下载线程，避免阻塞主线程
        self.download_thread = threading.Thread(target=self.download_file)
        self.download_thread.start()

    def download_file(self):
        """
        实际执行下载的线程函数，实时更新进度条和速度。
        """
        try:
            response = requests.get(self.url, stream=True)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))  # 文件总大小
            downloaded = 0
            last_downloaded = 0
            start_time = time.time()

            with open(self.file_path, "wb") as f:
                for data in response.iter_content(chunk_size=4096):
                    if not self.downloading:
                        break
                    downloaded += len(data)
                    f.write(data)
                    current_time = time.time()
                    speed = (downloaded - last_downloaded) / (current_time - start_time)
                    last_downloaded = downloaded
                    start_time = current_time

                    # 主线程安全地更新进度条和速度标签
                    wx.CallAfter(self.progress_bar.SetValue, int((downloaded / total_size) * 100))
                    wx.CallAfter(self.speed_label.SetLabel, f"{downloaded/1024/1024:.2f} MB / {total_size/1024/1024:.2f} MB @ {speed/1024/1024:.2f} MB/s")
        except requests.RequestException as e:
            wx.MessageBox(f"下载失败: {e}", "错误", wx.OK | wx.ICON_ERROR)

        wx.CallAfter(self.Close)

    def on_close(self, event):
        """
        关闭窗口时安全终止下载线程，防止资源泄漏。
        """
        self.downloading = False
        self.download_thread.join()
        self.Destroy()

class LoadingFrame(wx.Frame):
    """
    加载提示窗口类
    用于在拉取KDK列表时显示加载动画和提示，提升用户体验。
    """
    def __init__(self, parent, title):
        super(LoadingFrame, self).__init__(parent, title=title, size=(300, 100), style=wx.STAY_ON_TOP)
        panel = wx.Panel(self)

        # 标题标签
        self.title_label = wx.StaticText(panel, label="正在获取KDK信息...", pos=(50, 10))
        self.title_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        # 进度条（仅作动画效果）
        self.progress_bar = wx.Gauge(panel, range=100, pos=(50, 40), size=(200, 20))
        self.progress_bar.SetValue(50)  # 50%表示正在加载

        self.Centre()
        self.Show()

    def close(self):
        """
        关闭加载窗口
        """
        self.Destroy()

class DownloadListCtrl(wx.ListCtrl):
    """
    KDK下载列表控件类
    用于展示所有可用KDK版本及其信息，支持选择、复制、下载等操作。
    """
    def __init__(self, parent):
        super(DownloadListCtrl, self).__init__(parent, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        # 设置表头
        self.InsertColumn(0, "版本", width=80)
        self.InsertColumn(1, "系统", width=100)
        self.InsertColumn(2, "日期", width=120)
        self.InsertColumn(3, "下载链接", width=225)
        self.data = []  # 存储每个条目的数据，便于后续操作

    def SetData(self, MetalLib_data):
        """
        填充KDK数据到列表控件
        :param MetalLib_data: KDK数据列表（每项为dict）
        """
        self.data = []  # 清空旧数据
        for item in MetalLib_data:
            version = f"{item['build']}"  # KDK版本号
            size = f"macOS {item['version']}"  # 适用系统
            date = item['date'].split('T')[0]  # 发布时间
            url = item['url']  # 下载链接
            index = self.InsertItem(self.GetItemCount(), version)
            self.SetItem(index, 1, size)
            self.SetItem(index, 2, date)
            self.SetItem(index, 3, url)
            self.data.append({'version': version, 'url': url})  # 存储数据，便于后续复制/下载

    def get_selected_data(self):
        """
        获取当前选中的KDK条目数据
        :return: dict，包含version和url
        """
        selected_index = self.GetFirstSelected()
        if selected_index != -1:
            return self.data[selected_index]
        return None
        #kdkurl = item['url']

class DownloadKDKFrame(wx.Frame):
    """
    KDK下载主窗口类
    包含KDK列表、下载按钮、复制按钮、加载动画等，负责整体交互流程。
    """
    def __init__(self, parent, global_constants: Constants):
        # 记录全局常量，便于后续判断代理等
        self.constants: constants.Constants = global_constants
        super(DownloadKDKFrame, self).__init__(parent, title="KDK下载", size=(600, 400))
        panel = wx.Panel(self)

        # KDK列表控件
        self.list_ctrl = DownloadListCtrl(panel)
        # 下载按钮
        self.download_button = wx.Button(panel, label="下载", pos=(-250, 35))
        # 复制链接按钮
        self.copy_button = wx.Button(panel, label="复制链接", pos=(30, 350))
        self.copy_button.Bind(wx.EVT_BUTTON, self.on_copy)
        self.download_button.Bind(wx.EVT_BUTTON, self.on_download)

        # 布局管理，垂直排列
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        sizer.Add(self.download_button, proportion=0, flag=wx.CENTER | wx.ALL, border=5)
        sizer.Add(self.copy_button, proportion=0, flag=wx.CENTER | wx.ALL, border=5)

        panel.SetSizer(sizer)
        self.Show()
        # 加载动画窗口，提升体验
        self.loading_frame = LoadingFrame(self, title="正在加载")
        self.loading_frame.Show()
        # 拉取KDK数据
        self.fetch_kdk_data()

    def fetch_kdk_data(self):
        """
        拉取KDK数据，自动判断是否使用代理，拉取后填充到列表控件。
        该方法在新线程中调用，防止主界面卡死。
        """
        if self.constants.use_github_proxy == True:
            KDK_API_LINK: str = KDK_API_LINK_PROXY
        else:
            KDK_API_LINK: str = KDK_API_LINK_ORIGIN
        try:
            response = requests.get(KDK_API_LINK)
            response.raise_for_status()
            kdk_data = response.json()
            # 主线程安全地填充数据和关闭加载动画
            wx.CallAfter(self.list_ctrl.SetData, kdk_data)
            wx.CallAfter(self.loading_frame.close)
        except requests.RequestException as e:
            wx.MessageBox(f"获取KDK信息失败: {e}", "错误", wx.OK | wx.ICON_ERROR)
            wx.CallAfter(self.loading_frame.close)
    
    def on_copy(self, event):
        """
        复制所选KDK的下载链接到剪贴板
        用法：点击“复制链接”按钮后触发
        """
        selected_data = self.list_ctrl.get_selected_data()
        if selected_data:
            url = selected_data['url']
            wx.TheClipboard.Open()
            wx.TheClipboard.SetData(wx.TextDataObject(url))
            wx.TheClipboard.Close()
            wx.MessageBox("链接已复制到剪贴板", "成功", wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox("请选择一个KDK版本进行复制", "提示", wx.OK | wx.ICON_INFORMATION)

    def on_download(self, event):
        """
        下载所选KDK文件，弹出保存对话框，显示下载进度。
        用法：点击“下载”按钮后触发
        """
        selected_data = self.list_ctrl.get_selected_data()
        if selected_data:
            # 弹出文件保存对话框，用户选择保存路径
            with wx.FileDialog(self, "保存文件", wildcard="PKG Files (*.dmg)|*.dmg", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dlg:
                if dlg.ShowModal() == wx.ID_CANCEL:
                    return
                file_path = dlg.GetPath()
            url = selected_data['url']
            # 弹出下载进度窗口，自动开始下载
            DPF_Window = DownloadProgressFrame(self, title="下载进度", url=url, file_path=file_path)
            DPF_Window.Show()
        else:
            wx.MessageBox("请选择一个KDK版本进行下载", "提示", wx.OK | wx.ICON_INFORMATION)