
def update_category(ordr_startr_product, product_categories:list, tag_set:set):
    tag_name = ordr_startr_product.get('supplierName')
    if tag_name not in tag_set:
            product_categories.append(tag_name)
            tag_set.add(tag_name)