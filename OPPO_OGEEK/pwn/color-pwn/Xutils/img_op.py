import os

def handle_color_table(s,split,split2):
	l = s.replace('\n','').replace(split,'').split(split2)[:-1]
	painting = "<br>"
	for i in l:
		sum = int(i,16)
		b = (sum>>24)&0xff;g = (sum>>16)&0xff;r = (sum>>8)&0xff;a = 0x100-(sum&0xff);
		painting += '<canvas width="40" height="40" style="background-color:rgba(%d,%d,%d,%d)"> </canvas> '%(r,g,b,a)
	return painting