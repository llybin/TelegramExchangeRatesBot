"""currencies_chat_request_foreigns

Revision ID: 79fd60fe1187
Revises: 91196c1f9f51
Create Date: 2019-03-06 19:34:47.031946

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.declarative import declarative_base

# revision identifiers, used by Alembic.
revision = '79fd60fe1187'
down_revision = '91196c1f9f51'
branch_labels = None
depends_on = None

Base = declarative_base()

# https://www.currency-iso.org/dam/downloads/lists/list_one.xml
# https://github.com/dahlia/iso4217 [{'code': c.code, 'name': c.currency_name} for c in iso4217.Currency]
ISO_CURRENCIES = [
    {'code': 'AED', 'name': 'UAE Dirham'}, {'code': 'AFN', 'name': 'Afghani'},
    {'code': 'ALL', 'name': 'Lek'}, {'code': 'AMD', 'name': 'Armenian Dram'},
    {'code': 'ANG', 'name': 'Netherlands Antillean Guilder'}, {'code': 'AOA', 'name': 'Kwanza'},
    {'code': 'ARS', 'name': 'Argentine Peso'}, {'code': 'AUD', 'name': 'Australian Dollar'},
    {'code': 'AWG', 'name': 'Aruban Florin'}, {'code': 'AZN', 'name': 'Azerbaijan Manat'},
    {'code': 'BAM', 'name': 'Convertible Mark'}, {'code': 'BBD', 'name': 'Barbados Dollar'},
    {'code': 'BDT', 'name': 'Taka'}, {'code': 'BGN', 'name': 'Bulgarian Lev'},
    {'code': 'BHD', 'name': 'Bahraini Dinar'}, {'code': 'BIF', 'name': 'Burundi Franc'},
    {'code': 'BMD', 'name': 'Bermudian Dollar'}, {'code': 'BND', 'name': 'Brunei Dollar'},
    {'code': 'BOB', 'name': 'Boliviano'}, {'code': 'BOV', 'name': 'Mvdol'},
    {'code': 'BRL', 'name': 'Brazilian Real'}, {'code': 'BSD', 'name': 'Bahamian Dollar'},
    {'code': 'BTN', 'name': 'Ngultrum'}, {'code': 'BWP', 'name': 'Pula'},
    {'code': 'BYN', 'name': 'Belarusian Ruble'}, {'code': 'BZD', 'name': 'Belize Dollar'},
    {'code': 'CAD', 'name': 'Canadian Dollar'}, {'code': 'CDF', 'name': 'Congolese Franc'},
    {'code': 'CHE', 'name': 'WIR Euro'}, {'code': 'CHF', 'name': 'Swiss Franc'},
    {'code': 'CHW', 'name': 'WIR Franc'}, {'code': 'CLF', 'name': 'Unidad de Fomento'},
    {'code': 'CLP', 'name': 'Chilean Peso'}, {'code': 'CNY', 'name': 'Yuan Renminbi'},
    {'code': 'COP', 'name': 'Colombian Peso'}, {'code': 'COU', 'name': 'Unidad de Valor Real'},
    {'code': 'CRC', 'name': 'Costa Rican Colon'}, {'code': 'CUC', 'name': 'Peso Convertible'},
    {'code': 'CUP', 'name': 'Cuban Peso'}, {'code': 'CVE', 'name': 'Cabo Verde Escudo'},
    {'code': 'CZK', 'name': 'Czech Koruna'}, {'code': 'DJF', 'name': 'Djibouti Franc'},
    {'code': 'DKK', 'name': 'Danish Krone'}, {'code': 'DOP', 'name': 'Dominican Peso'},
    {'code': 'DZD', 'name': 'Algerian Dinar'}, {'code': 'EGP', 'name': 'Egyptian Pound'},
    {'code': 'ERN', 'name': 'Nakfa'}, {'code': 'ETB', 'name': 'Ethiopian Birr'},
    {'code': 'EUR', 'name': 'Euro'}, {'code': 'FJD', 'name': 'Fiji Dollar'},
    {'code': 'FKP', 'name': 'Falkland Islands Pound'}, {'code': 'GBP', 'name': 'Pound Sterling'},
    {'code': 'GEL', 'name': 'Lari'}, {'code': 'GHS', 'name': 'Ghana Cedi'},
    {'code': 'GIP', 'name': 'Gibraltar Pound'}, {'code': 'GMD', 'name': 'Dalasi'},
    {'code': 'GNF', 'name': 'Guinean Franc'}, {'code': 'GTQ', 'name': 'Quetzal'},
    {'code': 'GYD', 'name': 'Guyana Dollar'}, {'code': 'HKD', 'name': 'Hong Kong Dollar'},
    {'code': 'HNL', 'name': 'Lempira'}, {'code': 'HRK', 'name': 'Kuna'},
    {'code': 'HTG', 'name': 'Gourde'}, {'code': 'HUF', 'name': 'Forint'},
    {'code': 'IDR', 'name': 'Rupiah'}, {'code': 'ILS', 'name': 'New Israeli Sheqel'},
    {'code': 'INR', 'name': 'Indian Rupee'}, {'code': 'IQD', 'name': 'Iraqi Dinar'},
    {'code': 'IRR', 'name': 'Iranian Rial'}, {'code': 'ISK', 'name': 'Iceland Krona'},
    {'code': 'JMD', 'name': 'Jamaican Dollar'}, {'code': 'JOD', 'name': 'Jordanian Dinar'},
    {'code': 'JPY', 'name': 'Yen'}, {'code': 'KES', 'name': 'Kenyan Shilling'},
    {'code': 'KGS', 'name': 'Som'}, {'code': 'KHR', 'name': 'Riel'},
    {'code': 'KMF', 'name': 'Comorian Franc'}, {'code': 'KPW', 'name': 'North Korean Won'},
    {'code': 'KRW', 'name': 'Won'}, {'code': 'KWD', 'name': 'Kuwaiti Dinar'},
    {'code': 'KYD', 'name': 'Cayman Islands Dollar'}, {'code': 'KZT', 'name': 'Tenge'},
    {'code': 'LAK', 'name': 'Lao Kip'}, {'code': 'LBP', 'name': 'Lebanese Pound'},
    {'code': 'LKR', 'name': 'Sri Lanka Rupee'}, {'code': 'LRD', 'name': 'Liberian Dollar'},
    {'code': 'LSL', 'name': 'Loti'}, {'code': 'LYD', 'name': 'Libyan Dinar'},
    {'code': 'MAD', 'name': 'Moroccan Dirham'}, {'code': 'MDL', 'name': 'Moldovan Leu'},
    {'code': 'MGA', 'name': 'Malagasy Ariary'}, {'code': 'MKD', 'name': 'Denar'},
    {'code': 'MMK', 'name': 'Kyat'}, {'code': 'MNT', 'name': 'Tugrik'},
    {'code': 'MOP', 'name': 'Pataca'}, {'code': 'MRU', 'name': 'Ouguiya'},
    {'code': 'MUR', 'name': 'Mauritius Rupee'}, {'code': 'MVR', 'name': 'Rufiyaa'},
    {'code': 'MWK', 'name': 'Malawi Kwacha'}, {'code': 'MXN', 'name': 'Mexican Peso'},
    {'code': 'MXV', 'name': 'Mexican Unidad de Inversion (UDI)'}, {'code': 'MYR', 'name': 'Malaysian Ringgit'},
    {'code': 'MZN', 'name': 'Mozambique Metical'}, {'code': 'NAD', 'name': 'Namibia Dollar'},
    {'code': 'NGN', 'name': 'Naira'}, {'code': 'NIO', 'name': 'Cordoba Oro'},
    {'code': 'NOK', 'name': 'Norwegian Krone'}, {'code': 'NPR', 'name': 'Nepalese Rupee'},
    {'code': 'NZD', 'name': 'New Zealand Dollar'}, {'code': 'OMR', 'name': 'Rial Omani'},
    {'code': 'PAB', 'name': 'Balboa'}, {'code': 'PEN', 'name': 'Sol'},
    {'code': 'PGK', 'name': 'Kina'}, {'code': 'PHP', 'name': 'Philippine Peso'},
    {'code': 'PKR', 'name': 'Pakistan Rupee'}, {'code': 'PLN', 'name': 'Zloty'},
    {'code': 'PYG', 'name': 'Guarani'}, {'code': 'QAR', 'name': 'Qatari Rial'},
    {'code': 'RON', 'name': 'Romanian Leu'}, {'code': 'RSD', 'name': 'Serbian Dinar'},
    {'code': 'RUB', 'name': 'Russian Ruble'}, {'code': 'RWF', 'name': 'Rwanda Franc'},
    {'code': 'SAR', 'name': 'Saudi Riyal'}, {'code': 'SBD', 'name': 'Solomon Islands Dollar'},
    {'code': 'SCR', 'name': 'Seychelles Rupee'}, {'code': 'SDG', 'name': 'Sudanese Pound'},
    {'code': 'SEK', 'name': 'Swedish Krona'}, {'code': 'SGD', 'name': 'Singapore Dollar'},
    {'code': 'SHP', 'name': 'Saint Helena Pound'}, {'code': 'SLL', 'name': 'Leone'},
    {'code': 'SOS', 'name': 'Somali Shilling'}, {'code': 'SRD', 'name': 'Surinam Dollar'},
    {'code': 'SSP', 'name': 'South Sudanese Pound'}, {'code': 'STN', 'name': 'Dobra'},
    {'code': 'SVC', 'name': 'El Salvador Colon'}, {'code': 'SYP', 'name': 'Syrian Pound'},
    {'code': 'SZL', 'name': 'Lilangeni'}, {'code': 'THB', 'name': 'Baht'},
    {'code': 'TJS', 'name': 'Somoni'}, {'code': 'TMT', 'name': 'Turkmenistan New Manat'},
    {'code': 'TND', 'name': 'Tunisian Dinar'}, {'code': 'TOP', 'name': 'Pa’anga'},
    {'code': 'TRY', 'name': 'Turkish Lira'}, {'code': 'TTD', 'name': 'Trinidad and Tobago Dollar'},
    {'code': 'TWD', 'name': 'New Taiwan Dollar'}, {'code': 'TZS', 'name': 'Tanzanian Shilling'},
    {'code': 'UAH', 'name': 'Hryvnia'}, {'code': 'UGX', 'name': 'Uganda Shilling'},
    {'code': 'USD', 'name': 'US Dollar'}, {'code': 'USN', 'name': 'US Dollar (Next day)'},
    {'code': 'UYI', 'name': 'Uruguay Peso en Unidades Indexadas (UI)'},
    {'code': 'UYU', 'name': 'Peso Uruguayo'}, {'code': 'UYW', 'name': 'Unidad Previsional'},
    {'code': 'UZS', 'name': 'Uzbekistan Sum'}, {'code': 'VES', 'name': 'Bolívar Soberano'},
    {'code': 'VND', 'name': 'Dong'}, {'code': 'VUV', 'name': 'Vatu'},
    {'code': 'WST', 'name': 'Tala'}, {'code': 'XAF', 'name': 'CFA Franc BEAC'},
    {'code': 'XCD', 'name': 'East Caribbean Dollar'}, {'code': 'XOF', 'name': 'CFA Franc BCEAO'},
    {'code': 'XPF', 'name': 'CFP Franc'}, {'code': 'YER', 'name': 'Yemeni Rial'},
    {'code': 'ZAR', 'name': 'Rand'}, {'code': 'ZMW', 'name': 'Zambian Kwacha'},
    {'code': 'ZWL', 'name': 'Zimbabwe Dollar'},
]

EXCLUDED_ISO_CURRENCIES = [
    {'code': 'ZMK', 'name': 'Zambian Kwacha'},  # -> ZMW https://en.wikipedia.org/wiki/Zambian_kwacha
    {'code': 'VEF', 'name': 'Bolívar Soberano'},  # -> VES https://en.wikipedia.org/wiki/Venezuelan_bol%C3%ADvar
    {'code': 'BYR', 'name': 'Belarusian Ruble'},  # -> BYN https://en.wikipedia.org/wiki/Belarusian_ruble
    {'code': 'STD', 'name': 'Dobra'},  # -> STN https://en.wikipedia.org/wiki/S%C3%A3o_Tom%C3%A9_and_Pr%C3%ADncipe_dobra
    {'code': 'MRO', 'name': 'Ouguiya'},  # -> MRU https://en.wikipedia.org/wiki/Mauritanian_ouguiya
]

NOT_ISO_CURRENCIES = [
    {'code': 'JEP', 'name': 'Jersey pound'},  # == GBP https://en.wikipedia.org/wiki/Jersey_pound
    {'code': 'GGP', 'name': 'Guernsey pound'},  # == GBP https://en.wikipedia.org/wiki/Guernsey_pound
]

X_CURRENCIES = [
    {'code': 'XAG', 'name': 'Gold'},
    {'code': 'XAU', 'name': 'Silver'},
    {'code': 'XDR', 'name': 'Special drawing rights'},  # also abbreviated SDR, https://en.wikipedia.org/wiki/Special_drawing_rights  # NOQA
    {'code': 'XPD', 'name': 'Palladium'},
    {'code': 'XPT', 'name': 'Platinum'},
]

# https://api.bittrex.com/api/v1.1/public/getcurrencies
# rj = requests.get('https://api.bittrex.com/api/v1.1/public/getcurrencies').json()['result']
# rj = filter(lambda x: x['IsActive'] and not x['IsRestricted'], rj)
# [{'code': c['Currency'], 'name': c['CurrencyLong']} for c in rj]
CRYPTO_CURRENCIES = [
    {'code': '1ST', 'name': 'Firstblood'}, {'code': '2GIVE', 'name': '2GIVE'},
    {'code': 'ABY', 'name': 'ArtByte'}, {'code': 'ADT', 'name': 'adToken'},
    {'code': 'ADX', 'name': 'AdEx'}, {'code': 'AEON', 'name': 'Aeon'},
    {'code': 'AID', 'name': 'AidCoin'}, {'code': 'AMP', 'name': 'SynereoAmp'},
    {'code': 'ANT', 'name': 'Aragon'}, {'code': 'APX', 'name': 'Apx'},
    {'code': 'ARDR', 'name': 'Ardor'}, {'code': 'ARK', 'name': 'Ark'},
    {'code': 'AUR', 'name': 'AuroraCoin'}, {'code': 'BAT', 'name': 'Basic Attention Token'},
    {'code': 'BAY', 'name': 'BitBay'}, {'code': 'BCH', 'name': 'Bitcoin Cash (ABC)'},
    {'code': 'BCPT', 'name': 'BlockMason Credit Protocol'}, {'code': 'BFT', 'name': 'BnkToTheFuture'},
    {'code': 'BITB', 'name': 'BitBean'}, {'code': 'BITCNY', 'name': 'BitCNY'},
    {'code': 'BITS', 'name': 'Bitswift'}, {'code': 'BKX', 'name': 'Bankex'},
    {'code': 'BLK', 'name': 'BlackCoin'}, {'code': 'BLOCK', 'name': 'Blocknet'},
    {'code': 'BLT', 'name': 'Bloom'}, {'code': 'BNT', 'name': 'Bancor'},
    {'code': 'BOXX', 'name': 'Blockparty'}, {'code': 'BRK', 'name': 'Breakout'},
    {'code': 'BRX', 'name': 'Breakout Stake'},
    # {'code': 'BSD', 'name': 'BitSend'}, conflict
    {'code': 'BSV', 'name': 'Bitcoin SV'}, {'code': 'BTC', 'name': 'Bitcoin'},
    {'code': 'BTM', 'name': 'Bytom'}, {'code': 'BTS', 'name': 'BitShares'},
    {'code': 'BURST', 'name': 'BURST'}, {'code': 'BYC', 'name': 'Bytecent'},
    {'code': 'CANN', 'name': 'CannabisCoin'}, {'code': 'CBC', 'name': 'CashBet'},
    {'code': 'CLOAK', 'name': 'CloakCoin'}, {'code': 'CMCT', 'name': 'Crowd Machine'},
    {'code': 'COVAL', 'name': 'Circuits of Value'}, {'code': 'CRB', 'name': 'CreditBit'},
    {'code': 'CRW', 'name': 'Crown'}, {'code': 'CURE', 'name': 'CureCoin'},
    {'code': 'CVC', 'name': 'Civic'}, {'code': 'DASH', 'name': 'Dash'},
    {'code': 'DCR', 'name': 'Decred'}, {'code': 'DGB', 'name': 'DigiByte'},
    {'code': 'DGD', 'name': 'Digix DAO'}, {'code': 'DMD', 'name': 'Diamond'},
    {'code': 'DMT', 'name': 'DMarket'}, {'code': 'DNT', 'name': 'district0x'},
    {'code': 'DOGE', 'name': 'Dogecoin'}, {'code': 'DOPE', 'name': 'DopeCoin'},
    {'code': 'DTA', 'name': 'Data'}, {'code': 'DTB', 'name': 'Databits'},
    {'code': 'DYN', 'name': 'Dynamic'}, {'code': 'EBST', 'name': 'eBoost'},
    {'code': 'EDG', 'name': 'Edgeless'}, {'code': 'EDR', 'name': 'Endor'},
    {'code': 'EFL', 'name': 'ElectronicGulden'}, {'code': 'EGC', 'name': 'EverGreenCoin'},
    {'code': 'EMC', 'name': 'EmerCoin'}, {'code': 'EMC2', 'name': 'Einsteinium'},
    {'code': 'ENG', 'name': 'Enigma'}, {'code': 'ENJ', 'name': 'Enjin'},
    {'code': 'ENRG', 'name': 'EnergyCoin'}, {'code': 'ETC', 'name': 'Ethereum Classic'},
    {'code': 'ETH', 'name': 'Ethereum'}, {'code': 'EXCL', 'name': 'ExclusiveCoin'},
    {'code': 'EXP', 'name': 'Expanse'}, {'code': 'FAIR', 'name': 'FairCoin'},
    {'code': 'FCT', 'name': 'Factom'}, {'code': 'FLDC', 'name': 'FoldingCoin'},
    {'code': 'FLO', 'name': 'FLO'}, {'code': 'FTC', 'name': 'Feathercoin'},
    {'code': 'FUN', 'name': 'FunFair'}, {'code': 'GAM', 'name': 'Gambit'},
    {'code': 'GAME', 'name': 'GameCredits'}, {'code': 'GBG', 'name': 'Gbg'},
    {'code': 'GBYTE', 'name': 'Bytes'}, {'code': 'GEO', 'name': 'GeoCoin'},
    {'code': 'GLD', 'name': 'GoldCoin'}, {'code': 'GNO', 'name': 'Gnosis'},
    {'code': 'GNT', 'name': 'Golem'}, {'code': 'GO', 'name': 'GoChain'},
    {'code': 'GOLOS', 'name': 'Golos'}, {'code': 'GRC', 'name': 'GridCoin'},
    {'code': 'GRS', 'name': 'Groestlcoin'}, {'code': 'GTO', 'name': 'Gifto'},
    {'code': 'GUP', 'name': 'Guppy'}, {'code': 'HMQ', 'name': 'Humaniq'},
    {'code': 'HYDRO', 'name': 'Hydro'}, {'code': 'IGNIS', 'name': 'Ignis'},
    {'code': 'IHT', 'name': 'I-House Token'}, {'code': 'INCNT', 'name': 'Incent'},
    {'code': 'IOC', 'name': 'I/OCoin'}, {'code': 'ION', 'name': 'Ion'},
    {'code': 'IOP', 'name': 'Internet Of People'}, {'code': 'KMD', 'name': 'Komodo'},
    {'code': 'KORE', 'name': 'Kore'}, {'code': 'LBA', 'name': 'Cred'},
    {'code': 'LBC', 'name': 'LBRY Credits'}, {'code': 'LMC', 'name': 'Lomocoin'},
    {'code': 'LOOM', 'name': 'Loom Network'}, {'code': 'LRC', 'name': 'Loopring'},
    {'code': 'LSK', 'name': 'Lisk'}, {'code': 'LTC', 'name': 'Litecoin'},
    {'code': 'LUN', 'name': 'Lunyr'}, {'code': 'MAID', 'name': 'MaidSafeCoin'},
    {'code': 'MANA', 'name': 'Decentraland'}, {'code': 'MCO', 'name': 'Crypto.com'},
    {'code': 'MEME', 'name': 'Memetic'}, {'code': 'MER', 'name': 'Mercury'},
    {'code': 'MET', 'name': 'Metronome'}, {'code': 'MFT', 'name': 'Mainframe'},
    {'code': 'MLN', 'name': 'Melon'}, {'code': 'MOBI', 'name': 'Mobius'},
    {'code': 'MOC', 'name': 'Mossland'}, {'code': 'MONA', 'name': 'MonaCoin'},
    {'code': 'MORE', 'name': 'More'}, {'code': 'MTL', 'name': 'METAL'},
    {'code': 'MUE', 'name': 'MonetaryUnit'}, {'code': 'MUSIC', 'name': 'Musicoin'},
    {'code': 'MYST', 'name': 'Mysterium'}, {'code': 'NAV', 'name': 'NAVCoin'},
    {'code': 'NBT', 'name': 'Nubits'}, {'code': 'NEO', 'name': 'Neo'},
    {'code': 'NEOS', 'name': 'NeosCoin'}, {'code': 'NGC', 'name': 'Naga'},
    {'code': 'NLC2', 'name': 'NoLimitCoin'}, {'code': 'NLG', 'name': 'Gulden'},
    {'code': 'NMR', 'name': 'Numeraire'}, {'code': 'NXC', 'name': 'Nexium'},
    {'code': 'NXS', 'name': 'Nexus'}, {'code': 'NXT', 'name': 'NXT'},
    {'code': 'OCN', 'name': 'Odyssey'}, {'code': 'OK', 'name': 'OkCash'},
    {'code': 'OMG', 'name': 'OmiseGO'}, {'code': 'OMNI', 'name': 'OmniCoin'},
    {'code': 'PART', 'name': 'Particl'}, {'code': 'PAX', 'name': 'Paxos Standard'},
    {'code': 'PAY', 'name': 'TenX Pay Token'}, {'code': 'PINK', 'name': 'PinkCoin'},
    {'code': 'PIVX', 'name': 'Pivx'}, {'code': 'PMA', 'name': 'PumaPay'},
    {'code': 'POLY', 'name': 'Polymath'}, {'code': 'POT', 'name': 'PotCoin'},
    {'code': 'POWR', 'name': 'PowerLedger'}, {'code': 'PPC', 'name': 'Peercoin'},
    {'code': 'PRO', 'name': 'Propy'}, {'code': 'PTC', 'name': 'PesetaCoin '},
    {'code': 'PTOY', 'name': 'Patientory'}, {'code': 'QRL', 'name': 'Quantum Resistant Ledger'},
    {'code': 'QTUM', 'name': 'Qtum'}, {'code': 'QWARK', 'name': 'Qwark'},
    {'code': 'RADS', 'name': 'Radium'}, {'code': 'RCN', 'name': 'Ripio Credit Network'},
    {'code': 'RDD', 'name': 'ReddCoin'}, {'code': 'REP', 'name': 'Augur'},
    {'code': 'RFR', 'name': 'Refereum'}, {'code': 'RISE', 'name': 'Rise'},
    {'code': 'RLC', 'name': 'iEx.ec'}, {'code': 'RVN', 'name': 'RavenCoin'},
    {'code': 'RVR', 'name': 'RevolutionVR'}, {'code': 'SALT', 'name': 'Salt'},
    # {'code': 'SBD', 'name': 'SteemDollars'}, conflict
    {'code': 'SC', 'name': 'Siacoin'},
    {'code': 'SEQ', 'name': 'Sequence'}, {'code': 'SHIFT', 'name': 'Shift'},
    {'code': 'SIB', 'name': 'Sibcoin'}, {'code': 'SLR', 'name': 'SolarCoin'},
    {'code': 'SLS', 'name': 'SaluS'}, {'code': 'SNGLS', 'name': 'SingularDTV'},
    {'code': 'SNT', 'name': 'Status Network Token'}, {'code': 'SOLVE', 'name': 'Solve.Care'},
    {'code': 'SPC', 'name': 'SpaceChain'}, {'code': 'SPND', 'name': 'Spendcoin'},
    {'code': 'SRN', 'name': 'Sirin Token'}, {'code': 'STEEM', 'name': 'STEEM'},
    {'code': 'STORJ', 'name': 'STORJ'}, {'code': 'STORM', 'name': 'Storm'},
    {'code': 'STRAT', 'name': 'Stratis'}, {'code': 'SWT', 'name': 'Swarm City Token'},
    {'code': 'SYNX', 'name': 'Syndicate'}, {'code': 'SYS', 'name': 'SysCoin'},
    {'code': 'THC', 'name': 'HempCoin'}, {'code': 'TIX', 'name': 'Blocktix'},
    {'code': 'TKS', 'name': 'Tokes'}, {'code': 'TRST', 'name': 'Trustcoin'},
    {'code': 'TRX', 'name': 'Tron'}, {'code': 'TUBE', 'name': 'BitTube'},
    {'code': 'TUSD', 'name': 'TrueUSD'}, {'code': 'TX', 'name': 'TransferCoin'},
    {'code': 'UBQ', 'name': 'Ubiq'}, {'code': 'UKG', 'name': 'UnikoinGold'},
    {'code': 'UP', 'name': 'UpToken'}, {'code': 'UPP', 'name': 'Sentinel Protocol'},
    # {'code': 'USD', 'name': 'US Dollar'}, duplicate
    {'code': 'USDS', 'name': 'StableUSD'}, {'code': 'USDT', 'name': 'Tether'},
    {'code': 'VEE', 'name': 'BLOCKv'}, {'code': 'VIA', 'name': 'ViaCoin'},
    {'code': 'VIB', 'name': 'Viberate'}, {'code': 'VRC', 'name': 'VeriCoin'},
    {'code': 'VRM', 'name': 'Verium'}, {'code': 'VTC', 'name': 'Vertcoin'},
    {'code': 'WAVES', 'name': 'Waves'}, {'code': 'WAX', 'name': 'Worldwide Asset Exchange'},
    {'code': 'WINGS', 'name': 'Wings DAO'}, {'code': 'XCP', 'name': 'Counterparty'},
    {'code': 'XEL', 'name': 'XEL'}, {'code': 'XEM', 'name': 'NEM'},
    {'code': 'XHV', 'name': 'Haven Protocol'}, {'code': 'XLM', 'name': 'Lumen'},
    {'code': 'XMG', 'name': 'Magi'}, {'code': 'XMR', 'name': 'Monero'},
    {'code': 'XMY', 'name': 'Myriad'}, {'code': 'XNK', 'name': 'Ink Protocol'},
    {'code': 'XRP', 'name': 'XRP'}, {'code': 'XST', 'name': 'Stealth'},
    {'code': 'XVG', 'name': 'Verge'}, {'code': 'XWC', 'name': 'WhiteCoin'},
    {'code': 'XZC', 'name': 'ZCoin'}, {'code': 'ZCL', 'name': 'Zclassic'},
    {'code': 'ZEC', 'name': 'ZCash'}, {'code': 'ZEN', 'name': 'Horizen'},
    {'code': 'ZRX', 'name': '0x Protocol'},
]


class Chat(Base):
    __tablename__ = 'chats'

    id = sa.Column(sa.BigInteger, primary_key=True)


class Currency(Base):
    __tablename__ = 'currencies'

    id = sa.Column(sa.Integer, primary_key=True)
    code = sa.Column(sa.Text, unique=True, nullable=False)
    name = sa.Column(sa.Text, nullable=False)
    is_active = sa.Column(sa.Boolean, index=True, nullable=False)
    is_crypto = sa.Column(sa.Boolean, index=True, nullable=False)


class ChatRequests(Base):
    __tablename__ = 'chat_requests'

    id = sa.Column(sa.Integer, primary_key=True)
    chat_id = sa.Column(sa.BigInteger, sa.ForeignKey('chats.id'), nullable=False)
    first_currency_id = sa.Column(sa.Integer, sa.ForeignKey('currencies.id'), nullable=True)
    second_currency_id = sa.Column(sa.Integer, sa.ForeignKey('currencies.id'), nullable=True)
    currencies = sa.Column(sa.Text, nullable=False)
    times = sa.Column(sa.Integer, server_default='0', nullable=False)
    modified_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)

    first_currency = relationship('Currency', foreign_keys=[first_currency_id])
    second_currency = relationship('Currency', foreign_keys=[second_currency_id])


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('currencies',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('code', sa.Text(), nullable=False),
                    sa.Column('name', sa.Text(), nullable=False),
                    sa.Column('is_active', sa.Boolean(), nullable=False),
                    sa.Column('is_crypto', sa.Boolean(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('code')
                    )
    op.create_index(op.f('ix_currencies_is_active'), 'currencies', ['is_active'], unique=False)
    op.create_index(op.f('ix_currencies_is_crypto'), 'currencies', ['is_crypto'], unique=False)
    op.add_column('chat_requests', sa.Column('first_currency_id', sa.Integer(), nullable=True))
    op.add_column('chat_requests', sa.Column('second_currency_id', sa.Integer(), nullable=True))
    op.alter_column('chat_requests', 'cnt', new_column_name='times')
    op.create_foreign_key(None, 'chat_requests', 'currencies', ['second_currency_id'], ['id'])
    op.create_foreign_key(None, 'chat_requests', 'currencies', ['first_currency_id'], ['id'])
    # ### end Alembic commands ###

    # fill iso currencies
    currencies = [Currency(code=c['code'], name=c['name'], is_active=True, is_crypto=False) for c in ISO_CURRENCIES]
    session = Session(bind=op.get_bind())
    session.add_all(currencies)
    session.flush()

    # fill excluded iso currencies
    currencies = [Currency(code=c['code'], name=c['name'], is_active=False, is_crypto=False) for c in EXCLUDED_ISO_CURRENCIES]  # NOQA
    session = Session(bind=op.get_bind())
    session.add_all(currencies)
    session.flush()

    # fill not iso currencies
    currencies = [Currency(code=c['code'], name=c['name'], is_active=True, is_crypto=False) for c in NOT_ISO_CURRENCIES]
    session = Session(bind=op.get_bind())
    session.add_all(currencies)
    session.flush()

    # fill x currencies
    currencies = [Currency(code=c['code'], name=c['name'], is_active=True, is_crypto=False) for c in X_CURRENCIES]
    session = Session(bind=op.get_bind())
    session.add_all(currencies)
    session.flush()

    # fill crypto currencies
    currencies = [Currency(code=c['code'], name=c['name'], is_active=True, is_crypto=True) for c in CRYPTO_CURRENCIES]
    session = Session(bind=op.get_bind())
    session.add_all(currencies)
    session.flush()

    def replace_cur(cur):
        if cur == 'B_C':
            return 'BURST'
        else:
            return cur

    # migrating currencies to foreignkey
    i = 0
    for x in session.query(ChatRequests).yield_per(1000):
        first_currency_code = replace_cur(x.currencies[:3])
        second_currency_code = replace_cur(x.currencies[3:])

        try:
            first_currency = session.query(Currency).filter_by(code=first_currency_code).one()
            second_currency = session.query(Currency).filter_by(code=second_currency_code).one()
            x.first_currency = first_currency
            x.second_currency = second_currency
            session.add(x)

            i += 1
            if i % 100 == 0:
                session.flush()
        except NoResultFound:
            print(f'Not found: {x.currencies}, delete.')
            session.delete(x)

    op.drop_column('chat_requests', 'currencies')
    op.alter_column('chat_requests', sa.Column('first_currency_id', sa.Integer(), nullable=False))
    op.alter_column('chat_requests', sa.Column('second_currency_id', sa.Integer(), nullable=False))


def downgrade():
    pass