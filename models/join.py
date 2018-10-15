async def post_user(posts,db):
    users = [i['user'] for i in posts]
    users = db.users.find({'_id': {'$in': users}})
    user_dict = {}
    async for user in users:
        user_dict[user['_id']] = user
    posts_new = []
    for post in posts:
        post['user'] = user_dict[post['user']]
        post['post_date'] = post['post_date'].strftime("%Y-%m-%d %H:%M")
        posts_new.append(post)
    return posts_new
