select
    order_date,
    count(*) as completed_orders,
    sum(amount) as revenue
from {{ ref('stg_orders') }}
where status = 'completed'
group by order_date
