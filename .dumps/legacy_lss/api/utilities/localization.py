from config import shopping_cart_url


def get_localization_msg(def_msg, lz_msgs, lang=None):
    lang = lang.lower()
    return lz_msgs[lang] if lang in lz_msgs else def_msg


def localization_msg_react_to_close_campaign_product(order_code, lang=None):
    def_msg = f'Order code: {order_code} has closed.'
    lz_msgs = {
        'zh-tw': f"下單代碼： {order_code} 已停止接單。",
        'zh-cn': f"下单代码： {order_code} 已停止接单。",
        'ms-my': f"Kod Pesanan: {order_code} telah ditutup.",
        'id-id': f"Kode pesanan: {order_code} telah ditutup.",
        'th-th': f"รหัสคำสั่งซื้อ: {order_code} ปิดแล้ว",
        'vi-vn': f"Mã đặt hàng: {order_code} đã đóng.",
        'ja-jp': f"注文コード：{order_code}が閉じています。",
        'ko-kr': f"주문 코드 : {order_code}가 마감되었습니다.",
        'es-es': f"Código de pedido: {order_code} se ha cerrado.",

    }
    return get_localization_msg(def_msg, lz_msgs, lang)


def localization_msg_react_to_sold_out_campaign_product(order_code, lang=None):
    def_msg = f'Order code: {order_code} is sold out.'
    lz_msgs = {
        'zh-tw': f"下單代碼： {order_code} 已售完。",
        'zh-cn': f"下单代码： {order_code} 已售完。",
        'ms-my': f"Kod pesanan: {order_code} habis terjual.",
        'id-id': f"Kode pesanan: {order_code} terjual habis.",
        'th-th': f"รหัสคำสั่งซื้อ: {order_code} ขายหมดแล้ว",
        'vi-vn': f"Mã đặt hàng: {order_code} đã bán hết.",
        'ja-jp': f"注文コード：{order_code}は売り切れです。",
        'ko-kr': f"주문 코드 : {order_code}이 (가) 매진되었습니다.",
        'es-es': f"Código de pedido: {order_code} está agotado.",

    }
    return get_localization_msg(def_msg, lz_msgs, lang)


def localization_msg_react_to_campaign_invalid_order(order_code, lang=None):
    def_msg = f"Sorry, the product ({order_code}) is unavailable."
    lz_msgs = {
        'zh-tw': f"抱歉，下單代碼 ({order_code}) 的商品目前無法供應。",
        'zh-cn': f"抱歉，下单代码 ({order_code}) 的商品目前无法供应。",
        'ms-my': f'Maaf, produk ({order_code}) tidak tersedia.',
        'id-id': f'Maaf, produk ({order_code}) tidak tersedia.',
        'th-th': f'ขออภัย ผลิตภัณฑ์ ({order_code}) ไม่พร้อมใช้งาน',
        'vi-vn': f'Xin lỗi, sản phẩm ({order_code}) không có sẵn.',
        'ja-jp': f'申し訳ありませんが、製品（{order_code}）はご利用いただけません。',
        'ko-kr': f'죄송합니다. 제품 ({order_code})을 사용할 수 없습니다.',
        'es-es': f'Lo sentimos, el producto ({order_code}) no está disponible.',

    }
    return get_localization_msg(def_msg, lz_msgs, lang)


def localization_msg_react_to_campaign_congrats_lucky_draw_winner(fb_campaign_comment, fb_campaign_product, lang=None):
    def_msg = f"Congratulations to {fb_campaign_comment.fb_user_name} on wining luckydraw! Prize: {fb_campaign_product.name}. Please check your shopping cart."
    lz_msgs = {
        'zh-tw': f"中獎公告：恭喜 {fb_campaign_comment.fb_user_name} 中獎，獲得 {fb_campaign_product.name}！請至購物車確認您的獎品。",
        'zh-cn': f"中奖公告：恭喜 {fb_campaign_comment.fb_user_name} 中奖，获得 {fb_campaign_product.name}！请至购物车确认您的奖品。",
        'ms-my': f'Tahniah untuk {fb_campaign_comment.fb_user_name} kerana berjaya memenangi cabutan bertuah! Hadiah: {fb_campaign_product.name}. Sila periksa keranjang belanja anda.',
        'id-id': f'Selamat kepada {fb_campaign_comment.fb_user_name} karena memenangkan undian berhadiah! Hadiah: {fb_campaign_product.name}. Silakan periksa keranjang belanja Anda.',
        'th-th': f'ขอแสดงความยินดีกับ {fb_campaign_comment.fb_user_name} สำหรับการจับรางวัล! รางวัล: {fb_campaign_product.name} กรุณาตรวจสอบตะกร้าสินค้าของคุณ',
        'vi-vn': f'Xin chúc mừng {fb_campaign_comment.fb_user_name} đã giành được giải rút thăm may mắn! Giải thưởng: {fb_campaign_product.name}. Vui lòng kiểm tra giỏ hàng của bạn.',
        'ja-jp': f'ラッキードローを獲得してくださった{fb_campaign_comment.fb_user_name}におめでとうございます！賞：{fb_campaign_product.name} ショッピングカートをご確認ください。',
        'ko-kr': f'행운의 추첨에 당첨 된{fb_campaign_comment.fb_user_name}을 축하합니다! 상: {fb_campaign_product.name} 쇼핑 카트를 확인하시기 바랍니다.',
        'es-es': f'¡Felicitaciones a {fb_campaign_comment.fb_user_name} por ganar el sorteo! Premio: {fb_campaign_product.name}. Por favor revise su carrito de compras.',

    }
    return get_localization_msg(def_msg, lz_msgs, lang)


