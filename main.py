import PIL
from PIL import Image
import time
import os
import multiprocessing
from multiprocessing import Process
from multiprocessing import queues
from multiprocessing import process
import sys
p = []	#进程列表
ori_img = Image.open('1.jpg')#.resize((480,270))#读取原图
wt,ht = ori_img.size	#原图尺寸
delta = 5				#分割大小
subimgsize = 64		#素材图片大小
imglist = []			#素材图片列表
outputlist = []			#输出结果部分列表
newwt = int(subimgsize*wt/delta)#输出的宽
newht = int(subimgsize*ht/delta)#输出的高
img_num = 504		#引用素材数量
#	E:\WEB积木\拼图素材\img	素材2-5004
def averrgb(img):
	iw,ih = img.size
	pix = img.getpixel
	ar,ag,ab = 0,0,0
	for ai in range(iw):
		for aj in range(ih):
			ar += pix((ai,aj))[0]
			ag += pix((ai,aj))[1]
			ab += pix((ai,aj))[2]
	argb = ar/iw/ih,ag/iw/ih,ab/iw/ih
	#print(argb)
	return argb

def find(colour,imglist):
	fr=colour[0]
	fg=colour[1]
	fb=colour[2]
	offset = 99999
	num = 0
	for fi in range(0,len(imglist)):
		temp = abs(fr-imglist[fi][1][0])+abs(fg-imglist[fi][1][1])+abs(fb-imglist[fi][1][2])
		if(temp<offset):
			offset = temp
			num = fi
	return num

def calcu_paste(CPUS,i,imglist,imgqueue):
	halfoutput = Image.new('RGB', (int(newwt/CPUS),int(newht)))#n
	ori_img = Image.open('1.jpg')
	for ii in range(int(i*wt/CPUS/delta),int((i+1)*wt/CPUS/delta)):
		print('拼凑第'+str(i)+'部分第'+str(ii)+'行')
		for jj in range(0,int (ht/delta)):
			left = int (ii*subimgsize-newwt/CPUS*i)
			up = int (jj*subimgsize)
			right = int (left+subimgsize)
			down = int (up+subimgsize)
			pice = ori_img.crop((ii*delta,jj*delta,ii*delta+delta,jj*delta+delta))
			rgb = averrgb(pice)
			#print('rgb='+str(rgb))
			t = imglist[find(rgb,imglist)][0]
			halfoutput.paste(t,(left,up,right,down))
	imgqueue.put((halfoutput,i))
	print('第'+str(i)+'部分拼凑完成')
	halfoutput.save('p'+str(i)+'.jpg')
	time.sleep(15)
	#os._exit(0)

def loadimg(start,end,imgqueue):
	for i in range(start,end+1):
		print(str(i)+'  ')
		imgpath1 = 'E:\WEB积木\拼图素材\img\\' + str(i) + '.jpg'
		imgpath2 = 'E:\WEB积木\拼图素材\img\\' + str(i) + '.png'
		if(os.path.exists(imgpath1)):
			img = Image.open(imgpath1).resize((subimgsize,subimgsize))
		elif(os.path.exists(imgpath2)):
			img = Image.open(imgpath2).resize((subimgsize,subimgsize))
		else:
			pass
		imgqueue.put((img,averrgb(img)))
		time.sleep(0.01)
	print('done')
	#time.sleep(25)
	os._exit(0)


#main begin
if __name__ == '__main__':
	#rgbqueue = queues.Queue(5000,ctx=multiprocessing)
	imgqueue = queues.Queue(5000,ctx=multiprocessing)
	
	ts=time.time()
	n = 0
	
	CPUS = os.cpu_count()
	averthread_num = int(img_num/CPUS)
	#读取图片
	for i in range(0,CPUS):
		p.append(Process(target = loadimg,args = (i*averthread_num+1,(i+1)*averthread_num,imgqueue,)))
	for i in range(0,CPUS):
		p[i].start()

	while (len(imglist)!=img_num):#生产者消费者模型
		while not imgqueue.empty():
			imglist.append(imgqueue.get())
		
	for i in range(0,CPUS):
		p[i].join()
	'''
	print('rgbqueue')
	print(rgbqueue.qsize())
	print('imgqueue')
	print(imgqueue.qsize())
	'''
	
	print('imglist长度'+str(len(imglist)))
	newimg = Image.new('RGB', (int(newwt),int(newht)))#创建新图片
	p.clear()
	for i in range(0,CPUS):
		p.append(Process(target=calcu_paste,args = (CPUS,i,imglist,imgqueue,)))
	for i in range(0,CPUS):
		p[i].start()

	while (len(outputlist)!=CPUS):
		while not imgqueue.empty():
			#outputlist.append(imgqueue.get())
			temp = imgqueue.get()
			newimg.paste(temp[0],(int(temp[1]*newwt/CPUS),0,int((temp[1]+1)*newwt/CPUS),newht))
			#p[temp[1]].join()

	for i in range(0,CPUS):
		for j in range(0,CPUS):
				p[i].join()


	print('用时:'+str(time.time()-ts)+'秒')
	newimg.save('output.jpg')
	input()
