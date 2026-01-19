# Search URL Templates for targeted scraping

UAE_SITES = [
    {
        "name": "Dubizzle",
        "url_template": "https://uae.dubizzle.com/motors/used-cars/{make}/{model}/?year__gte={year_min}&year__lte={year_max}",
        "region": "UAE"
    },
    {
        "name": "YallaMotor",
        "url_template": "https://www.yallamotor.com/used-cars/{make}/{model}/{year_min}-{year_max}",
        "region": "UAE"
    },
    {
        "name": "DubiCars",
        "url_template": "https://www.dubicars.com/search?c=used&ma={make}&mo={model}&y={year_min}&y={year_max}",
        "region": "UAE"
    },
    {
        "name": "Cars24",
        "url_template": "https://www.cars24.com/ae/buy-used-cars-uae/?mn={make}&mo={model}&yr={year_min}-{year_max}",
        "region": "UAE"
    },
     {
        "name": "AutoTrader UAE",
        "url_template": "https://www.autotraderuae.com/used-cars/{make}/{model}/year-{year_min}/{year_max}/",
        "region": "UAE"
    }
]

USA_SITES = [
    {
        "name": "Cars.com",
        "url_template": "https://www.cars.com/shopping/results/?stock_type=used&makes[]={make}&models[]={make}-{model}&year_min={year_min}&year_max={year_max}",
        "region": "USA"
    },
    {
        "name": "AutoTrader",
        "url_template": "https://www.autotrader.com/cars-for-sale/all-cars/{make}/{model}/{year_min}?endYear={year_max}",
        "region": "USA"
    },
    {
        "name": "Copart",
        "url_template": "https://www.copart.com/lotSearchResults?free=true&query={make}%20{model}%20{year_min}-{year_max}",
        "region": "USA"
    }
]

JAPAN_SITES = [
    {
        "name": "SBT Japan",
        "url_template": "https://www.sbtjapan.com/used-cars/{make}/{model}/?year_from={year_min}&year_to={year_max}",
        "region": "Japan"
    },
    {
        "name": "BeForward",
        "url_template": "https://www.beforward.jp/stocklist/make={make}/model={model}/year_from={year_min}/year_to={year_max}",
        "region": "Japan"
    },
    {
        "name": "TC-V",
        "url_template": "https://www.tc-v.com/used_car/{make}/{model}/?year_from={year_min}&year_to={year_max}",
        "region": "Japan"
    }
]

KOREA_SITES = [
    {
        "name": "Autowini",
        "url_template": "https://www.autowini.com/search/cars?kwd={make}%20{model}&yearFrom={year_min}&yearTo={year_max}",
        "region": "Korea"
    },
    {
        "name": "Encar",
        "url_template": "http://www.encar.com/dc/dc_carsearch.do?carType=kor&searchType=model&model={model}&make={make}&minYear={year_min}&maxYear={year_max}",
        "region": "Korea"
    }
]

CHINA_SITES = [
    {
        "name": "Alibaba",
        "url_template": "https://www.alibaba.com/trade/search?fsb=y&IndexArea=product_en&CatId=&SearchText={make}+{model}+{year_min}",
        "region": "China"
    },
    {
        "name": "Made-in-China",
        "url_template": "https://www.made-in-china.com/productdirectory.do?word={make}+{model}+{year_min}",
        "region": "China"
    }
]

EUROPE_SITES = [
    {
        "name": "Mobile.de",
        "url_template": "https://suchen.mobile.de/fahrzeuge/search.html?dam=0&isSearchRequest=true&ms={make};{model};;&od=up&sb=p&vc=Car&y={year_min}:{year_max}",
        "region": "Europe"
    },
    {
        "name": "AutoScout24",
        "url_template": "https://www.autoscout24.com/lst/{make}/{model}?fregfrom={year_min}&fregto={year_max}",
        "region": "Europe"
    }
]

ALL_SITES_CONFIG = {
    "UAE": UAE_SITES,
    "USA": USA_SITES,
    "Japan": JAPAN_SITES,
    "Korea": KOREA_SITES,
    "China": CHINA_SITES,
    "Europe": EUROPE_SITES,
}
