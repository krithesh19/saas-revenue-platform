with invoices as (
    select * from {{ ref('stg_invoices') }}
),

subscriptions as (
    select * from {{ ref('stg_subscriptions') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

mrr_base as (
    select
        i.invoice_month,
        i.customer_id,
        c.segment,
        c.industry,
        c.country,
        s.plan_name,
        s.billing_cycle,
        sum(i.amount_paid)              as mrr,
        count(distinct i.invoice_id)    as invoice_count,
        sum(i.amount_due)               as amount_billed,
        sum(i.amount_outstanding)       as amount_outstanding
    from invoices i
    left join subscriptions s 
        on i.subscription_id = s.subscription_id
    left join customers c 
        on i.customer_id = c.customer_id
    where i.is_paid = true
    group by 1,2,3,4,5,6,7
),

final as (
    select
        invoice_month,
        customer_id,
        segment,
        industry,
        country,
        plan_name,
        billing_cycle,
        mrr,
        mrr * 12                        as arr,
        invoice_count,
        amount_billed,
        amount_outstanding
    from mrr_base
)

select * from final