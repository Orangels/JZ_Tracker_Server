from .db import *

# 人员 face
class Person(db_eng.Document):
    meta = {
        'collection': 'face'
    }
    _id = db_eng.ObjectIdField()
    personID = db_eng.IntField(db_field='id')
    registerTime = db_eng.IntField(db_field='time')
    feature = db_eng.ListField(db_field='feature')
    imgPath = db_eng.StringField(db_field='path')
    name = db_eng.StringField(db_field='name')


# 自定义函数
# 序列化处理，排除指定字段
def m2d_exclude(obj, _id='_id', *args):
    model_dict = obj.to_mongo().to_dict()
    if _id:
        list(map(model_dict.pop, [_id]))
    if args:
        list(map(model_dict.pop, list(args)))
    if "_id" in model_dict.keys():
        model_dict["_id"] = str(model_dict["_id"])
    return model_dict