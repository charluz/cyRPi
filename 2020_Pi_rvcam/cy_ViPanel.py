# -*- encoding: utf-8 -*-

import time
import cv2
import numpy as np
import six

import tkinter as TK
from PIL import Image
from PIL import ImageTk

from cy_Utils.cy_CvOSD import CvOSD as OSD

#------------------------------------------------------------------
# TODO: resize image to fit panel size
# TODO: pan/zoom feature
#------------------------------------------------------------------


#--------------------------------------------------
# 常數 ID: 標定 Frame List 的 frame index
# Frame 編號採 counterclockwise
#--------------------------------------------------
LEFT = 0
RIGHT = 1

TOP = 0
BOTTOM = 1

TRI_TOP = 0
TRI_LEFT = 1
TRI_RIGHT = 2

QUAD_1 = 0
QUAD_2 = 1
QUAD_3 = 2
QUAD_4 = 3

ID_1 = 0
ID_2 = 1
ID_3 = 2
ID_4 = 3
ID_5 = 4
ID_6 = 5
ID_7 = 6
ID_8 = 7
ID_9 = 8

#---------------------------------------------------------------------------------------------------

#---------------------------------------------------------
# CLASS: tkRadioButton
#---------------------------------------------------------
class tkRadioButton:
	"""以 TK.LabelFrame()、TK.Radiobutton() 建立 多選一 UI
		Tkinter 的 radio button 感覺很驢: 他其實是一堆 button 的集合，所以每個選項都要 create 一個 button。
			每個 button 都有一個 command 可以設定。
		哪麼: 如何綁定一群 radio button 是同一個群組呢? 關鍵就在: 使用同一個 variable 變數 !!

	@param 	lable			LableFrame 的 標籤。如果 label="" 則不使用 LableFrame。
	@param	buttons			LIST of tuple: [ (Text , Val), (Text, Val) ]，
								每個 tuple 用來設定 button 的標籤文字以及對應值(numberic or string)，
								Example: [('item-1', 1), ('item-2', 2)]
							如果 buttons=None, 表示後續使用 add_buttons() 方式建立 buttons
								以及 pack_buttons() 排列。
	@param	value			Initial value
	@param	isRadio			BOOLEAN。 True: 傳統的 radio button，False: 沒有 radio 圈圈。
	@param	pack_type		Radio button 排列方式: "H"、"V"、"GRID" 分別對應: 水平、垂直、棋盤。
	@param	pack_column		如果排列方式設定為 "GRID"，必須同時設定 column=N 標示棋盤的橫向個數
	"""
	def __init__(self, rootWin, label="", buttons=None, value=0, isRadio=True,
					pack_type="GRID", pack_column=3, border=2, debug=False):
		self.debug = debug
		self.root = rootWin
		self.clsName = "radioButtons" if not label else label
		self.isRadio = isRadio
		self.initVal = value

		self.pack_type = pack_type
		self.pack_column = pack_column

		#-- Create a LabelFrame to place all radio buttons
		#
		self.rootFrame = self.root
		if label:
			self.labelFrame = TK.LabelFrame(self.root, text=label, bd=border, padx=2, pady=2)
			self.labelFrame.pack(fill=TK.BOTH, expand=TK.YES)
			self.rootFrame = self.labelFrame

		#-- Create Radio Buttons
		#
		self._buttons = []		#-- 紀錄 [(txt, val), (txt, val) ...]
		self.Buttons = []		#-- 紀錄最終 create 出來的且 pack 好的 buttons
		self.isPacked = False
		if buttons is not None:
			#-- add buttons
			self.add_buttons(buttons)

			#-- Pack Radio Buttons
			self.pack_buttons(self.pack_type, self.pack_column)


	def add_buttons(self, buttons):
		"""Add buttons to Radio Button group (LIST).
		@param	buttons		格式為 list of tuple: [ (btn_text, btn_val), (btn_text, btn_val), ... ]
		"""
		if self.isPacked:
			if self.debug:
				print("[{}]: Error!! Already packed, can't add buttons.")
				return

		if len(self._buttons) == 0:
			#-- 表示這是第一次設定 buttons --> 先判斷 button variable 的型態 (numeric or string)
			#-- 先檢查 button 變數是 數值 或是 字串，建立對應的 button variable。
			# button variable 是唯一用來標定 buttons 屬於哪個 Radio Button 的方法 !!
			if isinstance(buttons[0][1], six.string_types):
				self.radioVal = TK.StringVar()
			else:
				self.radioVal = TK.IntVar()

			self.radioVal.set(self.initVal)

		for btn in buttons:
			self._buttons.append(btn)
			# btn = TK.Radiobutton(self.rootFrame, text=txt, variable=self.radioVal, value=val, indicatoron=self.isRadio)


	def pack_buttons(self, type="", column=0):
		"""
		@param	type		Radio button 排列方式: "H"、"V"、"GRID" 分別對應: 水平、垂直、棋盤。
		@param	column		如果排列方式設定為 "GRID"，必須同時設定 column=N 標示棋盤的橫向個數
		"""
		if self.isPacked:
			if self.debug:
				print("[{}]: Error!! Already packed, can't change layout.")
				return

		if not type:
			type = self.pack_type

		if not column:
			column = self.pack_column

		if type == "GRID":
			self._pack_GRID(column)
		elif type == "H":
			self._pack_Horizontal()
		else: #-- "V"
			self._pack_Vertical()

	def _pack_GRID(self, column):
		"""使用 tkV3Frame 做為排列基礎，也就是說目前最多只支援 3 列，但是 column 不限制。
		"""
		n_buttons = len(self._buttons)
		if n_buttons > column*3:
			if self.debug:
				print("[{}] Too many buttons({}) to place, maximun= {}".format(self.clsName, n_buttons, column * 3))
			return

		packFrames = tkV3Frame(self.rootFrame).Frames
		frame_idx = 0
		pack_frame = packFrames[frame_idx]
		for i, btn in enumerate(self._buttons):
			# print(btn[0], btn[1])
			b = TK.Radiobutton(pack_frame, text=btn[0], variable=self.radioVal, value=btn[1], indicatoron=self.isRadio)
			b.pack(side=TK.LEFT)
			self.Buttons.append(b)
			next = i+1
			if (next % column) == 0 and (next < n_buttons):
				frame_idx += 1
				# print(">>> i={}, frame_idx={}".format(i, frame_idx))
				pack_frame = packFrames[frame_idx]

		self.isPacked = True


	def _pack_Horizontal(self):
		for btn in self._buttons:
			b = TK.Radiobutton(self.rootFrame, text=btn[0], variable=self.radioVal, value=btn[1], indicatoron=self.isRadio)
			b.pack(side=TK.LEFT)
			self.Buttons.append(b)


	def _pack_Vertical(self):
		for btn in self._buttons:
			b = TK.Radiobutton(self.rootFrame, text=btn[0], variable=self.radioVal, value=btn[1], indicatoron=self.isRadio)
			b.pack(side=TK.TOP)
			self.Buttons.append(b)


	def enable(self, en, idx=-1):
		state = TK.NORMAL if en else TK.DISABLED
		if idx < 0:
			for btn in self.Buttons:
				btn.configure(state=state)
		elif idx in range(0, len(self.Buttons)):
			self.Buttons[idx].configure(state=state)
		else:
			if self.debug:
				print("[{}] idx({}) is illegal!!".format(self.clsName, idx))


	def set_command(self, cmd_func, idx=-1):
		"""Radiobutton() 是每個 button 設定個別的 command function
		"""
		if idx < 0:
			for btn in self.Buttons:
				btn.configure(command=cmd_func)
		elif idx in range(0, len(self.Buttons)):
			self.Buttons[idx].configure(command=cmd_func)
		else:
			if self.debug:
				print("[{}] idx({}) is illegal!!".format(self.clsName, idx))


	def set_value(self, val):
		# values_ = [self.Buttons[i].value for i in range(0, len(self.Buttons))]
		# print(values_)
		self.radioVal.set(val)

	def get_value(self):
		return self.radioVal.get()

