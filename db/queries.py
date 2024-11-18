create_schema = """CREATE SCHEMA IF NOT EXISTS coupons;"""

delete_tables = ["DROP TABLE IF EXISTS coupons.categories;",
                 "DROP TABLE IF EXISTS coupons.brand;"
                 "DROP TABLE IF EXISTS coupons.offer;"]

create_tables = [
"""
CREATE TABLE IF NOT EXISTS coupons.categories (
	category_id VARCHAR(1000) PRIMARY KEY,
	product_category VARCHAR(1000),
	is_child_category_to VARCHAR(1000)
);
""",
"""
CREATE TABLE IF NOT EXISTS coupons.brand (
	brand VARCHAR(1000),
	brand_category VARCHAR(1000)
);
""",
"""
CREATE TABLE IF NOT EXISTS coupons.offer (
	offer VARCHAR(1000),
	retailer VARCHAR(1000), 
    brand VARCHAR(1000),
    offer_id VARCHAR(1000) PRIMARY KEY
);
"""]

insert_values = [
"INSERT INTO coupons.categories VALUES ('{}', '{}', '{}');",
"INSERT INTO coupons.brand VALUES ('{}', '{}');",
"INSERT INTO coupons.offer VALUES ('{}', '{}', '{}', '{}');"
]
