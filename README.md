# Computing the Shapley Value of Tuples in Query Answering

This repository is the official implementation of "Computing the Shapley Value of Tuples in Query Answering". 


## Requirements

###### Prerequisites

1. Installation of PostgreSQL >= 9.5
2. Installation of [ProvSQL](https://github.com/PierreSenellart/provsql)
3. Installation of [c2d](http://reasoning.cs.ucla.edu/c2d/download.php)


###### Datasets

Download and import the following databases to PostgreSQL.
1. [IMDB](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/2QYZBT) 
2. [TPC-H](https://github.com/tvondra/pg_tpch)

Each table should be tracked by ProvSQL.
```
SET search_path TO public, provsql;

SELECT add_provenance('[Table name]');
SELECT create_provenance_mapping('[Table name]_id', '[Table name]', '[Table primary index]');
```


## Example
[Example.ipynb](notebooks/Example.ipynb) depict how to compute the exact Shapley value of tuples given a provenance as a d-DNNF. 


## Main results
`notebooks` directory depicts subset of the results presented in the paper.

Results include:
* [Exact computation](notebooks/Exact.ipynb) present the computation of exact Shapley values. We investigate the running time as a function of the provenance complexity.
* [Inexact computation](notebooks/Approximate.ipynb) compare several approximation and heuristics over a wide range of metics.