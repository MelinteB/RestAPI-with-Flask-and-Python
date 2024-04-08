import uuid
from flask import request
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from schemas import StoreSchema,StoreUpdateSchema
from db import db
from models import StoreModel
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
blp=Blueprint("stores",__name__,description="Operations on stores")

@blp.route("/store/<int:store_id>")
class Store(MethodView):
    @jwt_required()
    @blp.response(200,StoreSchema)
    def get(self,store_id):
        store=StoreModel.query.get_or_404(store_id)
        return store
    
    @jwt_required()
    def delete(self,store_id):
        store=StoreModel.query.get(store_id)
        store_name=store.name
        db.session.delete(store)
        db.session.commit()
        return f"message=Store:*{store_name}* deleted!"

    @jwt_required()
    @blp.arguments(StoreUpdateSchema)
    @blp.response(201, StoreSchema)
    def put(self,store_data,store_id):
        store=StoreModel.query.get(store_id)
        
        if store:
            store.name=store_data["name"]
        else:
            store=StoreModel(id=store_id,**store_data)

        db.session.add(store)
        db.session.commit()
        return store

@blp.route("/store")
class StoreList(MethodView):
    @jwt_required()
    @blp.response(200,StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()  
    
    @jwt_required()
    @blp.arguments(StoreSchema)
    @blp.response(201,StoreSchema)
    def post(self,store_data):
        store= StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(400, message="A store with that name already exists.")
        except SQLAlchemyError:
            abort(500, message="Error occurs when tring to create the store.")
        
        return store,201