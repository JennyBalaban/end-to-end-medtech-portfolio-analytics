# Star Schema

## Dimensions (lookup tables)
- **dim_date** (Power BI-generated): one row per day, used by all time-based reporting
- **dim_account** (crm_accounts_full.csv): region, country, segment
- **dim_campaign** (marketing_campaigns_full.csv): channel, start/end, objective, spend
- **dim_product** (we’ll create later): product_line hierarchy (optional v1)

## Facts (event tables)
- **fact_leads** (crm_leads_full.csv): funnel events (lead → MQL → SQL)
- **fact_opportunities** (crm_opportunities_full.csv): pipeline + revenue + stage
- **fact_shipments** (erp_shipments_full.csv): operational volume + doctor submitters

## Keys (how tables connect)
- dim_account[account_id] → fact_opportunities[account_id]
- dim_account[account_id] → fact_shipments[account_id]
- dim_campaign[campaign_id] → fact_leads[campaign_id]
- fact_leads[lead_id] → fact_opportunities[lead_id]  (attribution bridge)

## Time handling (important)
- dim_date[date] → fact_leads[created_date]
- dim_date[date] → fact_opportunities[created_date]
- dim_date[date] → fact_opportunities[close_date] (inactive relationship, used with USERELATIONSHIP)
- dim_date[date] → fact_shipments[ship_date]

## Mermaid diagram

```mermaid
erDiagram
  dim_account ||--o{ fact_opportunities : account_id
  dim_account ||--o{ fact_shipments : account_id
  dim_campaign ||--o{ fact_leads : campaign_id
  fact_leads ||--o{ fact_opportunities : lead_id

  dim_date ||--o{ fact_leads : created_date
  dim_date ||--o{ fact_opportunities : created_date
  dim_date ||--o{ fact_shipments : ship_date
