select
    order_id,
    customer_id,
    order_date,
    amount,
    status
from {{ source('raw', 'orders') }}