def localization_msg_react_to_buyer_on_ordering_create_pm(fb_campaign_order, lang=None):
    def_msg = f"Product added. Order code: {fb_campaign_order.order_code}. Order quantity: {str(fb_campaign_order.order_qty)}. Shopping cart: "
    lz_msgs = {
        'zh-tw': f"下單成功！商品： {fb_campaign_order.order_code}，{str(fb_campaign_order.order_qty)} 件已新增至購物車。點此前往購物車：",
        'zh-cn': f"下单成功！商品： {fb_campaign_order.order_code}，{str(fb_campaign_order.order_qty)} 件已新增至购物车。点此前往购物车：",
        'ms-my': f'Produk ditambah. Kod pesanan: {fb_campaign_order.order_code}. Kuantiti: {str(fb_campaign_order.order_qty)}. Troli membeli-belah:',
        'id-id': f'Produk ditambahkan. Kode pemesanan: {fb_campaign_order.order_code}. Kuantitas: {str(fb_campaign_order.order_qty)}. Kereta belanja:',
        'th-th': f'เพิ่มสินค้าแล้ว รหัสการสั่งซื้อ: {fb_campaign_order.order_code} ปริมาณ: {str(fb_campaign_order.order_qty)} ตะกร้าสินค้า:',
        'vi-vn': f'Sản phẩm được thêm vào. Mã đặt hàng: {fb_campaign_order.order_code}. Định lượng: {str(fb_campaign_order.order_qty)}. Giỏ hàng:',
        'ja-jp': f'製品が追加されました。注文コード：{fb_campaign_order.order_code} 量：{str(fb_campaign_order.order_qty)} ショッピングカート：',
        'ko-kr': f'제품이 추가되었습니다. 주문 코드: {fb_campaign_order.order_code} 수량: {str(fb_campaign_order.order_qty)} 쇼핑 카트:',
        'es-es': f'Producto añadido. Código de orden: {fb_campaign_order.order_code}. Cantidad: {str(fb_campaign_order.order_qty)}. Carrito de compras:',

    }
    return get_localization_msg(def_msg, lz_msgs, lang)


