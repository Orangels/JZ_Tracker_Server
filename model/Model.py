from mongoengine import *


# 人员 face
class Person(Document):
    meta = {
        'collection': 'face'
    }
    id_ = IntField(db_field='id')
    _id = ObjectIdField()
    time = IntField()
    feature = ListField()
    path = StringField()
    name = StringField()


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