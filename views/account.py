from tornado.web import RequestHandler
from tornado.concurrent import run_on_executor
import uuid
import hashlib
from config import session_ttl
import tornado
import config
from .base import BlockingBaseHandler
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import parseaddr,formataddr
import datetime

class EmailHandler(BlockingBaseHandler):
    def _format_addr(self,s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    @run_on_executor
    def send_mail(self,email,text):
        msgRoot = MIMEMultipart()
        msgBody = MIMEText(text, 'html')
        msgRoot.attach(msgBody)
        msgRoot['From'] = self._format_addr('{} <{}>'.format(config.site_name,config.smtp_login))
        msgRoot['to'] = Header(email, 'utf8')
        msgRoot['Subject'] = Header('subject', 'utf-8')
        smtp = smtplib.SMTP()
        smtp.connect(config.smtp_hostname)
        smtp.login(config.smtp_login, config.smtp_pass)
        smtp.sendmail(config.smtp_login, [email], msgRoot.as_string())
        smtp.quit()

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


class RegisterHandler(EmailHandler):
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
            u = await self.application.db.users.insert_one({"user_name": email,"email":email,"password":{"salt":user_salt,"hash":user_hash},"is_real":1,"is_active":0,"createTime":datetime.datetime.now()})
            email_code = uuid.uuid4().hex
            email_hashstr =  tornado.escape.utf8(email_code + user_salt + email_code)
            email_hash = hashlib.sha512(email_hashstr).hexdigest()
            email_code = await self.application.db.code.insert_one(
                {"u_id":u['_id'],"type":"email","code":email_code,"createTime":datetime.datetime.now()})
            verify_link = '{}/account/email_verify/?code={}'.format(config.site_domain,email_code)
            #TODO 邮箱html格式
            await self.send_mail(email,verify_link)
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


#TODO 邮箱链接验证
#邮箱验证链接过期后的重新生成

class EmailVerifyHandler(EmailHandler):
    async def get(self):
        await self.send_mail('ttt')