from datetime import datetime, timedelta

import pymysql
import pytz

db_host = '172.27.131.60'
db_user = 'root'
db_password = 'actowiz'
db_port = 3306
db_name = 'fk_meesho_vertial_master'

today = datetime.now(pytz.timezone('Asia/Calcutta'))

# FOR TODAY's Date (in case running after 1:30 PM in india and RUNNING IN OVH)
delivery_date = str(datetime.today().strftime("%Y%m%d"))

# FOR TODAY's + 1  Date (in case running before 1:30 PM in india and RUNNING IN OVH)
# delivery_date = (datetime.today() + timedelta(days=1)).strftime("%Y%m%d"
