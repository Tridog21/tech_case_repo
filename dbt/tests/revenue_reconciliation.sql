select 1 as failure
where (
    select coalesce(sum(revenue), 0)
    from {{ ref('daily_revenue') }}
) != (
    select coalesce(sum(amount), 0)
    from {{ ref('stg_orders') }}
    where status = 'completed'
)
