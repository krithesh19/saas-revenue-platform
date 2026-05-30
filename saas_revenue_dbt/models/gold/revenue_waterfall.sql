with monthly_mrr as (
    select * from {{ ref('mrr_monthly') }}
),

-- Get each customer's MRR per month
customer_monthly as (
    select
        invoice_month,
        customer_id,
        sum(mrr) as mrr
    from monthly_mrr
    group by 1, 2
),

-- Get previous month MRR per customer
with_prev as (
    select
        curr.invoice_month,
        curr.customer_id,
        curr.mrr                        as current_mrr,
        prev.mrr                        as previous_mrr
    from customer_monthly curr
    left join customer_monthly prev
        on curr.customer_id = prev.customer_id
        and dateadd('month', -1, 
            to_date(curr.invoice_month || '-01')) = 
            to_date(prev.invoice_month || '-01')
),

-- Classify each customer-month
classified as (
    select
        invoice_month,
        customer_id,
        current_mrr,
        previous_mrr,
        case
            when previous_mrr is null 
                then 'New'
            when current_mrr > previous_mrr 
                then 'Expansion'
            when current_mrr < previous_mrr 
                then 'Contraction'
            else 'Retained'
        end                             as mrr_movement_type,
        current_mrr - 
            coalesce(previous_mrr, 0)   as mrr_change
    from with_prev
),

final as (
    select
        invoice_month,
        mrr_movement_type,
        count(distinct customer_id)     as customer_count,
        sum(current_mrr)                as total_mrr,
        sum(mrr_change)                 as mrr_change
    from classified
    group by 1, 2
)

select * from final