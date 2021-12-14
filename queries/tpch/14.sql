select
    True,
    save_circuit(provenance(), 'lineitem_id', '{path}')
from
    lineitem,
    part
where
    l_partkey = p_partkey
    and l_shipdate >= date '1995-09-01'
    and l_shipdate < date '1995-09-01' + interval '1' month
    and l_partkey%512=0
GROUP BY TRUE