# SupplyIQ - using SnowFlakes

## 1. Problem Statement: 

> SupplyChain data is distributed across muliple fields : procurement, suppliers, logistics, sales and inventory systems. When the data is avaiable, teams can use different definitions for the same KPI.
> Modern supply chains generate large volumes of structured operational data, but accessing data is only part of the problem, the same business concept must retain the same meaning across procurement, logistics, inventory, and planning workflows.

Actual pain point exists :

<div align="center">

<img width="512" height="299" alt="image" src="https://github.com/user-attachments/assets/d2367f4b-75c2-44ce-b4cc-8df06e89aae2" />

</div>

## 2. About Data:

 - SupplyIQ is built on a **synthetic 365-day supply-chain and ERP simulation dataset** designed to represent the flow of products from suppliers through procurement and inventory to customers.
 - The dataset contains information across multiple operational areas, including **products, suppliers, sourcing relationships, transportation routes, purchase orders, customers, sales, and daily inventory levels**.
 - Rather than treating these datasets independently, SupplyIQ connects them to create a unified view of the supply chain.
 - Link : https://www.kaggle.com/datasets/umuttuygurr/supply-chain-v2?resource=download

### Data Used in SupplyIQ : 

For the current version, **8 core datasets** are used:

| Dataset | What it Represents |
|---|---|
| `PRODUCT` | Product master data including category, pricing, cost, and unit of measure |
| `SUPPLIER` | Supplier information including location and active status |
| `PRODUCT_SUPPLIER` | Sourcing relationships between products and suppliers |
| `SUPPLY_ROUTE` | Logistics routes, transport modes, expected lead times, and shipment costs |
| `PURCHASING` | Purchase-order activity including ordered/received quantities, supplier, route, cost, and receipt dates |
| `CUSTOMER_COMPANY` | Customer information including location and customer segment |
| `SALES` | Product sales, quantities, prices, discounts, customers, and order dates |
| `DAILY_STOCK` | Daily product-level inventory including on-hand, reserved, and in-transit quantities |

### How the Data Connects:

The datasets represent different parts of the same supply-chain process:

<div align = "center">
  
<img width="536" height="320" alt="image" src="https://github.com/user-attachments/assets/04b5ab34-6d19-4764-b7c4-09e128ff918c" />

</div>

**From Raw Data to Analytics** :
```
RAW DATA
   │
   ├── Product
   ├── Supplier
   ├── Purchasing
   ├── Supply Route
   ├── Sales
   ├── Customer
   └── Inventory
   │
   ▼
CURATED LAYER
   │
   ├── PROCUREMENT
   ├── SALES_ANALYTICS
   └── INVENTORY
   │
   ▼
SEMANTIC LAYER

```

## 3. Architecture Diagram:


<img width="952" height="318" alt="image" src="https://github.com/user-attachments/assets/798421ac-a193-401a-848a-b8d96b5837b4" />


 - Snowflake: storage + transformations + semantic layer
 - Cortex Analyst: natural language → governed analytical query
 - Snowpark: application-side Snowflake interaction
 - Streamlit: SupplyIQ UI



## 4. Project Folder:

```text
SupplyIQ/
│
├── app/
│   └── streamlit_app.py
│
├── sql/
│   ├── 01_setup.sql
│   ├── 02_curated_views.sql
│   └── 03_metric_validation.sql
│   └── 04_validate_metrices.sql

│
├── semantic/
│   └── semantic_model.md
│
│
├── assets/
│   └── screenshots/
│
├── data/
│   └── README.md
│
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

## 5. Measured technical outcomes:

## Project Results: 

| Metric | Result |
|---|---:|
| Source Tables Integrated | **8** |
| Curated Analytical Domains | **3** |
| Canonical Governed KPIs | **4** |
| Natural-Language Analytics | **Working** |
| Independent SQL Validation | **Completed** |
| Fill Rate | **97.09%** |
| On-Time Delivery (OTD) | **48.43%** |
| Procurement Deliveries Analyzed | **3,159** |
| Units Ordered | **371,897** |
| Units Received | **361,078** |


## 6. Streamlit Portal:


<img width="1175" height="335" alt="image" src="https://github.com/user-attachments/assets/892061e5-fd19-42d7-907a-3b1d60d1709e" />



Lets test it : 
Questions is : compare on-time delivery percentage by transport mode?

<img width="1038" height="347" alt="image" src="https://github.com/user-attachments/assets/3362689e-8147-4d65-9ad3-0ddb1a46d4e2" />

<img width="1013" height="141" alt="image" src="https://github.com/user-attachments/assets/86859022-9c72-4236-bb5a-ce2f14ba09c3" />





