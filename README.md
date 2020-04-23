# Episode mining
An inplementation of sequential patterm mining method [1] in Python.

## Installation

```bash
git clone https://github.com/duytri/EpisodeMining.git
cd EpisodeMining
python setup.py install
```
or using pip
```bash
cd EpisodeMining
pip install ./
```

## How to use
1. Set event sequence and episodes

```python
sequence = sorted([
    (31, 'E'), (32, 'D'), (33, 'F'), (35, 'A'), (37, 'B'), (38, 'C'), (39, 'E'),
    (40, 'F'), (42, 'C'), (44, 'D'), (46, 'B'), (47, 'A'), (48, 'D'), (50, 'C'),
    (53, 'E'), (54, 'F'), (55, 'C'), (57, 'B'), (58, 'E'), (59, 'A'), (60, 'E'),
    (61, 'C'), (62, 'F'), (65, 'A'), (67, 'D'),
], key=lambda x:x[0])
```

2. Initialize WINEPI class

```python
>>> from episode_mining.winepi import WINEPI, WinEpiRules
>>> alg = WINEPI(sequence, episode_type='parallel')
# to mine serial episodes, set 'serial' instead of 'parallel'
```

3. Discover frequent (parallel) episodes

```python
>>> freqItems, suppData = alg.WinEpi(width=5, step=1, minFrequent=0.1)
```

4. Generate rules

```python
>>> winepiRules = WinEpiRules(freqItems, suppData, width=5, minConfidence=0.7)
>>> ruleList = winepiRules.generateRules()
>>> winepiRules.printRules(ruleList)

~ Output:
WINEPIRule: ['F'] ==> ['C', 'F'] [5] [0.34146341463414637, 0.7000000000000001]
WINEPIRule: ['E'] ==> ['E', 'C'] [5] [0.3902439024390244, 0.7272727272727273]
WINEPIRule: ['F'] ==> ['E', 'F'] [5] [0.36585365853658536, 0.75]
WINEPIRule: ['E', 'C'] ==> ['E', 'C', 'F'] [5] [0.2926829268292683, 0.7499999999999999]
WINEPIRule: ['E', 'F'] ==> ['E', 'C', 'F'] [5] [0.2926829268292683, 0.7999999999999999]
WINEPIRule: ['C', 'F'] ==> ['E', 'C', 'F'] [5] [0.2926829268292683, 0.857142857142857]
WINEPIRule: ['E', 'B'] ==> ['E', 'B', 'C'] [5] [0.17073170731707318, 0.875]
WINEPIRule: ['B', 'C'] ==> ['E', 'B', 'C'] [5] [0.17073170731707318, 0.7000000000000001]
WINEPIRule: ['E', 'A'] ==> ['E', 'A', 'C'] [5] [0.12195121951219512, 0.7142857142857142]
```

## TODO

* Implement MINEPI method

# Reference
1. H. Mannila, H. Toivonen, and A. I. Verkamo, “Discovery of Frequent Episodes in Event Sequences,” Data Min. Knowl. Discov., vol. 1, no. 3, pp. 259–289, 1997.
