select
    l_shipmode,
    save_circuit(provenance(), 'lineitem_id', '{path}')
from
    orders,
    lineitem
where
    o_orderkey = l_orderkey
    and l_shipmode in ('MAIL', 'SHIP')
    and l_commitdate < l_receiptdate
    and l_shipdate < l_commitdate
    and l_receiptdate >= date '1994-01-01'
    and l_receiptdate < date '1994-01-01' + interval '1' year
    and l_partkey%512=0    
group by
    l_shipmode
order by
    l_shipmode