#---------------------------------------------------------
# CLASS: tkScale
#---------------------------------------------------------
class tkScale:
	"""以 TK.Scale() 建立 slider (預設為水平方向、帶標籤)
	"""
	def __init__(self, rootWin, label="Scale", value=5, range=(1, 10), resolution=1,
					orient=TK.HORIZONTAL, border=2, debug=False):
		self.clsName = label
		self.debug = debug
		self.root = rootWin

		self.range = range

		self.slidebar = TK.Scale(self.root, from_=range[0], to=range[1], resolution=resolution,
							orient=orient, label=label,
							length=120, bd=border, showvalue=True )
		self.value = self.set_value(value)
		self.slidebar.pack(expand=TK.YES)


	def enable(self, en):
		state = TK.NORMAL if en else TK.DISABLED
		self.slidebar.configure(state=state)

	def set_value(self, val):
		v = self.range[0] if val < self.range[0] else val
		v = self.range[1] if v > self.range[1] else val
		self.slidebar.set(v)
		if self.debug and v != val:
			print("[{}] Illegal value({}) ... overrided to ({})".format(self.clsName, val, v))

	def get_value(self):
		return self.slidebar.get()

	def set_size(self, size):
		self.slidebar.configure(length=size)

	def set_resolution(self, val):
		self.slidebar.configure(resolution=val)

	def set_orientation(self, orient):
		"""
		@param	orient	"V"=TK.VERITCAL, "H"=TK.HORIZONTAL
		"""
		_orient = TK.VERTICAL if orient == "V" else TK.HORIZONTAL
		self.slidebar.configure(orient=_orient)

	def set_label(self, val):
		self.slidebar.configure(label=val)

