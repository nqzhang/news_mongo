from tornado.web import RequestHandler
import uuid
import hashlib
from config import session_ttl
import tornado
import config

class LoginHandler(RequestHandler):
    async def post(self):
        next = self.get_argument('src','/')
        email = self.get_argument('email')
        passwd = self.get_argument('passwd')
        user = await self.application.db.users.find_one({'email':email,"is_real":1})
        user_salt = user['password']['salt']
        user_hash = user['password']['hash']
        user_id = str(user['_id'])
        hashstr = tornado.escape.utf8(passwd + user_salt)
        if hashlib.sha512(hashstr).hexdigest() == user_hash:
            sessionid = uuid.uuid4().hex
            hashstr = tornado.escape.utf8(sessionid + user_salt + user_id)
            await self.application.redis.set(user_id, user_salt,expire=session_ttl)
            sig = hashlib.sha512(hashstr).hexdigest()
            print(sig)
            self.set_secure_cookie('sessionid',sessionid)
            self.set_secure_cookie('sig', sig)
            self.set_secure_cookie('uid', user_id)
            self.redirect(next)
        else:
            self.write('密码错误')
        #salt = uuid.uuid4().hex

        #self.set_secure_cookie("username", self.get_argument("username"))
        #self.redirect("/")
        #self.write(email + passwd)


class RegisterHandler(RequestHandler):
    async def get(self):
        self.render('register.html',config=config)
    async def post(self):
        next = self.get_query_argument('src','/')
        email = self.get_argument('email')
        passwd = self.get_argument('passwd')
        user = await self.application.db.users.find_one({'email':email,"is_real":1})
        if not user:
            user_salt = uuid.uuid4().hex
            hashstr = tornado.escape.utf8(passwd + user_salt)
            user_hash = hashlib.sha512(hashstr).hexdigest()
            u = await self.application.db.users.insert_one({"user_name": email,"email":email,"password":{"salt":user_salt,"hash":user_hash},"is_real":1})
            self.render('register_success.html')
        else:
            self.write('邮箱已存在')
            #salt = uuid.uuid4().hex


        #self.set_secure_cookie("username", self.get_argument("username"))
        #self.redirect("/")
        #self.write(email + passwd)

class IsEmailExistHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass
    async def post(self,email):
        user = await self.application.db.users.find_one({'email': email})
        if user:
            self.write('郵箱已經註冊')
        else:
            self.write('郵箱可用')

