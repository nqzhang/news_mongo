from tornado.web import RequestHandler
from tornado.concurrent import run_on_executor
import uuid
import hashlib
from config import session_ttl
import tornado
from tornado.web import authenticated
import config
from .base import BlockingBaseHandler
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import parseaddr,formataddr
import datetime
from .user import UserHander
from bson import ObjectId

reg_text = '''
            感謝您註冊{}!<br/>
            您的登陸郵箱為：{}<br/>
            要啟用帳戶並確認電子郵件地址，請單擊以下鏈接：<br/> 
            <a href='{}'>{}</a><br/>
            (請在30分鐘內完成確認，30分鐘後郵件失效，您將需要重新填寫註冊信息)<br/>
            如果通過點擊以上鏈接無法訪問，請將該網址復制並粘貼至新的瀏覽器窗口中。<br/>
            如果您錯誤地收到了此電子郵件，您無需執行任何操作來取消帳戶！此帳戶將不會啟動。<br/>
            這只是一封公告郵件。我們並不監控或回答對此郵件的回復。'''

pass_reset_text = '''
            尊敬的{}：<br/>
            我們收到了一項請求，要求通過您的電子郵件地址重設您的帳號密碼。<br/>
            請點擊以下鏈接重設您的密碼。<br/>
            <a href='{}'>{}</a><br/>
            (請在30分鐘內完成確認，30分鐘後郵件失效，您將需要重新發起密碼重置請求)<br/>'''

class EmailHandler(BlockingBaseHandler):
    def _format_addr(self,s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))
    def generate_verify_link(self,user_salt):
        email_code = uuid.uuid4().hex
        email_hashstr = tornado.escape.utf8(email_code + user_salt + email_code)
        email_hash = hashlib.sha512(email_hashstr).hexdigest()
        verify_link = '{}/account/email_verify/?code={}'.format(config.site_domain, email_hash)
        return email_hash,verify_link
    def generate_pass_reset_link(self,user_salt):
        email_code = uuid.uuid4().hex
        email_hashstr = tornado.escape.utf8(email_code + user_salt + email_code)
        email_hash = hashlib.sha512(email_hashstr).hexdigest()
        verify_link = '{}/account/password_reset/?code={}'.format(config.site_domain, email_hash)
        return email_hash,verify_link
    @run_on_executor
    def send_mail(self,email,subject,text):
        msgRoot = MIMEMultipart()
        msgBody = MIMEText(text, 'html')
        msgRoot.attach(msgBody)
        msgRoot['From'] = self._format_addr('{} <{}>'.format(config.site_name,config.smtp_login))

        msgRoot['to'] = Header(email, 'utf8')
        msgRoot['Subject'] = subject
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
            self.set_secure_cookie('sessionid',sessionid,domain=config.cookie_domain)
            self.set_secure_cookie('sig', sig,domain=config.cookie_domain)
            self.set_secure_cookie('uid', user_id,domain=config.cookie_domain)
            self.redirect(next)
        else:
            self.write('密码错误')
        #salt = uuid.uuid4().hex

        #self.set_secure_cookie("username", self.get_argument("username"))
        #self.redirect("/")
        #self.write(email + passwd)

class LogoutHandler(UserHander):
    @authenticated
    async def get(self):
        next = self.get_argument('next', '/')
        user_id = self.current_user.decode()
        self.clear_cookie('sessionid',domain=config.cookie_domain)
        self.clear_cookie('sig',domain=config.cookie_domain)
        self.clear_cookie('uid',domain=config.cookie_domain)
        await self.application.redis.delete(user_id)
        self.redirect(next)

class RegisterHandler(EmailHandler):
    async def get(self):
        self.render('page/register.html',config=config)
    async def post(self):
        next = self.get_query_argument('src','/')
        email = self.get_argument('email')
        passwd = self.get_argument('passwd')
        userAgent = self.request.headers['user-agent']
        url = self.request.path
        x = self.get_cookie("_xsrf")
        verify_str = userAgent + url + x + email + passwd
        def md5(str):
            str = str.encode('utf-8')
            import hashlib
            m = hashlib.md5()
            m.update(str)
            return m.hexdigest()
        if md5(verify_str) != self.get_argument('verify'):
            raise tornado.web.HTTPError(500, reason='register blocked')
        if not email:
            self.set_status(500,'请输入邮箱')
            self.write('请输入邮箱<br/>')
        if not passwd:
            self.set_status(500,'请输入密码')
            self.write('请输入密码<br/>')
        if not email or not passwd:
            return
        user = await self.application.db.users.find_one({'email':email,"is_real":1})
        if not user:
            user_salt = uuid.uuid4().hex
            hashstr = tornado.escape.utf8(passwd + user_salt)
            user_hash = hashlib.sha512(hashstr).hexdigest()
            user_name = email.split('@')[0]
            u = await self.application.db.users.insert_one({"user_name": user_name,"email":email,"password":{"salt":user_salt,"hash":user_hash},"is_real":1,"is_active":0,"createTime":datetime.datetime.now()})
            email_hash,verify_link = self.generate_verify_link(user_salt)
            u_id = str(u.inserted_id)
            email_code = await self.application.db.code.insert_one({"u_id": ObjectId(u_id), "type": "email_verify", "code": email_hash,"is_used":0,"createTime": datetime.datetime.now()})
            #註冊后登陸
            sessionid = uuid.uuid4().hex
            hashstr = tornado.escape.utf8(sessionid + user_salt + u_id)
            await self.application.redis.set(u_id, user_salt, expire=session_ttl)
            sig = hashlib.sha512(hashstr).hexdigest()
            self.set_secure_cookie('sessionid',sessionid,domain=config.cookie_domain)
            self.set_secure_cookie('sig', sig,domain=config.cookie_domain)
            self.set_secure_cookie('uid', u_id,domain=config.cookie_domain)
            self.render('page/register_success.html', config=config)
            email_text = reg_text.format(config.site_name,email,verify_link,verify_link)
            subject = Header('[{}]註冊確認'.format(config.site_name), 'utf-8')
            await self.send_mail(email, subject, email_text)
        else:
            self.write('邮箱已存在')
            #salt = uuid.uuid4().hex


        #self.set_secure_cookie("username", self.get_argument("username"))
        #self.redirect("/")
        #self.write(email + passwd)
