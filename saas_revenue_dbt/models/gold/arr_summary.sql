with mrr_data as (
    select * from {{ ref('mrr_monthly') }}
),

monthly_summary as (
    select
        invoice_month,
        count(distinct customer_id)     as total_customers,
        sum(mrr)                        as total_mrr,
        sum(arr)                        as total_arr,
        avg(mrr)                        as avg_mrr_per_customer,
        sum(amount_billed)              as total_billed,
        sum(amount_outstanding)         as total_outstanding,
        -- By segment
        sum(case when segment = 'Enterprise' 
            then mrr else 0 end)        as enterprise_mrr,
        sum(case when segment = 'Mid-Market' 
            then mrr else 0 end)        as midmarket_mrr,
        sum(case when segment = 'SMB' 
            then mrr else 0 end)        as smb_mrr,
        -- By plan
        sum(case when plan_name = 'Starter' 
            then mrr else 0 end)        as starter_mrr,
        sum(case when plan_name = 'Growth' 
            then mrr else 0 end)        as growth_mrr,
        sum(case when plan_name = 'Business' 
            then mrr else 0 end)        as business_mrr,
        sum(case when plan_name = 'Enterprise' 
            then mrr else 0 end)        as enterprise_plan_mrr
    from mrr_data
    group by 1
),

final as (
    select
        *,
        -- MoM Growth
        lag(total_mrr) over (
            order by invoice_month)     as prev_month_mrr,
        div0(
            total_mrr - lag(total_mrr) over (order by invoice_month),
            lag(total_mrr) over (order by invoice_month)
        ) * 100                         as mrr_growth_pct
    from monthly_summary
)

select * from final