with source as (
    select * from {{ source('raw', 'subscriptions') }}
),

renamed as (
    select
        subscription_id,
        customer_id,
        plan_name,
        cast(mrr as float)              as mrr,
        cast(start_date as date)        as start_date,
        cast(end_date as date)          as end_date,
        status,
        billing_cycle,
        cast(upgraded as boolean)       as is_upgraded,
        cast(discount_pct as float)     as discount_pct,
        -- Derived fields
        case
            when status = 'Active' then true
            else false
        end                             as is_active,
        datediff('month', 
            cast(start_date as date), 
            coalesce(cast(end_date as date), current_date())
        )                               as tenure_months,
        current_timestamp()             as _loaded_at
    from source
)

select * from renamed