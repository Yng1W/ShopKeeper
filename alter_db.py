import pymysql
try:
    conn = pymysql.connect(host='localhost', user='root', password='', db='shopkeeper')
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE invoices ADD COLUMN payment_option VARCHAR(50) NOT NULL DEFAULT 'standard';")
    conn.commit()
    conn.close()
    print('ALTER TABLE successful')
except Exception as e:
    print('Error:', e)
