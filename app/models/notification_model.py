from datetime import datetime
from app.extensions import mongo
from bson.objectid import ObjectId

class Notification:
    @staticmethod
    def create(user_id, message, exercise_id=None):
        notification = {
            'user_id': user_id,
            'message': message,
            'created_at': datetime.utcnow(),
            'is_read': False,
        }
        if exercise_id:
            notification['exercise_id'] = exercise_id
        mongo.db.notifications.insert_one(notification)

    @staticmethod
    def get_unread(user_id):
        return list(mongo.db.notifications.find({'user_id': user_id, 'is_read': False}))

    @staticmethod
    def mark_all_read(user_id):
        mongo.db.notifications.update_many({'user_id': user_id, 'is_read': False}, {'$set': {'is_read': True}})

    @staticmethod
    def get_all(user_id):
        return list(mongo.db.notifications.find({'user_id': user_id}).sort('created_at', -1))

    @staticmethod
    def mark_read(notification_id, user_id):
        mongo.db.notifications.update_one(
            {'_id': ObjectId(notification_id), 'user_id': user_id},
            {'$set': {'is_read': True}}
        )

    @staticmethod
    def get_unread_sorted(user_id, limit=5):
        return list(mongo.db.notifications.find({'user_id': user_id, 'is_read': False}).sort('created_at', -1).limit(limit))

    @staticmethod
    def get_paginated(user_id, skip=0, limit=5):
        return list(mongo.db.notifications.find({'user_id': user_id}).sort('created_at', -1).skip(skip).limit(limit))

    @staticmethod
    def get_latest_per_exercise(user_id, limit=5):
        # Aggregate to get the latest UNREAD notification for each exercise_id
        pipeline = [
            {'$match': {'user_id': user_id, 'is_read': False}},
            {'$sort': {'created_at': -1}},
            {'$group': {
                '_id': '$exercise_id',
                'doc': {'$first': '$$ROOT'}
            }},
            {'$replaceRoot': {'newRoot': '$doc'}},
            {'$sort': {'created_at': -1}},
            {'$limit': limit}
        ]
        return list(mongo.db.notifications.aggregate(pipeline)) 