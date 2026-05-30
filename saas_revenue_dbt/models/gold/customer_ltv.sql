with invoices as (
    select * from {{ ref('stg_invoices') }}
),

subscriptions as (
    select * from {{ ref('stg_subscriptions') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

-- Total revenue per customer
customer_revenue as (
    select
        customer_id,
        sum(amount_paid)                as total_revenue,
        count(distinct invoice_month)   as active_months,
        min(invoice_date)               as first_invoice_date,
        max(invoice_date)               as last_invoice_date,
        avg(amount_paid)                as avg_monthly_revenue
    from invoices
    where is_paid = true
    group by 1
),

-- Subscription details per customer
customer_subs as (
    select
        customer_id,
        plan_name,
        mrr,
        status,
        tenure_months,
        billing_cycle,
        is_upgraded
    from subscriptions
),

final as (
    select
        c.customer_id,
        c.company_name,
        c.segment,
        c.industry,
        c.country,
        c.acquisition_channel,
        c.signup_date,
        s.plan_name,
        s.mrr,
        s.status,
        s.tenure_months,
        s.billing_cycle,
        s.is_upgraded,
        r.total_revenue,
        r.active_months,
        r.avg_monthly_revenue,
        r.first_invoice_date,
        r.last_invoice_date,
        -- LTV calculation
        r.total_revenue                 as historical_ltv,
        -- Projected LTV (avg monthly revenue * expected lifetime)
        case
            when s.status = 'Active' 
            then r.avg_monthly_revenue * 24
            else r.total_revenue
        end                             as projected_ltv,
        -- LTV to CAC ratio bucket
        case
            when r.total_revenue >= 10000 then 'High Value'
            when r.total_revenue >= 3000  then 'Mid Value'
            else 'Low Value'
        end                             as customer_value_tier
    from customers c
    left join customer_subs s 
        on c.customer_id = s.customer_id
    left join customer_revenue r 
        on c.customer_id = r.customer_id
)

select * from final