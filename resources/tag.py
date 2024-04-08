from db import db
from models import StoreModel,TagModel, ItemModel
from schemas import TagSchema, TagAndItemSchema
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

blp= Blueprint("Tags","tags", description="Operations on tags")

@blp.route("/store/<int:store_id>/tag")
class TagInStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self,store_id):
        store=StoreModel.query.get_or_404(store_id)

        return store.tags.all()
    
    @blp.arguments(TagSchema)
    @blp.response(201,TagSchema)
    def post(self,tag_data,store_id):
        tag=TagModel(**tag_data,store_id=store_id)

        try:
            db.session.add(tag)
            db.session.commit()

        except SQLAlchemyError as e:
            abort(
                500,
                message=str(e)
            )

        return tag
    

@blp.route("/tag/<int:tag_id>")
class Tag(MethodView):
    @blp.response(200,TagSchema)
    def get(self, tag_id):
        tag=TagModel.query.get_or_404(tag_id)
        return tag
    
    @blp.response(
        202,
        description="Deletes a tag if no item is tagged with it.",
        example={"message":"Tag deleted."}
    )
    @blp.alt_response(404, description="Tag not found.")
    @blp.alt_response(
        400,
        description="Returned if the tag is assigned to one or more items. In this case the tag is not deleted."
    )
    def delete(self,tag_id):
        tag=TagModel.query.get_or_404(tag_id)

        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message":f"Tag:{tag.name} deleted."}
        abort(
            400,
            message="Could not delete tag. Make sure tag is not assosiated with any items, then try again."
        )


@blp.route("/item/<int:item_id>/tag/<int:tag_id>")
class LinkTagsToItem(MethodView):
    @blp.response(201,TagSchema)
    def post(self,item_id,tag_id):
        item=ItemModel.query.get_or_404(item_id)
        tag=TagModel.query.get_or_404(tag_id)


        item.tags.append(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"An error occoured while inserting the tag:{e}")

    @blp.response(200, TagAndItemSchema)
    def remove(self,item_id,tag_id):
        item= ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.remove(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"An error occured while removing the tag:{e}")

        return {"message":"Item removed from tag", "item":item , "tag":tag}
    