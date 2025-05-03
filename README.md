# piratedb

Builds an SQLite database of items directly from game files.

## Usage
Install Katsuba through PyPi
```
pip install katsuba
```

Head over to the [arrtype repository](https://github.com/wizspoil/arrtype)
and follow README instructions to dump a types JSON from the game client.

Then execute the following commands:

```
# Clone this repository to piratedb/
git clone https://github.com/ItzGray/piratedb
cd piratedb

...
# Copy the game's Root.wad file to piratedb/Root.wad

# Copy previously dumped arrtype file to piratedb/types.json
...

# Now build the db
python -m piratedb

# You will see the database file piratedb/items.db on success.
```

## Notes
This is not fully finished, but I figured I'd drop it on here now anyway. Please forgive my crappy code.

Also, huge thanks to the people who worked on wizdb, without which I would have had no clue where to start. I've mostly labeled this as a fork due to the fact I used so much of that original code it felt wrong to not do so.
