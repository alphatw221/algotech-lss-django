from config import db, ma
from marshmallow.fields import *
from datetime import datetime


class FBCampaign(db.Model):
    __tablename__ = "lss_fb_campaign"

    fb_campaign_id = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    fb_page_id = db.Column(db.String(50), nullable=False)
    fb_post_id = db.Column(db.String(50), nullable=True)
    fb_live_video_id = db.Column(db.String(50), nullable=True)
    embed_url = db.Column(db.Text, nullable=True)
    title = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    fb_user_id_added = db.Column(db.String(50), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.now)
    date_modified = db.Column(
        db.DateTime, nullable=False, onupdate=datetime.now, default=datetime.now)

    def __init__(self, fb_page_id, fb_post_id, fb_live_video_id, embed_url, title, description,
                 status, start_time, end_time, fb_user_id_added):
        self.fb_page_id = fb_page_id
        self.fb_post_id = fb_post_id
        self.fb_live_video_id = fb_live_video_id
        self.embed_url = embed_url
        self.title = title
        self.description = description
        self.status = status
        self.start_time = start_time
        self.end_time = end_time
        self.fb_user_id_added = fb_user_id_added


class CampaignMeta(db.Model):
    __tablename__ = "lss_fb_campaign_meta"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fb_campaign_id = db.Column(db.Integer, db.ForeignKey(
        "lss_fb_campaign.fb_campaign_id"), nullable=False)
    meta_key = db.Column(db.String(225), nullable=False)
    meta_value = db.Column(db.Text, nullable=True)

    def __init__(self,
                 fb_campaign_id,
                 meta_key,
                 meta_value):

        self.fb_campaign_id = fb_campaign_id
        self.meta_key = meta_key
        self.meta_value = meta_value


class CampaignMetaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('id',
                  'fb_campaign_id',
                  'meta_key',
                  'meta_value')

        id = Integer()
        fb_campaign_id = Integer()
        meta_key = Str()
        meta_value = Str()


class FBCampaignSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('fb_campaign_id', 'fb_page_id', 'fb_post_id', 'fb_live_video_id', 'embed_url', 'title', 'description',
                  'status', 'start_time', 'end_time', 'fb_user_id_added', 'date_added', 'date_modified')

        fb_campaign_id = Integer()
        fb_page_id = Str()
        fb_post_id = Str()
        fb_live_video_id = Str()
        embed_url = Str()
        title = Str()
        description = Str()
        status = Str()
        start_time = DateTime()
        end_time = DateTime()
        fb_user_id_added = Str()
        date_added = DateTime()
        date_modified = DateTime()


class FBCampaignProduct(db.Model):
    __tablename__ = "lss_fb_campaign_product"

    fb_campaign_id = db.Column(db.Integer, db.ForeignKey(
        "lss_fb_campaign.fb_campaign_id"), primary_key=True)
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True, default="")
    order_code = db.Column(db.String(50), nullable=False)
    product_type = db.Column(db.String(50), nullable=True)
    product_quantity = db.Column(
        db.Integer, nullable=False, default=0)
    product_order_amount = db.Column(
        db.Integer, nullable=False, default=0)
    max_order_amount = db.Column(db.Integer, default=0)
    customer_removable = db.Column(db.Boolean, nullable=False, default=False)
    customer_editable = db.Column(db.Boolean, nullable=False, default=False)
    product_active_stat = db.Column(
        db.Integer, nullable=False, default=0)

    def __init__(self, fb_campaign_id, product_id, name, order_code, product_type,
                 product_quantity, product_order_amount, max_order_amount, customer_removable, customer_editable, product_active_stat):
        self.fb_campaign_id = fb_campaign_id
        self.product_id = product_id
        self.name = name
        self.order_code = order_code
        self.product_type = product_type
        self.product_quantity = product_quantity
        self.product_order_amount = product_order_amount
        self.max_order_amount = max_order_amount
        self.customer_removable = customer_removable
        self.customer_editable = customer_editable
        self.product_active_stat = product_active_stat


class FBCampaignProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('fb_campaign_id', 'product_id', 'name', 'order_code', 'product_type',
                  'product_quantity', 'product_order_amount', 'max_order_amount', 'customer_removable', 'customer_editable', 'product_active_stat')

        fb_campaign_id = Integer()
        product_id = Integer()
        name = Str()
        order_code = Str()
        product_type = Str()
        product_quantity = Integer()
        product_order_amount = Integer()
        max_order_amount = Integer()
        customer_removable = Boolean()
        customer_editable = Boolean()
        product_active_stat = Integer()


