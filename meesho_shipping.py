import json
import os
import gzip
import pymysql
import requests
import db_config
from evpn import ExpressVpnApi

cookies = {
    'isDownloadCta': 'true',
    '_cfuvid': 'l7Ne5jXINlPi7LgxqOEjkA.fb7sPxUfbVrXrVlrHXpY-1721711747522-0.0.1.1-604800000',
    '_gcl_au': '1.1.67570501.1721711748',
    '_ga': 'GA1.1.250436850.1721711748',
    '_fbp': 'fb.1.1721711748528.232891243109385515',
    'isWG': 'false',
    'cf_clearance': 'uKckvJgSKsOR8nNCs3pONd4ELx4OXJHGb_MubYFeNGs-1721726163-1.0.1.1-6G3jbZNY_sB0gVd8_Tktv5q7o.6L5AyD77QgnW9Fn3asBg8_MnDnFTLWeJKWCaAvoAe8PLxzu.ZhYPMWIfydOg',
    '_ga_ZB97HR591S': 'GS1.1.1721735861.5.0.1721735861.60.0.0',
    'CAT_NAV_V2_COOKIE': '0.5301677149198294',
    'ANONYMOUS_USER_CONFIG': 'j%3A%7B%22clientId%22%3A%22a40e6a9c-5cfc-4869-8758-059e41b2%22%2C%22instanceId%22%3A%22a40e6a9c-5cfc-4869-8758-059e41b2%22%2C%22xo%22%3A%22eyJ0eXBlIjoiY29tcG9zaXRlIn0%3D.eyJqd3QiOiJleUpvZEhSd2N6b3ZMMjFsWlhOb2J5NWpiMjB2ZG1WeWMybHZiaUk2SWpFaUxDSm9kSFJ3Y3pvdkwyMWxaWE5vYnk1amIyMHZhWE52WDJOdmRXNTBjbmxmWTI5a1pTSTZJa2xPSWl3aVlXeG5Jam9pU0ZNeU5UWWlmUS5leUpwWVhRaU9qRTNNalkzTWpjeE56Y3NJbVY0Y0NJNk1UZzRORFF3TnpFM055d2lhSFIwY0hNNkx5OXRaV1Z6YUc4dVkyOXRMMmx1YzNSaGJtTmxYMmxrSWpvaVlUUXdaVFpoT1dNdE5XTm1ZeTAwT0RZNUxUZzNOVGd0TURVNVpUUXhZaklpTENKb2RIUndjem92TDIxbFpYTm9ieTVqYjIwdllXNXZibmx0YjNWelgzVnpaWEpmYVdRaU9pSXpaakJrWkRFM05TMWtPVFEwTFRRNU9XRXRPV0k1Tnkwd1pqRmpaVFl6TkdGbU1UQWlmUS5PQ3Nhc21mT2pjd21mQWlOUUJ0QS1ESnBZeDJiTnZZbm9LYklsOWhfajZNIiwieG8iOm51bGx9%22%2C%22createdAt%22%3A%222024-09-19T06%3A26%3A17.483Z%22%7D',
    'ak_bmsc': 'BBBE12E440E999CC34FBF088A7904B84~000000000000000000000000000000~YAAQHP7UFylezmaSAQAALqF6lBmA6Yzb++poC/tJQNk1NKilyKz2XbWOGL+4HKlJ1Zy3/h/WYm3iZRkV/UNfVmUF+wqRWnraJegZOFIFezTbtWULJwk4LbtXfNlkw8cntoW3LtUmKY4IceVmQyC9p5EHUyE/JuF8XPwy9FIb2YKbWp8qty0h7UQwAS2GV7QiNLJmN5C4DSnjAzAcr8OYGtlrKVUatRbDAdKNTpz1085lqHYzfLbM0aVXNQpApGtPveTcAmynyjrI6VjR7jvsifRw0iogqUqXD9vL6gT6TOzqebSrqV45+zlvMOyXaESLvAaA9JW5LVZzQho3pz0wYfwiyul6kfhOyHAwBfDF01QqfaUQEmNqjbA/LIVqOs3dKpY4T+FHqHvcxl7pG+hyqV/QfQdlb/Ms6NKPAXLDnNmNnSuouMvRRJ1uMwv/PMB6w5zasZtDcUw=',
    '__logged_in_user_id_': '395064559',
    'INP_POW': '0.9562994555995177',
    '_abck': 'D82B7C75360AD6DD31D67DEEA2BF3197~0~YAAQqIzQF46I/4uSAQAAYL+YlAwRi43IGKYNUZcu6eKITtY1SSKf6Kyd/UhQm7eLLnvWUFJX6AXx7uGoyfDZGVpoNwp1LDWKPnXTKLfDZ7af9M3kXz32GkyZ4Qo0H1xAQfUpnvgqRSFIWZ2dJun3KcA74yIMvrfeOQfgKRjUKm+ZC/gxeRzOs428qwQn1SJWW0FqXvemk0DziWABjoulwruhHOSORvrU+hbKJYLiClwpY2b4YWfIs7dbf6Hl8oFZb1WcNPjieicXjSb6YLhXoyqMKxu/kopbCpbls9JES36VtSMahF8nJB4EEwaoZ1FA5E+riNZGkYkzwDGpKe+pkRVvpGSab2n+ALYtzG9sw5HsJFeZ81lWOxIFHGJuUQNjD0O5sxTNAhx3BKWXzrZP1To+G1UThmlttyJUVTYGkXv5j3tpwz/iZ3OwKYXeEsyaNUoj7hN75TbxeRTUarQz/uAmSE+m6aIxXER5WQIAxy2YyzI7i/4vIKmCFA7BlIJaDp1VwfSkl/MAuxSf7mjonmv9aJu8xUjGVGV9NJ2sCw2a8X9uwDpmfZlFwDDZ4nh1D4fAxwx3TQ9cF9YOlOBM/X0GqGI0OTMCzO1kBMdZRDyaCftoQx0Ee2hwooLIaWfMvL7Ftf8qKW+nFrrg~-1~||0||~1729071516',
    'bm_sz': 'B06CA9D5D67466FA2C90A36098B41764~YAAQqIzQF4+I/4uSAQAAYL+YlBmp1YgMx1LC9Wb5Ml+1wDvLA/Q7Rg2v4BUK0jM85/R+2mpxkvlcS2d2mzf1eLL/E/YegKZcIQ1zTyWWUZLDP4uQH1RKwdw/NXRFsdGzdf1n1BJ4JtdGYn0Q6/dbcul7vQj2b7UsihsRN4esssqUmakqsZ0NFdr2wZuFQLtyNDn/SvV9Z8idlIPGD82wWwxhheQop8503YVflOpGkwAXj1QF6xFab/Mu0uiVQMbQdV7FZ1ZQYzFB0qFhLrXktRK3X/5UZOEtPmjDZh3IdtK+sHqLNz03zuDqbsh/bWk4Tlr8gzY7aEXFR3iJ6LDp9yNczGhJanJG6IDftt8O50pp/pp5WNpBVrxVSS7pUUMjE3/pShAF1rtakgt9/3gcBNzLbCkmbAhUObLTY2hD7GZxJnYAyCEd9iyKIMGamyMNK6AOS84X7hNE91p0Hzw+CK7E~4539188~3224389',
    'bm_sv': 'C4338B10E3054B708DEE94E591FC9E40~YAAQqIzQF5SI/4uSAQAASMGYlBne+r8ep7Y6k4+w3I4YL/FxIHvoRN8GBNJXyWGEQp4wZVk+sIm32cxMWBt/5lx+E5R9Ll6YL/gubWXwr2Ctp+Ep39fwbClaGePlmcxrYdpEb64HMkh496227KKgSPlNl1cZWJrqJ7rDmFREJNFcMvD61os8PLq1VL5eWA5eZZK0ouzEsl//y5qDud8veUzJJo3O9u8jmm8UUDRCHsD2AM9tJmZ8H+czfU+UzxpG9g==~1',
    'mp_60483c180bee99d71ee5c084d7bb9d20_mixpanel': '%7B%22distinct_id%22%3A%20%2219294986ac5af-062865bbb97419-26001051-144000-19294986ac6372%22%2C%22%24device_id%22%3A%20%2219294986ac5af-062865bbb97419-26001051-144000-19294986ac6372%22%2C%22Session%20ID%22%3A%20%225db7033c-4832-4de2-9d8e-9638cb7a%22%2C%22last%20event%20time%22%3A%201729069875167%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%2C%22%24user_id%22%3A%20%2219294986ac5af-062865bbb97419-26001051-144000-19294986ac6372%22%2C%22Is%20Anonymous%22%3A%20%22True%22%2C%22Instance_Id%22%3A%20%22a40e6a9c-5cfc-4869-8758-059e41b2%22%2C%22V2%20Cat-Nav%20Exp%20Enabled%22%3A%20true%7D',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,id;q=0.8',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
}

