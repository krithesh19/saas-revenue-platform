with subscriptions as (
    select * from {{ ref('stg_subscriptions') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

churn_base as (
    select
        s.subscription_id,
        s.customer_id,
        c.company_name,
        c.segment,
        c.industry,
        c.country,
        c.acquisition_channel,
        s.plan_name,
        s.mrr,
        s.start_date,
        s.end_date,
        s.status,
        s.tenure_months,
        s.billing_cycle,
        -- Churn month
        case 
            when s.status = 'Churned' 
            then date_trunc('month', s.end_date)
            else null 
        end                             as churn_month,
        -- Churn reason bucket based on tenure
        case
            when s.status = 'Churned' and s.tenure_months <= 3  
                then 'Early Churn'
            when s.status = 'Churned' and s.tenure_months <= 12 
                then 'Mid-Term Churn'
            when s.status = 'Churned' and s.tenure_months > 12  
                then 'Long-Term Churn'
            else 'Active'
        end                             as churn_category,
        -- Revenue lost
        case 
            when s.status = 'Churned' then s.mrr 
            else 0 
        end                             as lost_mrr
    from subscriptions s
    left join customers c 
        on s.customer_id = c.customer_id
),

final as (
    select
        *,
        -- Cohort month (when customer first started)
        date_trunc('month', start_date) as cohort_month
    from churn_base
)

select * from final