import wx, sys
import numpy as np
from numpy.linalg import norm
from scipy import interpolate

if sys.version_info[0]==2:memoryview=np.getbuffer

class ViewPort(wx.Panel):
    """ HistCanvas: diverid from wx.core.Panel """
    def __init__(self, parent):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, 
                            pos = wx.DefaultPosition, size = wx.Size(-1,-1), 
                            style = wx.TAB_TRAVERSAL )
        self.init_buf()
        self.img = None
        self.boximg = None
        self.boxpan = None
        self.box = (0,0)
        self.ibox = (100,100)
        self.dirty = False
        self.loc = (0,0)
        self.drag = False

        self.Bind(wx.EVT_SIZE, self.on_size)  
        self.Bind(wx.EVT_IDLE, self.on_idle)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_ld)
        self.Bind(wx.EVT_LEFT_UP, self.on_lu)
        self.Bind(wx.EVT_MOTION, self.on_mv)

    def update(self): self.dirty = True

    def init_buf(self):
        self.box = box = self.GetClientSize()
        self.buffer = wx.Bitmap(box.width, box.height)
        
    def on_size(self, event):
        self.init_buf()
        self.update()
        
    def on_idle(self, event):
        if self.dirty == True:
            self.draw()
            self.dirty = False

    def on_paint(self, event):
        wx.BufferedPaintDC(self, self.buffer)

    def on_ld(self, event):
        x, y = event.GetX(), event.GetY()
        x = 1.0*(x-self.offx)/self.imgw
        y = 1.0*(y-self.offy)/self.imgh
        if x<0 or x>1 or y<0 or y>1:return
        self.loc = (x*self.ibox[0], y*self.ibox[1])
        self.handle()
        self.drag = True

    def on_lu(self, event):
        self.drag = False

    def on_mv(self, event):
        if not self.drag:return
        x, y = event.GetX(), event.GetY()
        x = 1.0*(x-self.offx)/self.imgw
        y = 1.0*(y-self.offy)/self.imgh
        if x<0 or x>1 or y<0 or y>1:return
        self.loc = (x*self.ibox[0], y*self.ibox[1])
        self.handle()

    def GetValue(self):return self.loc

    def set_img(self, img, size):
        self.ibox = size[:2][::-1]
        bmp = wx.Bitmap.FromBuffer(img.shape[1], img.shape[0], memoryview(img.copy()))
        if 1.0*self.box[0]/self.box[1]<1.0*self.ibox[0]/self.ibox[1]:
            k = 1.0*self.box[0]/self.ibox[0]
            self.imgw, self.imgh = self.box[0], self.ibox[1]*k
            self.offx, self.offy = 0, (self.box[1]-self.imgh)/2.0
            self.img = bmp.ConvertToImage().Rescale(self.imgw, self.imgh).ConvertToBitmap()
        else:
            k = 1.0*self.box[1]/self.ibox[1]
            self.imgw, self.imgh = self.ibox[0]*k, self.box[1]
            self.offx, self.offy = (self.box[0]-self.imgw)/2.0, 0
            print(self.imgw, self.imgh)
            self.img = bmp.ConvertToImage().Rescale(self.imgw, self.imgh).ConvertToBitmap()


    def set_box(self, boximg, boxpan):
        self.boximg, self.boxpan = boximg, boxpan
        self.update()

    def draw(self):
        # get client device context buffer
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        dc.SetBrush(wx.Brush((0,0,0), wx.BRUSHSTYLE_TRANSPARENT))
        dc.Clear()
        if self.boximg is None:
            dc.SetPen(wx.Pen((100,100,100), width=1, style=wx.SOLID))
            dc.DrawRectangle(0, 0, self.box[0], self.box[1])
            return
        # w, h = self.GetClientSize()
        l = 1.0*max(self.boxpan[0]-self.boximg[0], 0)/self.boximg[2]
        r = 1.0*min((self.boxpan[2]-self.boximg[0])/self.boximg[2],1)
        t = 1.0*max(self.boxpan[1]-self.boximg[1], 0)/self.boximg[3]
        b = 1.0*min((self.boxpan[3]-self.boximg[1])/self.boximg[3],1)
        # the main draw process 
        
        
        dc.DrawBitmap(self.img, self.offx, self.offy)
        dc.SetPen(wx.Pen((100,100,100), width=1, style=wx.SOLID))
        dc.DrawRectangle(self.offx, self.offy, self.imgw, self.imgh)
        x,y,w,h = l*self.imgw+self.offx, t*self.imgh+self.offy,(r-l)*self.imgw,(b-t)*self.imgh
        dc.SetPen(wx.Pen((255,0,0), width=1, style=wx.SOLID))
        dc.DrawRectangle(x,y,w,h)

        
    def handle(self):pass
    
    def set_handle(self, handle):self.handle = handle

if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = wx.Frame(None)
    hist = ViewPort(frame)
    #hist.set_img(np.zeros((6,10)))
    hist.set_box([0,0,10,6],[0,0,5,5])
    frame.Fit()
    frame.Show(True)
    app.MainLoop() 