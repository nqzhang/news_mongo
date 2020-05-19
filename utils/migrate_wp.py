import pymysql.cursors
from pymongo import MongoClient
from bson import ObjectId
import json
from collections import defaultdict
import requests
import traceback
from multiprocessing import Process


class myprocess(Process):
    def __init__(self, start_id, end_id, i):
        super(myprocess, self).__init__()
        self.start_id = start_id
        self.end_id = end_id
        self.process_num = i

    def run(self):
        conn = pymysql.connect(host='195.201.164.101',
                               user='root',
                               password='11QQqqWW',
                               db='news.xuehua.us',
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cur:
            print(self.start_id, self.end_id)
            while self.start_id < self.end_id:
                post_sql = 'SELECT * FROM wp_posts where ID >={} and ID < {} and  ' \
                           'post_type="post" and post_status="publish"'.format(self.start_id, self.start_id + 1000)
                cur.execute('SET SESSION MAX_STATEMENT_TIME=300;')
                cur.execute(post_sql)
                posts = cur.fetchall()
                if posts:
                    posts_id = ','.join([str(x['ID']) for x in posts])
                    post_users = ','.join([str(x['post_author']) for x in posts])
                    post_term_sql = 'SELECT p.ID,r.term_taxonomy_id,t.taxonomy,wt.* FROM wp_posts p INNER JOIN wp_term_relationships r ON r.object_id = p.ID ' \
                                    'INNER JOIN wp_term_taxonomy t ON t.term_taxonomy_id = r.term_taxonomy_id ' \
                                    'INNER JOIN wp_terms wt ON wt.term_id = t.term_id WHERE ' \
                                    'p.ID in ({})'.format(posts_id)

                    cur.execute(post_term_sql)
                    post_terms = cur.fetchall()
                    post_categorys = [i for i in post_terms if i['taxonomy'] == "category"]
                    post_tags = [i for i in post_terms if i['taxonomy'] == "post_tag"]
                    tmp_d = defaultdict(lambda: defaultdict(list))
                    for x in post_terms:
                        if x['taxonomy'] == "category":
                            tmp_d[x['ID']]['category'].append(x)
                        elif x['taxonomy'] == "post_tag":
                            tmp_d[x['ID']]['tags'].append(x)
                    post_user_sql = "SELECT ID,display_name from wp_users where ID in ({})".format(post_users)
                    cur.execute(post_user_sql)
                    post_users = cur.fetchall()
                    tmp_u = {}
                    for x in post_users:
                        tmp_u[x['ID']] = x
                    # print(tmp_u)
                    for x in posts:
                        try:
                            x['code'] = 'qtRjhwcGLHnXPQlC'
                            x['post_type'] = 'article'
                            x['category'] = [y['name'] for y in tmp_d[x['ID']]['category']]
                            x['tags'] = [y['name'] for y in tmp_d[x['ID']]['tags']]
                            x['title'] = x.pop('post_title')
                            x['content'] = x.pop('post_content')
                            x['user'] = tmp_u[x['post_author']]['display_name']
                            x['post_date'] = x['post_date'].strftime("%Y-%m-%d %H:%M:%S")
                            requests.post('http://tmp.xuehua.us/backend/newpost', data=json.dumps(x, default=str))
                        except Exception as e:
                            traceback.print_exc()
                self.start_id += 1000
                print('进程' + str(self.process_num), self.start_id, self.end_id)


if __name__ == '__main__':
    conn = pymysql.connect(host='195.201.164.101',
                           user='root',
                           password='11QQqqWW',
                           db='news.xuehua.us',
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    with conn.cursor() as cur:
        cur.execute("select max(ID) from wp_posts")
        end_id = (cur.fetchone())['max(ID)']
        cur.execute("select min(ID) from wp_posts")
        start_id = (cur.fetchone())['min(ID)']

    s = (end_id - start_id) // 20
    process_list = []

    for i in range(1, 21):  # 开启5个子进程执行fun1函数
        p = myprocess(s * (i - 1), s * i, i)  # 实例化进程对象
        p.start()
        process_list.append(p)

    for p in process_list:
        p.join()

    print('结束测试')