#---------------------------------------------------------
# CLASS: tkMessagePanel
#---------------------------------------------------------
class tkMessagePanel:
	"""使用 Tk.Label() 建立 Text message panel

	@param	rootWin		Message Panel 的上層 Tkinter 物件
	@param	lines		Message Entry 的列數
	@param	border		Panel 邊框大小
	@param	name/debug	Class debug
	"""
	def __init__(self, rootWin, lines=6, width=40, border=2,name="Text", debug=False):
		self.clsName	= name
		self.debug = debug

		if rootWin is None:
			self.dbgPrint("ERROR: Null rootWin !!")
			return

		self.rootTk = rootWin
		self.lines = lines

		self.text = TK.StringVar()
		self.panel = TK.Label(self.rootTk, height=lines, width=width, textvariable=self.text, anchor="w", justify=TK.LEFT, padx=2, pady=2, bd=border)
		self.panel.pack(fill=TK.X, expand=TK.YES)

	def print(self, text):
		self.text.set(text)


#---------------------------------------------------------
# CLASS: tkTextPanel
#---------------------------------------------------------
class tkTextPanel:
	"""使用 Tk.Text() 建立 Text display panel

	@param	rootWin		Text Panel 的上層 Tkinter 物件
	@param	lines		Text Entry 的列數
	@param	width		Text Entry 每一列的字數
	@param	border		Panel 邊框大小
	@param	name/debug	Class debug
	"""
	def __init__(self, rootWin, lines=6, width=30, border=2,name="Text", debug=False):
		self.clsName	= name
		self.debug = debug

		if rootWin is None:
			self.dbgPrint("ERROR: Null rootWin !!")
			return

		self.rootTk = rootWin
		self.lines = lines
		self.width = width

		self.vscroll = TK.Scrollbar(self.rootTk)
		self.panel = TK.Text(self.rootTk, height=self.lines, width=self.width, bd=border)

		self.vscroll.pack(side=TK.RIGHT, fill=TK.Y)
		self.panel.pack(side=TK.LEFT, fill=TK.Y)

		self.vscroll.config(command=self.panel.yview)
		self.panel.config(yscrollcommand=self.vscroll.set)

	def insert(self, text):
		self.panel.insert(TK.END, text)



#---------------------------------------------------------
# Function: create_PIL_image
#---------------------------------------------------------
def create_PIL_image(width, height, dtype=np.uint8):
	data = np.zeros((height, width, 3), dtype=dtype)
	image = Image.fromarray(data)
	image = ImageTk.PhotoImage(image)
	return image


#---------------------------------------------------------
# Function: convert_CV_to_PIL
#---------------------------------------------------------
def convert_CV_to_PIL(img):
	if len(img.shape) < 3:
		image = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
	else:
		image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	image = Image.fromarray(image)
	image = ImageTk.PhotoImage(image)

	return image


