with source as (
    select * from {{ source('raw', 'customers') }}
),

renamed as (
    select
        customer_id,
        company_name,
        industry,
        segment,
        country,
        cast(signup_date as date)     as signup_date,
        acquisition_channel,
        account_manager,
        -- Derived fields
        case 
            when segment = 'Enterprise' then 1
            when segment = 'Mid-Market' then 2
            else 3
        end                           as segment_rank,
        current_timestamp()           as _loaded_at
    from source
)

select * from renamed