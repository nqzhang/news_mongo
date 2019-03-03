def post_time_format(post):
    post['post_date'] = post['post_date'].strftime("%Y-%m-%d %H:%M:%S")
    return post


async def related_sort(terms_id,related_posts,related_type='tags'):
    orders = {}
    for i, term_id in enumerate(terms_id):
        orders[term_id] = i
    sort_key = {}
    for related_post in related_posts:
        order_match_count = -sum(el in  terms_id for el in related_post[related_type])
        order_first = min(orders[t] for t in related_post[related_type] if t in terms_id)
        sort_key[related_post['_id']] = (order_match_count,order_first)
    return sorted(related_posts, key=lambda x: sort_key[x['_id']])