#---------------------------------------------------------
# CLASS: tkViPanel
#---------------------------------------------------------
class tkViPanel:
	"""使用 Tk.Label() 建立 Visual Image Panel

	@param	rootWin		Panel 的上層 Tkinter 物件
	@param	size		Panel 的大小
	@param	border		Panel 邊框大小
	@param	showOSD		OSD 顯示 frame rate, name
	@param	name/debug	Class debug
	"""
	def __init__(self, rootWin, size=(320, 240), border=2,
					osdEn=True, osdScale=1.0, osdColor=(255, 255, 255),
					name="ViP", debug=False):
		self.clsName	= name
		self.debug	= debug
		self.osdOn = osdEn
		self.osdScale = osdScale
		self.osdColor = osdColor
		if self.osdOn:
			self.osd = OSD()
			self.osd.set_property(fontScale=self.osdScale, fontColor=self.osdColor)
			self.timeLastFrame = time.time()

		if rootWin is None:
			self.dbgPrint("ERROR: Null rootWin !!")
			return

		self.rootTk = rootWin
		self.size = size
		self.image = create_PIL_image(size[0], size[1])

		self.panel = TK.Label(self.rootTk, image=self.image, fg="black", width=size[0], height=size[1], bd=border)
		self.panel.pack(fill=TK.X)

		self.callbackObj = None

		self.fps_last, self.fps_min, self.fps_max = 0.0, 9999.0, 0.0

	def off(self):
		self.image = create_PIL_image(self.size[0], self.size[1])
		self.panel.configure(image=self.image, fg="black")

	def configure(self, osdScale=None, osdColor=None, name=None):
		if self.osdOn:
			self.osdScale = self.osdScale if osdScale is None else osdScale
			self.osdColor = self.osdColor if osdColor is None else osdColor

			# print("osdColor ={}, self.osdColor= {}".format(osdColor, self.osdColor))
			self.osd.set_property(fontScale=self.osdScale, fontColor=self.osdColor)

		self.clsName = self.clsName if name is None else name


	def show(self, cv2_img, name="", pan=(0, 0), zoom=1.0):
		h = cv2_img.shape[0]
		w = cv2_img.shape[1]

		if self.callbackObj is not None:
			self.callbackObj.draw(cv2_img)
			pass

		if self.osdOn:
			now = time.time()
			#fps = (self.fps_last + (1.0 / (now - self.timeLastFrame)))/2.0
			if (now- self.timeLastFrame) <= 0:
				fps = self.fps_last
			else:
				fps = (1.0 / (now - self.timeLastFrame))
			self.timeLastFrame = now
			self.fps_min = fps if fps < self.fps_min else self.fps_min
			self.fps_max = fps if fps > self.fps_max else self.fps_max
			showName = self.clsName if not name else name
			text = "{}, fps{:.1f} - max{:.1f}".format(showName, fps, self.fps_max)
			self.fps_last = fps
			self.osd.show(cv2_img, text)

		# print(">>> input size: ", w, h)
		# print(">>> panel size: ", self.size)
		if (w, h) != self.size:
			# print("resize to: ", self.size)
			new_w = self.size[0]
			new_h = int(new_w * h / w)
			cv2_img = cv2.resize(cv2_img, (new_w, new_h))
			# print("new size: ", cv2_img.shape)

		tk_image = convert_CV_to_PIL(cv2_img)

		self.panel.configure(image=tk_image)
		self.panel.image=tk_image 	#--- !! 這一行不能少 !!
		pass


	def set_callbackObj(self, callbackObj=None):
		"""在 panel 上畫圖。draw_panel() 必須在 show() 前呼叫。
			image 的變更是在 show() 裡面執行，而且必須是 showEx()
			或 show(EXmode=True) 才會生效。

			callbackObj should be an external class object
		"""
		self.callbackObj = callbackObj
		pass

	def dbgPrint(self, *args):
		if self.debug:
			print("[{}]".format(self.clsName), end="")
			print(*args)


