from bson import ObjectId

async def get_tname_by_tid(db,t_id):
    term = await db.terms.find_one({'_id': ObjectId(t_id)})
    return term['name']
