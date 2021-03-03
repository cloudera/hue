# coding: utf-8
# Tests for django_util
# Some parts based on http://www.djangosnippets.org/snippets/1044/
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from builtins import object
import datetime

from nose.tools import assert_true, assert_equal, assert_not_equal

from desktop.lib.python_util import CaseInsensitiveDict, force_dict_to_strings, force_list_to_strings, check_encoding


class TestPythonUtil(object):
  def test_case_insensitive_dictionary(self):
    d = CaseInsensitiveDict()
    d["Test"] = "Test"
    assert_true("Test" in d)
    assert_true("test" in d)
    assert_equal("Test", d['Test'])
    assert_equal("Test", d['test'])
    assert_not_equal("test", d['Test'])
    assert_not_equal("test", d['test'])

  def test_force_dict_to_strings(self):
    unicode_dict = {u'test': u'test'}
    string_dict = {'test': 'test'}
    transformed_dict = force_dict_to_strings(unicode_dict)
    assert_equal(string_dict, transformed_dict)

    # Embedded
    unicode_dict = {u'test': {u'test': u'test'}}
    string_dict = {'test': {'test': 'test'}}
    transformed_dict = force_dict_to_strings(unicode_dict)
    assert_equal(string_dict, transformed_dict)

    # Embedded list
    unicode_dict = {u'test': [{u'test': u'test'}]}
    string_dict = {'test': [{'test': 'test'}]}
    transformed_dict = force_dict_to_strings(unicode_dict)
    assert_equal(string_dict, transformed_dict)

  def test_force_list_to_strings(self):
    unicode_list = [u'test', {u'test': u'test'}]
    string_list = ['test', {'test': 'test'}]
    transformed_list = force_list_to_strings(unicode_list)
    assert_equal(string_list, transformed_list)


  def test_check_encoding(self):
    shift_jis = u"""
都道府県,都道府県庁所在地,人口,面積,人口密度,集積度,備考
北海道,札幌市の市旗（北海道） 札幌市,"1,961,690","1,121.26","1,750",37.5,政令指定都市
青森県,青森市の市旗（青森県） 青森市,"272,565",824.61,331,22.2,中核市
岩手県,盛岡市の市旗（岩手県） 盛岡市,"290,700",886.47,328,24.1,中核市
宮城県,仙台市の市旗（宮城県） 仙台市,"1,092,317",786.3,"1,389",47.7,政令指定都市
秋田県,秋田市の市旗（秋田県） 秋田市[14],"303,337",906.07,335,32,中核市
山形県,山形市の市旗（山形県） 山形市[14],"247,422",381.3,649,23.3,中核市
福島県,福島市の市旗（福島県） 福島市,"284,646",767.72,371,15.6,中核市
茨城県,水戸市の市旗（茨城県） 水戸市[14],"269,186",217.32,"1,239",9.4,中核市
栃木県,宇都宮市の市旗（栃木県） 宇都宮市,"518,443",416.85,"1,244",26.9,中核市
群馬県,前橋市の市旗（群馬県） 前橋市,"331,695",311.59,"1,065",17.2,中核市
埼玉県,さいたま市の市旗（埼玉県） さいたま市,"1,320,197",217.43,"6,072",18,政令指定都市
千葉県,千葉市の市旗（千葉県） 千葉市,"981,871",271.77,"3,613",15.6,政令指定都市
東京都,新宿区の区旗（東京都） 新宿区[7][13][14],"346,735",18.22,"19,030",2.5,特別区
,東京都区部（東京）[7],"9,650,247",627.57[15],"15,377",69.2,旧東京市
神奈川県,横浜市の市旗（神奈川県） 横浜市,"3,757,630",437.56,"8,588",40.8,政令指定都市
新潟県,新潟市の市旗（新潟県） 新潟市[14],"791,326",726.45,"1,089",36.1,政令指定都市
富山県,富山市の市旗（富山県） 富山市,"413,723","1,241.77",333,40.1,中核市
石川県,金沢市の市旗（石川県） 金沢市[14],"462,479",468.64,987,41,中核市
福井県,福井市の市旗（福井県） 福井市,"260,807",536.41,486,34.3,中核市
山梨県,甲府市の市旗（山梨県） 甲府市,"187,316",212.47,882,23.3,中核市
長野県,長野市の市旗（長野県） 長野市,"367,582",834.81,440,18.1,中核市
岐阜県,岐阜市の市旗（岐阜県） 岐阜市[14],"400,118",203.6,"1,965",20.3,中核市
静岡県,静岡市の市章（静岡県） 静岡市,"686,085","1,411.90",486,19,政令指定都市
愛知県,名古屋市の市旗（愛知県） 名古屋市,"2,327,723",326.45,"7,130",30.9,政令指定都市
三重県,津市の市旗（三重県） 津市,"273,267",711.19,384,15.5,?
滋賀県,大津市の市旗（滋賀県） 大津市,"342,716",464.51,738,24.3,中核市
京都府,京都市の市旗（京都府） 京都市,"1,455,377",827.83,"1,758",56.8,政令指定都市
大阪府,大阪市の市旗（大阪府） 大阪市,"2,753,476",225.21,"12,226",31.2,政令指定都市
兵庫県,神戸市の市旗（兵庫県） 神戸市,"1,514,434",557.02,"2,719",27.9,政令指定都市
奈良県,奈良市の市旗（奈良県） 奈良市[14],"352,571",276.94,"1,273",26.7,中核市
和歌山県,和歌山市の市旗（和歌山県） 和歌山市,"353,486",208.84,"1,693",38.8,中核市
鳥取県,鳥取市の市旗（鳥取県） 鳥取市,"187,442",765.31,245,34.1,中核市
島根県,松江市の市旗（島根県） 松江市,"202,008",572.99,353,30.4,中核市
岡山県,岡山市の市旗（岡山県） 岡山市,"720,456",789.95,912,38.3,政令指定都市
広島県,広島市の市旗（広島県） 広島市[14],"1,198,224",906.68,"1,322",42.9,政令指定都市
山口県,山口市の市旗（山口県） 山口市,"193,796","1,023.23",189,14.5,?
徳島県,徳島市の市旗（徳島県） 徳島市[14],"254,510",191.39,"1,330",35.3,?
香川県,高松市の市旗（香川県） 高松市,"417,814",375.41,"1,113",44,中核市
愛媛県,松山市の市旗（愛媛県） 松山市,"506,749",429.4,"1,180",38.3,中核市
高知県,高知市の市旗（高知県） 高知市,"325,807",309,"1,054",47.4,中核市
福岡県,福岡市の市旗（福岡県） 福岡市,"1,603,043",343.39,"4,668",31.4,政令指定都市
佐賀県,佐賀市の市旗（佐賀県） 佐賀市,"232,485",431.84,538,28.8,施行時特例市
長崎県,長崎市の市旗（長崎県） 長崎市,"405,090",405.86,998,31,中核市
熊本県,熊本市の市旗（熊本県） 熊本市,"738,469",390.32,"1,892",42.6,政令指定都市
大分県,大分市の市旗（大分県） 大分市,"477,354",502.38,950,42.5,中核市
宮崎県,宮崎市の市旗（宮崎県） 宮崎市,"397,560",643.67,618,37.5,中核市
鹿児島県,鹿児島市の市旗（鹿児島県） 鹿児島市[14],"593,808",547.58,"1,084",37.4,中核市
沖縄県,那覇市の市旗（沖縄県） 那覇市[14],"316,196",39.98,"7,909",21.6,中核市
    """

    gb2312 = u"""
Before,Chinese,After,Chinese,Renamed date
Weihaiwei,威海卫市,Weihai,威海市,1949-11-01
Xingshan,兴山市,Hegang,鹤岗市,1950-03-23
Xi'an,西安市,Liaoyuan,辽源市,1952-04-03
Nanzheng,南郑市,Hanzhong,汉中市,1953-10-24
Dihua,迪化市,?rümqi,乌鲁木齐市,1953-11-20
Guisui,归绥市,Hohhot,呼和浩特市,1954-04-20
Xinhailian,新海连市,Lianyungang,连云港市,1961-09-02
Andong,安东市,Dandong,丹东市,1965-01-20
Suixi,濉溪市,Huaibei,淮北市,1971-03-30
Anda,安达市,Daqing,大庆市,1979-12-14
Sucheng,宿城市,Suzhou,宿州市,1980-02-29
Lüda,旅大市,Dalian,大连市,1981-02-09
Dukou,渡口市,Panzhihua,攀枝花市,1987-01-23
Meixian,梅县市,Meizhou,梅州市,1988-01-07
Daxian,达县市,Dazhou,达州市,1993-07-05
Hunjiang,浑江市,Baishan,白山市,1994-01-31
Dayong,大庸市,Zhangjiajie,张家界市,1994-04-04
Jinxi,锦西市,Huludao,葫芦岛市,1994-09-20
Jingsha,荆沙市,Jingzhou,荆州市,1996-11-20
Puqi,蒲圻市,Chibi,赤壁市,1998-06-11
Zhicheng,枝城市,Yidu,宜都市,1998-06-11
Huaiyin,淮阴市,Huai'an,淮安市,2000-12-21
Tongza,通什市,Wuzhishan,五指山市,2001-07-05
Tiefa,铁法市,Diaobingshan,调兵山市,2002-02-20
Beining,北宁市,Beizhen,北镇市,2006-02-08
Simao,思茅市,Pu'er,普洱市,2007-01-21
Luxi,潞西市,Mangshi,芒市,2007-12-30
Xiangfan,襄樊市,Xiangyang,襄阳市,2010-11-26
  """
    big_5 = u"""
Name,Chinese,County,Founded,"Population"
Kaohsiung,高雄市,none,1979-07-01,"1,402,914"
New Taipei,新北市,none,2010-12-25,"3,974,911"
Taichung,臺中市,none,2010-12-25,"2,759,887"
Tainan,臺南市,none,2010-12-25,"1,885,499"
Taipei,臺北市,none,1967-07-01,"2,696,316"
Taoyuan,桃園市,none,2014-12-25,"2,136,702"
Chiayi,嘉義市,none,1982-07-01,"269,890"
Hsinchu,新竹市,none,1982-07-01,"436,220"
Keelung,基隆市,none,1945-10-25,"372,019"
Changhua,彰化市,Changhua,1951-12-01,"234,721"
Douliu,斗六市,Yunlin,1981-12-25,"108,098"
Hualien,花蓮市,Hualien,1946-01-16,"106,368"
Magong,馬公市,Penghu,1981-12-25,"60,335"
Miaoli,苗栗市,Miaoli,1981-12-25,"90,963"
Nantou,南投市,Nantou,1981-12-25,"102,314"
Pingtung,屏東市,Pingtung,1951-12-01,"203,866"
Puzi,朴子市,Chiayi,1992-09-10,"43,250"
Taibao,太保市,Chiayi,1991-07-01,"37,038"
Taitung,臺東市,Taitung,1976-01-01,"106,969"
Toufen,頭份市,Miaoli,2015-10-05,"102,654"
Yilan,宜蘭市,Yilan,1946-01-16,"95,879"
Yuanlin,員林市,Changhua,2015-08-08,"124,730"
Zhubei,竹北市,Hsinchu,1988-10-31,"203,195"
    """

    euc_kr = u"""
Before,Hangul,Hanja,After,Hangul,Hanja,Renamed date
Chungmu,충무시,忠武市,Tongyeong,통영시,統營市,1995-01-01
Daecheon,대천시,大川市,Boryeong,보령시,保寧市,1995-01-01
Donggwangyang,동광양시,東光陽市,Gwangyang,광양시,光陽市,1995-01-01
Geumseong,금성시,錦城市,Naju,나주시,羅州市,1986-01-01
Gyeongseong,경성부,京城府,Seoul,서울특별자유시,特別自由市,1946-08-16
Iri,이리시,裡里市,Iksan,익산시,益山市,1995-05-10
Jangseungpo,장승포시,長承浦市,Geoje,거제시,巨濟市,1995-01-01
Jeomchon,점촌시,店村市,Mungyeong,문경시,聞慶市,1995-01-01
Jeongju,정주시,井州市,Jeongeup,정읍시,井邑市,1995-01-01
Migeum,미금시,渼金市,Namyangju,남양주시,南楊州市,1995-01-01
Onyang,온양시,溫陽市,Asan,아산시,牙山市,1995-01-01
Samcheonpo,삼천포시,三千浦市,Sacheon,사천시,泗川市,1995-05-10
    """

    iso_8859 = u"""
ID,Commune,Département,Statut,Région,2017,2016,2014,2013,2006,1999,1990,1982,1975,1968
1,Maubeuge,Nord,--,Hauts-de-France,29 944,29 679,30 347,30 567,32 699,33 546,34 989,36 061,35 399,32 028
2,Aix-les-Bains,Savoie,--,Auvergne-Rhône-Alpes,29 794,29 799,30 291,29 580,27 375,25 782,24 683,23 451,22 210,20 627
3,Mont-de-Marsan,Landes,Préfecture,Nouvelle-Aquitaine,29 554,29 885,31 009,31 334,30 230,29 489,28 328,27 326,26 166,24 444
4,Clichy-sous-Bois,Seine-Saint-Denis,--,Île-de-France,29 348,29 835,29 933,30 725,29 412,28 288,28 180,24 654,22 422,16 357
5,Vienne,Isère,Sous-préfecture,Auvergne-Rhône-Alpes,29 306,29 454,29 096,29 325,30 092,29 975,29 449,28 294,27 830,29 057
6,Dieppe,Seine-Maritime,Sous-préfecture,Normandie,29 080,29 606,30 086,30 214,33 618,34 653,35 894,35 957,39 466,30 016
7,Sotteville-lès-Rouen,Seine-Maritime,--,Normandie,28 965,28 991,28 910,28 704,30 076,29 553,29 544,30 558,31 659,34 495
8,Saint-Étienne-du-Rouvray,Seine-Maritime,--,Normandie,28 641,28 696,28 752,28 738,27 815,29 092,30 731,32 444,37 242,34 713
9,Soissons,Aisne,Sous-préfecture,Hauts-de-France,28 530,28 466,28 290,28 472,28 442,29 453,29 829,30 213,30 009,25 890
10,Saint-Laurent-du-Var,Alpes-Maritimes,--,Provence-Alpes-Côte d'Azur,28 453,28 645,29 067,28 891,30 076,27 141,24 426,20 678,15 503,10 156
11,Saumur,Maine-et-Loire,Sous-préfecture,Pays de la Loire,26 734,27 125,27 301,27 413,28 654,28 935,30 131,32 149,32 515,31 629
12,Vallauris,Alpes-Maritimes,--,Provence-Alpes-Côte d'Azur,26 672,26 618,26 302,27 465,30 610,25 773,24 325,21 205,17 182,12 880
13,Vierzon,Cher,Sous-préfecture,Centre-Val de Loire,25 903,26 365,27 050,27 113,28 147,29 719,32 235,34 209,35 699,33 775
14,Alençon,Orne,Préfecture,Normandie,25 848,26 129,26 028,26 350,28 458,28 935,29 988,31 608,33 680,31 656
15,Le Grand-Quevilly,Seine-Maritime,--,Normandie,25 698,25 897,25 273,24 967,26 226,26 679,27 658,31 650,31 963,25 611
16,Aurillac,Cantal,Préfecture,Auvergne-Rhône-Alpes,25 499,25 954,26 135,26 572,29 477,30 551,30 773,30 963,30 863,28 226
17,Biarritz,Pyrénées-Atlantiques,--,Nouvelle-Aquitaine,25 404,24 777,24 713,24 993,26 690,30 055,28 742,26 598,27 595,26 750
18,Montbéliard,Doubs,Sous-préfecture,Bourgogne-Franche-Comté,25 395,25 304,25 521,25 697,26 535,27 570,29 005,31 836,30 425,23 908
19,Vichy,Allier,Sous-préfecture,Auvergne-Rhône-Alpes,24 166,24 383,26 279,25 325,26 108,26 528,27 714,30 527,32 117,33 506
20,Saint-Dizier,Haute-Marne,Sous-préfecture,Grand Est,24 012,24 932,25 505,25 626,26 972,30 900,33 552,35 189,37 266,36 616
21,Orly,Val-de-Marne,--,Île-de-France,23 801,23 378,22 603,22 377,21 197,20 470,21 646,23 766,26 104,30 197
22,Bruay-la-Buissière,Pas-de-Calais,--,Hauts-de-France,21 831,22 230,22 579,22 802,23 813,23 998,24 927,26 649,29 435,32 341
23,Le Creusot,Saône-et-Loire,--,Bourgogne-Franche-Comté,21 630,21 752,21 991,22 308,23 813,26 283,28 909,32 149,33 366,34 102
    """

    cp1252 = u"""
Rank,City/town,Russian,Federal subject,Federal district,Population,Change
1,Moscow,Москва,Moscow (federal city)[3],Central,"12,480,481",8.49%
2,Saint Petersburg,Санкт-Петербург,Saint Petersburg (federal city)[4],Northwest,"5,398,064",10.63%
3,Novosibirsk,Новосибирск,Novosibirsk Oblast,Siberia,"1,625,631",10.31%
4,Yekaterinburg,Екатеринбург,Sverdlovsk Oblast,Ural,"1,493,749",10.67%
5,Kazan,Казань,Republic of Tatarstan,Volga,"1,257,391",9.96%
6,Nizhny Novgorod,Нижний Новгород,Nizhny Novgorod Oblast,Volga,"1,252,236",0.13%
7,Chelyabinsk,Челябинск,Chelyabinsk Oblast,Ural,"1,196,680",5.89%
8,Samara,Самара,Samara Oblast,Volga,"1,156,659",-0.69%
9,Omsk,Омск,Omsk Oblast,Siberia,"1,154,507",0.03%
10,Rostov-on-Don,Ростов-на-Дону,Rostov Oblast,South[5],"1,137,904",4.47%
11,Ufa,Уфа,Republic of Bashkortostan,Volga,"1,128,787",6.26%
12,Krasnoyarsk,Красноярск,Krasnoyarsk Krai,Siberia,"1,093,771",12.32%
13,Voronezh,Воронеж,Voronezh Oblast,Central,"1,058,261",18.95%
14,Perm,Пермь,Perm Krai,Volga,"1,055,397",6.48%
15,Volgograd,Волгоград,Volgograd Oblast,South,"1,008,998",-1.20%
16,Krasnodar,Краснодар,Krasnodar Krai,South,"932,629",25.19%
17,Saratov,Саратов,Saratov Oblast,Volga,"838,042",0.02%
18,Tyumen,Тюмень,Tyumen Oblast,Ural,"807,271",38.73%
19,Tolyatti,Тольятти,Samara Oblast,Volga,"699,429",-2.81%
20,Izhevsk,Ижевск,Udmurt Republic,Volga,"648,146",3.25%
21,Barnaul,Барнаул,Altai Krai,Siberia,"632,391",3.26%
22,Ulyanovsk,Ульяновск,Ulyanovsk Oblast,Volga,"627,705",2.10%
23,Irkutsk,Иркутск,Irkutsk Oblast,Siberia,"623,562",6.07%
24,Khabarovsk,Хабаровск,Khabarovsk Krai,Far East,"616,372",6.74%
25,Yaroslavl,Ярославль,Yaroslavl Oblast,Central,"608,353",2.85%
26,Vladivostok,Владивосток,Primorsky Krai,Far East,"606,561",2.45%
27,Makhachkala,Махачкала,Republic of Dagestan,North Caucasus,"603,518",5.50%
28,Tomsk,Томск,Tomsk Oblast,Siberia,"576,624",9.90%
29,Orenburg,Оренбург,Orenburg Oblast,Volga,"572,188",4.35%
30,Kemerovo,Кемерово,Kemerovo Oblast,Siberia,"556,382",4.39%
31,Novokuznetsk,Новокузнецк,Kemerovo Oblast,Siberia,"549,403",0.27%
32,Ryazan,Рязань,Ryazan Oblast,Central,"539,290",2.74%
33,Naberezhnye Chelny,Набережные ЧелныRepublic of Tatarstan,Volga,"533,839",4.02%
34,Astrakhan,Астрахань,Astrakhan Oblast,South,"529,793",1.82%
35,Penza,Пенза,Penza Oblast,Volga,"520,300",0.58%
36,Kirov,Киров,Kirov Oblast,Volga,"518,348",9.43%
37,Lipetsk,Липецк,Lipetsk Oblast,Central,"508,573",-0.06%
38,Balashikha,Балашиха,Moscow Oblast,Central,"507,366",135.44%
39,Cheboksary,Чебоксары,Chuvash Republic,Volga,"497,618",9.67%
40,Kaliningrad,Калининград,Kaliningrad Oblast,Northwest,"489,359",13.30%
41,Tula,Тула,Tula Oblast,Central,"475,161",-5.19%
42,Kursk,Курск,Kursk Oblast,Central,"452,976",9.11%
43,Stavropol,Ставрополь,Stavropol Krai,North Caucasus,"450,680",13.08%
44,Sochi,Сочи,Krasnodar Krai,South,"443,562",29.19%
45,Ulan-Ude,Улан-Удэ,Republic of Buryatia,Far East,"439,128",8.58%
46,Tver,Тверь,Tver Oblast,Central,"425,072",5.32%
47,Magnitogorsk,Магнитогорск,Chelyabinsk Oblast,Ural,"413,253",1.34%
48,Ivanovo,Иваново,Ivanovo Oblast,Central,"404,598",-0.91%
    """


    test_dict = {
      'shift-jis': shift_jis.encode('shift-jis'),
      'gb2312': gb2312.encode('gb2312'),
      'big5': big_5.encode('big5'),
      'EUC-KR': euc_kr.encode('EUC-KR'),
      'iso-8859-1': iso_8859.encode('iso-8859-1'),
      ### 'cp1252': cp1252.encode('cp1252')
    }

    for key in test_dict:
      enc_code = check_encoding(test_dict[key])
      assert_equal(key, enc_code, "compare target encoding %s with tested encoding %s" % (key, enc_code))