#---------------------------------------------------------
# CLASS: tkFrameID (Frame 編號常數)
#---------------------------------------------------------
class tkFrameID:
	def __init__(self):
		ID_1 = 0
		ID_2 = 1
		ID_3 = 2
		ID_4 = 3
		ID_5 = 4
		ID_6 = 5
		ID_7 = 6
		ID_8 = 7
		ID_9 = 8


#---------------------------------------------------------
# CLASS: tkH2Frame (雙框: 左、右)
#---------------------------------------------------------
class tkH2Frame:
	""" GUI 橫向 (左、右) 雙框
	@param	rootWin			上層 Tkinter 物件
	@param	layout			Frame 的編號方式:
								"LEFT":	由左到右,
								"RIGHT":由右到左
	@param	name, debug		Debug control.
	"""
	def __init__(self, rootWin, layout="left", name="H2Fm", debug=False):
		self.clsName = name
		self.debug = debug

		if rootWin is None:
			self.dbgPrint("ERROR: Null rootWin !!")
			return
		self.rootTk = rootWin

		#-------------------------------------------
		# 左框
		#-------------------------------------------
		self.Left = TK.Frame(self.rootTk)
		self.Left.pack(side=TK.LEFT, fill=TK.BOTH)

		#-------------------------------------------
		# 右框
		#-------------------------------------------
		self.Right = TK.Frame(self.rootTk)
		self.Right.pack(expand=TK.YES)

		#--- 打包
		if layout == "RIGHT":
			self.Frames = [self.Right, self.Left]
		else:
			#-- Default
			self.Frames = [self.Left, self.Right]


	def dbgPrint(self, *args):
		if self.debug:
			print("[{}]".format(self.clsName), end="")
			print(*args)




#---------------------------------------------------------
# CLASS: tkV2Frame  (雙框: 上、下)
#---------------------------------------------------------
class tkV2Frame:
	""" GUI 縱向 (上、下) 雙框
	@param	rootWin			上層 Tkinter 物件
	@param	layout			Frame 的編號方式:
								"TOP":		由上到下,
								"BOTTOM":	由下到上
	@param	name, debug		Debug control.
	"""
	def __init__(self, rootWin, layout="top", name="V2Fm", debug=False):
		self.clsName = name
		self.debug = debug

		if rootWin is None:
			self.dbgPrint("ERROR: Null rootWin !!")
			return
		self.rootTk = rootWin

		#-------------------------------------------
		# 上框
		#-------------------------------------------
		self.Top = TK.Frame(self.rootTk)
		self.Top.pack()

		#-------------------------------------------
		# 下框
		#-------------------------------------------
		self.Bottom = TK.Frame(self.rootTk)
		self.Bottom.pack()

		#--- 打包
		if layout == "BOTTOM":
			self.Frames = [self.Bottom, self.Top]
		else:
			#-- deafult -- top - down
			self.Frames = [self.Top, self.Bottom]


	def dbgPrint(self, *args):
		if self.debug:
			print("[{}]".format(self.clsName), end="")
			print(*args)



#---------------------------------------------------------
# CLASS: tkTriFrame (三框: 上、左、右)
#---------------------------------------------------------
class tkTriFrame:
	""" GUI 品字三框: 上、左、右
	@param	rootWin			上層 Tkinter 物件
	@param	layout			Frame 的編號方式:
								"CW":	clockwise,
								"CCW":	counter-clockwise (default)
	@param	name, debug		Debug control.
	"""
	def __init__(self, rootWin, layout="CCW", name="T3Fm", debug=False):
		self.clsName = name
		self.debug = debug

		if rootWin is None:
			self.dbgPrint("ERROR: Null rootWin !!")
			return
		self.rootTk = rootWin

		#-------------------------------------------
		# 上框
		#-------------------------------------------
		self.Top = TK.Frame(self.rootTk)
		self.Top.pack()

		#-------------------------------------------
		# 下框
		#-------------------------------------------
		self.Bottom = TK.Frame(self.rootTk)
		self.Bottom.pack()

		#--- 左下框
		self.Bottom_Left = TK.Frame(self.Bottom)
		self.Bottom_Left.pack(side=TK.LEFT, fill=TK.Y)

		#--- 右下框
		self.Bottom_Right = TK.Frame(self.Bottom)
		self.Bottom_Right.pack(expand=TK.YES)

		#--- 打包
		if layout == "CW":
			self.Frames = [self.Top, self.Bottom_Right, self.Bottom_Left]
		else:
			#-- defult - CCW
			self.Frames = [self.Top, self.Bottom_Left, self.Bottom_Right]


	def dbgPrint(self, *args):
		if self.debug:
			print("[{}]".format(self.clsName), end="")
			print(*args)


