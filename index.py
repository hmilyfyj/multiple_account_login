from flask import Flask
from flask import render_template
from oauth2 import APIClient 
from flask import request
from douban_client import DoubanClient
from flask.ext.session import Session
from flask import session
import db


app = Flask(__name__)

# Check Configuration section for more details
#SESSION_TYPE = 'redis'
app.config.from_object(__name__)
#Session(app)
sess=Session()

db.init(db_type = 'mysql', db_schema = 'login_db', db_host = 'localhost', db_port = 3306, db_user = 'root', db_password = '8925')
QQ_APP_KEY = '101225287'
QQ_APP_SECRET = '7c72dc7d60d7f66d5f5eec97119c9c21' 
QQ_CALLBACK_URL = 'http://xuyu.koding.io/qq_callback' # callback url
qq_client=APIClient(app_key=QQ_APP_KEY, 
               app_secret=QQ_APP_SECRET,
               redirect_uri=QQ_CALLBACK_URL,
               domain='graph.qq.com',
               oauth_uri='oauth2.0',
               type='qq') 
               
WB_APP_KEY = '387065349'
WB_APP_SECRET = '95f04f8d7af6ca6a2f278865b3b862c9' 
WB_CALLBACK_URL = 'http://xuyu.koding.io/wb_callback'
#wb_client = APIClient(app_key=WB_APP_KEY, app_secret=WB_APP_SECRET, redirect_uri=WB_CALLBACK_URL) 
wb_client = APIClient(app_key=WB_APP_KEY, 
               app_secret=WB_APP_SECRET,
               redirect_uri=WB_CALLBACK_URL,
               domain='api.weibo.com',
               oauth_uri='oauth2',
               format='json',
               version='2',
               type='sina')


#douban_api
DB_API_KEY = '08dcd104556fb39f1a96730d004f1add'
DB_API_SECRET = '947d66ec23ff7b32' 
DB_CALLBACK_URL = 'http://xuyu.koding.io/db_callback' # callback url
SCOPE = 'douban_basic_common,shuo_basic_r,shuo_basic_w'
db_client = DoubanClient(DB_API_KEY, DB_API_SECRET, DB_CALLBACK_URL, SCOPE)


qq_url = qq_client.get_authorize_url()
wb_url = wb_client.get_authorize_url()
db_url = db_client.authorize_url
print qq_url
print wb_url
print db_url

@app.route('/')
def hello_world():
    return render_template('index.html')
    #session['is_login']=False
    # user=dict(
    #     qq_openid=1,
    #     wb_openid=2,
    #     db_openid=3,
    #     op_count=1
    #     )
    # #db.insert('user', **user)
    # users = db.select('select * from user where id=?',2)
    # if not users:
    #     print 'doesn\'t exist'
    # else:
    #     print users
    #return '<meta property="qc:admins" content="450061555156374167617" />'
    
    return 'success'



def create_new_user(qq_id='',wb_id='',db_id=''):
    op_count=1
    user = dict(
        qq_id=qq_id,
        wb_id=wb_id,
        db_id=db_id,
        op_count=1
        )
    db.insert('user',**user)
    
def bind_other_user(user,type,id):
    user[type]=id
    user['op_count']+=1
    db.update()
    
    
def delete_user(type,id):
    pass

def delete_id(type,id):
    if session['op_count']<2:
	return
    user[type]=''
    user['op_count']-=1
    db.update()

def is_login():
    if session.has_key('is_login'):
        return session['is_login']
    else:
        session['is_login']=False
        return False


   
def logout():
    session['is_login']=False

def login_in(type,id):
    if is_new_user(id):
	    print "new user"
	    if is_login():
	        cur_user=session['user']
	        cur_user[type]=id
	        db.update_kw('user','id=?',cur_user['id'],**cur_user)
	    else:
	        create_new_user(wb_id=id)
	        print "new"
	        login_in(type,id)
	        return 'new'
	        
    user=db.select('select * from user where wb_id=? or qq_id=? or db_id=?',id,id,id)
    print str(id)
    print user
    if user:
    	session['user']=user
    	session['is_login']=True
    	print "login success"
    else:
	    return 'FAIL'


def is_new_user(id):
    if db.select('select * from user where qq_id=? or db_id=? or wb_id=?',id,id,id):
        return False
    else:
        return True
    

@app.route('/wb_7d421e76fdf48306.txt')   
def rrr():
    return 'open.weibo.com'

@app.route('/wb_callback')
def weibo():
    code= request.args['code']
    token = wb_client.request_access_token(code, token_uri='access_token', method='POST')
    result=wb_client.wb_openID(uri='get_token_info')
    print result
    id=result['uid']
    print id
    print type(id)
    #id=id['openid'].encode('utf-8') 
    #print type(id)
    # print is_new_user(id)
    # if is_new_user(id):
    #     add_new_user(wb_openid=id)
    login_in('wb_id',id)
    return 'success'
    

@app.route('/qq_callback')
def qq():
    id=0
    code= request.args['code']
    token = qq_client.request_access_token(code, token_uri='token', method='GET')
    id = qq_client.request_openID() 
    #qq_client.set_request_params(oauth_consumer_key=id.client_id, openid = id.openid, access_token = token.access_token) 
    #userinfo = qq_client.user__get_user_info(format='json')

    print type(id)
    id=id['openid'].encode('utf-8') 
    print type(id)
    print is_new_user(id)
    if is_new_user(id):
        add_new_user(qq_openid=id)
    return 'success'

@app.route('/db_callback')
def say2():
    code=request.args['code']
    db_client.auth_with_code(code)
    token_code = db_client.token_code
    me=db_client.user.me
    id=me['id']
    print id
    print type(id)
    #id=id['openid'].encode('utf-8') 
    #print type(id)
    print is_new_user(id)
    if is_new_user(id):
        add_new_user(db_openid=id)
    return 'success'


if __name__ == '__main__':
    app.secret_key = 'PS#yio`%_!((f_or(%)))s'
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)
    # sess.init_app(app)
    app.run(host='0.0.0.0',port=80)
