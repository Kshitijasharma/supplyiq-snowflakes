USE DATABASE SUPPLY_CHAIN_DB;
USE SCHEMA RAW;

SELECT
    p.po_line_id,
    p.product_id,
    pr.product_name,
    p.supplier_id,
    s.supplier_name,
    p.route_id,
    r.transport_mode,
    p.qty_ordered,
    p.qty_received
FROM PURCHASING p

JOIN PRODUCT pr
    ON p.product_id = pr.product_id

JOIN SUPPLIER s
    ON p.supplier_id = s.supplier_id

JOIN SUPPLY_ROUTE r
    ON p.route_id = r.route_id

LIMIT 20;



SELECT
    s.sales_id,
    s.product_id,
    p.product_name,
    s.customer_id,
    c.customer_name,
    c.customer_segment,
    s.order_date,
    s.qty,
    s.unit_price
FROM SALES s

JOIN PRODUCT p
    ON s.product_id = p.product_id

JOIN CUSTOMER_COMPANY c
    ON s.customer_id = c.customer_id

LIMIT 20;

SELECT
    ds.date,
    ds.product_id,
    p.product_name,
    p.category,
    ds.on_hand_qty,
    ds.in_transit_qty,
    ds.reserved_qty
FROM DAILY_STOCK ds

JOIN PRODUCT p
    ON ds.product_id = p.product_id

LIMIT 20;