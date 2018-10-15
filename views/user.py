from views.base import UserHander
import tornado.web
from views.base import authenticated_async
import datetime

class PostEditHandler(UserHander):
    @authenticated_async
    async def get(self):
        #print(self.current_user)
        self.render('user/postedit.html')


class PostAjaxHandler(UserHander):
    @authenticated_async
    async def post(self):
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(self.current_user)
        print(self.get_argument('title'))
        print(self.get_argument('content'))
        print(self.get_argument('tags'))
        print(self.get_argument('category_person'))
        print(self.get_argument('category_site'))
        print(self.get_argument('category'))

        self.write('qqq')