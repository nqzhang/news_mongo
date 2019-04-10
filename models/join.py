#传入的posts是多个post的列表
async def post_user(posts,db):
    users = [i['user'] for i in posts]
    users = db.users.find({'_id': {'$in': users}})
    user_dict = {}
    async for user in users:
        user_dict[user['_id']] = user
    posts_new = []
    for post in posts:
        try:
            post['user'] = user_dict[post['user']]
            post['post_date'] = post['post_date'].strftime("%Y-%m-%d %H:%M")
        except:
            continue
        posts_new.append(post)
    return posts_new

#传入的posts是单个post的字典
async def post_tags(post,db):
    tags = [x for x in post['tags']]
    tags = db.terms.find({'_id': {'$in': tags}})
    tag_dict = {}
    async for tag in tags:
        tag_dict[tag['_id']] = tag
    post['tags'] = [tag_dict[i] for i in post['tags']]
    return post

#传入的posts是单个post的字典
async def post_category(post,db):
    category = [x for x in post['category']]
    category = db.terms.find({'_id': {'$in': category}})
    category_dict = {}
    async for category in category:
        category_dict[category['_id']] = category
    post['category'] = [category_dict[i] for i in post['category']]
    return post

