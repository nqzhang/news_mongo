from bson import ObjectId
import datetime
import time, math

def hot_calc (post_views, post_comments, post_score, post_comments_score, post_age, post_updated):
    post_age = round(post_age / 3600)
    post_updated = round(post_updated/ 3600)
    return (math.log10(post_views + 1) * 4 + (post_comments + 1) * (post_score + 1) / 5 + post_comments_score )/(pow((post_age + 1) - (post_age - post_updated) / 2,1.5))

async def hot(db,post_id):
    date_now = datetime.datetime.now()
    post = await db.posts.find_one({ "_id": ObjectId(post_id)},{ "_id": 0,"views": 1 ,"like":1,"post_date":1})
   # 取该文章浏览量
    post_views = int(post.get('views',0))
    post_date = post.get('post_date')
    post_age = (date_now - post_date).total_seconds()
    #计算文章点赞和踩的差
    if "like" not in post:
        post_score = 0
    else:
        post_like  = post['like'].get('article_like',0)
        post_unlike = post['like'].get('article_unlike',0)
        post_score = post_like - post_unlike
    #post_comments = await db.comments.count({"post_id":post_id,"reply_to" : { "$exists" : False }})
    #取该文章所有评论数量
    post_comments = await db.comments.count({"post_id":post_id})

    #计算该文章所有评论的点赞和踩的差 post_comments_score
    post_comments_score =  await db.comments.aggregate([{"$match":{"post_id": post_id}},
                                                        {"$group": {"_id": "$post_id","CommentsLikeScore": {"$sum": "$like.comment_like"},
                                                                    "CommentsUnlikeScore": {"$sum": "$like.comment_unlike"}}}]).to_list(length=None)
    if post_comments_score:
        post_comments_score = post_comments_score[0]
        post_comments_like_score = post_comments_score.get('CommentsLikeScore',0)
        post_comments_unlike_score = post_comments_score.get('CommentsUnlikeScore',0)
        post_comments_score = post_comments_like_score - post_comments_unlike_score
    else:
        post_comments_score = 0
    post_updated =   await db.comments.aggregate([{"$match":{"post_id": post_id,"reply_to" : { "$exists" : False }}},
                                                    {"$group": {"_id": "$post_id","post_updated": {"$max": "$comment_date"},}}]).to_list(length=None)
    if post_updated:
        post_updated = post_updated[0]['post_updated']
        post_updated = (date_now - post_updated).total_seconds()
    else:
        post_updated = post_age
    #print(post_views,post_comments,post_score,post_comments_score,post_age,post_updated)
    post_score = hot_calc(post_views,post_comments,post_score,post_comments_score,post_age,post_updated)

    await db.posts.update_one({'_id': ObjectId(post_id)}, {"$set": {"score":post_score}})
    print(post_score)
    return post_score
    #post_views,post_comments,post_score,post_date