class FBCampaignOrder(db.Model):
    __tablename__ = "lss_fb_campaign_order"

    id = db.Column(db.Integer, primary_key=True)
    fb_campaign_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    fb_user_id = db.Column(db.Text, nullable=False)
    fb_user_name = db.Column(db.Text, nullable=False)
    order_qty = db.Column(db.Integer, nullable=False)
    order_code = db.Column(db.Text, nullable=False)
    comment_id = db.Column(db.Text, nullable=False)
    comment_message = db.Column(db.Text, nullable=False)
    comment_created_time = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.Integer, nullable=True, default=0)
    order_stat = db.Column(db.Text, nullable=False)

    def __init__(self, fb_campaign_id, product_id, fb_user_id, fb_user_name, order_qty,
                 order_code, comment_id, comment_message, comment_created_time, order_stat):
        self.fb_campaign_id = fb_campaign_id
        self.product_id = product_id
        self.fb_user_id = fb_user_id
        self.fb_user_name = fb_user_name
        self.order_qty = order_qty
        self.order_code = order_code
        self.comment_id = comment_id
        self.comment_message = comment_message
        self.comment_created_time = comment_created_time
        self.order_stat = order_stat


class FBCampaignOrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('id', 'fb_campaign_id', 'product_id', 'fb_user_id', 'fb_user_name',
                  'order_qty', 'order_code', 'comment_id', 'comment_message', 'comment_created_time', 'order_id', 'order_stat')

        id = Integer()
        fb_campaign_id = Integer()
        product_id = Integer()
        fb_user_id = Str()
        fb_user_name = Str()
        order_qty = Integer()
        order_code = Str()
        comment_id = Str()
        comment_message = Str()
        comment_created_time = Integer()
        order_id = Integer()
        order_stat = Str()


class FBLuckyDraw(db.Model):
    __tablename__ = "lss_fb_campaign_lucky_draw"

    fb_lucky_draw_id = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    fb_campaign_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=True)
    order_code = db.Column(db.Text, nullable=True)
    prize_product_id = db.Column(db.Integer, nullable=True)
    num_of_winner = db.Column(db.Integer, nullable=False)
    candidate_set = db.Column(db.Text, nullable=False)
    winner_list = db.Column(db.Text, nullable=False)
    event_created_time = db.Column(
        db.DateTime, nullable=False, default=datetime.now)

    def __init__(self, fb_campaign_id, product_id, order_code, prize_product_id,
                 num_of_winner, candidate_set, winner_list, ):
        self.fb_campaign_id = fb_campaign_id
        self.product_id = product_id
        self.order_code = order_code
        self.prize_product_id = prize_product_id
        self.num_of_winner = num_of_winner
        self.candidate_set = candidate_set
        self.winner_list = winner_list


class FBLuckyDrawSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('fb_campaign_id', 'product_id', 'order_code', 'prize_product_id',
                  'num_of_winner', 'candidate_set', 'winner_list', 'event_created_time')

        fb_campaign_id = Integer()
        product_id = Integer()
        order_code = Str()
        prize_product_id = Integer()
        num_of_winner = Integer()
        candidate_set = Str()
        winner_list = Str()
        event_created_time = DateTime()


class FBCampaignComment(db.Model):
    __tablename__ = "lss_fb_campaign_comment"

    fb_campaign_id = db.Column(db.Integer, primary_key=True)
    fb_comment_id = db.Column(db.String(100), primary_key=True)
    fb_user_id = db.Column(db.Text, nullable=False, default='')
    fb_user_name = db.Column(db.Text, nullable=False, default='')
    message = db.Column(db.Text, nullable=False, default='')
    created_time = db.Column(db.Integer, nullable=False, default='')
    picture_url = db.Column(db.String(512), nullable=False, default='')

    def __init__(self, fb_campaign_id, fb_comment_id, fb_user_id, fb_user_name,
                 message, created_time, picture_url):
        self.fb_campaign_id = fb_campaign_id
        self.fb_comment_id = fb_comment_id
        self.fb_user_id = fb_user_id
        self.fb_user_name = fb_user_name
        self.message = message
        self.created_time = created_time
        self.picture_url = picture_url


class FBCampaignCommentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('fb_campaign_id', 'fb_comment_id', 'fb_user_id', 'fb_user_name',
                  'message', 'created_time', 'picture_url')

        fb_campaign_id = Integer()
        fb_comment_id = Str()
        fb_user_id = Str()
        fb_user_name = Str()
        message = Str()
        order_code = Str()
        created_time = Integer()
        picture_url = Str()


class FBCampaignStat(db.Model):
    __tablename__ = "lss_fb_campaign_stat"

    fb_campaign_id = db.Column(db.Integer, db.ForeignKey(
        "lss_fb_campaign.fb_campaign_id"), primary_key=True)
    total_orders = db.Column(db.Integer, nullable=True, default=0)
    total_revenue = db.Column(db.Float, nullable=True, default=0)
    paid_orders = db.Column(db.Integer, nullable=True, default=0)
    paid_revenue = db.Column(db.Float, nullable=True, default=0)
    credit_card_orders = db.Column(db.Integer, nullable=True, default=0)
    credit_card_revenue = db.Column(db.Float, nullable=True, default=0)
    pay_now_orders = db.Column(db.Integer, nullable=True, default=0)
    pay_now_revenue = db.Column(db.Float, nullable=True, default=0)
    unpaid_orders = db.Column(db.Integer, nullable=True, default=0)
    unpaid_revenue = db.Column(db.Float, nullable=True, default=0)

    def __init__(self, fb_campaign_id, total_orders, total_revenue, paid_orders, paid_revenue,
                 credit_card_orders, credit_card_revenue, pay_now_orders, pay_now_revenue, unpaid_orders, unpaid_revenue):
        self.fb_campaign_id = fb_campaign_id
        self.total_orders = total_orders
        self.total_revenue = total_revenue
        self.paid_orders = paid_orders
        self.paid_revenue = paid_revenue
        self.credit_card_orders = credit_card_orders
        self.credit_card_revenue = credit_card_revenue
        self.pay_now_orders = pay_now_orders
        self.pay_now_revenue = pay_now_revenue
        self.unpaid_orders = unpaid_orders
        self.unpaid_revenue = unpaid_revenue


class FBCampaignStatSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('fb_campaign_id', 'total_orders', 'total_revenue', 'paid_orders', 'paid_revenue',
                  'credit_card_orders', 'credit_card_revenue', 'pay_now_orders', 'pay_now_revenue', 'unpaid_orders', 'unpaid_revenue')

        fb_campaign_id = Integer()
        total_orders = Integer()
        total_revenue = Float()
        paid_orders = Integer()
        paid_revenue = Float()
        credit_card_orders = Integer()
        credit_card_revenue = Float()
        pay_now_orders = Integer()
        pay_now_revenue = Float()
        unpaid_orders = Integer()
        unpaid_revenue = Float()


class FBCampaignProductActive(db.Model):
    __tablename__ = "lss_fb_campaign_product_active"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fb_user_id = db.Column(db.String(50), nullable=False, default='')
    campaign_id = db.Column(db.Integer, nullable=False, default=0)
    campaign_product_id = db.Column(db.Integer, nullable=False, default=0)
    user_order_id = db.Column(db.Integer, nullable=False, default=0)
    fb_page_id = db.Column(db.String(32),  nullable=False, default='')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(
        db.DateTime, nullable=False, onupdate=datetime.now, default=datetime.now)

    def __init__(self,
                 fb_user_id,
                 campaign_id,
                 campaign_product_id,
                 user_order_id,
                 fb_page_id,):
        self.fb_user_id = fb_user_id
        self.campaign_id = campaign_id
        self.campaign_product_id = campaign_product_id
        self.user_order_id = user_order_id
        self.fb_page_id = fb_page_id


class FBCampaignProductActiveSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = (
            'id',
            'fb_user_id',
            'campaign_id',
            'campaign_product_id',
            'user_order_id',
            'fb_page_id',
            'created_at',
            'updated_at'
        )

    id = Integer()
    fb_user_id = Str()
    campaign_id = Integer()
    campaign_product_id = Integer()
    user_order_id = Integer()
    fb_page_id = Str()
    created_at = DateTime()
    updated_at = DateTime()
