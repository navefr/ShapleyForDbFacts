select
    CAST(c_custkey AS text)||'_'||CAST(c_name AS text)||'_'||CAST(c_acctbal AS text)||'_'||CAST(n_name AS text),
    save_circuit(provenance(), 'customer_id', '{path}')
from
    customer,
    orders,
    lineitem,
    nation
where
    c_custkey = o_custkey
    and l_orderkey = o_orderkey
    and o_orderdate >= date '1993-10-01'
    and o_orderdate < date '1993-10-01' + interval '3' month
    and l_returnflag = 'R'
    and c_nationkey = n_nationkey
    and l_partkey%64=0
group by
    c_custkey,
    c_name,
    c_acctbal,
    c_phone,
    n_name,
    c_address,
    c_comment
LIMIT 10;