json_data = {
    'include_catalog': True,
    'ad_active': True,
}

conn = pymysql.connect(host=db_config.db_host, user=db_config.db_user, password=db_config.db_password,
                       database=db_config.db_name, autocommit=True)
cur = conn.cursor()
# api = ExpressVpnApi().connect(152)

# time.sleep(3)


page_save_path = r"C:\Meesho_shipping_data\meesho_page_save"
os.makedirs(page_save_path, exist_ok=True)
start_id = 50001
end_id = 100000

cur.execute(
    f"select meesho_pid from product_links_20241014 where status_560001='pending' and meesho_pid is not null and id between {start_id} and {end_id}")
results = cur.fetchall()

for result in results:
    product_id = result[0]
    response = requests.post(f'https://www.meesho.com/api/v1/product/{product_id}', cookies=cookies, headers=headers,json=json_data)
    print(response.status_code)
    if response.status_code == 403:
        break
    if response.status_code == 200:
        with gzip.open(fr'{page_save_path}\{product_id}.html.gz', 'wb') as f:
            f.write(json.dumps(response.json()).encode('utf-8'))
        print(f"Product Page Saved.. {product_id}")
        cur.execute('update product_links_20241014 set status_560001="DONE" where meesho_pid=%s', product_id)
        print("=" * 10)

