from config import db, ma
from marshmallow.fields import *
from datetime import datetime


class Plan(db.Model):
    __tablename__ = "lss_plan"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(225), nullable=False)
    description = db.Column(db.Text, nullable=True)
    max_items = db.Column(db.Integer, nullable=True)
    max_campaign = db.Column(db.Integer, nullable=True)
    max_campaign_time = db.Column(db.Float, nullable=True)
    max_product_sold = db.Column(db.Integer, nullable=True)
    max_product_uploads = db.Column(db.Integer, nullable=True)
    max_transaction = db.Column(db.Integer, nullable=True)
    max_transaction_amount = db.Column(db.Float, nullable=True)
    max_payment_gateway = db.Column(db.Integer, nullable=True)
    max_delivery = db.Column(db.Integer, nullable=True)
    max_report = db.Column(db.Integer, nullable=True)
    max_region = db.Column(db.Integer, nullable=True)
    max_server_usage = db.Column(db.JSON, nullable=True)

    def __init__(self,
                 name,
                 description,
                 max_items,
                 max_campaign,
                 max_campaign_time,
                 max_product_sold,
                 max_product_uploads,
                 max_transaction,
                 max_transaction_amount,
                 max_payment_gateway,
                 max_delivery,
                 max_report,
                 max_region,
                 max_server_usage):

        self.name = name
        self.description = description
        self.max_items = max_items
        self.max_campaign = max_campaign
        self.max_campaign_time = max_campaign_time
        self.max_product_sold = max_product_sold
        self.max_product_uploads = max_product_uploads
        self.max_transaction = max_transaction
        self.max_transaction_amount = max_transaction_amount
        self.max_payment_gateway = max_payment_gateway
        self.max_delivery = max_delivery
        self.max_report = max_report
        self.max_region = max_region
        self.max_server_usage = max_server_usage


class PlanSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('id',
                  'name',
                  'description',
                  'max_items',
                  'max_campaign',
                  'max_campaign_time',
                  'max_product_sold',
                  'max_product_uploads',
                  'max_transaction',
                  'max_transaction_amount',
                  'max_payment_gateway',
                  'max_delivery',
                  'max_report',
                  'max_region',
                  'max_server_usage')

        id = Integer()
        name = Str()
        description = Str()
        max_items = Integer()
        max_campaign = Integer()
        max_campaign_time = Float()
        max_product_sold = Integer()
        max_product_uploads = Integer()
        max_transaction = Integer()
        max_transaction_amount = Float()
        max_payment_gateway = Integer()
        max_delivery = Integer()
        max_report = Integer()
        max_region = Integer()
        max_server_usage = Str()


class PlanGroup(db.Model):
    __tablename__ = "lss_plan_group"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(225), nullable=False)
    description = db.Column(db.Text, nullable=True)
    plan_id = db.Column(db.Integer, db.ForeignKey(
        "lss_plan.id"), nullable=True)

    def __init__(self,
                 name,
                 description,
                 plan_id):

        self.name = name
        self.description = description
        self.plan_id = plan_id


class PlanGroupSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('id',
                  'name',
                  'description',
                  'plan_id')

        id = Integer()
        name = Str()
        description = Str()
        plan_id = Integer()


class PlanGroupUsers(db.Model):
    __tablename__ = "lss_plan_group_users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    plan_group_id = db.Column(db.Integer, db.ForeignKey(
        "lss_plan_group.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        "lss_user.id"), nullable=False)
    user_type = db.Column(db.String(255), nullable=False, default='')

    __table_args__ = (
        db.UniqueConstraint(plan_group_id, user_id),
    )

    def __init__(self,
                 plan_group_id,
                 user_id,
                 user_type):

        self.plan_group_id = plan_group_id
        self.user_id = user_id
        self.user_type = user_type


class PlanGroupUsersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('id',
                  'plan_group_id',
                  'user_id',
                  'user_type')

        id = Integer()
        plan_group_id = Integer()
        user_id = Integer()
        user_type = Str()


class PlanGroupItems(db.Model):
    __tablename__ = "lss_plan_group_items"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    plan_group_id = db.Column(db.Integer, db.ForeignKey(
        "lss_plan_group.id"), nullable=False)
    item_id = db.Column(db.String(225), nullable=False)
    item_type = db.Column(db.String(225), nullable=False)

    __table_args__ = (
        db.UniqueConstraint(plan_group_id, item_id),
    )

    def __init__(self,
                 plan_group_id,
                 item_id,
                 item_type):

        self.plan_group_id = plan_group_id
        self.item_id = item_id
        self.item_type = item_type


class PlanGroupItemsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('id',
                  'plan_group_id',
                  'item_id',
                  'item_type')

        id = Integer()
        plan_group_id = Integer()
        item_id = Str()
        item_type = Str()
