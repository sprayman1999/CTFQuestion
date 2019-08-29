import os,uuid

from flask import Flask, request, render_template, url_for,redirect,make_response,session
from flask import send_from_directory,send_file
from werkzeug.utils import secure_filename

from forms.upload_file_form import UploadFileForm
from werkzeug.datastructures import CombinedMultiDict
from subprocess import Popen,STDOUT,PIPE
from Xutils.img_op import handle_color_table
from base64 import b64decode

app = Flask(__name__)
app.config['SECRET_KEY']=os.urandom(24)
UPLOAD_PATH = os.path.join(os.path.dirname(__file__), 'upload/')

dict_io = {}
dict_payload = {}

def random_filename(filename):
	ext = os.path.splitext(filename)[1]
	new_filename = uuid.uuid4().hex + ext
	return new_filename

@app.route('/')
def index():
	return redirect('/upload')

@app.route('/upload', methods=['POST', 'GET'])
def settings():
	def panic():
		os.remove(os.path.join(UPLOAD_PATH, session.get('filename')))
		session.clear()
		dict_io[app.config['SECRET_KEY']].terminate()
		del dict_payload[app.config['SECRET_KEY']]
		del dict_io[app.config['SECRET_KEY']]
	if 'isSubmitted' not in session and 'isDownloaded' not in session and 'isColorShowed' not in session and 'isOp1' not in session and 'isOp2' not in session and 'filename' not in session:
		if request.method == 'GET':
			return render_template('main.html')
		elif request.method == "POST":
			form = UploadFileForm(CombinedMultiDict([request.form, request.files]))
			if form.validate():
				try:
					avatar = request.files.get('avatar')
					filename = random_filename(secure_filename(avatar.filename))
					avatar.save(os.path.join(UPLOAD_PATH, filename))
					session['isSubmitted'] = True
					argv=[os.path.join(os.path.dirname(__file__),'bin/jebmp'),os.path.join(UPLOAD_PATH, filename)]
					dict_io[app.config['SECRET_KEY']] = Popen(args=argv,shell=False,stdin=PIPE,stdout=PIPE)
					dict_payload[app.config['SECRET_KEY']]=""
					dict_io[app.config['SECRET_KEY']].stdout.readline()
					buf = dict_io[app.config['SECRET_KEY']].stdout.readline();#print(pio)
					dict_io[app.config['SECRET_KEY']].stdout.flush();dict_io[app.config['SECRET_KEY']].stdin.flush();
					content = handle_color_table(str(buf,encoding="utf-8"),'#','\t')
					session['isColorShowed'] = content
					session['isOp1'] = True
					session['isOp2'] = False
					session['filename'] = filename
					session['isDownloaded'] = False
					return render_template('op.html',content = session.get('isColorShowed'))
				except Exception:
					os.remove(os.path.join(UPLOAD_PATH,filename))
					session.clear()
					return redirect("/")
			else:
				print(form.errors)
				return 'fail'
	elif 'isSubmitted' in session and 'isColorShowed' in session and session.get('isDownloaded') == False and 'isOp1' in session and 'isOp2' in session:
		if session.get('isOp1') == True and session.get('isOp2') == False:
			if request.method == 'GET':
				return render_template('op.html',content = session.get('isColorShowed'))
			elif request.method == 'POST':
				
				op = request.form.get('op')
				opnum = int(op)
				print(opnum)
				if(opnum == 1):
					dict_payload[app.config['SECRET_KEY']]+="1\n"
					session['isOp2'] = True
					session['isOp1'] = False
					return render_template('menu.html')
				elif(opnum == 2):
					dict_payload[app.config['SECRET_KEY']]+="2\n"
					return render_template('op.html',content = session.get('isColorShowed'))
				elif(opnum == 3):
					dict_payload[app.config['SECRET_KEY']]+="3\n";
					dict_io[app.config['SECRET_KEY']]._stdin_write(dict_payload[app.config['SECRET_KEY']].encode('latin-1'));print(dict_payload[app.config['SECRET_KEY']].encode('latin-1'));
					response = make_response(send_file(os.path.join(UPLOAD_PATH, session.get('filename'))))
					response.headers["Content-Disposition"] = "attachment; filename={}".format(session.get('filename').encode().decode('latin-1'))
					session['isDownloaded'] = True
					return response
				#else:
				#	raise ExitException("Terminate by user")
				#except Exception:
				#	print("Error in op1",Exception)
				#	panic()
				#	return redirect('/')
                                
			else:
				print("INVALID")
				panic()
				return redirect('/')
		elif session.get('isOp1') == False and session.get('isOp2') == True:
			if request.method == 'GET':
				return render_template('menu.html')
			elif request.method == 'POST':
				try:
					commitor = request.form.get("commitor")
					commits = request.form.get("commits")
					op2bmp = int(request.form.get("op2bmp"))
					print(commitor,' ',commits)
					if op2bmp > 0 and op2bmp <= 7:
						dict_payload[app.config['SECRET_KEY']]+=str(op2bmp)+'\n'+b64decode(commitor).decode('latin-1')+b64decode(commits).decode('latin-1')
						session['isOp1'] = True
						session['isOp2'] = False
						return render_template('op.html',content = session.get('isColorShowed'))
					else:
						raise FormatException("Error in committing")
				except Exception:
					panic()
					return redirect('/')
			else:
				print("INVALID")
				panic()
				return redirect('/')
	else:
		print("ILLEGAL")
		panic()
		return redirect('/')

if __name__ == '__main__':
	app.run(host='0.0.0.0')
