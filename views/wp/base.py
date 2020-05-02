import tornado.web
import logging
from views.base import BlockingHandler,DBMixin

class WpBaseHandler(BlockingHandler,DBMixin):
    async def generate_category_link(self,categorys,language,is_more=False):
        category_dict = {}
        for i, category in enumerate(categorys):
            if language:
                if is_more:
                    category_url = "/category/更多/{}/".format(category) + language + '/'
                else:
                    category_url = "/category/{}/".format(category) + language + '/'
                category_text = await self.cc_async_s2t(category)
            else:
                if is_more:
                    category_url = "/category/更多/{}/".format(category)
                else:
                    category_url = "/category/{}/".format(category)
                category_text = category
            category_dict[i] = [category_url, category_text]
        return category_dict

    async def prepare(self):
        language = self.path_kwargs['language']
        categorys = ['推荐', "热点", "科技", "娱乐", "游戏", "体育", "军事", "汽车", "财经", "搞笑", "视频"]
        categorys_more = ['成长', "文化", "婚恋", "两性", "科普"]
        self.data= {}
        self.data['category_dict'] = await self.generate_category_link(categorys, language)
        self.data['category_more_dict'] = await self.generate_category_link(categorys_more, language, True)
        self.data['language'] = language