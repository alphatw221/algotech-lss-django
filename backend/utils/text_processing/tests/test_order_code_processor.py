from backend.utils.text_processing.order_code_processor import OrderCodeTextProcessor


def test_empty_text_or_order_code():
    assert OrderCodeTextProcessor.process('', 'order_code') == None
    assert OrderCodeTextProcessor.process('text', '') == None


def test_is_a_question():
    text = 'Can I have AAA +3?'
    order_code = 'AAA'
    assert OrderCodeTextProcessor.process(text, order_code) == None
    text = 'Can I have some? AAA +3'
    order_code = 'AAA'
    assert OrderCodeTextProcessor.process(text, order_code) != None


def test_text_has_order_code():
    text = 'Can I have AAA +3'
    order_code = 'AAA'
    assert OrderCodeTextProcessor.process(text, order_code) != None


def test_regular_cases():
    assert OrderCodeTextProcessor.process("apple*10", "apple") == 10
    assert OrderCodeTextProcessor.process("guava+8888", "guava") == 8888
    assert OrderCodeTextProcessor.process("guava + 10", "guava") == 10
    assert OrderCodeTextProcessor.process("guava X10", "guava") == 10
    assert OrderCodeTextProcessor.process("guavax10", "guava") == 10
    assert OrderCodeTextProcessor.process("guavaX 10", "guava") == 10


def test_regular_negative_cases():
    assert OrderCodeTextProcessor.process("guava 10", "guava") == None


def test_extreme_cases():
    comment = "chee6*30"
    order_code = "chee6"
    assert OrderCodeTextProcessor.process(comment, order_code) == 30


def test_extreme_negative_cases():
    comment = "chee6*sadfasdf200"
    order_code = "chee6"
    assert OrderCodeTextProcessor.process(comment, order_code) == None


def test_cases_for_question_mark():
    comment = "Hi! How's your day? I want guava + 10"
    order_code = "guava"
    assert OrderCodeTextProcessor.process(comment, order_code) == 10

    comment = "Hi! How's your day? guava *00300"
    order_code = "guava"
    assert OrderCodeTextProcessor.process(comment, order_code) == 300

    comment = "What if I buy guava * 10, is there any discount?"
    order_code = "guava"
    assert OrderCodeTextProcessor.process(comment, order_code) == None


def test_text_after_order_code():
    assert OrderCodeTextProcessor._get_text_after_order_code(
        'AAA +3', 'BBB') == None
    assert OrderCodeTextProcessor._get_text_after_order_code(
        'BBBAAA', 'AAA') == ''
    assert OrderCodeTextProcessor._get_text_after_order_code(
        'AAA +3', 'AAA') == ' +3'
    assert OrderCodeTextProcessor._get_text_after_order_code(
        'BBBAAAA', 'AAA') == 'A'
    assert OrderCodeTextProcessor._get_text_after_order_code(
        'BBBAAAA+10', 'AAA') == 'A+10'
    assert OrderCodeTextProcessor._get_text_after_order_code(
        'BBBAA', 'AAA') == None


def test_get_order_qty():
    assert OrderCodeTextProcessor._get_order_qty(' +3') == 3
    assert OrderCodeTextProcessor._get_order_qty(' + 33') == 33
    assert OrderCodeTextProcessor._get_order_qty(' + 3 3') == 3
    assert OrderCodeTextProcessor._get_order_qty(' + 0') == 0


def test_get_order_qty_invalid():
    assert OrderCodeTextProcessor._get_order_qty('whatever +5') == None
    assert OrderCodeTextProcessor._get_order_qty(' + a03') == None


def test_get_order_qty_edge():
    assert OrderCodeTextProcessor._get_order_qty(' + 00') == 0
    assert OrderCodeTextProcessor._get_order_qty(' + 03') == 3
