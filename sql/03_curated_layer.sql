USE DATABASE SUPPLY_CHAIN_DB;
USE SCHEMA CURATED;

/* -------------------------------------------------- */

CREATE OR REPLACE VIEW CURATED.PROCUREMENT AS

SELECT
    /* Identifiers */
    pu.po_line_id,
    pu.product_id,
    pu.supplier_id,
    pu.route_id,

    /* Product information */
    pr.product_code,
    pr.product_name,
    pr.category,
    pr.uom,

    /* Supplier information */
    su.supplier_name,
    su.supplier_city,
    su.supplier_country,

    /* Route information */
    sr.origin_city,
    sr.destination_city,
    sr.transport_mode,
    sr.lead_time_mean_days,
    sr.lead_time_std_days,
    sr.shipment_cost,

    /* Purchase information */
    pu.order_date,
    pu.receipt_date,
    pu.qty_ordered,
    pu.qty_received,
    pu.unit_cost,
    pu.purch_currency,

    /* -------------------------
       DERIVED BUSINESS FIELDS
       ------------------------- */

    DATEDIFF(
        'day',
        pu.order_date,
        pu.receipt_date
    ) AS actual_lead_time_days,

    DATEADD(
        'day',
        ROUND(sr.lead_time_mean_days),
        pu.order_date
    ) AS expected_receipt_date,

    CASE
        WHEN pu.receipt_date <= DATEADD(
            'day',
            ROUND(sr.lead_time_mean_days),
            pu.order_date
        )
        THEN TRUE
        ELSE FALSE
    END AS is_on_time,

    pu.qty_received / NULLIF(pu.qty_ordered, 0)::FLOAT
        AS line_fill_rate,

    pu.qty_received * pu.unit_cost
        AS procurement_cost,

    (pu.qty_received * pu.unit_cost)
        + sr.shipment_cost
        AS landed_cost

FROM RAW.PURCHASING pu

JOIN RAW.PRODUCT pr
    ON pu.product_id = pr.product_id

JOIN RAW.SUPPLIER su
    ON pu.supplier_id = su.supplier_id

JOIN RAW.SUPPLY_ROUTE sr
    ON pu.route_id = sr.route_id;

/* -------------------------------------------------- */

SELECT *
FROM CURATED.PROCUREMENT
LIMIT 20;

/* -------------------------------------------------- */

SELECT
    po_line_id,
    supplier_name,
    product_name,
    transport_mode,
    actual_lead_time_days,
    expected_receipt_date,
    is_on_time,
    line_fill_rate,
    procurement_cost,
    landed_cost
FROM CURATED.PROCUREMENT
LIMIT 20;

/* ------------------- Sales Analytics------------------------------- */

CREATE OR REPLACE VIEW CURATED.SALES_ANALYTICS AS

SELECT
    /* Identifiers */
    s.sales_id,
    s.product_id,
    s.customer_id,

    /* Product information */
    p.product_code,
    p.product_name,
    p.category,
    p.uom,

    /* Customer information */
    c.customer_name,
    c.customer_city,
    c.customer_segment,

    /* Sales information */
    s.order_date,
    s.qty,
    s.unit_price,
    s.discount_rate,
    s.sale_currency,

    /* -------------------------
       DERIVED BUSINESS FIELDS
       ------------------------- */

    s.qty * s.unit_price
        AS gross_sales_amount,

    (s.qty * s.unit_price) * s.discount_rate
        AS discount_amount,

    (s.qty * s.unit_price) *
        (1 - s.discount_rate)
        AS net_sales_amount

FROM RAW.SALES s

JOIN RAW.PRODUCT p
    ON s.product_id = p.product_id

JOIN RAW.CUSTOMER_COMPANY c
    ON s.customer_id = c.customer_id;
/* ------------------------------------------------ */

SELECT
    sales_id,
    order_date,
    product_name,
    category,
    customer_name,
    customer_segment,
    qty,
    unit_price,
    discount_rate,
    gross_sales_amount,
    discount_amount,
    net_sales_amount
FROM CURATED.SALES_ANALYTICS
LIMIT 20;

/* ----------------- Daily Stock ---------------------- */

CREATE OR REPLACE VIEW CURATED.INVENTORY AS

WITH PRODUCT_DEMAND AS (

    SELECT
        product_id,

        SUM(qty) AS total_sales_qty,

        COUNT(DISTINCT order_date) AS selling_days,

        DATEDIFF(
            'day',
            MIN(order_date),
            MAX(order_date)
        ) + 1 AS demand_period_days,

        SUM(qty) /
        NULLIF(
            DATEDIFF(
                'day',
                MIN(order_date),
                MAX(order_date)
            ) + 1,
            0
        )::FLOAT AS avg_daily_demand

    FROM RAW.SALES

    GROUP BY product_id
)

SELECT

    /* Identifiers */
    ds.product_id,
    ds.date AS inventory_date,

    /* Product information */
    p.product_code,
    p.product_name,
    p.category,
    p.uom,

    /* Inventory information */
    ds.on_hand_qty,
    ds.in_transit_qty,
    ds.reserved_qty,

    /* Available stock */
    ds.on_hand_qty - ds.reserved_qty
        AS available_qty,

    /* Demand information */
    pd.total_sales_qty,
    pd.demand_period_days,
    pd.avg_daily_demand,

    /* -------------------------
       DERIVED BUSINESS METRIC
       ------------------------- */

    ds.on_hand_qty /
        NULLIF(pd.avg_daily_demand, 0)
        AS days_of_inventory

FROM RAW.DAILY_STOCK ds

JOIN RAW.PRODUCT p
    ON ds.product_id = p.product_id

LEFT JOIN PRODUCT_DEMAND pd
    ON ds.product_id = pd.product_id;

/* --------------- view -------------------- */

SELECT
    inventory_date,
    product_id,
    product_name,
    category,
    on_hand_qty,
    reserved_qty,
    available_qty,
    avg_daily_demand,
    days_of_inventory
FROM CURATED.INVENTORY
LIMIT 20;