def localization_msg_react_to_buyer_on_ordering_create_comment(fb_campaign_order, lang=None):
    def_msg = f"Product added. Order code: {fb_campaign_order.order_code}. Order quantity: {str(fb_campaign_order.order_qty)}. Shopping Cart link is sent via FB Messenger, please contact page admin if not received any notification."
    lz_msgs = {
        'zh-tw': f"下單成功！商品： {fb_campaign_order.order_code}，{str(fb_campaign_order.order_qty)} 件已新增至購物車。購物車連結已傳送至您的 FB Messenger，若沒有收到訊息，請聯絡粉絲專頁管理員/小編。",
        'zh-cn': f"下单成功！商品： {fb_campaign_order.order_code}，{str(fb_campaign_order.order_qty)} 件已新增至购物车。购物车连结已传送至您的 FB Messenger，若没有收到讯息，请联络粉丝专页管理员/小编。",
        'ms-my': f'Produk ditambah. Kod pesanan: {fb_campaign_order.order_code}. Kuantiti: {str(fb_campaign_order.order_qty)}. Pautan Keranjang Belanja dihantar melalui FB Messenger. Sila hubungi pentadbir halaman jika tidak menerima pemberitahuan.',
        'id-id': f'Produk ditambahkan. Kode pemesanan: {fb_campaign_order.order_code}. Kuantitas: {str(fb_campaign_order.order_qty)}. Tautan keranjang belanja dikirim melalui FB Messenger. Silakan hubungi admin halaman jika tidak menerima pemberitahuan apa pun.',
        'th-th': f'เพิ่มสินค้าแล้ว รหัสการสั่งซื้อ: {fb_campaign_order.order_code} ปริมาณ: {str(fb_campaign_order.order_qty)} ลิงก์ตะกร้าสินค้าถูกส่งผ่าน FB Messenger โปรดติดต่อแอดมินเพจหากไม่ได้รับการแจ้งเตือนใดๆ',
        'vi-vn': f'Sản phẩm được thêm vào. Mã đặt hàng: {fb_campaign_order.order_code}. Định lượng: {str(fb_campaign_order.order_qty)}. Liên kết giỏ hàng được gửi qua FB Messenger. Vui lòng liên hệ quản trị trang nếu không nhận được bất kỳ thông báo nào.',
        'ja-jp': f'製品が追加されました。注文コード：{fb_campaign_order.order_code} 量：{str(fb_campaign_order.order_qty)} ショッピングカートのリンクは、FBメッセンジャーを介して送信されます。通知がない場合は、ページ管理者に連絡してください。',
        'ko-kr': f'제품이 추가되었습니다. 주문 코드: {fb_campaign_order.order_code} 수량: {str(fb_campaign_order.order_qty)} 장바구니 링크는 FB 메신저를 통해 전송됩니다. 알림을받지 못한 경우 페이지 관리자에게 문의하십시오.',
        'es-es': f'Producto añadido. Código de orden: {fb_campaign_order.order_code}. Cantidad: {str(fb_campaign_order.order_qty)}. El enlace del carrito de compras se envía a través de FB Messenger. Póngase en contacto con el administrador de la página si no ha recibido ninguna notificación.',

    }
    return get_localization_msg(def_msg, lz_msgs, lang)


def localization_msg_react_to_buyer_on_ordering_update_pm(fb_campaign_order, lang=None):
    def_msg = f"Product updated. Order code: {fb_campaign_order.order_code}. Order quantity: {str(fb_campaign_order.order_qty)}. Shopping cart: "
    lz_msgs = {
        'zh-tw': f"訂單更新成功！商品： {fb_campaign_order.order_code}，{str(fb_campaign_order.order_qty)} 件已新增至購物車。點此前往購物車：",
        'zh-cn': f"订单更新成功！商品： {fb_campaign_order.order_code}，{str(fb_campaign_order.order_qty)} 件已新增至购物车。点此前往购物车：",
        'ms-my': f'Produk dikemas kini. Kod pesanan: {fb_campaign_order.order_code}. Kuantiti: {str(fb_campaign_order.order_qty)}. Troli membeli-belah:',
        'id-id': f'Produk diperbarui. Kode pemesanan: {fb_campaign_order.order_code}. Kuantitas: {str(fb_campaign_order.order_qty)}. Kereta belanja:',
        'th-th': f'อัพเดทสินค้า รหัสการสั่งซื้อ: {fb_campaign_order.order_code} ปริมาณ: {str(fb_campaign_order.order_qty)} ตะกร้าสินค้า:',
        'vi-vn': f'Đã cập nhật sản phẩm. Mã đặt hàng: {fb_campaign_order.order_code}. Định lượng: {str(fb_campaign_order.order_qty)}. Giỏ hàng:',
        'ja-jp': f'製品が更新されました。注文コード：{fb_campaign_order.order_code} 量：{str(fb_campaign_order.order_qty)} ショッピングカート：',
        'ko-kr': f'제품이 업데이트되었습니다. 주문 코드: {fb_campaign_order.order_code} 수량: {str(fb_campaign_order.order_qty)} 쇼핑 카트:',
        'es-es': f'Producto actualizado. Código de orden: {fb_campaign_order.order_code}. Cantidad: {str(fb_campaign_order.order_qty)}. Carrito de compras:',

    }
    return get_localization_msg(def_msg, lz_msgs, lang)


