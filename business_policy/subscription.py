DECIMAL_1000 =-3
DECIMAL_100 =-2
DECIMAL_10 =-1
DECIMAL_1 =0
DECIMAL_01 =1
DECIMAL_001 =2

DECIMAL_CHOICES = [
    (DECIMAL_1000,'1000'),
    (DECIMAL_100,'100'),
    (DECIMAL_10,'10'),
    (DECIMAL_1,'1'),
    (DECIMAL_01,'0.1'),
    (DECIMAL_001,'0.01'),]

CURRENCY_USD='USD'
CURRENCY_TWD='TWD'
CURRENCY_SGD='SGD'
CURRENCY_IDR='IDR'
CURRENCY_PHP='PHP'
CURRENCY_MYR='MYR'
CURRENCY_VND='VND'
CURRENCY_RMB='RMB'
CURRENCY_KHR='KHR'
CURRENCY_AUD='AUD'
CURRENCY_HKD='HKD'

CURRENCY_CHOICES=[
    (CURRENCY_USD,'USD'),
    (CURRENCY_TWD,'TWD'),
    (CURRENCY_SGD,'SGD'),
    (CURRENCY_IDR,'IDR'),
    (CURRENCY_PHP,'PHP'),
    (CURRENCY_MYR,'MYR'),
    (CURRENCY_VND,'VND'),
    (CURRENCY_RMB,'RMB'),
    (CURRENCY_KHR,'KHR'),
    (CURRENCY_AUD,'AUD'),
    (CURRENCY_HKD,'HKD'),
    ]
CURRENCY_SIGN = {
    CURRENCY_USD: "$",
    CURRENCY_TWD: "$",
    CURRENCY_PHP: "₱"
}

LANGUAGE_ENGLICH='en'
LANGUAGE_INDONESIAN='id'
LANGUAGE_SIMPLIFY_CHINESE='zh_hans'
LANGUAGE_TRANDITIONAL_CHINESE='zh_hant'

LANGUAGE_CHOICES=[
    (LANGUAGE_ENGLICH,'English'),
    (LANGUAGE_INDONESIAN,'Chinese-Simplify'),
    (LANGUAGE_SIMPLIFY_CHINESE,'Chinese-Tranditional'),
    (LANGUAGE_TRANDITIONAL_CHINESE,'Indonesian'),
]

PRICE_UNIT_UNIT='1'
PRICE_UNIT_TEN='10'
PRICE_UNIT_HUNDRED='100'
PRICE_UNIT_THOUSAND='1000'
PRICE_UNIT_TEN_THOUSAND='10000'
PRICE_UNIT_HUNDRED_THOUSAND='100000'
PRICE_UNIT_MILLION='1000000'

PRICE_UNIT_CHOICES=[
    (PRICE_UNIT_UNIT,'1'),
    (PRICE_UNIT_TEN,'10'),
    (PRICE_UNIT_HUNDRED,'100'),
    (PRICE_UNIT_THOUSAND,'1000'),
    (PRICE_UNIT_TEN_THOUSAND,'10000'),
    (PRICE_UNIT_HUNDRED_THOUSAND,'100000'),
    (PRICE_UNIT_MILLION,'1000000'),
]

TYPE_TRIAL='trial'
TYPE_LITE='lite'
TYPE_STANDARD='standard'
TYPE_PREMIUM='premium'
TYPE_DEALER='dealer'

TYPE_CHOICES = [
    (TYPE_TRIAL, 'Trial'),
    (TYPE_LITE, 'Lite'),
    (TYPE_STANDARD, 'Standard'),
    (TYPE_PREMIUM, 'Premium'),
    (TYPE_DEALER,'Dealer'),
]