#---------------------------------------------------------
# CLASS: tkQuadFrame (田字四框 2x2)
#---------------------------------------------------------
class tkQuadFrame:
	""" GUI 田字四框 2x2
	@param	rootWin			上層 Tkinter 物件
	@param	layout			Frame 的編號方式:
								"N":	倒 N 字形順序排列
								"Z":	Z 字形順序排列 (default)
	@param	name, debug		Debug control.
	"""
	def __init__(self, rootWin, layout="Z", name="QFm", debug=False):
		self.clsName = name
		self.debug = debug

		if rootWin is None:
			self.dbgPrint("ERROR: Null rootWin !!")
			return
		self.rootTk = rootWin

		#-------------------------------------------
		# 上框
		#-------------------------------------------
		self.Top = TK.Frame(self.rootTk)
		self.Top.pack()
		self.topFrames = tkH2Frame(self.Top, name="top2").Frames

		#--- 上(1)框
		self.top_1 = self.topFrames[0]
		#--- 上(2)框
		self.top_2 = self.topFrames[1]


		#-------------------------------------------
		# 下框
		#-------------------------------------------
		self.Bottom = TK.Frame(self.rootTk)
		self.Bottom.pack()
		self.bttmFrame = tkH3Frame(self.Bottom, name="bttm2").Frames

		#--- 下(1)框
		self.bttm_1 = self.bttmFrame[0]
		#--- 下(2)框
		self.bttm_2 = self.bttmFrame[1]

		#--- 打包
		if layout == "N":
			self.Frames = [self.top_1, self.bttm_1, self.top_2, self.bttm_2]
		else:
			#-- defult - "Z"
			self.Frames = [self.top_1, self.top_2, self.bttm_1, self.bttm_2]


	def dbgPrint(self, *args):
		if self.debug:
			print("[{}]".format(self.clsName), end="")
			print(*args)


#---------------------------------------------------------
# CLASS: tkH3Frame (三框: 左、中、右)
#---------------------------------------------------------
class tkH3Frame:
	""" GUI 橫向一字三框 : 左、中、右
	@param	rootWin			上層 Tkinter 物件
	@param	layout			Frame 的編號方式:
								"LEFT":		左到右(default)
								"RIGHT":	右到左
	@param	name, debug		Debug control.
	"""
	def __init__(self, rootWin, layout="LEFT", name="H3Fm", debug=False):
		self.clsName = name
		self.debug = debug

		if rootWin is None:
			self.dbgPrint("ERROR: Null rootWin !!")
			return
		self.rootTk = rootWin

		#-------------------------------------------
		# 左框
		#-------------------------------------------
		self.Left = TK.Frame(self.rootTk)
		self.Left.pack(side=TK.LEFT, fill=TK.BOTH)

		#-------------------------------------------
		# 中框
		#-------------------------------------------
		self.Mid = TK.Frame(self.rootTk)
		self.Mid.pack(side=TK.LEFT, fill=TK.BOTH)

		#-------------------------------------------
		# 右框
		#-------------------------------------------
		self.Right = TK.Frame(self.rootTk)
		self.Right.pack(expand=TK.YES)

		#--- 打包
		if layout == "RIGHT":
			self.Frames = [self.Right, self.Mid, self.Left]
		else:
			self.Frames = [self.Left, self.Mid, self.Right]


	def dbgPrint(self, *args):
		if self.debug:
			print("[{}]".format(self.clsName), end="")
			print(*args)


