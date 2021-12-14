select
    CAST(c_name AS text)||'_'||CAST(c_custkey AS text),
    save_circuit(provenance(), 'customer_id', '{path}')    
from
    customer,
    orders,
    lineitem
where
    c_custkey = o_custkey
    and o_orderkey = l_orderkey
    and l_partkey%64=0
group by
    c_name,
    c_custkey,
    o_orderkey,
    o_orderdate,
    o_totalprice
LIMIT 10;