class PasswordForgotHandler(EmailHandler):
    async def get(self):
        self.render('page/password_forgot.html',config=config)

class PasswordResetHandler(EmailHandler):
    async def get(self):
        self.render('page/password_reset.html',config=config)

class ApiPasswordResetHandler(EmailHandler):
    async def post(self):
        email_hash = self.get_argument('code')
        email_code = await self.application.db.code.find_one({"code": email_hash})
        passwd = self.get_argument('passwd')
        if email_code:
            if email_code['createTime'] - datetime.datetime.now() > datetime.timedelta(seconds=1800):
                self.write('链接已失效')
            elif email_code['is_used'] == 1:
                self.write('链接已失效')
            else:
                if email_code['type'] == 'email_pass_reset':
                    u_id = email_code['u_id']
                    u = await self.application.db.users.find_one({'_id': u_id})
                    user_salt = u['password']['salt']
                    hashstr = tornado.escape.utf8(passwd + user_salt)
                    user_hash = hashlib.sha512(hashstr).hexdigest()
                    await self.application.db.users.update_one({"_id":email_code['u_id']},{"$set": {"password.hash":user_hash}})
                    #await self.application.db.code.update_one({"code": email_hash}, {"$set": {"is_used": 1}})
                    self.write('密码重置成功')
        else:
            self.write('验证链接无效')

class IsEmailExistHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass
    async def post(self,email):
        user = await self.application.db.users.find_one({'email': email})
        if user:
            self.write('郵箱已經註冊')
        else:
            self.write('郵箱可用')


class EmailVerifyHandler(EmailHandler):
    async def get(self):
        email_hash = self.get_argument('code')
        email_code = await self.application.db.code.find_one({"code": email_hash})
        if email_code:
            if email_code['createTime'] - datetime.datetime.now() > datetime.timedelta(seconds=1800):
                self.write('链接已失效')
            elif email_code['is_used'] == 1:
                self.write('链接已失效')
            else:
                if email_code['type'] == 'email_verify':
                    await self.application.db.users.update_one({"_id":email_code['u_id']},{"$set": {"is_active":1}})
                    await self.application.db.code.update_one({"code": email_hash}, {"$set": {"is_used": 1}})
                    self.write('激活成功')
        else:
            self.write('验证链接无效')

class EmailResendHandler(EmailHandler,UserHander):
    @authenticated
    async def get(self):
        self.write('郵件已重新發送')
        u_id = self.current_user.decode()
        u = await self.application.db.users.find_one({'_id':ObjectId(u_id)})
        email_hash, verify_link = self.generate_verify_link(u['password']['salt'])
        email=u['email']
        email_text = reg_text.format(config.site_name, email, verify_link, verify_link)
        email_code = await self.application.db.code.replace_one({'u_id': u['_id']},
                                                                {"u_id": u['_id'], "type": "email_verify", "code": email_hash,"is_used":0, "createTime": datetime.datetime.now()},upsert=True)
        subject = Header('[{}]註冊確認'.format(config.site_name), 'utf-8')
        await self.send_mail(u['email'], subject, email_text)

class PasswordForgotSendMailHandler(EmailHandler,UserHander):
    async def post(self):
        self.render('page/password_forgot_send_mail_success.html',config=config)
        email = self.get_argument('email')
        u = await self.application.db.users.find_one({'email':email})
        u_id = u['_id']
        user_salt = uuid.uuid4().hex
        email_hash, verify_link = self.generate_pass_reset_link(user_salt)
        email_code = await self.application.db.code.insert_one(
            {"u_id": ObjectId(u_id), "type": "email_pass_reset", "code": email_hash, "is_used": 0,
             "createTime": datetime.datetime.now()})
        email_text = pass_reset_text.format(email,verify_link, verify_link)
        subject = Header('[{}]密碼重設確認'.format(config.site_name), 'utf-8')
        await self.send_mail(email, subject, email_text)