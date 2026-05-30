with source as (
    select * from {{ source('raw', 'invoices') }}
),

renamed as (
    select
        invoice_id,
        subscription_id,
        customer_id,
        cast(invoice_date as date)      as invoice_date,
        invoice_month,
        cast(amount_due as float)       as amount_due,
        cast(amount_paid as float)      as amount_paid,
        payment_status,
        plan_name,
        -- Derived fields
        cast(amount_due as float) - 
        cast(amount_paid as float)      as amount_outstanding,
        case 
            when payment_status = 'Paid' then true 
            else false 
        end                             as is_paid,
        current_timestamp()             as _loaded_at
    from source
)

select * from renamed