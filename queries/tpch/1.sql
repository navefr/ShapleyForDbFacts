select
    CAST(l_returnflag AS text)||'_'||CAST(l_linestatus AS text),
    save_circuit(provenance(), 'lineitem_id', '{path}')
from
    lineitem
where
    l_shipdate <= date '1998-12-01' - interval ':1' day
    and l_partkey%512=0
group by
    l_returnflag,
    l_linestatus
order by
    l_returnflag,
    l_linestatus
LIMIT 100