USE DATABASE SUPPLY_CHAIN_DB;
USE SCHEMA CURATED;

/*------------------------------ Fill Rate = (total quantity received / total qunatity ordered) X 100 ----------- */

SELECT
    SUM(qty_ordered) AS total_ordered,
    SUM(qty_received) AS total_received,

    ROUND(
        100.0 * SUM(qty_received)
        / NULLIF(SUM(qty_ordered), 0),
        2
    ) AS fill_rate_pct

FROM CURATED.PROCUREMENT;

/* -------------- validate on time delivery --------------------- */
/* ------- Expected Receipt Date = Order Date + Route Mean Lead Time | On time = Receipt Date <= Expected Reciept Date ----- */

SELECT
    COUNT(*) AS total_deliveries,

    COUNT_IF(is_on_time = TRUE)
        AS on_time_deliveries,

    ROUND(
        100.0 * COUNT_IF(is_on_time = TRUE)
        / NULLIF(COUNT(*), 0),
        2
    ) AS on_time_delivery_pct

FROM CURATED.PROCUREMENT
WHERE receipt_date IS NOT NULL;


/* ----------- validate landed cost ---------------- */
/* ----------- Landed cost = (Qty Received x Unit Cost) + Shipment cost */

SELECT
    ROUND(SUM(procurement_cost), 2)
        AS total_procurement_cost,

    ROUND(SUM(shipment_cost), 2)
        AS total_shipment_cost,

    ROUND(SUM(landed_cost), 2)
        AS total_landed_cost

FROM CURATED.PROCUREMENT;

/* -------------- validate days of Inventory ----------- */
SELECT
    inventory_date,
    product_name,
    on_hand_qty,
    ROUND(avg_daily_demand, 2)
        AS avg_daily_demand,

    ROUND(days_of_inventory, 2)
        AS days_of_inventory

FROM CURATED.INVENTORY

WHERE avg_daily_demand > 0

ORDER BY inventory_date DESC

LIMIT 20;




