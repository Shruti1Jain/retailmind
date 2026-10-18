import os
import random
from datetime import datetime, timedelta, timezone
from google.cloud import bigquery

random.seed(42)
project = os.environ['GOOGLE_CLOUD_PROJECT']
dataset = os.getenv('BQ_DATASET','retailmind')
client = bigquery.Client(project=project)
client.create_dataset(bigquery.Dataset(f'{project}.{dataset}'),exists_ok=True)
items = [
 ('Running Shoes','Footwear',3499,'Lightweight cushioned shoes for running'),
 ('Walking Shoes','Footwear',2499,'Comfortable everyday walking shoes'),
 ('Training Sneakers','Footwear',3999,'Breathable sneakers for gym training'),
 ('Cotton T-Shirt','Apparel',799,'Soft cotton casual shirt'),
 ('Yoga Mat','Fitness',1199,'Non-slip exercise and yoga mat'),
 ('Water Bottle','Accessories',599,'Reusable stainless steel bottle'),
 ('Wireless Earbuds','Electronics',2999,'Bluetooth earbuds with charging case'),
 ('Backpack','Accessories',1899,'Durable lightweight daily backpack'),
 ('Fitness Band','Electronics',3299,'Activity tracking wrist band'),
 ('Sports Socks','Apparel',399,'Breathable sports socks')]
products = [{'product_id':f'P{i+1:03}','name':name,'category':category,'price':price,'description':description} for i,(name,category,price,description) in enumerate(items)]
inventory = [{'product_id':p['product_id'],'stock':random.randint(0,60)} for p in products]
transactions = []
for i in range(400):
    p = random.choice(products)
    transactions.append({'transaction_id':f'T{i+1:05}','product_id':p['product_id'], 'quantity':random.randint(1,3),'unit_price':p['price'],'transaction_date':(datetime.now(timezone.utc)-timedelta(days=random.randint(0,89))).date().isoformat()})
schemas = {
 'products':[bigquery.SchemaField('product_id','STRING'),bigquery.SchemaField('name','STRING'),bigquery.SchemaField('category','STRING'),bigquery.SchemaField('price','FLOAT'),bigquery.SchemaField('description','STRING')],
 'inventory':[bigquery.SchemaField('product_id','STRING'),bigquery.SchemaField('stock','INTEGER')],
 'transactions':[bigquery.SchemaField('transaction_id','STRING'),bigquery.SchemaField('product_id','STRING'),bigquery.SchemaField('quantity','INTEGER'),bigquery.SchemaField('unit_price','FLOAT'),bigquery.SchemaField('transaction_date','DATE')]
}
for name,rows in [('products',products),('inventory',inventory),('transactions',transactions)]:
    table=f'{project}.{dataset}.{name}'
    client.load_table_from_json(rows,table,job_config=bigquery.LoadJobConfig(schema=schemas[name],write_disposition='WRITE_TRUNCATE')).result()
    print(f'Loaded {len(rows)} rows into {table}')

