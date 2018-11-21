def post_time_format(post):
    post['post_date'] = post['post_date'].strftime("%Y-%m-%d %H:%M:%S")
    return post