def localization_msg_react_to_buyer_on_ordering_update_comment(fb_campaign_order, lang=None):
    def_msg = f"Product updated. Order code: {fb_campaign_order.order_code}. Order quantity: {str(fb_campaign_order.order_qty)}. Shopping Cart link is sent via FB Messenger, please contact page admin if not received any notification."
    lz_msgs = {
        'zh-tw': f"訂單更新成功！商品： {fb_campaign_order.order_code}，{str(fb_campaign_order.order_qty)} 件已新增至購物車。購物車連結已傳送至您的 FB Messenger，若沒有收到訊息，請聯絡粉絲專頁管理員/小編。",
        'zh-cn': f"订单更新成功！商品： {fb_campaign_order.order_code}，{str(fb_campaign_order.order_qty)} 件已新增至购物车。购物车连结已传送至您的 FB Messenger，若没有收到讯息，请联络粉丝专页管理员/小编。",
        'ms-my': f'Produk dikemas kini. Kod pesanan: {fb_campaign_order.order_code}. Kuantiti: {str(fb_campaign_order.order_qty)}. Pautan Keranjang Belanja dihantar melalui FB Messenger. Sila hubungi pentadbir halaman jika tidak menerima pemberitahuan.',
        'id-id': f'Produk diperbarui. Kode pemesanan: {fb_campaign_order.order_code}. Kuantitas: {str(fb_campaign_order.order_qty)}. Tautan keranjang belanja dikirim melalui FB Messenger. Silakan hubungi admin halaman jika tidak menerima pemberitahuan apa pun.',
        'th-th': f'อัพเดทสินค้า รหัสการสั่งซื้อ: {fb_campaign_order.order_code} ปริมาณ: {str(fb_campaign_order.order_qty)} ลิงก์ตะกร้าสินค้าถูกส่งผ่าน FB Messenger โปรดติดต่อแอดมินเพจหากไม่ได้รับการแจ้งเตือนใดๆ',
        'vi-vn': f'Đã cập nhật sản phẩm. Mã đặt hàng: {fb_campaign_order.order_code}. Định lượng: {str(fb_campaign_order.order_qty)}. Liên kết giỏ hàng được gửi qua FB Messenger. Vui lòng liên hệ quản trị trang nếu không nhận được bất kỳ thông báo nào.',
        'ja-jp': f'製品が更新されました。注文コード：{fb_campaign_order.order_code} 量：{str(fb_campaign_order.order_qty)} ショッピングカートのリンクは、FBメッセンジャーを介して送信されます。通知がない場合は、ページ管理者に連絡してください。',
        'ko-kr': f'제품이 업데이트되었습니다. 주문 코드: {fb_campaign_order.order_code} 수량: {str(fb_campaign_order.order_qty)} 장바구니 링크는 FB 메신저를 통해 전송됩니다. 알림을받지 못한 경우 페이지 관리자에게 문의하십시오.',
        'es-es': f'Producto actualizado. Código de orden: {fb_campaign_order.order_code}. Cantidad: {str(fb_campaign_order.order_qty)}. El enlace del carrito de compras se envía a través de FB Messenger. Póngase en contacto con el administrador de la página si no ha recibido ninguna notificación.',

    }
    return get_localization_msg(def_msg, lz_msgs, lang)


def localization_msg_react_to_campaign_invalid_exceed_max_order(order_code, max_order_amount, lang=None):
    def_msg = f"Sorry, the product ({order_code}) has a maximum ordering quantity of {max_order_amount}."
    lz_msgs = {
        'zh-tw': f"抱歉，下單代碼 ({order_code}) 的商品單次限購數量為 {max_order_amount} 件。",
        'zh-cn': f"抱歉，下单代码 ({order_code}) 的商品单次限购数量为 {max_order_amount} 件。",
        'ms-my': f'Maaf, produk ({order_code}) mempunyai kuantiti pesanan maksimum {max_order_amount}.',
        'id-id': f'Maaf, produk ({order_code}) memiliki jumlah pemesanan maksimum {max_order_amount}.',
        'th-th': f'ขออภัย ผลิตภัณฑ์ ({order_code}) มีปริมาณการสั่งซื้อสูงสุด {max_order_amount}',
        'vi-vn': f'Xin lỗi, sản phẩm ({order_code}) có số lượng đặt hàng tối đa là {max_order_amount}.',
        'ja-jp': f'申し訳ありませんが、商品（{order_code}）の最大注文数量は {max_order_amount} です。',
        'ko-kr': f'죄송합니다. 제품 ({order_code}) 의 최대 주문 수량은 {max_order_amount} 입니다.',
        'es-es': f'Lo sentimos, el producto ({order_code}) tiene una cantidad máxima de pedido de {max_order_amount}.',

    }
    return get_localization_msg(def_msg, lz_msgs, lang)


