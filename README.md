# Lambda, SQLite, and Amazon EFS

## Inspiration

- While working on my [graphql-dynamodb](https://github.com/therastal/graphql-dynamodb) project, I started looking into alternatives to DynamoDB for the underlying datastore (while keeping essentially a key-value structure)
  - I came across [DiskCache](https://github.com/grantjenks/python-diskcache), which got me wondering if I could [use SQLite](https://grantjenks.com/docs/diskcache/sf-python-2017-meetup-talk.html#sqlite) as the underlying key-value store
  - But I still wanted to use AWS Lambda if possible
  - Since [AWS Lambda Functions can have an Amazon Elastic File System mounted to them](https://docs.aws.amazon.com/lambda/latest/dg/services-efs.html), I thought I could possibly use that for storing the SQLite databases

## Development

- EFS mounted to AWS Lambda Function
- "Sharded" by fieldname by creating a new SQLite database for each fieldname
  - I had to use a different implementation for node IDs than I used in my [graphql-dynamodb project](https://github.com/therastal/graphql-dynamodb), since I wanted to get the performance benefits of using an [integer primary key](https://www.sqlite.org/lang_createtable.html#rowid) (aka create my own rowid alias)
  - [Python UUIDs](https://docs.python.org/3.9/library/uuid.html) are too large to store as normal SQLite integers
  - ended up porting Mediagone's [Small UID](https://github.com/Mediagone/small-uid) library for PHP, with some slight modifications to avoid duplicating UIDs when generating thousands per second (see implementation [in this project](/lambdas/graphql/package/uid.py) or [in its own repo](https://github.com/therastal/uid))
- I couldn't use a local script to load the test data like I could with DynamoDB, so I created a [Lambda Function](lambdas/graphql/package/debug.py) for handling the initial load
  - I used Python Threads and Queues to parallelize by fieldname (aka the "shard ID")

## Results

- It worked better than expected! (was honestly surprised that it worked at all 😅)
- I did run into issues when I tried to use SQLite's Write-Ahead Logging ("WAL"), so I stuck with the rollback journal mode
  - [SQLite WAL is documented as not working with NFS](https://www.sqlite.org/wal.html#overview) (see #2 under "disadvantages"), and my guess was that EFS uses something like NFS under the hood, so I wasn't surpised when I ran into issues with it
- It isn't as scalable as DynamoDB (EFS can only handle [35,000 read or 7,000 write IOs per second](https://docs.aws.amazon.com/efs/latest/ug/limits.html#limits-fs-specific)), but it's much cheaper for equivalent amounts of data and traffic