#---------------------------------------------------------
# CLASS: tkV3Frame (三框: 上、中、下)
#---------------------------------------------------------
class tkV3Frame:
	""" GUI 橫向一字三框: 上、中、下
	@param	rootWin			上層 Tkinter 物件
	@param	layout			Frame 的編號方式:
								"TOP":		由上到下,
								"BOTTOM":	由下到上
	@param	name, debug		Debug control.
	"""
	def __init__(self, rootWin, layout="TOP", name="V3Fm", debug=False):
		self.clsName = name
		self.debug = debug

		if rootWin is None:
			self.dbgPrint("ERROR: Null rootWin !!")
			return
		self.rootTk = rootWin

		#-------------------------------------------
		# 上框
		#-------------------------------------------
		self.Top = TK.Frame(self.rootTk)
		self.Top.pack(side=TK.TOP, fill=TK.BOTH)

		#-------------------------------------------
		# 中框
		#-------------------------------------------
		self.Mid = TK.Frame(self.rootTk)
		self.Mid.pack(side=TK.TOP, fill=TK.BOTH)

		#-------------------------------------------
		# 下框
		#-------------------------------------------
		self.Bottom = TK.Frame(self.rootTk)
		self.Bottom.pack(expand=TK.YES)

		#--- 打包
		if layout == "BOTTOM":
			self.Frames = [self.Bottom, self.Mid, self.Top]
		else:
			self.Frames = [self.Top, self.Mid, self.Bottom]


	def dbgPrint(self, *args):
		if self.debug:
			print("[{}]".format(self.clsName), end="")
			print(*args)



#---------------------------------------------------------
# CLASS: tkN3x3Frame (3x3框)
#---------------------------------------------------------
class tk3x3Frame:
	""" GUI 橫向一字三框 : 左、中、右
	@param	rootWin			上層 Tkinter 物件
	@param	layout			Frame 的編號方式:
								"N":	倒 N 字形順序排列
								"Z":	Z 字形順序排列 (default)
	@param	name, debug		Debug control.
	"""
	def __init__(self, rootWin, layout="Z", name="3x3Fm", debug=False):
		self.clsName = name
		self.debug = debug

		if rootWin is None:
			self.dbgPrint("ERROR: Null rootWin !!")
			return
		self.rootTk = rootWin

		#-------------------------------------------
		# 上框
		#-------------------------------------------
		self.Top = TK.Frame(self.rootTk)
		self.Top.pack()
		self.topFrames = tkH3Frame(self.Top, name="top3").Frames

		#--- 上(1)框
		self.top_1 = self.topFrames[0]
		#--- 上(2)框
		self.top_2 = self.topFrames[1]
		#--- 上(3)框
		self.top_3 = self.topFrames[2]

		#-------------------------------------------
		# 中框
		#-------------------------------------------
		self.Mid = TK.Frame(self.rootTk)
		self.Mid.pack()
		self.midFrames = tkH3Frame(self.Mid, name="mid3").Frames

		#--- 中(1)框
		self.mid_1 = self.midFrames[0]
		#--- 中(2)框
		self.mid_2 = self.midFrames[1]
		#--- 中(3)框
		self.mid_3 = self.midFrames[2]

		#-------------------------------------------
		# 下框
		#-------------------------------------------
		self.Bottom = TK.Frame(self.rootTk)
		self.Bottom.pack()
		self.bttmFrame = tkH3Frame(self.Bottom, name="bttm3").Frames

		#--- 下(1)框
		self.bttm_1 = self.bttmFrame[0]
		#--- 下(2)框
		self.bttm_2 = self.bttmFrame[1]
		#--- 下(3)框
		self.bttm_3 = self.bttmFrame[2]

		#--- 打包 -------------------------------------------------------------
		if layout == "N":
			self.Frames = [self.top_1, self.mid_1, self.bttm_1,
							self.top_2, self.mid_2, self.bttm_2,
							self.top_3, self.mid_3, self.bttm_3]
		else:
			#-- defult = "Z"
			self.Frames = [self.top_1, self.top_2, self.top_3,
							self.mid_1, self.mid_2, self.mid_3,
							self.bttm_1, self.bttm_2, self.bttm_3]


	def dbgPrint(self, *args):
		if self.debug:
			print("[{}]".format(self.clsName), end="")
			print(*args)





#---------------------------------------------------------
# Unit Tests
#---------------------------------------------------------
# See test_ViPanel.py