def localization_msg_react_to_campaign_invalid_sold_out(order_code, lang=None):
    def_msg = f"Sorry, the product ({order_code}) is sold out."
    lz_msgs = {
        'zh-tw': f"抱歉，下單代碼 ({order_code}) 的商品已售完。",
        'zh-cn': f"抱歉，下单代码 ({order_code}) 的商品已售完。",
        'ms-my': f'Maaf, produk ({order_code}) habis terjual.',
        'id-id': f'Maaf, produk ({order_code}) sudah habis terjual.',
        'th-th': f'ขออภัย สินค้า ({order_code}) ขายหมดแล้ว',
        'vi-vn': f'Xin lỗi, sản phẩm ({order_code}) đã được bán hết.',
        'ja-jp': f'申し訳ありませんが、商品（{order_code}）は売り切れです。',
        'ko-kr': f'죄송합니다. 제품 ({order_code}) 이 매진되었습니다.',
        'es-es': f'Lo sentimos, el producto ({order_code}) está agotado.',

    }
    return get_localization_msg(def_msg, lz_msgs, lang)


def localization_msg_react_to_buyer_on_ordering_canceled(order_code, lang=None):
    def_msg = f"The product ({order_code}) is removed from your shopping cart."
    lz_msgs = {
        'zh-tw': f"訂單更新成功！商品： ({order_code}) 已從您的購物車移除。",
        'zh-cn': f"订单更新成功！商品： ({order_code}) 已从您的购物车移除。",
        'ms-my': f'Produk ({order_code}) dikeluarkan dari keranjang belanja anda.',
        'id-id': f'Produk ({order_code}) dihapus dari keranjang belanja Anda.',
        'th-th': f'ผลิตภัณฑ์ ({order_code}) ถูกลบออกจากตะกร้าสินค้าของคุณ',
        'vi-vn': f'Sản phẩm ({order_code}) đã bị xóa khỏi giỏ hàng của bạn.',
        'ja-jp': f'商品（{order_code}）がショッピングカートから削除されます。',
        'ko-kr': f'제품 ({order_code})이 장바구니에서 제거됩니다.',
        'es-es': f'El producto ({order_code}) se elimina de su carrito de compras.',

    }
    return get_localization_msg(def_msg, lz_msgs, lang)


def localization_msg_react_to_buyer_on_comment_keyword_order(order, order_products, delivery_charge, modify_total, lang=None):
    def_msg = ['Your order', 'Qty', 'Delivery',
               'Option', 'Total', 'Find out details']
    lz_msgs = {
        'zh-tw': ['訂單明細', '數量', '運費', '其他', '總金額', '點此前往購物車'],
        'zh-cn': ['订单明细', '数量', '运费', '其他', '总金额', '点此前往购物车'],
        'ms-my': ['Pesanan anda', 'Kuantiti', 'Cas penghantaran', 'Pilihan', 'Jumlah', 'Dapatkan maklumat terperinci'],
        'id-id': ['Pesanan anda', 'Kuantitas', 'Biaya pengiriman', 'Pilihan', 'Total', 'Cari tahu detailnya'],
        'th-th': ['คำสั่งของคุณ', 'ปริมาณ', 'ค่าจัดส่ง', 'ตัวเลือก', 'รวม', 'ดูรายละเอียด'],
        'vi-vn': ['Đơn đặt hàng của bạn', 'Định lượng', 'Phí giao hàng', 'Lựa chọn', 'Toàn bộ', 'Tìm hiểu chi tiết'],
        'ja-jp': ['ご注文', '量', '配達料', 'オプション', '合計', '詳細をご覧ください'],
        'ko-kr': ['주문', '수량', '배송비', '선택권', '합계', '자세한 내용을 알아보십시오'],
        'es-es': ['Su pedido', 'Cantidad', 'Gastos de envío', 'Opción', 'Total', 'Descubra los detalles'],
    }
    msg_params = get_localization_msg(def_msg, lz_msgs, lang)

    msg = list(f"{msg_params[0]}:\n-----\n")
    index = 1
    for product in order_products:
        if product.quantity > 0:
            if index != 1:
                msg.append("\n")
            msg.append(
                f"{index:02d}. {product.name} {msg_params[1]}:{product.quantity} ${float(product.total):.2f}\n")
            index += 1
    msg.append(
        f"-----\n"
        f"{msg_params[2]}: ${float(delivery_charge):.2f}\n"
        f"{msg_params[3]}: {get_option_sign(float(modify_total))}${abs(float(modify_total)):.2f}\n"
        f"-----\n"
        f"{msg_params[4]}: ${float(order.total):.2f}\n\n"
        f"{msg_params[5]}: {shopping_cart_url}/{str(order.campaign_id)}/{order.fb_user_id}"
    )
    return ''.join(msg)


def get_option_sign(modify_total):
    if modify_total > 0:
        return '+'
    elif modify_total < 0:
        return '-'
    return ''
